#!/usr/bin/env pwsh
# Repository Cleanup Script for GitHub Push
# Removes debug scripts, datasets, and generated files

Write-Host "Repository Cleanup for GitHub Push" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# List of files/directories to remove
$itemsToRemove = @(
    # Debug/test scripts
    "debug_experiment6.py",
    "detailed_debug_exp6.py",
    "quick_test_exp6.py",
    "test_abe.py",
    "test_attr_names.py",
    "test_exp4_fix.py",
    "test_policy_formats.py",
    
    # Large datasets
    "synthea",
    "synthea-dataset-100",
    "synthea-pt30k-lc-data-sel.csv",
    "synthea-pt30k-stroke-ml-table-sel.csv",
    "set100",
    
    # Generated files
    "experiment_run.log",
    "csv",
    "diagnostic_data.csv",
    "global_index_raw_data.csv",
    "per_patient_raw_data.csv",
    "combined_summary.png",
    "latency_cdf.png",
    "latency_comparison_boxplot.png",
    "latency_histogram.png",
    "latency_timeseries.png",
    "statistics_comparison.png",
    
    # Archive and old files
    "archive",
    "ACTUAL_EXPERIMENTAL_RESULTS.txt",
    "final_evaluation_results.txt",
    "FORMAL_EXPERIMENTAL_REPORT.txt",
    "resource_usage_report.txt",
    "search_performance_results.txt"
)

Write-Host "This will delete:" -ForegroundColor Yellow
foreach ($item in $itemsToRemove) {
    if (Test-Path $item) {
        Write-Host "  - $item" -ForegroundColor Yellow
    }
}
Write-Host ""

$confirm = Read-Host "Continue? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Cleanup cancelled." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Green

$deletedCount = 0
$totalSize = 0

foreach ($item in $itemsToRemove) {
    if (Test-Path $item) {
        try {
            $size = (Get-ChildItem $item -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            Remove-Item $item -Recurse -Force -ErrorAction Stop
            Write-Host "  Deleted: $item" -ForegroundColor Green
            $deletedCount++
            $totalSize += $size
        }
        catch {
            Write-Host "  Failed to delete: $item" -ForegroundColor Red
        }
    }
}

# Clean __pycache__
Get-ChildItem -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  Deleted: $($_.FullName)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Cleanup Complete!" -ForegroundColor Green
Write-Host "  Items deleted: $deletedCount" -ForegroundColor White
Write-Host "  Space freed: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. git status" -ForegroundColor Yellow
Write-Host "  2. git add ." -ForegroundColor Yellow
Write-Host "  3. git commit -m 'Cleanup for GitHub push'" -ForegroundColor Yellow
Write-Host "  4. git push" -ForegroundColor Yellow
