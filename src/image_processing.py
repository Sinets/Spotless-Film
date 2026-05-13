#!/usr/bin/env python3
"""
Image Processing for Dust Removal App

Advanced image processing functions matching Spotless-Film's capabilities.
"""

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
import cv2
from typing import Optional, Tuple
import threading
import time


# Import model architecture (copy from notebook)
class UNet(nn.Module):
    def __init__(self):
        super().__init__()

        def conv_block(in_c, out_c):
            return nn.Sequential(
                nn.Conv2d(in_c, out_c, 3, padding=1), nn.ReLU(),
                nn.Conv2d(out_c, out_c, 3, padding=1), nn.ReLU()
            )

        # 1 channel for greyscale
        self.enc1 = conv_block(1, 64)
        self.enc2 = conv_block(64, 128)
        self.enc3 = conv_block(128, 256)
        self.enc4 = conv_block(256, 512)

        self.pool = nn.MaxPool2d(2)

        self.middle = conv_block(512, 1024)

        self.up4 = nn.ConvTranspose2d(1024, 512, 2, stride=2)
        self.dec4 = conv_block(1024, 512)
        self.up3 = nn.ConvTranspose2d(512, 256, 2, stride=2)
        self.dec3 = conv_block(512, 256)
        self.up2 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.dec2 = conv_block(256, 128)
        self.up1 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.dec1 = conv_block(128, 64)

        self.final = nn.Conv2d(64, 1, 1)

    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))

        m = self.middle(self.pool(e4))

        d4 = self.dec4(torch.cat([self.up4(m), e4], dim=1))
        d3 = self.dec3(torch.cat([self.up3(d4), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))

        return torch.sigmoid(self.final(d1))


# IOPaint（原 LaMa Cleaner）优先；不支持时再尝试旧版 lama-cleaner
try:
    from iopaint.model_manager import ModelManager as IOPaintModelManager
    from iopaint.schema import InpaintRequest, HDStrategy, LDMSampler

    IOPAINT_AVAILABLE = True
except ImportError:
    IOPAINT_AVAILABLE = False
    IOPaintModelManager = None  # type: ignore[misc, assignment]
    InpaintRequest = None  # type: ignore[misc, assignment]
    HDStrategy = None  # type: ignore[misc, assignment]
    LDMSampler = None  # type: ignore[misc, assignment]

try:
    from lama_cleaner.model_manager import ModelManager as LegacyLamaModelManager
    from lama_cleaner.schema import Config as LegacyLamaConfig

    LEGACY_LAMA_AVAILABLE = True
except ImportError:
    LEGACY_LAMA_AVAILABLE = False
    LegacyLamaModelManager = None  # type: ignore[misc, assignment]
    LegacyLamaConfig = None  # type: ignore[misc, assignment]


class LamaInpainter:
    """LaMa 图像修复封装：IOPaint → 旧 lama-cleaner → OpenCV."""

    BACKEND_IO_PAINT = "iopaint"
    BACKEND_LEGACY = "lama_cleaner"
    BACKEND_NONE = "none"

    def __init__(self) -> None:
        self.device = torch.device(
            "mps"
            if torch.backends.mps.is_available()
            else "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
        self.available = False
        self.backend = LamaInpainter.BACKEND_NONE
        self.model = None  # IOPaint ModelManager | Legacy Manager
        self._iopaint_request: Optional[object] = None
        self._legacy_config: Optional[object] = None

        if IOPAINT_AVAILABLE:
            try:
                assert IOPaintModelManager is not None and InpaintRequest is not None
                assert HDStrategy is not None and LDMSampler is not None

                mgr = IOPaintModelManager(
                    name="lama",
                    device=self.device,
                    no_half=False,
                    low_mem=True,
                    cpu_offload=False,
                    disable_nsfw_checker=True,
                )
                self._iopaint_request = InpaintRequest(
                    ldm_steps=20,
                    ldm_sampler=LDMSampler.plms.value,
                    hd_strategy=HDStrategy.RESIZE.value,
                    hd_strategy_crop_margin=32,
                    hd_strategy_crop_trigger_size=1024,
                    hd_strategy_resize_limit=2048,
                )
                self.model = mgr
                self.backend = LamaInpainter.BACKEND_IO_PAINT
                self.available = True
                print("✅ LaMa (IOPaint) loaded successfully")
                return
            except Exception as e:
                print(f"IOPaint LaMa unavailable: {e}")

        if LEGACY_LAMA_AVAILABLE:
            try:
                assert LegacyLamaModelManager is not None and LegacyLamaConfig is not None
                self.model = LegacyLamaModelManager(
                    name="lama",
                    device=self.device,
                    no_half=False,
                    low_mem=True,
                    cpu_offload=False,
                    disable_nsfw=True,
                )
                self._legacy_config = LegacyLamaConfig(
                    ldm_steps=20,
                    ldm_sampler="plms",
                    hd_strategy="Resize",
                    hd_strategy_crop_margin=32,
                    hd_strategy_crop_trigger_size=1024,
                    hd_strategy_resize_limit=2048,
                )
                self.backend = LamaInpainter.BACKEND_LEGACY
                self.available = True
                print("✅ LaMa (lama-cleaner) loaded successfully")
            except Exception as e:
                print(f"Legacy lama-cleaner failed: {e}")
                self.available = False
    
    def inpaint(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        """LaMa；失败或未安装时退回 OpenCV TELEA."""
        if not self.available:
            return self._fallback_inpaint(image, mask)
        
        try:
            image_np = np.asarray(image.convert("RGB"), dtype=np.uint8)
            mask_np = np.asarray(mask.convert("L"), dtype=np.uint8)
            if mask_np.ndim != 2:
                mask_np = mask_np.squeeze()
            # 与 IOPaint erase 模型一致：255 = 修补区域；全 0 时直接跳过
            if not mask_np.any():
                return image.convert("RGB")

            if self.backend == LamaInpainter.BACKEND_IO_PAINT:
                assert self.model is not None and self._iopaint_request is not None
                # ModelManager.__call__ 返回 BGR uint8
                result_bgr = self.model(image_np, mask_np, self._iopaint_request)
                result_rgb = cv2.cvtColor(np.asarray(result_bgr), cv2.COLOR_BGR2RGB)
                return Image.fromarray(result_rgb)

            if self.backend == LamaInpainter.BACKEND_LEGACY:
                assert self.model is not None and self._legacy_config is not None
                legacy_out = self.model(image_np, mask_np, self._legacy_config)
                if hasattr(legacy_out, "convert"):
                    return legacy_out.convert("RGB")
                return Image.fromarray(np.asarray(legacy_out))
            
            return self._fallback_inpaint(image, mask)

        except Exception as e:
            print(f"LaMa failed: {e}, falling back to CV2")
            return self._fallback_inpaint(image, mask)

    @staticmethod
    def cv2_inpaint_telex(
        image: Image.Image,
        mask: Image.Image,
        radius: int = 5,
    ) -> Image.Image:
        """单遍 CV2 TELEA（导出给 UI 在非 LaMa 环境复用同一实现）."""
        image_np = np.asarray(image.convert("RGB"), dtype=np.uint8)
        mask_np = np.asarray(mask.convert("L"), dtype=np.uint8)
        result = cv2.inpaint(
            image_np, mask_np, inpaintRadius=radius, flags=cv2.INPAINT_TELEA
        )
        return Image.fromarray(result)
    
    def _fallback_inpaint(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        """TELEA 单遍 OpenCV inpainting."""
        out = LamaInpainter.cv2_inpaint_telex(image, mask, radius=5)
        print("✅ Fallback CV2 TELEA inpainting (radius=5)")
        return out


class ImageProcessingService:
    """Service for handling image processing operations"""
    
    @staticmethod
    def load_model(weights_path: str, device: torch.device) -> UNet:
        """Load U-Net model from weights file (exact match to main.ipynb architecture)"""
        try:
            print(f"🔍 Loading model from: {weights_path}")
            print(f"🔍 Device: {device}")
            
            # Create model with exact same architecture as main.ipynb
            model = UNet()
            
            # Load weights (map to device)
            state_dict = torch.load(weights_path, map_location=device)
            model.load_state_dict(state_dict)
            
            # Move to device and set to eval mode
            model.to(device)
            model.eval()
            
            print(f"✅ Model loaded successfully from {weights_path}")
            print(f"✅ Model is on device: {next(model.parameters()).device}")
            
            # Test model with dummy input to verify it works
            with torch.no_grad():
                test_input = torch.randn(1, 1, 1024, 1024).to(device)
                test_output = model(test_input)
                print(f"✅ Model test successful - Output shape: {test_output.shape}")
                print(f"✅ Output range: {test_output.min():.6f} to {test_output.max():.6f}")
            
            return model
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    @staticmethod
    def predict_dust_mask(model: UNet, image_path_or_image, threshold: float = 0.5, 
                         window_size: int = 1024, stride: int = 512, 
                         device: torch.device = None, progress_callback: Optional[callable] = None) -> np.ndarray:
        """
        Fast path: scale the original image to 1024x1024 (squeezed), run once,
        then scale the probability map back to the original resolution.

        window_size/stride are ignored in this mode (kept for API compatibility).
        """
        if device is None:
            device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

        # Load image in grayscale
        if isinstance(image_path_or_image, str):
            image = Image.open(image_path_or_image).convert('L')
        else:
            image = image_path_or_image.convert('L') if image_path_or_image.mode != 'L' else image_path_or_image

        orig_w, orig_h = image.size
        print(f"🔍 Input image size: {orig_w}x{orig_h}")

        # Force-resize to 1024x1024 (squeezed if necessary)
        target = 1024
        image_1024 = image.resize((target, target), Image.Resampling.BILINEAR)

        img_np = np.array(image_1024, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(img_np).unsqueeze(0).unsqueeze(0).to(device)

        if progress_callback:
            progress_callback(0.1)

        with torch.no_grad():
            pred = model(tensor)
            pred_np = pred.squeeze().detach().cpu().numpy().astype(np.float32)

        if progress_callback:
            progress_callback(0.7)

        # Resize prediction back to original dimensions (stretch back)
        up_pred = cv2.resize(pred_np, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR).astype(np.float32)

        if progress_callback:
            progress_callback(1.0)

        print(f"🔍 Final prediction shape: {up_pred.shape}")
        print(f"🔍 Prediction range: {up_pred.min():.6f} to {up_pred.max():.6f}")
        return up_pred
    
    @staticmethod
    def create_binary_mask(prediction: np.ndarray, threshold: float, 
                          original_size: Tuple[int, int]) -> Image.Image:
        """Create binary mask from prediction (matches Swift ImageProcessingService)"""
        print(f"🎯 Creating binary mask with threshold {threshold:.3f}")
        print(f"🔍 Prediction shape: {prediction.shape}, Original size: {original_size}")
        
        # Handle different prediction shapes (from PyTorch model)
        if len(prediction.shape) == 4:
            # Shape is typically (1, 1, H, W) from PyTorch
            prediction = prediction.squeeze()
        elif len(prediction.shape) == 3:
            # Shape might be (1, H, W)
            prediction = prediction.squeeze()
        elif len(prediction.shape) == 2:
            # Already (H, W)
            pass
        else:
            print(f"❌ Unexpected prediction shape: {prediction.shape}")
            return None
        
        print(f"🔍 Final prediction shape: {prediction.shape}")
        
        # Apply threshold (matches Swift app logic exactly)
        binary_mask = (prediction > threshold).astype(np.uint8) * 255
        
        # DEBUG: Print non-black pixel count
        non_black_pixels = (binary_mask > 0).sum()
        total_pixels = binary_mask.size
        percentage = (non_black_pixels / total_pixels) * 100
        print(f"🎯 DUST DETECTION: {non_black_pixels:,} non-black pixels out of {total_pixels:,} ({percentage:.2f}%)")
        
        # Convert to PIL Image
        mask_image = Image.fromarray(binary_mask, mode='L')
        
        print(f"🔍 Created mask size: {mask_image.size}")
        
        # Resize to original image size if needed
        if mask_image.size != original_size:
            print(f"🔍 Resizing mask from {mask_image.size} to {original_size}")
            mask_image = mask_image.resize(original_size, Image.Resampling.NEAREST)
            
            # DEBUG: Re-check after resize
            final_mask_array = np.array(mask_image)
            final_non_black = (final_mask_array > 0).sum()
            final_percentage = (final_non_black / final_mask_array.size) * 100
            print(f"🎯 FINAL DUST MASK: {final_non_black:,} non-black pixels ({final_percentage:.2f}%)")
        
        print(f"✅ Binary mask created: {mask_image.size}")
        return mask_image
    
    @staticmethod
    def dilate_mask(mask: Image.Image, kernel_size: int = 5) -> Image.Image:
        """Dilate mask for better inpainting coverage (fixed radius by default)."""
        # Convert to numpy
        mask_np = np.array(mask.convert('L'))
        
        # Use a fixed elliptical kernel size
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        
        # Apply dilation
        dilated = cv2.dilate(mask_np, kernel, iterations=1)
        
        print(f"🔍 Dilated mask with {kernel_size}x{kernel_size} kernel")
        
        return Image.fromarray(dilated, mode='L')
    
    @staticmethod
    def blend_images(original: Image.Image, inpainted: Image.Image, 
                    mask: Image.Image) -> Image.Image:
        """Blend original and inpainted images using mask"""
        # Ensure all images are same size and mode
        original = original.convert('RGB')
        inpainted = inpainted.convert('RGB')
        mask = mask.convert('L')
        
        # Resize inpainted and mask to match original if needed
        if inpainted.size != original.size:
            inpainted = inpainted.resize(original.size, Image.Resampling.LANCZOS)
        if mask.size != original.size:
            mask = mask.resize(original.size, Image.NEAREST)
        
        # Convert to numpy arrays
        orig_np = np.array(original, dtype=np.float32)
        inpaint_np = np.array(inpainted, dtype=np.float32)
        mask_np = np.array(mask, dtype=np.float32) / 255.0
        
        # Expand mask to 3 channels
        mask_3d = np.stack([mask_np] * 3, axis=2)
        
        # Blend: use inpainted where mask is white, original elsewhere
        blended = orig_np * (1 - mask_3d) + inpaint_np * mask_3d
        
        # Convert back to PIL
        result = Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8))
        
        print("✅ Images blended successfully")
        return result


class BrushTools:
    """Tools for brush and eraser operations on masks"""
    
    @staticmethod
    def apply_circular_brush(mask: Image.Image, center: Tuple[float, float], 
                           radius: int, is_erasing: bool = True) -> Image.Image:
        """Apply circular brush stroke to mask"""
        # Convert to numpy for processing
        mask_np = np.array(mask.convert('L'))
        h, w = mask_np.shape
        
        # Convert center to integer coordinates
        cx, cy = int(center[0]), int(center[1])
        
        # Bounds check
        if cx < 0 or cx >= w or cy < 0 or cy >= h:
            return mask
        
        # Create circular brush
        y, x = np.ogrid[:h, :w]
        mask_circle = (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2
        
        # Apply brush
        if is_erasing:
            mask_np[mask_circle] = 0  # Erase (set to black)
        else:
            mask_np[mask_circle] = 255  # Add dust (set to white)
        
        return Image.fromarray(mask_np, mode='L')
    
    @staticmethod
    def interpolated_stroke(mask: Image.Image, start_point: Tuple[float, float],
                          end_point: Tuple[float, float], radius: int, 
                          is_erasing: bool = True) -> Image.Image:
        """Apply interpolated stroke between two points"""
        # Calculate distance and steps
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        distance = np.sqrt(dx * dx + dy * dy)
        
        if distance < 1.0:
            # Single point application
            return BrushTools.apply_circular_brush(mask, end_point, radius, is_erasing)
        
        # Calculate number of steps based on brush size
        spacing = max(1.0, radius * 0.25)
        steps = max(1, int(distance / spacing))
        
        # Apply brush at interpolated points
        current_mask = mask
        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            interp_point = (
                start_point[0] + t * dx,
                start_point[1] + t * dy
            )
            current_mask = BrushTools.apply_circular_brush(
                current_mask, interp_point, radius, is_erasing
            )
        
        return current_mask


class ProcessingTask:
    """Async processing task wrapper"""
    
    def __init__(self, target_func, args=(), kwargs=None, callback=None, error_callback=None):
        self.target_func = target_func
        self.args = args
        self.kwargs = kwargs or {}
        self.callback = callback
        self.error_callback = error_callback
        self.thread = None
        self.result = None
        self.error = None
        self.completed = False
    
    def start(self):
        """Start the processing task"""
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
    
    def _run(self):
        """Run the task in background thread"""
        try:
            print("🧵 ProcessingTask thread started")
            start_time = time.time()
            self.result = self.target_func(*self.args, **self.kwargs)
            end_time = time.time()
            
            print(f"🧵 ProcessingTask completed, result type: {type(self.result)}")
            self.completed = True
            
            if self.callback:
                print("🧵 Calling completion callback...")
                self.callback(self.result, end_time - start_time)
            else:
                print("🧵 No callback provided")
        except Exception as e:
            print(f"🧵 ProcessingTask error: {e}")
            self.error = e
            self.completed = True
            
            if self.error_callback:
                print("🧵 Calling error callback...")
                self.error_callback(e)
            else:
                print("🧵 No error callback provided")
    
    def is_running(self) -> bool:
        """Check if task is still running"""
        return self.thread is not None and self.thread.is_alive()
    
    def join(self, timeout=None):
        """Wait for task completion"""
        if self.thread:
            self.thread.join(timeout)
