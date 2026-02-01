from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
import pickle
import base64

class CPABEProvider:
    """
    Wrapper for the Bethencourt-Sahai-Waters (BSW07) CP-ABE scheme.
    Requires 'charm-crypto' library.
    """

    def __init__(self, group_id='SS512'):
        """
        Initializes the pairing group.
        SS512 is a symmetric curve providing 80-bit security (fast for prototyping).
        MNT224 is an alternative.
        """
        self.group = PairingGroup(group_id)
        self.cpabe = CPabe_BSW07(self.group)

    def setup(self):
        """
        Runs the Setup algorithm.
        Returns (public_key, master_key).
        """
        (pk, mk) = self.cpabe.setup()
        return pk, mk

    def keygen(self, pk, mk, attributes: list):
        """
        Generates a private key for a user with the given list of attributes.
        attributes: List of strings e.g., ['DOCTOR', 'CARDIOLOGY']
        """
        # Upper case attributes for consistency
        attrs = [a.upper() for a in attributes]
        sk = self.cpabe.keygen(pk, mk, attrs)
        return sk

    def encrypt(self, pk, key_material: bytes, policy_str: str):
        """
        Encrypts a random symmetric key (key_material) under an access policy.
        policy_str: Boolean formula e.g., '((DOCTOR and CARDIOLOGY) or ADMIN)'
        """
        # Encrypt the symmetric key. 
        # Note: BSW07 encrypts a group element. We need to map bytes -> group element?
        # Standard approach: BSW07 generates a random session key (msg) as a group element GT.
        # We can let CP-ABE generate the GT element, then we hash it to get our symmetric key bytes?
        # OR we can try to encode our key into GT (hard).
        
        # Better Approach for Hybrid Encryption:
        # Let CP-ABE choose the random secret 'm' (in GT).
        # We assume 'encrypt' returns the ciphertext AND the random message 'm'.
        # But standard charm BSW encrypt takes a message 'm'.
        
        # So:
        # 1. Map our key_material to a GT element? (Difficult, GT is multiplicative group)
        # 2. Hashing approach (Standard KEM):
        #    Generate random GT element 'r'.
        #    Symmetric Key K = Hash(r).
        #    Ciphertext = CP-ABE.Encrypt(pk, r, policy).
        #    Return (Ciphertext, K).
        
        try:
            r = self.group.random(GT)
            ciphertext = self.cpabe.encrypt(pk, r, policy_str)
            
            # Derive symmetric key bytes from the group element 'r'
            import hashlib
            r_bytes = self.group.serialize(r)
            derived_key = hashlib.sha256(r_bytes).digest() 
            
            return ciphertext, derived_key
        except Exception as e:
            import traceback
            print(f"[CPABEProvider] Encryption failed for policy: {policy_str}")
            traceback.print_exc()
            return None, None

    def decrypt(self, pk, sk, ciphertext):
        """
        Decrypts the ciphertext using the secret key sk.
        Returns the derived symmetric key bytes if successful.
        """
        try:
            r_recovered = self.cpabe.decrypt(pk, sk, ciphertext)
            if r_recovered:
                r_bytes = self.group.serialize(r_recovered)
                import hashlib
                return hashlib.sha256(r_bytes).digest()
            else:
                raise Exception("Decryption failed (Attributes may not satisfy policy).")
        except Exception as e:
            raise Exception(f"Decryption error: {str(e)}")

    @staticmethod
    def serialize_artifact(artifact):
        """
        Helper to serialize Keys/Ciphertexts for storage/transmission.
        Since they contain C-objects, we use pickle + base64.
        """
        return base64.b64encode(pickle.dumps(artifact)).decode('utf-8')

    @staticmethod
    def deserialize_artifact(b64_str):
        """
        Helper to deserialize.
        """
        return pickle.loads(base64.b64decode(b64_str))
