from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import json
import base64

class AESProvider:
    """
    Provides Authenticated Symmetric Encryption (AES-256-GCM) for EHR records.
    """
    
    @staticmethod
    def generate_key():
        """Generates a random 256-bit (32 byte) symmetric key."""
        return get_random_bytes(32)

    @staticmethod
    def encrypt(data: bytes, key: bytes) -> dict:
        """
        Encrypts data using AES-GCM.
        Returns a dictionary containing the ciphertext, nonce, and tag (all base64 encoded strings).
        """
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        
        return {
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'nonce': base64.b64encode(cipher.nonce).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8')
        }

    @staticmethod
    def decrypt(enc_dict: dict, key: bytes) -> bytes:
        """
        Decrypts an AES-GCM encrypted dictionary.
        Expects keys: 'ciphertext', 'nonce', 'tag' (base64 strings).
        """
        try:
            nonce = base64.b64decode(enc_dict['nonce'])
            tag = base64.b64decode(enc_dict['tag'])
            ciphertext = base64.b64decode(enc_dict['ciphertext'])
            
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            data = cipher.decrypt_and_verify(ciphertext, tag)
            return data
        except (ValueError, KeyError) as e:
            raise ValueError("Decryption failed: Invalid key or corrupted data.") from e
