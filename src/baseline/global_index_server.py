class GlobalIndexServer:
    """
    Baseline Server for Exp 5.
    Stores a SINGLE massive index for all patients.
    """
    def __init__(self):
        self.storage = {} # { patient_id: enc_record }
        self.global_index = {} # { trapdoor: [List of (patient_id, doc_id)] }

    def upload(self, patient_id, enc_record, keywords, trapdoor_func):
        self.storage[patient_id] = enc_record
        for kw in keywords:
            # In a traditional global-index DSSE, we just use a global key
            # and append to a massive list.
            t = trapdoor_func(kw)
            if t not in self.global_index:
                self.global_index[t] = []
            self.global_index[t].append((patient_id, "main_record"))

    def search(self, trapdoors):
        """Search across all patients (returns all matches)."""
        results = []
        for t in trapdoors:
            hits = self.global_index.get(t, [])
            results.extend(hits)
        return results
    
    def search_for_patient(self, patient_id, trapdoors):
        """
        Search for a SPECIFIC patient (fair comparison with per-patient index).
        This is what a real system would need to do.
        """
        results = []
        for t in trapdoors:
            hits = self.global_index.get(t, [])
            # FILTER to specific patient (this is the extra cost!)
            patient_hits = [h for h in hits if h[0] == patient_id]
            results.extend(patient_hits)
        return results
