# run_experiments.ps1
# Quick script to run thesis experiments in Docker

$IMAGE_NAME = "hybrid-workflow:latest"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Hybrid Workflow System: Thesis Experiments" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Build Docker image
Write-Host "[Step 1] Building Docker Image..." -ForegroundColor Green
docker build -t $IMAGE_NAME .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[Step 2] Running Thesis Experiments..." -ForegroundColor Green
Write-Host "This will take approximately 10 minutes." -ForegroundColor Yellow
Write-Host ""

# Run experiments
docker run --rm `
    -v ${PWD}:/app/workspace `
    -w /app/workspace `
    $IMAGE_NAME `
    python scripts/thesis_experiments.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Experiments failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Experiments Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Results saved to: results/THESIS_OFFICIAL_RESULTS.txt" -ForegroundColor White
Write-Host ""
