import csv
import os

class DatasetLoader:
    """
    Utility to load and process Synthea datasets.
    """
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.patients_file = os.path.join(dataset_path, 'patients.csv')
        self.conditions_file = os.path.join(dataset_path, 'conditions.csv')

    def load_patients(self, limit=None):
        """
        Loads patient basic info.
        """
        patients = {}
        with open(self.patients_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                pid = row['Id']
                patients[pid] = {
                    'name': f"{row['FIRST']} {row['LAST']}",
                    'gender': row['GENDER'],
                    'birthdate': row['BIRTHDATE'],
                    'conditions': []
                }
                count += 1
                if limit and count >= limit:
                    break
        return patients

    def attach_conditions(self, patients):
        """
        Attaches conditions to the patient records.
        """
        with open(self.conditions_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = row['PATIENT']
                if pid in patients:
                    condition_desc = row['DESCRIPTION']
                    patients[pid]['conditions'].append(condition_desc)
        return patients

    def get_processed_records(self, limit=10):
        """
        Returns a list of structured records ready for encryption.
        """
        patients = self.load_patients(limit=limit)
        patients = self.attach_conditions(patients)
        
        records = []
        for pid, data in patients.items():
            content = f"Patient Name: {data['name']}\n"
            content += f"Gender: {data['gender']}\n"
            content += f"Birthdate: {data['birthdate']}\n"
            content += "Conditions: " + ", ".join(data['conditions'])
            
            # Keywords are basically the individual words in conditions + name
            keywords = set()
            for condition in data['conditions']:
                # Simple tokenization: lowercase and split
                tokens = condition.lower().replace(',', '').replace('(', '').replace(')', '').split()
                keywords.update(tokens)
            
            # Add patient name parts as keywords too
            keywords.update(data['name'].lower().split())
            
            records.append({
                'patient_id': pid,
                'content': content,
                'keywords': list(keywords)
            })
        return records

if __name__ == "__main__":
    # Quick test
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    dataset_dir = os.path.join(base_dir, 'synthea-dataset-100', 'set100', 'csv')
    loader = DatasetLoader(dataset_dir)
    records = loader.get_processed_records(limit=2)
    for r in records:
        print(f"ID: {r['patient_id']}")
        print(f"Keywords: {r['keywords'][:10]}...")
        print("-" * 20)
