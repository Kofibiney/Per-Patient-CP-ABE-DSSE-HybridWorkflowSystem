# Hybrid Workflow System: CP-ABE + DSSE for Secure EHR Management

A privacy-preserving Electronic Health Record (EHR) system combining **Ciphertext-Policy Attribute-Based Encryption (CP-ABE)** with **Dynamic Searchable Symmetric Encryption (DSSE)** for secure, searchable cloud storage.

## 📋 Overview

This system implements a hybrid cryptographic framework that enables:
- **Fine-grained access control** via CP-ABE policies
- **Searchable encryption** via per-patient DSSE indices
- **Privacy-preserving search** without revealing access patterns
- **Scalable architecture** for large-scale EHR deployments

### Key Features
- ✅ Per-patient encryption keys and search indices
- ✅ Attribute-based access policies (e.g., "DOCTOR and CARDIOLOGY")
- ✅ Forward-private dynamic search
- ✅ Sub-10 microsecond DSSE search latency
- ✅ Proven O(1) constant-time scalability

---

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ Data Owner  │────────▶│ Cloud Server │◀────────│    User     │
│             │         │              │         │             │
│ • Encrypts  │         │ • Stores CT  │         │ • Decrypts  │
│ • Indexes   │         │ • Searches   │         │ • Searches  │
└─────────────┘         └──────────────┘         └─────────────┘
       │                                                 │
       │                                                 │
       ▼                                                 ▼
  CP-ABE Encrypt                                  CP-ABE Decrypt
  DSSE Index Build                                DSSE Token Gen
```

### Components

1. **Data Owner**: Encrypts patient records, builds per-patient DSSE indices
2. **Cloud Server**: Stores encrypted data and indices, performs searches
3. **User**: Decrypts records (if authorized), generates search tokens
4. **CP-ABE**: Attribute-based encryption for access control
5. **DSSE**: Searchable encryption for keyword search

---

## 🚀 Quick Start

### Prerequisites
- Docker (recommended) OR Python 3.9+
- 4GB RAM minimum
- 10GB disk space (for dataset)

### Option 1: Docker (Recommended)

```powershell
# Build the Docker image
docker build -t hybrid-workflow:latest .

# Run experiments
docker run --rm -v ${PWD}:/app/workspace -w /app/workspace hybrid-workflow:latest python scripts/thesis_experiments.py

# View results
cat results/THESIS_OFFICIAL_RESULTS.txt
```

### Option 2: Local Python

```powershell
# Install dependencies
pip install -r requirements.txt

# Download dataset (see Data section below)
# Place in synthea/ directory

# Run experiments
python scripts/thesis_experiments.py
```

---

## 📊 Experiments

This repository includes 5 experiments from the thesis:

| Experiment | Purpose | Runtime |
|:-----------|:--------|:--------|
| **1. Scalability** | Encryption performance at scale (1K-10K patients) | ~5 min |
| **2. Keyword Density** | DSSE performance with varying keyword counts | ~1 min |
| **4. Concurrent Queries** | Multi-user concurrent access performance | ~2 min |
| **5. Baseline Comparison** | Per-patient vs global index comparison | ~1 min |
| **6. Policy Complexity** | CP-ABE overhead with increasing policy size | ~1 min |

### Running Individual Experiments

```python
# Edit scripts/thesis_experiments.py to comment out unwanted experiments
# Then run:
python scripts/thesis_experiments.py
```

### Expected Output

Results are written to `results/THESIS_OFFICIAL_RESULTS.txt`:
- Encryption throughput: ~72.7 patients/second
- DSSE search latency: ~4.5-7.9 microseconds
- Full workflow latency: ~2.77-18.94 milliseconds
- Per-patient vs Global: 5.5× faster

---

## 📁 Project Structure

```
HybridWorkflowSystem/
├── README.md                    # This file
├── .gitignore                   # Git exclusions
├── .dockerignore                # Docker exclusions
├── Dockerfile                   # Docker setup
├── requirements.txt             # Python dependencies
├── run_experiments.ps1          # Quick experiment runner
├── cleanup_for_github.ps1       # Repository cleanup script
│
├── src/                         # Source code
│   ├── entities/                # DataOwner, CloudServer, User
│   ├── core/                    # CP-ABE, DSSE, AES implementations
│   ├── baseline/                # Global index baseline
│   └── utils/                   # Dataset loader, helpers
│
├── scripts/                     # Utility scripts
│   ├── thesis_experiments.py              # Main experiment script
│   ├── proof_scalability.py               # Scalability proof (O(1) vs O(n))
│   ├── search_performance_comparison.py   # Baseline comparison
│   ├── visualize_search_performance.py    # Visualization generator
│   ├── measure_resource_usage.py          # Resource monitoring
│   ├── detailed_search_analysis.py        # Search analysis
│   ├── summarize_results.py               # Results summarizer
│   └── cleanup_old_experiments.py         # Cleanup utility
│
├── results/                     # Official results
│   ├── THESIS_OFFICIAL_RESULTS.txt        # Complete experimental results
│   ├── THESIS_METRICS_SUMMARY.md          # Metrics for thesis chapters
│   └── THESIS_RESULTS_MAPPING.md          # Results to thesis mapping
│
├── docs/                        # Additional documentation
│   └── DOCKER_OPTIMIZATION.md             # Docker optimization notes
│
└── data/                        # Dataset directory (gitignored)
    └── README.md                          # Dataset download instructions
