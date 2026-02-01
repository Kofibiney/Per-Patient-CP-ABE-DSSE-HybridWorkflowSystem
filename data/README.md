# Dataset Information

This directory should contain the **Synthea** synthetic EHR dataset.

## Why is this directory empty?

The dataset is **excluded from Git** due to its large size (~100MB+). You need to download or generate it separately.

## Option 1: Download Pre-generated Dataset

1. Visit: https://synthetichealth.github.io/synthea/
2. Download a pre-generated dataset (recommended: 1000+ patients)
3. Extract the FHIR JSON files to this directory
4. Ensure you have: `synthea/fhir/*.json`

## Option 2: Generate Your Own Dataset

```bash
# Clone Synthea
git clone https://github.com/synthetichealth/synthea.git
cd synthea

# Generate 1000 patients
./run_synthea -p 1000

# Copy output to this project
cp -r output/fhir ../HybridWorkflowSystem/synthea/
```

## Expected Structure

After setup, you should have:

```
synthea/
├── fhir/
│   ├── patient1.json
│   ├── patient2.json
│   ├── ...
│   └── patientN.json
└── README.md (this file)
```

## Minimum Requirements

- **Patients**: At least 100 (1000+ recommended for full experiments)
- **Format**: FHIR JSON
- **Size**: ~100KB per patient (~100MB for 1000 patients)

## Troubleshooting

**Issue**: "Dataset not found" error
- **Solution**: Ensure `synthea/fhir/*.json` files exist

**Issue**: "No keywords extracted" warning
- **Solution**: Ensure JSON files contain clinical notes/observations

**Issue**: Out of memory during experiments
- **Solution**: Reduce batch size in `thesis_experiments.py` or use smaller dataset

## Alternative: Use Small Test Dataset

For quick testing, you can use a minimal dataset:

```python
# In thesis_experiments.py, change:
records = load_synthea_dataset(limit=10)  # Use only 10 patients
```

This allows you to test the system without downloading the full dataset.
