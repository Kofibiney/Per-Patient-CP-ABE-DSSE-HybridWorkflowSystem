from src.core.aes_provider import AESProvider
from src.core.dsse_scheme import DynamicDSSEScheme
from src.core.abe_wrapper import CPABEProvider

class DataOwner:
    """
    Simulates the Hospital / Data Owner.
    Responsible for:
    1. System Setup (generating MK, PK).
    2. Encrypting Patient Records (AES + DSSE).
    3. Defining Access Policies (CP-ABE).
    """

    def __init__(self):
        self.abe = CPABEProvider()
        self.pk = None
        self.__mk = None
        # NEW: Persistent DSSE state per patient (client-side)
        self.dsse_states = {}  # { patient_id: DynamicDSSEScheme }
        self.patient_keys = {}  # { patient_id: (derived_sym_key, enc_key_ct) }

    def setup_system(self):
        """
        Initializes the cryptographic parameters.
        """
        print("[DataOwner] Setting up CP-ABE system...")
        self.pk, self.__mk = self.abe.setup()
        return self.pk

    def generate_user_key(self, attributes):
        """
        Issues a secret key to a user based on their attributes.
        """
        print(f"[DataOwner] Generating Key for attributes: {attributes}")
        return self.abe.keygen(self.pk, self.__mk, attributes)

    def encrypt_and_upload(self, patient_id, record_text, keywords, access_policy, server):
        """
        The core 'Workflow-Aware' Encryption process - NOW TRULY DYNAMIC:
        1. Encrypt Record (AES)
        2. Build/Update Index (DSSE) - PERSISTENT STATE
        3. Encrypt Key (CP-ABE)
        4. Upload to Server
        """
        print(f"\n[DataOwner] Processing Record for Patient: {patient_id}")
        
        # 1. Generate or reuse symmetric key
        if patient_id in self.patient_keys:
            derived_sym_key, enc_key_ct = self.patient_keys[patient_id]
            print(f"[DataOwner] Reusing existing key for Patient: {patient_id}")
        else:
            # First time: encrypt key with CP-ABE
            print(f"[DataOwner] Encrypting Key under Policy: {access_policy}")
            enc_key_ct, derived_sym_key = self.abe.encrypt(self.pk, b"", access_policy)
            self.patient_keys[patient_id] = (derived_sym_key, enc_key_ct)
        
        # 2. Encrypt content
        enc_record = AESProvider.encrypt(record_text.encode('utf-8'), derived_sym_key)
        
        # 3. Build/Update DSSE Index (PERSISTENT STATE)
        if patient_id not in self.dsse_states:
            self.dsse_states[patient_id] = DynamicDSSEScheme(derived_sym_key)
            print(f"[DataOwner] Created new DSSE state for Patient: {patient_id}")
        
        dsse = self.dsse_states[patient_id]
        enc_index_update = dsse.build_index(keywords, doc_id="main_record")
        
        # Merge update into existing index
        if patient_id in server.storage and 'enc_index' in server.storage[patient_id]:
            existing_index = server.storage[patient_id]['enc_index']
            existing_index.update(enc_index_update)
            print(f"[DataOwner] Updated existing index (+{len(enc_index_update)} trapdoors)")
        else:
            existing_index = enc_index_update
            print(f"[DataOwner] Created new index ({len(enc_index_update)} trapdoors)")
        
        # 4. Upload
        server.upload(patient_id, enc_record, existing_index, enc_key_ct)
        print("[DataOwner] Upload Complete.")

    def add_keywords(self, patient_id, new_keywords, server):
        """
        Dynamic update: add new keywords to an existing patient's index.
        This is the key operation that makes DSSE truly dynamic.
        """
        if patient_id not in self.dsse_states:
            raise ValueError(f"No DSSE state for patient {patient_id}. Must encrypt_and_upload first.")
        
        if patient_id not in server.storage:
            raise ValueError(f"Patient {patient_id} not found on server.")
        
        print(f"\n[DataOwner] Adding {len(new_keywords)} keywords to Patient: {patient_id}")
        
        dsse = self.dsse_states[patient_id]
        update_index = dsse.build_index(new_keywords, doc_id="main_record")
        
        # Merge into server-side index (FIXED: use 'enc_index' not 'index')
        server.storage[patient_id]['enc_index'].update(update_index)
        print(f"[DataOwner] Index updated (+{len(update_index)} new trapdoors)")

        
        return len(update_index)
    
    def delete_keywords(self, patient_id, keywords_to_delete, server):
        """
        Dynamic deletion: remove keywords from patient's index.
        """
        if patient_id not in self.dsse_states:
            raise ValueError(f"No DSSE state for patient {patient_id}.")
        
        if patient_id not in server.storage:
            raise ValueError(f"Patient {patient_id} not found on server.")
        
        print(f"\n[DataOwner] Deleting {len(keywords_to_delete)} keywords from Patient: {patient_id}")
        
        dsse = self.dsse_states[patient_id]
        index = server.storage[patient_id]['enc_index']  # FIXED

        
        deleted_count = 0
        for kw in keywords_to_delete:
            if kw in dsse.index_counters:
                count = dsse.index_counters[kw]
                for c in range(1, count + 1):
                    trapdoor = dsse._hash_keyword_with_count(kw, c)
                    if trapdoor in index:
                        del index[trapdoor]
                        deleted_count += 1
                dsse.index_counters[kw] = 0
        
        print(f"[DataOwner] Deleted {deleted_count} trapdoors")
        return deleted_count
    
    def generate_search_tokens(self, patient_id, keyword):
        """
        Generate search tokens using the persistent DSSE state.
        This ensures counters are always correct.
        """
        if patient_id not in self.dsse_states:
            raise ValueError(f"No DSSE state for patient {patient_id}.")
        
        dsse = self.dsse_states[patient_id]
        return dsse.generate_search_tokens(keyword)