```

---

## 📦 Dataset

This project uses the **Synthea** synthetic EHR dataset.

### Option 1: Download Pre-generated Dataset
1. Download from: https://synthetichealth.github.io/synthea/
2. Extract to `synthea/` directory
3. Ensure `synthea/fhir/*.json` files exist

### Option 2: Generate Your Own
```bash
# Clone Synthea
git clone https://github.com/synthetichealth/synthea.git
cd synthea

# Generate 1000 patients
./run_synthea -p 1000

# Copy output to project
cp -r output/fhir ../HybridWorkflowSystem/synthea/
```

**Note**: The dataset is excluded from Git (see `.gitignore`) due to size (~100MB+).

---

## 🔬 Reproducing Thesis Results

### Step 1: Setup Environment
```powershell
# Using Docker (recommended)
docker build -t hybrid-workflow:latest .
```

### Step 2: Run All Experiments
```powershell
docker run --rm -v ${PWD}:/app/workspace -w /app/workspace hybrid-workflow:latest python scripts/thesis_experiments.py
```

### Step 3: Verify Results
```powershell
# Compare with official results
diff results/THESIS_OFFICIAL_RESULTS.txt <your_output>

# Expected metrics:
# - Encryption: 13.75 ms/record
# - DSSE search: 4.5-7.9 μs
# - Per-patient vs Global: 5.5× faster
```

### Step 4: Generate Visualizations (Optional)
```powershell
python scripts/visualize_search_performance.py
python scripts/search_performance_comparison.py
```

---

## 🧪 Running Individual Components

### Test CP-ABE
```python
from src.entities.data_owner import DataOwner

owner = DataOwner()
pk = owner.setup_system()

# Encrypt with policy
ct, key = owner.abe.encrypt(pk, b"secret", "(DOCTOR and CARDIOLOGY)")

# Generate user key
sk = owner.generate_user_key(["DOCTOR", "CARDIOLOGY"])

# Decrypt
plaintext = owner.abe.decrypt(pk, sk, ct)
```

### Test DSSE
```python
from src.core.dsse_scheme import DynamicDSSEScheme

dsse = DynamicDSSEScheme()
state = dsse.setup()

# Add keywords
state = dsse.add_keywords(state, "patient_123", ["diabetes", "hypertension"], "doc_1")

# Search
tokens = dsse.generate_tokens(state, "patient_123", "diabetes")
results = dsse.search(state, tokens)
```

---

## 📈 Performance Metrics

From `THESIS_OFFICIAL_RESULTS.txt`:

| Metric | Value |
|:-------|:------|
| **Encryption Throughput** | 72.7 patients/second |
| **Encryption Latency** | 13.75 ms/record |
| **DSSE Search (isolated)** | 4.5-7.9 μs |
| **Full Workflow Search** | 2.77-18.94 ms |
| **Per-Patient vs Global** | 5.5× faster |
| **CP-ABE Overhead** | ~10.94 ms/attribute |
| **Memory per Patient** | ~38 KB |

### Scalability Proof
- **Per-patient**: Constant 3-6 μs (O(1)) regardless of DB size
- **Global index**: Linear growth 5.82 → 110.80 μs (O(n))
- **Gap widens**: 1.14× → 19.24× as DB scales from 10 to 500 patients

---

## 🛠️ Development

### Running Tests
```python
# Test scalability proof
python scripts/proof_scalability.py

# Measure resource usage
python scripts/measure_resource_usage.py
```

### Code Structure
- `src/entities/`: High-level entities (Owner, Server, User)
- `src/core/`: Cryptographic primitives (CP-ABE, DSSE, AES)
- `src/baseline/`: Baseline global index implementation
- `src/utils/`: Utilities (dataset loader, helpers)

---

## 📚 Documentation

- **results/THESIS_OFFICIAL_RESULTS.txt**: Complete experimental results
- **results/THESIS_METRICS_SUMMARY.md**: Metrics summary for thesis chapters
- **results/THESIS_RESULTS_MAPPING.md**: Mapping of results to thesis sections
- **docs/DOCKER_OPTIMIZATION.md**: Docker optimization notes
- **data/README.md**: Dataset download instructions

---

## 🐛 Known Issues & Limitations

1. **CP-ABE Attribute Names**: Cannot contain underscores (Charm library limitation)
   - ✅ Use: `ATTR0`, `DOCTOR`, `CARDIOLOGY`
   - ❌ Avoid: `ATTR_0`, `DOCTOR_ROLE`

2. **Dataset Size**: Synthea dataset is large (~100MB+)
   - Excluded from Git via `.gitignore`
   - Must be downloaded separately

3. **Concurrency**: Experiment 4 shows variable performance
   - Best at 10 concurrent users (360 qps)
   - Performance degrades at 20+ users

---

## 📄 License

This is research code for academic purposes. Please cite if used in publications.

---

## 👤 Author

**[Kofi Yeboah Asiedu-Biney]**  
Master's Thesis Project  
[Kwame Nkrumah University of Science and Technology]  
[2026]

---

## 🙏 Acknowledgments

- **Charm Crypto**: CP-ABE implementation
- **Synthea**: Synthetic EHR dataset
- **[Dr Emmanuel Ahene]**: Thesis supervision

---

## 📞 Contact

For questions or issues:
- Email: [kyasiedubiney@knust.edu.gh]
- GitHub Issues: [repository URL]

---

## 🔗 References

1. Synthea: https://synthetichealth.github.io/synthea/
