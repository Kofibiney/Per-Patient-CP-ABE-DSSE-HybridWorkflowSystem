from src.core.aes_provider import AESProvider
from src.core.dsse_scheme import DynamicDSSEScheme
from src.core.abe_wrapper import CPABEProvider

class User:
    """
    Simulates a Data User (Clinician).
    Capabilities:
    1. Holds CP-ABE attributes & secret key.
    2. 'Patient Lookup': Decrypts the patient's symmetric key.
    3. 'Search': Generates trapdoors.
    4. 'Retrieve': Decrypts the record.
    """

    def __init__(self, name, attributes, secret_key, public_key):
        self.name = name
        self.attributes = attributes
        self.sk = secret_key
        self.pk = public_key
        self.abe = CPABEProvider()

    def attempt_access_and_search(self, patient_id, search_keyword, server, owner):
        """
        Full workflow: Lookup -> Decrypt Key -> Search -> (Optional) Decrypt Record
        NOW USES OWNER'S PERSISTENT DSSE STATE (no counter guessing)
        """
        print(f"\n[User: {self.name}] Attempting to access Patient {patient_id}...")
        
        # 1. Fetch Encrypted Key
        enc_key_ct = server.get_encrypted_key(patient_id)
        if enc_key_ct is None:
            return False

        # 2. Try to Decrypt the Key (Patient Lookup Phase)
        try:
            sym_key = self.abe.decrypt(self.pk, self.sk, enc_key_ct)
            print("  -> [Success] Key decrypted! Access Granted.")
        except Exception as e:
            print(f"  -> [Failure] Access Denied. CP-ABE Policy check failed. {e}")
            return False

        # 3. Perform Search using owner's DSSE state (CORRECTED)
        print(f"  -> Searching for keyword: '{search_keyword}'")
        trapdoors = owner.generate_search_tokens(patient_id, search_keyword)
        
        results = server.search(patient_id, trapdoors)
        
        if results:
            print(f"  -> [Search Hit] Found documents: {results}")
            return True
        else:
            print("  -> [Search Miss] Keyword not found in record.")
            return False

    def decrypt_full_record(self, patient_id, server):
        """
        Decrypts the actual content of the record.
        """
        # (This repeats the key decryption... in a real app, we'd cache the session key)
        enc_key_ct = server.get_encrypted_key(patient_id)
        enc_record_dict = server.get_encrypted_record(patient_id)
        
        if enc_key_ct is None or enc_record_dict is None:
            return "Error: Missing patient data (key or record) on server."
        
        try:
            sym_key = self.abe.decrypt(self.pk, self.sk, enc_key_ct)
            plaintext = AESProvider.decrypt(enc_record_dict, sym_key)
            return plaintext.decode('utf-8')
        except Exception as e:
            return f"Error: {e}"
