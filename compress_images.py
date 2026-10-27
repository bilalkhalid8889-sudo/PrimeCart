"""
PrimeCart Image Compressor
==========================
Compresses all product images to WebP format.
Typically reduces file size by 60-80% with no visible quality loss.

HOW TO USE:
1. Make sure Python is installed (it usually is on Windows/Mac/Linux)
2. Install Pillow:  pip install Pillow
3. Put this file next to your "images" folder
4. Run:  python compress_images.py

Your original images are kept safe in "images_backup" folder.
New compressed images replace the originals in "images" folder.
"""

import os
import shutil
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is not installed.")
    print("Run this command first:  pip install Pillow")
    exit(1)

# ── Settings ──────────────────────────────────────────────────────────────────
IMAGES_FOLDER   = "images"          # your images folder name
BACKUP_FOLDER   = "images_backup"   # backup folder (created automatically)
QUALITY         = 82                # 80-85 is ideal: great quality, small size
MAX_WIDTH       = 800               # resize if wider than this (saves more space)
MAX_HEIGHT      = 800               # resize if taller than this
CONVERT_TO_WEBP = False             # True = convert to .webp (best compression)
                                    # False = keep original format (safer option)
# ──────────────────────────────────────────────────────────────────────────────

SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'}

def format_size(bytes):
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes/1024:.1f} KB"
    else:
        return f"{bytes/1024/1024:.2f} MB"

def compress_images():
    images_path = Path(IMAGES_FOLDER)
    backup_path = Path(BACKUP_FOLDER)

    if not images_path.exists():
        print(f"ERROR: '{IMAGES_FOLDER}' folder not found.")
        print("Make sure this script is in the same folder as your 'images' folder.")
        return

    # Collect all image files
    all_images = [
        f for f in images_path.rglob("*")
        if f.suffix.lower() in SUPPORTED and f.is_file()
    ]

    if not all_images:
        print(f"No images found in '{IMAGES_FOLDER}' folder.")
        return

    print(f"Found {len(all_images)} images to compress.\n")

    # Create backup
    if not backup_path.exists():
        print(f"Creating backup in '{BACKUP_FOLDER}'...")
        shutil.copytree(images_path, backup_path)
        print(f"Backup created! Your originals are safe.\n")
    else:
        print(f"Backup folder already exists, skipping backup.\n")

    total_before = 0
    total_after  = 0
    success      = 0
    failed       = 0

    for i, img_path in enumerate(all_images, 1):
        try:
            size_before = img_path.stat().st_size
            total_before += size_before

            with Image.open(img_path) as img:
                # Convert RGBA/palette to RGB for JPEG compatibility
                if img.mode in ('RGBA', 'P', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Resize if too large (preserves aspect ratio)
                if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
                    img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.LANCZOS)

                if CONVERT_TO_WEBP:
                    # Save as WebP
                    out_path = img_path.with_suffix('.webp')
                    img.save(out_path, 'WEBP', quality=QUALITY, method=6)
                    if out_path != img_path:
                        img_path.unlink()  # remove old file
                    save_path = out_path
                else:
                    # Save in original format
                    ext = img_path.suffix.lower()
                    if ext in ('.jpg', '.jpeg'):
                        img.save(img_path, 'JPEG', quality=QUALITY,
                                 optimize=True, progressive=True)
                    elif ext == '.png':
                        img.save(img_path, 'PNG', optimize=True, compress_level=7)
                    elif ext == '.webp':
                        img.save(img_path, 'WEBP', quality=QUALITY, method=6)
                    save_path = img_path

            size_after = save_path.stat().st_size
            total_after += size_after
            saving_pct = (1 - size_after / size_before) * 100 if size_before > 0 else 0
            success += 1

            # Progress every 50 images
            if i % 50 == 0 or i == len(all_images):
                print(f"  [{i}/{len(all_images)}] {img_path.name} "
                      f"  {format_size(size_before)} → {format_size(size_after)} "
                      f"  ({saving_pct:.0f}% smaller)")

        except Exception as e:
            print(f"  SKIP {img_path.name}: {e}")
            failed += 1

    # Summary
    print("\n" + "="*55)
    print("  COMPRESSION COMPLETE")
    print("="*55)
    print(f"  Images processed : {success}")
    if failed:
        print(f"  Images skipped   : {failed}")
    print(f"  Size before      : {format_size(total_before)}")
    print(f"  Size after       : {format_size(total_after)}")
    saved = total_before - total_after
    pct   = (saved / total_before * 100) if total_before > 0 else 0
    print(f"  Space saved      : {format_size(saved)} ({pct:.1f}% reduction)")
    print("="*55)
    print(f"\n  Originals backed up in: {BACKUP_FOLDER}/")
    if CONVERT_TO_WEBP:
        print("\n  NOTE: Images converted to .webp")
        print("  Update your HTML: change image extensions to .webp")
        print("  OR set CONVERT_TO_WEBP = False to keep original formats.")

if __name__ == "__main__":
    compress_images()