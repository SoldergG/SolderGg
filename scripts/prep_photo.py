#!/usr/bin/env python3
"""Prep a source photo for ASCII conversion.

1. Remove the background (rembg) so only the subject remains.
2. Boost local contrast with CLAHE — a flatly-lit face converts to a dark,
   unreadable blob otherwise; this is what gives it real highlights/shadows.
3. Composite onto pure white so the background maps to the blank end of the
   ASCII ramp (white -> spaces).

Usage: python scripts/prep_photo.py source-photo.jpg
Writes: source-prepped.png (grayscale)
"""
import io
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps
from rembg import remove

OUT_PATH = Path(__file__).resolve().parent.parent / "source-prepped.png"


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <source-photo>", file=sys.stderr)
        sys.exit(1)

    src_path = Path(sys.argv[1])

    # normalize EXIF rotation before anything else touches the pixels
    upright = ImageOps.exif_transpose(Image.open(src_path)).convert("RGB")
    buf = io.BytesIO()
    upright.save(buf, format="PNG")
    input_bytes = buf.getvalue()

    # 1. isolate the subject
    cutout_bytes = remove(input_bytes)
    rgba = Image.open(io.BytesIO(cutout_bytes)).convert("RGBA")
    rgba_arr = np.array(rgba)
    alpha = rgba_arr[:, :, 3].astype(np.float32) / 255.0

    # 2. CLAHE contrast boost on the grayscale subject
    gray = cv2.cvtColor(rgba_arr[:, :, :3], cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray).astype(np.float32)

    # 3. composite onto pure white using the cutout's alpha mask
    white = np.full_like(gray_eq, 255.0)
    composited = (gray_eq * alpha + white * (1 - alpha)).astype(np.uint8)

    Image.fromarray(composited, mode="L").save(OUT_PATH)
    print(f"Wrote {OUT_PATH} ({rgba.width}x{rgba.height})")


if __name__ == "__main__":
    main()
