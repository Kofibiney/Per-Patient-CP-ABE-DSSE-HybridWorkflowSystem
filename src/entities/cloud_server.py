class CloudServer:
    """
    Simulates the Cloud Server in the EHR system.
    Stores encrypted records, encrypted indexes, and CP-ABE encrypted keys.
    Honest-but-curious: Follows protocol but technically could try to minimize leakage (not implemented here).
    """

    def __init__(self):
        # In-memory storage:
        # { patient_id: { 'record': enc_record_dict, 'index': enc_index_dict, 'key_ct': cpabe_ct } }
        self.storage = {}

    def upload(self, patient_id, enc_record, enc_index, enc_key_ct):
        """
        Stores the encrypted artifacts for a patient.
        """
        # In a real system, might append or update. Here we overwrite for simplicity.
        self.storage[patient_id] = {
            'record': enc_record,
            'enc_index': enc_index,  # FIXED: was 'index', now 'enc_index'
            'key_ct': enc_key_ct
        }
        print(f"[CloudServer] Stored data for Patient ID: {patient_id}")

    def get_encrypted_key(self, patient_id):
        """
        Retrieves the CP-ABE encrypted key for a patient.
        Access Control Step 1: User needs this to even try decrypting.
        """
        if patient_id in self.storage:
            return self.storage[patient_id]['key_ct']
        print(f"[CloudServer] Patient {patient_id} not found in storage.")
        return None

    def get_encrypted_record(self, patient_id):
        """
        Retrieves the full encrypted record (for decryption).
        """
        if patient_id in self.storage:
            return self.storage[patient_id]['record']
        return None

    def search(self, patient_id, trapdoors):
        """
        Performs the search operation on the encrypted index.
        Returns 'True' (Found) or matching document pointers if the keyword exists.
        Accepts a LIST of trapdoors (tokens) to handle forwarded privacy (historical occurrences).
        """
        if patient_id not in self.storage:
            print(f"[CloudServer] Search failed: Patient {patient_id} not found.")
            return []

        # DSSE Search
        # The index is a dict: { hashed_keyword: [doc_ptr] }
        index = self.storage[patient_id]['enc_index']  # FIXED

        
        results = []
        # Support both list (Dynamic) and single string (Legacy/Static) if needed, but strictly list now.
        if isinstance(trapdoors, str):
            trapdoors = [trapdoors]
            
        for t in trapdoors:
            hits = index.get(t, [])
            results.extend(hits)
        
        if results:
            print(f"[CloudServer] Keyword Match found for Patient {patient_id}!")
        else:
            print(f"[CloudServer] No match for trapdoor in Patient {patient_id}.")
            
        return results
