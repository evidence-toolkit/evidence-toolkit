#!/usr/bin/env python3
"""Create test case by randomly sampling images from existing case

This script randomly selects N images from an existing case (like BCH with 1000+ images)
and creates copies with new SHA256 hashes via metadata modification. This allows fast
performance testing without analyzing real evidence or generating synthetic images.

Usage:
    # Sample 10 random images from BCH case (default)
    python create_test_images.py

    # Sample 20 random images from BCH case
    python create_test_images.py --count 20

    # Sample from different case directory
    python create_test_images.py --source-case data/cases/OTHER-CASE

The script will:
1. Find all images in the source case directory
2. Randomly select N images
3. Copy them with modified metadata to ensure unique SHA256 hashes
4. Set up a test case directory for performance testing
"""

import hashlib
import shutil
import random
from pathlib import Path
from PIL import Image, PngImagePlugin
import argparse


def add_random_metadata(image_path: Path, output_path: Path) -> str:
    """Add random metadata to image to create unique SHA256 hash

    Args:
        image_path: Source image path
        output_path: Destination image path with modified metadata

    Returns:
        SHA256 hash of the new image
    """
    # Open image
    img = Image.open(image_path)

    # Add random metadata to PNG
    meta = PngImagePlugin.PngInfo()
    meta.add_text("test_id", f"{random.randint(10000, 99999)}")
    meta.add_text("timestamp", f"{random.random()}")
    meta.add_text("random_data", f"{random.getrandbits(256)}")

    # Save with metadata
    img.save(output_path, "PNG", pnginfo=meta)

    # Calculate SHA256
    sha256 = hashlib.sha256()
    with open(output_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


def find_images_in_case(case_dir: Path) -> list[Path]:
    """Find all images in a case directory

    Args:
        case_dir: Path to case directory

    Returns:
        List of image file paths
    """
    if not case_dir.exists():
        return []

    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    images = []

    for file in case_dir.rglob('*'):
        if file.is_file() and file.suffix.lower() in image_extensions:
            images.append(file)

    return images


def create_test_case(source_images: list[Path], count: int = 10, output_dir: Path = Path("data/cases/PARALLEL-TEST")):
    """Create test case by randomly sampling from source images

    Args:
        source_images: List of source images to sample from
        count: Number of test images to create
        output_dir: Output directory for test case
    """
    print(f"🎨 Creating test case with {count} images...")
    print(f"   Sampling from {len(source_images)} available images")
    print(f"   Output: {output_dir}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Randomly sample images
    if count > len(source_images):
        print(f"   ⚠️  Requested {count} images but only {len(source_images)} available")
        count = len(source_images)

    sampled_images = random.sample(source_images, count)

    # Create unique images
    created_files = []
    sha256_hashes = []

    for i, source_image in enumerate(sampled_images, 1):
        # Preserve original extension
        output_path = output_dir / f"test_image_{i:02d}{source_image.suffix}"

        print(f"   Copying image {i}/{count} ({source_image.name})...", end='\r')

        # Copy with modified metadata to create unique hash
        sha256 = add_random_metadata(source_image, output_path)

        created_files.append(output_path)
        sha256_hashes.append(sha256)

    print(f"\n   ✅ Created {count} unique images")

    # Print SHA256 hashes for verification
    print(f"\n📋 Generated SHA256 hashes:")
    for i, (file, sha256) in enumerate(zip(created_files, sha256_hashes), 1):
        print(f"   {i:2d}. {file.name}: {sha256[:16]}...")

    # Verify all hashes are unique
    if len(set(sha256_hashes)) == len(sha256_hashes):
        print(f"\n   ✅ All {count} hashes are unique")
    else:
        print(f"\n   ⚠️  Warning: Some hashes are duplicates!")

    return created_files, sha256_hashes


def main():
    parser = argparse.ArgumentParser(description="Sample random images from existing case for testing")
    parser.add_argument('--source-case', type=Path, default=Path("data/cases/BCH_WORKPLACE_2025_2"),
                       help='Source case directory to sample from (default: data/cases/BCH_WORKPLACE_2025_2)')
    parser.add_argument('--count', type=int, default=10, help='Number of test images (default: 10)')
    parser.add_argument('--output-dir', type=Path, default=Path("data/cases/PARALLEL-TEST"),
                       help='Output directory (default: data/cases/PARALLEL-TEST)')

    args = parser.parse_args()

    print("=" * 70)
    print("🧪 TEST CASE GENERATOR - Random Image Sampling")
    print("=" * 70)

    # Find images in source case
    print(f"\n🔍 Scanning for images in {args.source_case}...")

    if not args.source_case.exists():
        print(f"\n❌ Source case directory not found: {args.source_case}")
        print(f"   Available cases:")
        cases_dir = Path("data/cases")
        if cases_dir.exists():
            for case in sorted(cases_dir.iterdir()):
                if case.is_dir():
                    print(f"   - {case}")
        return

    source_images = find_images_in_case(args.source_case)

    if not source_images:
        print(f"\n❌ No images found in {args.source_case}")
        return

    print(f"   ✅ Found {len(source_images)} images")

    # Create test case
    print()
    created_files, sha256_hashes = create_test_case(
        source_images,
        count=args.count,
        output_dir=args.output_dir
    )

    # Print usage instructions
    print("\n" + "=" * 70)
    print("✅ TEST CASE READY")
    print("=" * 70)

    print(f"\n📁 Test case directory: {args.output_dir}")
    print(f"📊 Image count: {len(created_files)}")

    print("\n🚀 Run parallel processing test:")
    print(f"\n   # Process with parallel processing (5 concurrent)")
    print(f"   uv run evidence-toolkit process-case {args.output_dir} \\")
    print(f"       --case-id PARALLEL-TEST \\")
    print(f"       --max-concurrent 5")

    print(f"\n   # Compare with sequential processing (1 concurrent)")
    print(f"   uv run evidence-toolkit process-case {args.output_dir} \\")
    print(f"       --case-id PARALLEL-TEST-SEQ \\")
    print(f"       --max-concurrent 1")

    print("\n📊 Run performance benchmark:")
    print(f"   python test_batch_performance.py")

    print(f"\n💡 Note: Images sampled from {args.source_case}")
    print("   Modified metadata ensures unique SHA256 hashes for testing")
    print("   Set OPENAI_API_KEY to test with actual AI analysis")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
