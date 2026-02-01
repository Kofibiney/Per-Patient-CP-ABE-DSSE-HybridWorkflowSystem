#!/usr/bin/env python3
"""
Cleanup Script: Archive Redundant Experimental Files
====================================================
This script moves old experimental scripts and result files to an archive folder.
"""

import os
import shutil
from pathlib import Path

# Files to archive
SCRIPTS_TO_ARCHIVE = [
    "detailed_evaluation.py",
    "detailed_evaluation_v2.py",
    "final_verified_evaluation.py",
    "dynamic_dsse_experiment.py",
    "diagnostic_measurements.py",
    "diagnostic_simple.py",
    "diag_abe_depth.py",
    "diag_file.py",
    "measure_cpabe_full.py",
    "measure_cpabe_simple.py",
    "measure_cpabe_v2.py",
    "measure_enc_only.py",
    "proof_real_measurements.py",
    "proof_variance.py",
    "run_exp4_corrected.py",
    "run_exp6_corrected.py",
    "extract_measurements.py",
    "real_data_simulation.py",
    "simulation.py",
    "debug_abe_docker.py",
    "verify_authenticity.py",
]

RESULTS_TO_ARCHIVE = [
    "final_results_dynamic.txt",
    "experiment_results.txt",
    "experiment_results_10k.txt",
    "experiment_results_1k.txt",
    "experiment_4_corrected_results.txt",
    "experiment_4_final_results.txt",
    "final_results_verified_v2.txt",
    "final_results_verified_v3.txt",
    "final_verified_results.txt",
    "fresh_experiment_results.txt",
    "results_dynamic.txt",
    "dynamic_dsse_results.txt",
    "dynamic_results.txt",
    "EXP6_CORRECTED_RESULTS.txt",
    "CORRECTED_MEASUREMENTS.txt",
    "diagnostic_output.txt",
    "diagnostic_results.txt",
    "output_log.txt",
    "cpabe_results.txt",
    "real_data_simulation_output_v1.txt",
    "CONCISE_DYNAMIC_RESULTS.md",
    "COMPREHENSIVE_EVALUATION_RESULTS.txt",
    "LOGIC_FLOW_COMPARISON.txt",
    "PROOF_AND_BASELINE_EXPLANATION.txt",
    "BASELINE_COMPARISON_VERIFICATION.md",
    "CURSOR_VERIFICATION_PROMPT.md",
]

def main():
    """Archive redundant files."""
    base_dir = Path(__file__).parent
    archive_dir = base_dir / "archive"
    
    # Create archive directory
    archive_dir.mkdir(exist_ok=True)
    print(f"Created archive directory: {archive_dir}")
    
    # Archive scripts
    scripts_archived = 0
    for script in SCRIPTS_TO_ARCHIVE:
        src = base_dir / script
        if src.exists():
            dst = archive_dir / script
            shutil.move(str(src), str(dst))
            print(f"  ✓ Archived: {script}")
            scripts_archived += 1
    
    # Archive results
    results_archived = 0
    for result in RESULTS_TO_ARCHIVE:
        src = base_dir / result
        if src.exists():
            dst = archive_dir / result
            shutil.move(str(src), str(dst))
            print(f"  ✓ Archived: {result}")
            results_archived += 1
    
    print(f"\n{'='*60}")
    print(f"  CLEANUP COMPLETE")
    print(f"{'='*60}")
    print(f"  Scripts archived: {scripts_archived}/{len(SCRIPTS_TO_ARCHIVE)}")
    print(f"  Results archived: {results_archived}/{len(RESULTS_TO_ARCHIVE)}")
    print(f"  Archive location: {archive_dir}")
    print(f"{'='*60}\n")
    
    print("Remaining canonical files:")
    print("  ✓ thesis_experiments.py (CANONICAL SCRIPT)")
    print("  ✓ ACTUAL_EXPERIMENTAL_RESULTS.txt (REFERENCE)")
    print("  ✓ FORMAL_EXPERIMENTAL_REPORT.txt (REFERENCE)")
    print("  ✓ THESIS_RESULTS_MAPPING.md (DOCUMENTATION)")
    print("\nNext step: Run 'python thesis_experiments.py' to generate THESIS_OFFICIAL_RESULTS.txt")

if __name__ == "__main__":
    main()
