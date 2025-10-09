#!/usr/bin/env python3
"""Create mixed-evidence test case by sampling from existing case

This script creates realistic test cases with multiple evidence types (documents, images)
by sampling from an existing case and creating unique SHA256 hashes via format-specific
metadata modification. This allows comprehensive pipeline testing without analyzing cached evidence.

Usage:
    # Standard test case (10 images + 3 documents)
    python create_test_case.py

    # Large test case (50 images + 10 documents)
    python create_test_case.py --large

    # Images only (backward compatibility)
    python create_test_case.py --images-only

    # Custom counts
    python create_test_case.py --images 20 --documents 5

The script will:
1. Find all evidence files in the source case directory
2. Randomly select N files of each type
3. Copy them with modified metadata to ensure unique SHA256 hashes
4. Set up a test case directory for comprehensive pipeline testing

Hash Spoofing Methods:
- Images: PNG metadata injection (existing method from create_test_images.py)
- Text files: Invisible trailing whitespace + UUID comment
- PDFs: Metadata modification (future - when PDFs exist in source case)
- EML: Header modification (future - when EMLs exist in source case)
"""

import hashlib
import shutil
import random
import uuid
from pathlib import Path
from PIL import Image, PngImagePlugin
import argparse


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file

    Args:
        file_path: Path to file

    Returns:
        SHA256 hash as hex string
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def spoof_image_hash(image_path: Path, output_path: Path) -> str:
    """Add random metadata to image to create unique SHA256 hash

    Uses PNG metadata injection for hash uniqueness while preserving visual content.

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
    return calculate_sha256(output_path)


def spoof_text_hash(text_path: Path, output_path: Path) -> str:
    """Modify text file to create unique SHA256 hash

    Appends invisible trailing whitespace and UUID comment to preserve readability
    while ensuring unique hash for testing.

    Args:
        text_path: Source text file path
        output_path: Destination text file path with modified content

    Returns:
        SHA256 hash of the new file
    """
    # Read original content
    with open(text_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Generate unique identifier
    unique_id = str(uuid.uuid4())

    # Append invisible modifications:
    # 1. Random trailing whitespace (invisible to humans)
    # 2. UUID comment at end (visible but harmless)
    whitespace = ' ' * random.randint(1, 10) + '\n'
    comment = f"\n\n<!-- Test ID: {unique_id} -->\n"

    modified_content = content + whitespace + comment

    # Write modified content
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    # Calculate SHA256
    return calculate_sha256(output_path)


def find_files_by_type(case_dir: Path, extensions: set[str]) -> list[Path]:
    """Find all files with specific extensions in a case directory

    Args:
        case_dir: Path to case directory
        extensions: Set of file extensions to search for (e.g., {'.txt', '.pdf'})

    Returns:
        List of file paths matching extensions
    """
    if not case_dir.exists():
        return []

    files = []
    for file in case_dir.rglob('*'):
        if file.is_file() and file.suffix.lower() in extensions:
            files.append(file)

    return files


def sample_and_spoof(source_files: list[Path], count: int, output_dir: Path,
                     prefix: str, spoof_func) -> tuple[list[Path], list[str]]:
    """Sample random files and create hash-spoofed copies

    Args:
        source_files: List of source files to sample from
        count: Number of files to sample
        output_dir: Output directory for test files
        prefix: Prefix for output filenames (e.g., 'test_doc_', 'test_image_')
        spoof_func: Function to use for hash spoofing (spoof_text_hash or spoof_image_hash)

    Returns:
        Tuple of (created_files, sha256_hashes)
    """
    if not source_files:
        return [], []

    # Adjust count if not enough source files
    if count > len(source_files):
        count = len(source_files)

    # Randomly sample files
    sampled_files = random.sample(source_files, count)

    # Create hash-spoofed copies
    created_files = []
    sha256_hashes = []

    for i, source_file in enumerate(sampled_files, 1):
        # Preserve original extension
        output_path = output_dir / f"{prefix}{i:02d}{source_file.suffix}"

        # Apply hash spoofing
        sha256 = spoof_func(source_file, output_path)

        created_files.append(output_path)
        sha256_hashes.append(sha256)

    return created_files, sha256_hashes


def create_test_case(source_case_dir: Path, output_dir: Path,
                    image_count: int = 10, document_count: int = 3,
                    images_only: bool = False):
    """Create comprehensive test case with mixed evidence types

    Args:
        source_case_dir: Source case directory to sample from
        output_dir: Output directory for test case
        image_count: Number of test images to create
        document_count: Number of test documents to create
        images_only: If True, only create images (backward compatibility)
    """
    print("=" * 70)
    print("🧪 TEST CASE GENERATOR - Mixed Evidence Sampling")
    print("=" * 70)

    print(f"\n📁 Source case: {source_case_dir}")
    print(f"📁 Output directory: {output_dir}")

    if images_only:
        print(f"🎨 Mode: Images only ({image_count} images)")
    else:
        print(f"🎨 Mode: Mixed evidence ({image_count} images + {document_count} documents)")

    # Verify source case exists
    if not source_case_dir.exists():
        print(f"\n❌ Source case directory not found: {source_case_dir}")
        print(f"   Available cases:")
        cases_dir = Path("data/cases")
        if cases_dir.exists():
            for case in sorted(cases_dir.iterdir()):
                if case.is_dir():
                    print(f"   - {case}")
        return

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find available evidence
    print(f"\n🔍 Scanning for evidence in {source_case_dir}...")

    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    text_extensions = {'.txt'}
    pdf_extensions = {'.pdf'}
    email_extensions = {'.eml'}

    source_images = find_files_by_type(source_case_dir, image_extensions)
    source_texts = find_files_by_type(source_case_dir, text_extensions)
    source_pdfs = find_files_by_type(source_case_dir, pdf_extensions)
    source_emails = find_files_by_type(source_case_dir, email_extensions)

    print(f"   ✅ Found {len(source_images)} images")
    print(f"   ✅ Found {len(source_texts)} text documents")
    print(f"   ✅ Found {len(source_pdfs)} PDFs")
    print(f"   ✅ Found {len(source_emails)} emails")

    # Track all created files
    all_files = []
    all_hashes = []

    # Sample images
    if source_images and image_count > 0:
        print(f"\n🎨 Creating {image_count} test images...")
        image_files, image_hashes = sample_and_spoof(
            source_images, image_count, output_dir, "test_image_", spoof_image_hash
        )
        all_files.extend(image_files)
        all_hashes.extend(image_hashes)
        print(f"   ✅ Created {len(image_files)} unique images")
    elif image_count > 0:
        print(f"\n⚠️  No images found in source case - skipping image sampling")

    # Sample documents (unless images-only mode)
    if not images_only:
        if source_texts and document_count > 0:
            print(f"\n📄 Creating {document_count} test documents...")
            doc_files, doc_hashes = sample_and_spoof(
                source_texts, document_count, output_dir, "test_doc_", spoof_text_hash
            )
            all_files.extend(doc_files)
            all_hashes.extend(doc_hashes)
            print(f"   ✅ Created {len(doc_files)} unique documents")
        elif document_count > 0:
            print(f"\n⚠️  No text documents found in source case - skipping document sampling")

        # Future: PDF sampling (when PDFs exist in source case)
        if source_pdfs:
            print(f"\n💡 {len(source_pdfs)} PDFs available (PDF hash spoofing not yet implemented)")

        # Future: Email sampling (when EMLs exist in source case)
        if source_emails:
            print(f"\n💡 {len(source_emails)} emails available (EML hash spoofing not yet implemented)")

    # Verify all hashes are unique
    print(f"\n📋 Generated {len(all_files)} files with SHA256 hashes:")
    for i, (file, sha256) in enumerate(zip(all_files, all_hashes), 1):
        print(f"   {i:2d}. {file.name}: {sha256[:16]}...")

    if len(set(all_hashes)) == len(all_hashes):
        print(f"\n   ✅ All {len(all_hashes)} hashes are unique")
    else:
        print(f"\n   ⚠️  Warning: Some hashes are duplicates!")

    # Print usage instructions
    print("\n" + "=" * 70)
    print("✅ TEST CASE READY")
    print("=" * 70)

    print(f"\n📁 Test case directory: {output_dir}")
    print(f"📊 Evidence count: {len(all_files)} files")

    if images_only:
        print(f"   - {len([f for f in all_files if f.suffix.lower() in image_extensions])} images")
    else:
        print(f"   - {len([f for f in all_files if f.suffix.lower() in image_extensions])} images")
        print(f"   - {len([f for f in all_files if f.suffix.lower() in text_extensions])} documents")

    print("\n🚀 Run complete pipeline:")
    print(f"\n   # Standard processing")
    print(f"   uv run evidence-toolkit process-case {output_dir} \\")
    print(f"       --case-id TEST-CASE")

    print(f"\n   # With AI entity resolution (v3.2+)")
    print(f"   uv run evidence-toolkit process-case {output_dir} \\")
    print(f"       --case-id TEST-CASE \\")
    print(f"       --ai-resolve")

    print(f"\n   # Workplace case with parallel processing (v3.3.1+)")
    print(f"   uv run evidence-toolkit process-case {output_dir} \\")
    print(f"       --case-id TEST-CASE \\")
    print(f"       --case-type workplace \\")
    print(f"       --max-concurrent 5")

    print(f"\n💡 Note: Evidence sampled from {source_case_dir}")
    print("   Modified metadata ensures unique SHA256 hashes for testing")
    print("   Set OPENAI_API_KEY to test with actual AI analysis")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Create mixed-evidence test case by sampling from existing case",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard test case (10 images + 3 documents)
  python create_test_case.py

  # Large test case (50 images + 10 documents)
  python create_test_case.py --large

  # Images only (backward compatibility)
  python create_test_case.py --images-only

  # Custom counts
  python create_test_case.py --images 20 --documents 5
        """
    )

    parser.add_argument(
        '--source-case',
        type=Path,
        default=Path("data/cases/BCH_WORKPLACE_2025_2"),
        help='Source case directory to sample from (default: data/cases/BCH_WORKPLACE_2025_2)'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path("data/cases/TEST-CASE"),
        help='Output directory (default: data/cases/TEST-CASE)'
    )

    parser.add_argument(
        '--images',
        type=int,
        help='Number of test images (default: 10 standard, 50 large)'
    )

    parser.add_argument(
        '--documents',
        type=int,
        help='Number of test documents (default: 3 standard, 10 large)'
    )

    parser.add_argument(
        '--large',
        action='store_true',
        help='Create large test case (50 images + 10 documents)'
    )

    parser.add_argument(
        '--images-only',
        action='store_true',
        help='Only create images (backward compatibility with create_test_images.py)'
    )

    args = parser.parse_args()

    # Determine counts based on flags
    if args.large:
        image_count = args.images if args.images is not None else 50
        document_count = args.documents if args.documents is not None else 10
    else:
        image_count = args.images if args.images is not None else 10
        document_count = args.documents if args.documents is not None else 3

    # Create test case
    create_test_case(
        source_case_dir=args.source_case,
        output_dir=args.output_dir,
        image_count=image_count,
        document_count=document_count,
        images_only=args.images_only
    )


if __name__ == "__main__":
    main()
