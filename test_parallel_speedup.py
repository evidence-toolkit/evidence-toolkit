#!/usr/bin/env python3
"""Quick parallel processing speedup test with REAL API calls

This script processes the PARALLEL-TEST case with both sequential and parallel
modes to demonstrate the actual speedup with real OpenAI Vision API calls.

Usage:
    export OPENAI_API_KEY="your-key"
    python test_parallel_speedup.py

The script will:
1. Process 10 test images sequentially (--max-concurrent 1)
2. Process same 10 images in parallel (--max-concurrent 5)
3. Show actual time comparison and cost
"""

import subprocess
import time
import os
import sys
from pathlib import Path


def run_process_case(case_id: str, max_concurrent: int, quiet: bool = False) -> float:
    """Run process-case command and return elapsed time

    Args:
        case_id: Case ID to use
        max_concurrent: Concurrency level
        quiet: Suppress output

    Returns:
        Elapsed time in seconds
    """
    print(f"\n{'='*70}")
    if max_concurrent == 1:
        print(f"🐌 SEQUENTIAL Processing ({max_concurrent} concurrent)")
    else:
        print(f"🚀 PARALLEL Processing ({max_concurrent} concurrent)")
    print(f"{'='*70}")

    cmd = [
        "uv", "run", "evidence-toolkit", "process-case",
        "data/cases/PARALLEL-TEST",
        "--case-id", case_id,
        "--max-concurrent", str(max_concurrent),
        "--storage-dir", "data/storage",
    ]

    if quiet:
        cmd.append("--quiet")

    print(f"\n⏱️  Starting timer...")
    start_time = time.time()

    # Run command
    result = subprocess.run(cmd, capture_output=quiet, text=True)

    elapsed = time.time() - start_time

    if result.returncode != 0:
        print(f"\n❌ Command failed with return code {result.returncode}")
        if quiet and result.stderr:
            print(f"Error: {result.stderr}")
        return None

    print(f"\n⏱️  ✅ Complete in {elapsed:.2f} seconds")

    return elapsed


def estimate_cost(num_images: int, avg_cost_per_image: float = 0.005) -> float:
    """Estimate API cost for image analysis

    Args:
        num_images: Number of images
        avg_cost_per_image: Average cost per image (default: $0.005 for gpt-4o-mini)

    Returns:
        Estimated cost in USD
    """
    return num_images * avg_cost_per_image


def main():
    """Run speedup comparison test"""
    print("="*70)
    print("🎯 PARALLEL IMAGE PROCESSING SPEEDUP TEST (REAL API CALLS)")
    print("="*70)

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ OPENAI_API_KEY not set")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    # Check test case exists
    test_case_dir = Path("data/cases/PARALLEL-TEST")
    if not test_case_dir.exists():
        print(f"\n❌ Test case not found: {test_case_dir}")
        print("   Run: uv run python create_test_images.py --count 10")
        sys.exit(1)

    # Count test images
    test_images = list(test_case_dir.glob("*.png"))
    print(f"\n📊 Test case: {test_case_dir}")
    print(f"   Images: {len(test_images)}")

    # Estimate cost
    estimated_cost = estimate_cost(len(test_images) * 2)  # 2 runs
    print(f"\n💰 Estimated cost: ${estimated_cost:.3f} ({len(test_images)} images × 2 runs)")
    print(f"   Using: gpt-4o-mini Vision API (~$0.005/image)")

    # Confirm before proceeding
    response = input("\n⚠️  This will make REAL API calls. Continue? [y/N]: ")
    if response.lower() != 'y':
        print("\n❌ Test cancelled")
        sys.exit(0)

    # Test 1: Sequential processing
    print("\n" + "="*70)
    print("TEST 1: SEQUENTIAL PROCESSING")
    print("="*70)

    seq_time = run_process_case(
        case_id="PARALLEL-TEST-SEQ",
        max_concurrent=1,
        quiet=False
    )

    if seq_time is None:
        print("\n❌ Sequential test failed")
        sys.exit(1)

    # Wait a bit between runs
    print("\n⏸️  Waiting 5 seconds before next test...")
    time.sleep(5)

    # Test 2: Parallel processing
    print("\n" + "="*70)
    print("TEST 2: PARALLEL PROCESSING")
    print("="*70)

    par_time = run_process_case(
        case_id="PARALLEL-TEST-PAR",
        max_concurrent=5,
        quiet=False
    )

    if par_time is None:
        print("\n❌ Parallel test failed")
        sys.exit(1)

    # Results
    print("\n" + "="*70)
    print("📊 PERFORMANCE RESULTS")
    print("="*70)

    speedup = seq_time / par_time if par_time > 0 else 0
    time_saved = seq_time - par_time

    print(f"\n   Sequential (1 concurrent):  {seq_time:6.2f}s")
    print(f"   Parallel   (5 concurrent):  {par_time:6.2f}s")
    print(f"\n   ⚡ Speedup:                  {speedup:.2f}x faster")
    print(f"   ⏱️  Time saved:               {time_saved:.2f}s ({time_saved/60:.1f} min)")

    print(f"\n   💰 Total cost: ~${estimated_cost:.3f}")
    print(f"   📊 Throughput:")
    print(f"      Sequential: {len(test_images)/seq_time:.2f} images/sec")
    print(f"      Parallel:   {len(test_images)/par_time:.2f} images/sec")

    # Extrapolation
    print(f"\n   📈 Extrapolated to 50 images:")
    seq_50 = (seq_time / len(test_images)) * 50
    par_50 = (par_time / len(test_images)) * 50
    print(f"      Sequential: {seq_50/60:.1f} minutes")
    print(f"      Parallel:   {par_50/60:.1f} minutes")
    print(f"      Time saved: {(seq_50-par_50)/60:.1f} minutes")

    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)

    print("\n📁 Generated packages:")
    print(f"   Sequential: data/packages/PARALLEL-TEST-SEQ*.zip")
    print(f"   Parallel:   data/packages/PARALLEL-TEST-PAR*.zip")

    print("\n💡 The analyses should be identical (except timestamps)")
    print("   because both use the same deterministic AI model.")


if __name__ == "__main__":
    main()
