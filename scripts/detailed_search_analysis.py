#!/usr/bin/env python3
"""
DETAILED SEARCH PERFORMANCE ANALYSIS
=====================================
Shows the actual raw data and methodology from the search comparison experiment.
Outputs CSV files with all individual measurements for further analysis.
"""

import time
import os
import sys
import hashlib
import numpy as np
import csv
from collections import defaultdict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.data_owner import DataOwner
from src.entities.cloud_server import CloudServer
from src.utils.dataset_loader import DatasetLoader
from src.baseline.global_index_server import GlobalIndexServer


def main():
    """Run detailed analysis with raw data output."""
    
    print("=" * 80)
    print("  DETAILED SEARCH PERFORMANCE ANALYSIS")
    print("  Showing actual measurements and methodology")
    print("=" * 80)
    
    # Load dataset
    dataset_dir = os.path.join(os.path.dirname(__file__), 'synthea', 'output', 'csv')
    loader = DatasetLoader(dataset_dir)
    records = loader.get_processed_records(limit=200)
    
    print(f"\n[STEP 1] Loaded {len(records)} patient records from Synthea dataset")
    print(f"  Each record contains:")
    print(f"    - patient_id: unique identifier")
    print(f"    - content: encrypted medical text")
    print(f"    - keywords: list of searchable terms")
    
    # Show sample record structure
    sample = records[0]
    print(f"\n[SAMPLE RECORD]")
    print(f"  Patient ID: {sample['patient_id']}")
    print(f"  Content length: {len(sample['content'])} characters")
    print(f"  Keywords ({len(sample['keywords'])}): {sample['keywords'][:5]}...")
    
    # Collect test keywords
    keyword_freq = defaultdict(int)
    for rec in records:
        for kw in rec['keywords']:
            keyword_freq[kw] += 1
    
    sorted_kws = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
    test_keywords = [kw for kw, freq in sorted_kws[:10]]
    
    print(f"\n[STEP 2] Selected 10 most common keywords for testing:")
    for i, (kw, freq) in enumerate(sorted_kws[:10], 1):
        print(f"  {i}. '{kw}' - appears in {freq} records ({freq/len(records)*100:.1f}%)")
    
    # Setup Per-Patient System
    print(f"\n[STEP 3] Setting up PER-PATIENT INDEX system")
    print(f"  - Creating CloudServer instance")
    print(f"  - Creating DataOwner instance")
    print(f"  - Initializing CP-ABE (generating public/master keys)")
    
    pp_server = CloudServer()
    pp_owner = DataOwner()
    pk = pp_owner.setup_system()
    
    print(f"  - Encrypting {len(records)} records...")
    print(f"    For each record:")
    print(f"      1. Encrypt content with AES-256-GCM")
    print(f"      2. Build DSSE index (HMAC-SHA256 trapdoors)")
    print(f"      3. Encrypt AES key with CP-ABE")
    print(f"      4. Upload to server")
    
    start_t = time.time()
    for rec in records:
        pp_owner.encrypt_and_upload(
            rec['patient_id'],
            rec['content'],
            rec['keywords'],
            "(DOCTOR and CARDIOLOGY)",
            pp_server
        )
    setup_time_pp = time.time() - start_t
    
    print(f"  ✓ Per-patient setup: {setup_time_pp:.2f}s")
    print(f"  ✓ {len(pp_server.storage)} patient indices created")
    
    # Setup Global Index System
    print(f"\n[STEP 4] Setting up GLOBAL INDEX system")
    print(f"  - Creating GlobalIndexServer instance")
    print(f"  - Using SHA-256 hash as trapdoor function")
    
    gl_server = GlobalIndexServer()
    
    def dummy_trapdoor(kw):
        return hashlib.sha256(kw.encode()).hexdigest()
    
    print(f"  - Indexing {len(records)} records into single global index...")
    print(f"    For each record:")
    print(f"      1. Generate trapdoors for all keywords")
    print(f"      2. Append (patient_id, doc_id) to global index")
    
    start_t = time.time()
    for rec in records:
        gl_server.upload(
            rec['patient_id'],
            {"data": rec['content']},
            rec['keywords'],
            dummy_trapdoor
        )
    setup_time_gl = time.time() - start_t
    
    print(f"  ✓ Global index setup: {setup_time_gl:.2f}s")
    print(f"  ✓ {len(gl_server.global_index)} unique trapdoors in global index")
    
    # Measure Per-Patient Search
    print(f"\n[STEP 5] Measuring PER-PATIENT search latency")
    print(f"  Method:")
    print(f"    1. Select patient and keyword")
    print(f"    2. Generate DSSE search tokens from owner's state")
    print(f"    3. TIME: server.search(patient_id, tokens)")
    print(f"    4. Record latency in microseconds")
    print(f"  Running 1000 iterations...")
    
    pp_latencies = []
    pp_details = []
    
    for i in range(1000):
        rec = records[i % len(records)]
        patient_id = rec['patient_id']
        keyword = test_keywords[i % len(test_keywords)]
        
        try:
            tokens = pp_owner.generate_search_tokens(patient_id, keyword)
            
            start_t = time.time()
            results = pp_server.search(patient_id, tokens)
            latency_us = (time.time() - start_t) * 1000000  # microseconds
            
            pp_latencies.append(latency_us)
            pp_details.append({
                'iteration': i,
                'patient_id': patient_id,
                'keyword': keyword,
                'latency_us': latency_us,
                'found': len(results) > 0
            })
        except:
            continue
    
    print(f"  ✓ Completed {len(pp_latencies)} searches")
    
    # Measure Global Index Search
    print(f"\n[STEP 6] Measuring GLOBAL INDEX search latency")
    print(f"  Method:")
    print(f"    1. Select patient and keyword")
    print(f"    2. Generate trapdoor hash")
    print(f"    3. TIME: server.search_for_patient(patient_id, trapdoors)")
    print(f"       (includes filtering global results by patient_id)")
    print(f"    4. Record latency in microseconds")
    print(f"  Running 1000 iterations...")
    
    gl_latencies = []
    gl_details = []
    
    for i in range(1000):
        rec = records[i % len(records)]
        patient_id = rec['patient_id']
        keyword = test_keywords[i % len(test_keywords)]
        
        trapdoors = [dummy_trapdoor(keyword)]
        
        start_t = time.time()
        results = gl_server.search_for_patient(patient_id, trapdoors)
        latency_us = (time.time() - start_t) * 1000000  # microseconds
        
        gl_latencies.append(latency_us)
        gl_details.append({
            'iteration': i,
            'patient_id': patient_id,
            'keyword': keyword,
            'latency_us': latency_us,
            'found': len(results) > 0
        })
    
    print(f"  ✓ Completed {len(gl_latencies)} searches")
    
    # Calculate statistics
    pp_arr = np.array(pp_latencies)
    gl_arr = np.array(gl_latencies)
    
    print(f"\n[STEP 7] Statistical Analysis")
    print(f"\n{'Metric':<20} | {'Per-Patient (μs)':<18} | {'Global Index (μs)':<18} | {'Speedup':<10}")
    print("-" * 75)
    print(f"{'Mean':<20} | {np.mean(pp_arr):<18.2f} | {np.mean(gl_arr):<18.2f} | {np.mean(gl_arr)/np.mean(pp_arr):<10.2f}x")
    print(f"{'Median':<20} | {np.median(pp_arr):<18.2f} | {np.median(gl_arr):<18.2f} | {np.median(gl_arr)/np.median(pp_arr):<10.2f}x")
    print(f"{'P95':<20} | {np.percentile(pp_arr, 95):<18.2f} | {np.percentile(gl_arr, 95):<18.2f} | {np.percentile(gl_arr, 95)/np.percentile(pp_arr, 95):<10.2f}x")
    print(f"{'P99':<20} | {np.percentile(pp_arr, 99):<18.2f} | {np.percentile(gl_arr, 99):<18.2f} | {np.percentile(gl_arr, 99)/np.percentile(pp_arr, 99):<10.2f}x")
    print(f"{'Min':<20} | {np.min(pp_arr):<18.2f} | {np.min(gl_arr):<18.2f} | -")
    print(f"{'Max':<20} | {np.max(pp_arr):<18.2f} | {np.max(gl_arr):<18.2f} | -")
    print(f"{'Std Dev':<20} | {np.std(pp_arr):<18.2f} | {np.std(gl_arr):<18.2f} | -")
    
    # Save raw data to CSV
    print(f"\n[STEP 8] Saving raw measurement data to CSV files")
    
    with open('per_patient_raw_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['iteration', 'patient_id', 'keyword', 'latency_us', 'found'])
        writer.writeheader()
        writer.writerows(pp_details)
    print(f"  ✓ Saved per_patient_raw_data.csv ({len(pp_details)} measurements)")
    
    with open('global_index_raw_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['iteration', 'patient_id', 'keyword', 'latency_us', 'found'])
        writer.writeheader()
        writer.writerows(gl_details)
    print(f"  ✓ Saved global_index_raw_data.csv ({len(gl_details)} measurements)")
    
    # Show sample measurements
    print(f"\n[SAMPLE MEASUREMENTS - First 10 searches]")
    print(f"\nPer-Patient Index:")
    print(f"{'Iter':<6} | {'Keyword':<15} | {'Latency (μs)':<15} | {'Found':<6}")
    print("-" * 50)
    for detail in pp_details[:10]:
        print(f"{detail['iteration']:<6} | {detail['keyword']:<15} | {detail['latency_us']:<15.2f} | {detail['found']}")
    
    print(f"\nGlobal Index:")
    print(f"{'Iter':<6} | {'Keyword':<15} | {'Latency (μs)':<15} | {'Found':<6}")
    print("-" * 50)
    for detail in gl_details[:10]:
        print(f"{detail['iteration']:<6} | {detail['keyword']:<15} | {detail['latency_us']:<15.2f} | {detail['found']}")
    
    # Distribution analysis
    print(f"\n[LATENCY DISTRIBUTION]")
    print(f"\nPer-Patient Index:")
    bins = [0, 5, 10, 20, 50, 100, float('inf')]
    labels = ['0-5μs', '5-10μs', '10-20μs', '20-50μs', '50-100μs', '100+μs']
    for i, (low, high) in enumerate(zip(bins[:-1], bins[1:])):
        count = np.sum((pp_arr >= low) & (pp_arr < high))
        pct = count / len(pp_arr) * 100
        print(f"  {labels[i]:<10}: {count:>4} searches ({pct:>5.1f}%)")
    
    print(f"\nGlobal Index:")
    for i, (low, high) in enumerate(zip(bins[:-1], bins[1:])):
        count = np.sum((gl_arr >= low) & (gl_arr < high))
        pct = count / len(gl_arr) * 100
        print(f"  {labels[i]:<10}: {count:>4} searches ({pct:>5.1f}%)")
    
    print("\n" + "=" * 80)
    print("  ✓ DETAILED ANALYSIS COMPLETE")
    print("  ✓ Raw data saved to CSV files for further analysis")
    print("=" * 80)


if __name__ == "__main__":
    main()
