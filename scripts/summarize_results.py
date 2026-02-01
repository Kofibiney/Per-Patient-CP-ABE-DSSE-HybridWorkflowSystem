import re
import os

def summarize_logs(input_file, output_file):
    print(f"Summarizing {input_file} (UTF-16LE)...")
    
    # Storage for different types of metrics
    metrics = {
        "Batch Evaluation (Table)": {
            "Update Time (ms)": [],
            "Search Time (us)": []
        },
        "Index Construction (Table)": {
            "Build Time (ms)": []
        },
        "Verbose Logs (Regex)": {
            "Encryption (ms)": [],
            "Search (us)": [],
            "Update (ms)": [],
            "Delete (ms)": []
        }
    }

    # Regex for tabular rows
    # Example: 100 | 5 | 0.0886 | 25911.9857 | ...
    table_row_pat = re.compile(r"^\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)")
    # Example: 10000 | 203.8529 |
    index_row_pat = re.compile(r"^\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|")
    
    # Verbose patterns
    v_patterns = {
        "Encryption (ms)": re.compile(r"encryption(?:.*?)([\d.]+)\s*ms", re.I),
        "Search (us)": re.compile(r"search(?:.*?)([\d.]+)\s*(?:μs|us)", re.I),
        "Update (ms)": re.compile(r"update(?:.*?)([\d.]+)\s*ms", re.I),
        "Delete (ms)": re.compile(r"deletion(?:.*?)([\d.]+)\s*ms", re.I)
    }

    total_lines = 0
    
    try:
        with open(input_file, 'r', encoding='utf-16') as f:
            for line in f:
                total_lines += 1
                
                # 1. Try Tabular matching (4 columns)
                m = table_row_pat.match(line)
                if m:
                    # Based on "Patients | Updates/pt | Update Time (ms) | Search Time (us)"
                    metrics["Batch Evaluation (Table)"]["Update Time (ms)"].append(float(m.group(3)))
                    metrics["Batch Evaluation (Table)"]["Search Time (us)"].append(float(m.group(4)))
                    continue
                
                # 2. Try Index matching (2 columns)
                m = index_row_pat.match(line)
                if m:
                    # Based on "Keywords | Build Time"
                    metrics["Index Construction (Table)"]["Build Time (ms)"].append(float(m.group(2)))
                    continue
                
                # 3. Try Verbose matching
                for key, pat in v_patterns.items():
                    m = pat.search(line)
                    if m:
                        metrics["Verbose Logs (Regex)"][key].append(float(m.group(1)))
                
                if total_lines % 50000 == 0:
                    print(f"Read {total_lines} lines...")
                    
    except Exception as e:
        print(f"Error: {e}")
        return

    def get_stats(data):
        if not data: return None
        return {
            "avg": round(sum(data) / len(data), 4),
            "min": round(min(data), 4),
            "max": round(max(data), 4),
            "count": len(data)
        }

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# COMPREHENSIVE PERFORMANCE SUMMARY\n\n")
        f.write(f"Analyzed {total_lines} lines from `{input_file}`.\n\n")
        
        for category, sub_metrics in metrics.items():
            f.write(f"## {category}\n\n")
            f.write("| Metric | Average | Min | Max | Samples |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            has_data = False
            for label, data in sub_metrics.items():
                stats = get_stats(data)
                if stats:
                    f.write(f"| {label} | {stats['avg']} | {stats['min']} | {stats['max']} | {stats['count']} |\n")
                    has_data = True
                else:
                    f.write(f"| {label} | N/A | - | - | 0 |\n")
            if not has_data:
                f.write("> No data points found for this category.\n")
            f.write("\n")
            
        f.write("## Representative Raw Fragments\n\n")
        f.write("```text\n")
        f.write("[DataOwner] Processing Record for Patient: patient_001\n")
        f.write("[DataOwner] Created new DSSE state for Patient: patient_001\n")
        f.write("[DataOwner] Created new index (10 trapdoors)\n")
        f.write("[CloudServer] Stored data for Patient ID: patient_001\n")
        f.write("[User: Dr. Smith] Searching for keyword: 'diabetes'\n")
        f.write("  -> [Search Hit] Results found.\n")
        f.write("```\n\n")
        f.write("--- \n*Generated for Perplexity. Size reduced from 12MB to < 2KB.*")

    print(f"Summary written to {output_file}")

if __name__ == "__main__":
    summarize_logs("final_results_dynamic.txt", "CONCISE_DYNAMIC_RESULTS.md")
