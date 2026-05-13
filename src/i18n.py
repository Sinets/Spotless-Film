#!/usr/bin/env python3
"""Spotless Film UI strings (English + 中文)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Final, List, Tuple

CONFIG_DIR: Final = Path.home() / ".config" / "spotless_film"
LOCALE_FILE: Final = CONFIG_DIR / "locale.json"

# Segment / display labels (value shown in UI → locale code)
LANGUAGE_CHOICES: Final[List[Tuple[str, str]]] = [
    ("en", "English"),
    ("zh", "中文"),
]

MESSAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "window.title": "✨ Spotless Film - AI-Powered Film Restoration",
        "app.title": "✨ Dust Remover",
        "app.subtitle": "AI-powered film restoration",
        "settings.language": "Language",
        "section.import": "Import",
        "section.detection": "Detection",
        "section.dust_removal": "Dust Removal",
        "import.no_image": "○ No image selected",
        "import.image_loaded": "● Image loaded",
        "import.choose_file": "📁 Choose File",
        "import.loading": "📁 Loading…",
        "import.size": "Size:",
        "import.format": "Format:",
        "detection.detect": "🔍 Detect Dust",
        "detection.detecting": "🔍 Detecting…",
        "removal.remove": "✨ Remove Dust",
        "removal.removing": "✨ Removing…",
        "removal.removing_elapsed": "✨ Removing… ({seconds}s)",
        "sensitivity.title": "🎯 Sensitivity",
        "sensitivity.less": "Less sensitive",
        "sensitivity.more": "More sensitive",
        "sensitivity.hint": "Adjust to fine-tune dust detection",
        "removal.time_label": "Processing time:",
        "toolbar.eraser": "Eraser",
        "toolbar.brush": "Brush",
        "toolbar.size": "Size:",
        "toolbar.export": "💾 Export",
        "toolbar.overlay": "👁 Overlay",
        "toolbar.overlay_hidden": "👁 Hidden",
        "view.single": "🔍 Single",
        "view.side_by_side": "🔄 Side by side",
        "view.split": "✂️ Split view",
        "toolbar.opacity": "Opacity",
        "status.device": "Device:",
        "status.ready": "Ready — import an image to begin",
        "status.ready_drag": "Ready — drag an image or use Import",
        "status.unet_loaded": "U‑Net model loaded",
        "status.no_model": "No model — put .pth files in weights/ next to SpotlessFilm.app",
        "status.no_model_found": "No model file found",
        "status.model_load_failed": "Model loading failed",
        "status.error": "Error occurred",
        "status.image_loaded": "Image loaded: {name}",
        "status.detect_progress": "Detecting dust… {pct}%",
        "status.detect_done": "Dust detected in {time:.2f}s",
        "status.remove_done": "Dust removed in {time:.2f}s",
        "status.remove_working": "Removing dust… ({seconds}s)",
        "status.saved": "Image saved: {name}",
        "lama.loading": "LaMa: Loading…",
        "lama.available": "LaMa: ✅ Available",
        "lama.unavailable": "LaMa: ❌ Unavailable",
        "canvas.title": "Spotless Film",
        "canvas.drop_hint": "Drag and drop an image here to begin",
        "canvas.import_hint": "Or use the Import button",
        "canvas.formats": "Supported formats: PNG, JPEG, TIFF, BMP",
        "canvas.original": "Original",
        "canvas.processed": "Processed",
        "canvas.process_placeholder": "Process the image to see the result",
        "dialog.error": "Error",
        "dialog.warning": "Warning",
        "dialog.export_warning": "Export warning",
        "dialog.export_success": "Export successful",
        "dialog.export_error": "Export error",
        "dialog.fatal": "Fatal error",
        "dialog.startup_error": "Startup error",
        "dialog.file_dialog_failed": "Failed to open file dialog: {detail}",
        "dialog.drop_invalid": "Please drop a valid image file",
        "dialog.no_export": "No processed image to export",
        "dialog.no_export_detail": "No processed image to export. Please process an image first.",
        "dialog.export_ok": "Image exported successfully to:\n{path}",
        "dialog.export_failed": "Failed to export image: {detail}",
        "dialog.app_error": "Application error: {detail}",
        "dialog.start_failed": "Failed to start application: {detail}",
        "file.select_image": "Select image",
        "file.image_files": "Image files",
        "file.jpeg": "JPEG files",
        "file.png": "PNG files",
        "file.tiff": "TIFF files",
        "file.all": "All files",
        "file.save_processed": "Save processed image",
        "file.export_full": "Export full resolution image",
        "err.load_image": "Failed to load image: {detail}",
        "op.dust_detection": "dust detection",
        "op.dust_removal": "dust removal",
        "err.operation_failed": "{operation} failed: {detail}",
    },
    "zh": {
        "window.title": "✨ Spotless Film - AI 胶片修复",
        "app.title": "✨ 除尘工具",
        "app.subtitle": "AI 驱动的胶片修复",
        "settings.language": "语言",
        "section.import": "导入",
        "section.detection": "检测",
        "section.dust_removal": "除尘",
        "import.no_image": "○ 尚未选择图片",
        "import.image_loaded": "● 图片已加载",
        "import.choose_file": "📁 选择文件",
        "import.loading": "📁 正在加载…",
        "import.size": "尺寸:",
        "import.format": "格式:",
        "detection.detect": "🔍 检测尘埃",
        "detection.detecting": "🔍 正在检测…",
        "removal.remove": "✨ 去除尘埃",
        "removal.removing": "✨ 正在去除…",
        "removal.removing_elapsed": "✨ 正在去除…（已 {seconds}s）",
        "sensitivity.title": "🎯 灵敏度",
        "sensitivity.less": "低灵敏度",
        "sensitivity.more": "高灵敏度",
        "sensitivity.hint": "拖动以微调尘埃检测",
        "removal.time_label": "处理耗时:",
        "toolbar.eraser": "橡皮擦",
        "toolbar.brush": "笔刷",
        "toolbar.size": "大小:",
        "toolbar.export": "💾 导出",
        "toolbar.overlay": "👁 叠加",
        "toolbar.overlay_hidden": "👁 已隐藏",
        "view.single": "🔍 单图",
        "view.side_by_side": "🔄 并排",
        "view.split": "✂️ 拆分",
        "toolbar.opacity": "不透明度",
        "status.device": "设备:",
        "status.ready": "就绪 — 请导入图片开始",
        "status.ready_drag": "就绪 — 拖入图片或使用导入",
        "status.unet_loaded": "U‑Net 模型已加载",
        "status.no_model": "未找到模型 — 请将 .pth 放在与 SpotlessFilm.app 同级的 weights 文件夹",
        "status.no_model_found": "未找到模型文件",
        "status.model_load_failed": "模型加载失败",
        "status.error": "发生错误",
        "status.image_loaded": "图片已加载: {name}",
        "status.detect_progress": "正在检测尘埃… {pct}%",
        "status.detect_done": "检测完成，用时 {time:.2f}s",
        "status.remove_done": "除尘完成，用时 {time:.2f}s",
        "status.remove_working": "正在除尘…（已 {seconds}s）",
        "status.saved": "图片已保存: {name}",
        "lama.loading": "LaMa: 加载中…",
        "lama.available": "LaMa: ✅ 可用",
        "lama.unavailable": "LaMa: ❌ 不可用",
        "canvas.title": "Spotless Film",
        "canvas.drop_hint": "将图片拖放到此处开始",
        "canvas.import_hint": "或使用左侧「导入」按钮",
        "canvas.formats": "支持格式: PNG、JPEG、TIFF、BMP",
        "canvas.original": "原图",
        "canvas.processed": "处理后",
        "canvas.process_placeholder": "请先处理图片以查看结果",
        "dialog.error": "错误",
        "dialog.warning": "警告",
        "dialog.export_warning": "导出提示",
        "dialog.export_success": "导出成功",
        "dialog.export_error": "导出错误",
        "dialog.fatal": "严重错误",
        "dialog.startup_error": "启动错误",
        "dialog.file_dialog_failed": "无法打开文件对话框: {detail}",
        "dialog.drop_invalid": "请拖放有效的图片文件",
        "dialog.no_export": "没有可导出的处理结果",
        "dialog.no_export_detail": "没有可导出的处理结果，请先处理图片。",
        "dialog.export_ok": "图片已成功导出到:\n{path}",
        "dialog.export_failed": "导出失败: {detail}",
        "dialog.app_error": "应用错误: {detail}",
        "dialog.start_failed": "无法启动应用: {detail}",
        "file.select_image": "选择图片",
        "file.image_files": "图片文件",
        "file.jpeg": "JPEG 图片",
        "file.png": "PNG 图片",
        "file.tiff": "TIFF 图片",
        "file.all": "所有文件",
        "file.save_processed": "保存处理后的图片",
        "file.export_full": "导出全分辨率图片",
        "err.load_image": "加载图片失败: {detail}",
        "op.dust_detection": "尘埃检测",
        "op.dust_removal": "除尘",
        "err.operation_failed": "{operation}失败: {detail}",
    },
}


class I18n:
    """Minimal gettext-style helper with JSON persistence."""

    def __init__(self, locale: str = "en") -> None:
        self.locale = locale if locale in MESSAGES else "en"

    @classmethod
    def load(cls) -> I18n:
        if LOCALE_FILE.exists():
            try:
                data = json.loads(LOCALE_FILE.read_text(encoding="utf-8"))
                loc = str(data.get("locale", "en"))
                return cls(loc)
            except (OSError, json.JSONDecodeError, TypeError):
                pass
        return cls("en")

    def save(self) -> None:
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            LOCALE_FILE.write_text(
                json.dumps({"locale": self.locale}, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def set_locale(self, locale: str) -> None:
        if locale in MESSAGES:
            self.locale = locale
            self.save()

    def t(self, key: str, **kwargs: Any) -> str:
        table = MESSAGES.get(self.locale) or MESSAGES["en"]
        text = table.get(key)
        if text is None:
            text = MESSAGES["en"].get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text

    @staticmethod
    def language_labels() -> List[str]:
        return [label for _, label in LANGUAGE_CHOICES]

    def label_for_locale(self) -> str:
        for code, label in LANGUAGE_CHOICES:
            if code == self.locale:
                return label
        return LANGUAGE_CHOICES[0][1]

    @staticmethod
    def locale_from_label(label: str) -> str:
        for code, lab in LANGUAGE_CHOICES:
            if lab == label:
                return code
        return "en"
