U-Net weights for Spotless Film
================================

Put PyTorch checkpoints (*.pth) here when developing from src/:

  Preferred filename (notebook default): v5_bce_unet_epoch30.pth

Other names are accepted; the app searches for v5_*.pth, v6_*.pth, *unet*.pth, then any *.pth.

Bundled macOS app (PyInstaller)
--------------------------------
If this folder exists and contains *.pth before you run PyInstaller, those files are copied into the
.app bundle automatically (see spotless_film.spec).

If you ship the app without bundled weights
-------------------------------------------
Create a folder named "weights" in the SAME directory as SpotlessFilm.app (sibling folder), for example:

  dist/
    SpotlessFilm.app
    weights/
      v5_bce_unet_epoch30.pth

Restart the application after copying the files.
