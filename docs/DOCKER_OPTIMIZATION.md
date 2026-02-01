# Docker Image Optimization Guide

## Problem
Your Docker image was **11.49GB** due to three main issues:

### 1. Synthea Directory (Largest Culprit)
- Contains **1,547 files** including source code, build artifacts, and generated data
- The `.dockerignore` wasn't excluding `synthea/output/` where CSV files are generated

### 2. Large CSV Files
- `synthea-pt30k-lc-data-sel.csv` (5.2 MB)
- `synthea-pt30k-stroke-ml-table-sel.csv` (18.7 MB)
- All files in `synthea/output/csv/` directory

### 3. Build Artifacts Not Cleaned
- Build tools (`build-essential`, `flex`, `bison`, `git`, `wget`)
- Source directories (`/tmp/pbc-0.5.14/`, `/tmp/charm/`)

## Solution

### Optimized Dockerfile
The new Dockerfile:
- ✅ Cleans up build artifacts after compilation
- ✅ Removes build tools after charm-crypto installation
- ✅ Only copies necessary source code (`src/`, `thesis_experiments.py`)
- ✅ Excludes all dataset files

### Updated .dockerignore
Now excludes:
- All CSV files (`*.csv`)
- Synthea output directory (`synthea/output`)
- Archive folder
- Result files (generated at runtime)
- Test scripts

## Expected Size Reduction

| Component | Before | After |
|:---|:---|:---|
| Base image | ~150 MB | ~150 MB |
| Build tools | ~500 MB | **0 MB** (removed) |
| PBC + Charm | ~200 MB | ~50 MB (cleaned) |
| Python packages | ~100 MB | ~100 MB |
| **Dataset files** | **~10 GB** | **0 MB** (excluded) |
| Source code | ~50 MB | ~5 MB (minimal) |
| **Total** | **~11 GB** | **~300-500 MB** |

## How to Use

### Build the Optimized Image
```bash
docker build -t hybrid-workflow:optimized .
```

### Run with Dataset as Volume
Since datasets are no longer in the image, mount them at runtime:

```bash
# Mount the synthea CSV directory
docker run --rm \
  -v $(pwd)/synthea/output/csv:/app/data \
  -v $(pwd):/app/output \
  hybrid-workflow:optimized python thesis_experiments.py
```

### Update thesis_experiments.py
Change the dataset path to use the mounted volume:

```python
# OLD:
dataset_dir = os.path.join(os.path.dirname(__file__), 'synthea', 'output', 'csv')

# NEW:
dataset_dir = os.path.join(os.path.dirname(__file__), 'data')
# Or use environment variable:
dataset_dir = os.getenv('DATASET_DIR', '/app/data')
```

## Benefits

✅ **95% size reduction**: 11GB → ~300-500MB  
✅ **Faster builds**: No need to copy gigabytes of data  
✅ **Faster pushes**: If pushing to registry  
✅ **Cleaner separation**: Code vs. data  
✅ **Flexibility**: Can swap datasets without rebuilding image

## Verification

After rebuilding, check the new image size:
```bash
docker images hybrid-workflow:optimized
```

You should see something like:
```
REPOSITORY              TAG         SIZE
hybrid-workflow         optimized   450MB
```

Instead of the previous **11.49GB**!
