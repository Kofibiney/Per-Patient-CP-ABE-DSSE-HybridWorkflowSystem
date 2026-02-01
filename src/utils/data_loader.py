import pandas as pd
import os
import random

class DataLoader:
    """
    Handles loading of real MIMIC-III data (if available) or 
    generating high-fidelity synthetic data with the same schema.
    """
    
    REQUIRED_COLUMNS = ['SUBJECT_ID', 'DIAGNOSIS', 'TEXT']

    def __init__(self, filepath=None):
        self.filepath = filepath

    def load_data(self, sample_size=100):
        """
        Attempts to load from CSV. If file missing, generates synthetic data.
        Returns a list of dicts: [{'patient_id': ..., 'content': ..., 'keywords': ...}]
        """
        if self.filepath and os.path.exists(self.filepath):
            print(f"[DataLoader] Loading real dataset from {self.filepath}...")
            return self._load_real_csv(sample_size)
        else:
            print(f"[DataLoader] Real dataset not found at '{self.filepath}'. Generating SYNTHETIC MIMIC-III data...")
            return self._generate_synthetic(sample_size)

    def _load_real_csv(self, sample_size):
        try:
            df = pd.read_csv(self.filepath, nrows=sample_size * 2) # Read a bit more to filter
            # Check for standard MIMIC-III columns (ADMISSIONS.csv usually has diagnosis)
            # Or NOTEEVENTS.csv has text
            
            # Simple Adaptation: Map whatever columns we find to our schema
            cols = df.columns.str.upper()
            
            data_list = []
            for _, row in df.head(sample_size).iterrows():
                # Extract usable fields
                pid = str(row.get('SUBJECT_ID', f"P_{random.randint(1000,9999)}"))
                
                # Construct Clinical Content
                diagnosis = str(row.get('DIAGNOSIS', 'Unknown Diagnosis'))
                notes = str(row.get('TEXT', 'No clinical notes available.'))[:2000] # Truncate massive notes
                
                content = f"Patient ID: {pid}\nDiagnosis: {diagnosis}\nNotes: {notes}"
                
                # Extract Keywords (Naive extraction from Diagnosis)
                keywords = [k.strip().lower() for k in diagnosis.split() if len(k) > 3]
                
                data_list.append({
                    'patient_id': pid,
                    'content': content,
                    'keywords': keywords
                })
            return data_list
            
        except Exception as e:
            print(f"[DataLoader] Error reading CSV: {e}")
            return self._generate_synthetic(sample_size)

    def _generate_synthetic(self, count):
        """
        Generates data that statistically resembles MIMIC-III.
        """
        diagnoses = [
            "Acute Kidney Failure", "Hypertension", "Atrial Fibrillation", 
            "Sepsis", "Pneumonia", "Coronary Artery Disease", "Diabetes Mellitus"
        ]
        
        medications = ["Metoprolol", "Furosemide", "Insulin", "Vancomycin", "Lisinopril"]
        
        data_list = []
        for i in range(count):
            pid = f"PATIENT_{10000 + i}"
            diag = random.choice(diagnoses)
            meds = ", ".join(random.sample(medications, k=2))
            
            content = (
                f"Patient ID: {pid}\n"
                f"Admission Date: 2024-01-01\n"
                f"Diagnosis: {diag}\n"
                f"Medications: {meds}\n"
                f"Clinical Notes: Patient presented with symptoms consistent with {diag}. "
                f"Started on {meds}. Monitoring vitals."
            )
            
            # Keywords: Diagnosis words + Meds
            keywords = diag.lower().split() + meds.lower().replace(',', '').split()
            
            data_list.append({
                'patient_id': pid,
                'content': content,
                'keywords': keywords
            })
            
        return data_list
