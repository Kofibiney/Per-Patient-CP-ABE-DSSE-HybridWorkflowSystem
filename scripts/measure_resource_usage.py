#!/usr/bin/env python3
"""
Measure actual resource usage during the search performance experiment.
Saves results to a file for easy viewing.
"""

import time
import os
import sys
import hashlib
import psutil
import threading
from collections import defaultdict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.data_owner import DataOwner
from src.entities.cloud_server import CloudServer
from src.utils.dataset_loader import DatasetLoader
from src.baseline.global_index_server import GlobalIndexServer


class ResourceMonitor:
    """Monitor CPU and memory usage during experiment."""
    
    def __init__(self):
        self.monitoring = False
        self.samples = []
        self.process = psutil.Process()
        
    def start(self):
        """Start monitoring in background thread."""
        self.monitoring = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """Stop monitoring and return statistics."""
        self.monitoring = False
        self.thread.join()
        
        if not self.samples:
            return {}
            
        cpu_values = [s['cpu_percent'] for s in self.samples]
        mem_values = [s['memory_mb'] for s in self.samples]
        
        return {
            'cpu_mean': sum(cpu_values) / len(cpu_values),
            'cpu_max': max(cpu_values),
            'cpu_min': min(cpu_values),
            'memory_mean_mb': sum(mem_values) / len(mem_values),
            'memory_max_mb': max(mem_values),
            'memory_min_mb': min(mem_values),
            'samples_count': len(self.samples)
        }
        
    def _monitor(self):
        """Background monitoring loop."""
        while self.monitoring:
            try:
                cpu = self.process.cpu_percent(interval=0.1)
                mem = self.process.memory_info().rss / (1024 * 1024)  # MB
                
                self.samples.append({
                    'timestamp': time.time(),
                    'cpu_percent': cpu,
                    'memory_mb': mem
                })
            except:
                pass
            time.sleep(0.1)  # Sample every 100ms


def main():
    output_lines = []
    
    def log(msg):
        print(msg)
        output_lines.append(msg)
    
    log("=" * 80)
    log("  ACTUAL RESOURCE USAGE MEASUREMENT")
    log("=" * 80)
    
    # Get system info
    log("\n[SYSTEM INFORMATION]")
    log(f"  CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical")
    log(f"  Total RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    log(f"  Available RAM: {psutil.virtual_memory().available / (1024**3):.2f} GB")
    
    # Load dataset (suppress output)
    dataset_dir = os.path.join(os.path.dirname(__file__), 'synthea', 'output', 'csv')
    loader = DatasetLoader(dataset_dir)
    records = loader.get_processed_records(limit=200)
    
    # Collect test keywords
    keyword_freq = defaultdict(int)
    for rec in records:
        for kw in rec['keywords']:
            keyword_freq[kw] += 1
    sorted_kws = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
    test_keywords = [kw for kw, freq in sorted_kws[:10]]
    
    # ========== PER-PATIENT SYSTEM ==========
    log("\n" + "=" * 80)
    log("  PER-PATIENT INDEX SYSTEM")
    log("=" * 80)
    
    monitor = ResourceMonitor()
    
    log("\n[1] Setup Phase (Encrypting 200 records)")
    monitor.start()
    setup_start = time.time()
    
    # Suppress print statements
    import io
    from contextlib import redirect_stdout
    
    with redirect_stdout(io.StringIO()):
        pp_server = CloudServer()
        pp_owner = DataOwner()
        pk = pp_owner.setup_system()
        
        for rec in records:
            pp_owner.encrypt_and_upload(
                rec['patient_id'],
                rec['content'],
                rec['keywords'],
                "(DOCTOR and CARDIOLOGY)",
                pp_server
            )
    
    setup_time = time.time() - setup_start
    setup_stats = monitor.stop()
    
    log(f"  Setup Time: {setup_time:.2f}s")
    log(f"  CPU Usage: {setup_stats['cpu_mean']:.1f}% (avg), {setup_stats['cpu_max']:.1f}% (peak)")
    log(f"  Memory Usage: {setup_stats['memory_mean_mb']:.1f} MB (avg), {setup_stats['memory_max_mb']:.1f} MB (peak)")
    
    log("\n[2] Search Phase (1000 iterations)")
    monitor = ResourceMonitor()
    monitor.start()
    search_start = time.time()
    
    with redirect_stdout(io.StringIO()):
        for i in range(1000):
            rec = records[i % len(records)]
            patient_id = rec['patient_id']
            keyword = test_keywords[i % len(test_keywords)]
            
            try:
                tokens = pp_owner.generate_search_tokens(patient_id, keyword)
                results = pp_server.search(patient_id, tokens)
            except:
                continue
    
    search_time = time.time() - search_start
    search_stats = monitor.stop()
    
    log(f"  Search Time: {search_time:.2f}s")
    log(f"  Throughput: {1000/search_time:.1f} searches/sec")
    log(f"  CPU Usage: {search_stats['cpu_mean']:.1f}% (avg), {search_stats['cpu_max']:.1f}% (peak)")
    log(f"  Memory Usage: {search_stats['memory_mean_mb']:.1f} MB (avg), {search_stats['memory_max_mb']:.1f} MB (peak)")
    
    # ========== GLOBAL INDEX SYSTEM ==========
    log("\n" + "=" * 80)
    log("  GLOBAL INDEX SYSTEM")
    log("=" * 80)
    
    log("\n[1] Setup Phase (Indexing 200 records)")
    monitor = ResourceMonitor()
    monitor.start()
    setup_start = time.time()
    
    gl_server = GlobalIndexServer()
    
    def dummy_trapdoor(kw):
        return hashlib.sha256(kw.encode()).hexdigest()
    
    for rec in records:
        gl_server.upload(
            rec['patient_id'],
            {"data": rec['content']},
            rec['keywords'],
            dummy_trapdoor
        )
    
    setup_time = time.time() - setup_start
    setup_stats = monitor.stop()
    
    log(f"  Setup Time: {setup_time:.2f}s")
    log(f"  CPU Usage: {setup_stats['cpu_mean']:.1f}% (avg), {setup_stats['cpu_max']:.1f}% (peak)")
    log(f"  Memory Usage: {setup_stats['memory_mean_mb']:.1f} MB (avg), {setup_stats['memory_max_mb']:.1f} MB (peak)")
    
    log("\n[2] Search Phase (1000 iterations)")
    monitor = ResourceMonitor()
    monitor.start()
    search_start = time.time()
    
    for i in range(1000):
        rec = records[i % len(records)]
        patient_id = rec['patient_id']
        keyword = test_keywords[i % len(test_keywords)]
        
        trapdoors = [dummy_trapdoor(keyword)]
        results = gl_server.search_for_patient(patient_id, trapdoors)
    
    search_time = time.time() - search_start
    search_stats = monitor.stop()
    
    log(f"  Search Time: {search_time:.2f}s")
    log(f"  Throughput: {1000/search_time:.1f} searches/sec")
    log(f"  CPU Usage: {search_stats['cpu_mean']:.1f}% (avg), {search_stats['cpu_max']:.1f}% (peak)")
    log(f"  Memory Usage: {search_stats['memory_mean_mb']:.1f} MB (avg), {search_stats['memory_max_mb']:.1f} MB (peak)")
    
    log("\n" + "=" * 80)
    log("  ✓ RESOURCE MEASUREMENT COMPLETE")
    log("=" * 80)
    
    # Save to file
    with open('resource_usage_report.txt', 'w') as f:
        f.write('\n'.join(output_lines))
    
    log("\n✓ Results saved to: resource_usage_report.txt")


if __name__ == "__main__":
    main()
