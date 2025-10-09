#!/usr/bin/env python3
"""Test script to demonstrate parallel image processing speedup

This script compares sequential vs. parallel image analysis performance.

Usage:
    python test_batch_performance.py

Requirements:
    - OPENAI_API_KEY environment variable set
    - Sample images in data/storage/raw/
"""

import asyncio
import time
from pathlib import Path

from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers.image import ImageAnalyzer
from evidence_toolkit.pipeline.batch import analyze_images_batch


def find_sample_images(storage: EvidenceStorage, limit: int = 10) -> list[str]:
    """Find sample image SHA256s from storage"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    image_sha256s = []

    for raw_dir in storage.raw_dir.iterdir():
        if raw_dir.is_dir() and raw_dir.name.startswith('sha256='):
            sha256 = raw_dir.name.replace('sha256=', '')
            original_file = storage.get_original_file_path(sha256)

            if original_file and original_file.suffix.lower() in image_extensions:
                image_sha256s.append(sha256)

                if len(image_sha256s) >= limit:
                    break

    return image_sha256s


async def test_parallel(sha256s: list[str], storage: EvidenceStorage, max_concurrent: int = 5):
    """Test parallel processing"""
    print(f"\n🚀 Testing PARALLEL processing ({max_concurrent} concurrent)...")
    print(f"   Processing {len(sha256s)} images...")

    start_time = time.time()

    results = await analyze_images_batch(
        sha256s,
        storage,
        case_id="PERF-TEST",
        max_concurrent=max_concurrent,
        quiet=False
    )

    elapsed = time.time() - start_time

    print(f"\n   ✅ Parallel complete: {elapsed:.2f} seconds")
    print(f"   ⚡ Average: {elapsed / len(sha256s):.2f}s per image")
    print(f"   📊 Throughput: {len(sha256s) / elapsed:.2f} images/second")

    return elapsed


def test_sequential(sha256s: list[str], storage: EvidenceStorage):
    """Test sequential processing (simulated)"""
    print(f"\n🐌 Testing SEQUENTIAL processing...")
    print(f"   Processing {len(sha256s)} images...")

    analyzer = ImageAnalyzer(verbose=False)
    start_time = time.time()

    for i, sha256 in enumerate(sha256s, 1):
        original_file = storage.get_original_file_path(sha256)
        if original_file:
            print(f"   Analyzing image {i}/{len(sha256s)}...", end='\r')
            try:
                result = analyzer.analyze_image(original_file)
            except Exception as e:
                print(f"   ⚠️  Error analyzing {sha256[:8]}: {e}")

    elapsed = time.time() - start_time

    print(f"\n   ✅ Sequential complete: {elapsed:.2f} seconds")
    print(f"   🐢 Average: {elapsed / len(sha256s):.2f}s per image")
    print(f"   📊 Throughput: {len(sha256s) / elapsed:.2f} images/second")

    return elapsed


def main():
    """Run performance comparison"""
    print("=" * 70)
    print("🎯 BATCH IMAGE PROCESSING PERFORMANCE TEST")
    print("=" * 70)

    # Initialize storage
    storage = EvidenceStorage(Path("data/storage"))

    # Find sample images
    print("\n🔍 Finding sample images...")
    sha256s = find_sample_images(storage, limit=10)

    if not sha256s:
        print("❌ No images found in storage. Run process-case first to ingest images.")
        return

    print(f"   Found {len(sha256s)} images for testing")

    # Test sequential first (for baseline)
    sequential_time = test_sequential(sha256s, storage)

    # Test parallel with different concurrency levels
    concurrency_levels = [1, 3, 5, 10]
    parallel_times = {}

    for max_concurrent in concurrency_levels:
        parallel_time = asyncio.run(test_parallel(sha256s, storage, max_concurrent))
        parallel_times[max_concurrent] = parallel_time

    # Print comparison
    print("\n" + "=" * 70)
    print("📊 PERFORMANCE COMPARISON")
    print("=" * 70)

    print(f"\n   Sequential:      {sequential_time:.2f}s")
    for max_concurrent, parallel_time in parallel_times.items():
        speedup = sequential_time / parallel_time
        print(f"   Parallel ({max_concurrent:2d}):     {parallel_time:.2f}s  ({speedup:.2f}x speedup)")

    print("\n" + "=" * 70)
    print("✅ Test complete!")
    print("=" * 70)

    # Recommendations
    best_concurrent = min(parallel_times, key=parallel_times.get)
    best_speedup = sequential_time / parallel_times[best_concurrent]

    print(f"\n💡 Recommendation: Use --max-concurrent={best_concurrent} for {best_speedup:.1f}x speedup")

    print("\nUsage example:")
    print(f"  uv run evidence-toolkit process-case data/cases/MY-CASE \\")
    print(f"    --case-id MY-CASE \\")
    print(f"    --max-concurrent {best_concurrent}")


if __name__ == "__main__":
    import os

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        exit(1)

    main()
