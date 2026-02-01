import hashlib
import os
from collections import defaultdict
import base64

class DynamicDSSEScheme:
    """
    Implements a Dynamic Searchable Symmetric Encryption (DSSE) scheme
    with Forward Privacy.
    
    Mechanism:
    - Maintains a state 'counter' for each keyword (c_w).
    - Trapdoor for index insertion: H(K, w || c_w)
    - Forward Privacy: Since c_w increments, future insertions use 
      different hashes than past searches.
    """

    def __init__(self, key: bytes):
        self.key = key
        # State: Maps keyword -> current counter (int)
        # In a real system, this state must be persisted securely by the Data Owner.
        self.index_counters = defaultdict(int)

    def _hash_keyword_with_count(self, keyword: str, count: int) -> str:
        """
        Computes the secure hash H(k, w || count).
        Unlinks new entries from old ones.
        """
        kw = keyword.lower().strip().encode('utf-8')
        count_bytes = str(count).encode('utf-8')
        
        # Inner: H(key || w || count)
        inner = hashlib.sha256(self.key + kw + count_bytes).digest()
        # Outer
        outer = hashlib.sha256(inner).hexdigest()
        return outer

    def build_index(self, keywords: list, doc_id: str) -> dict:
        """
        Adds entries to the dynamic index.
        Increments the counter for each keyword to ensure Forward Privacy.
        """
        index_entries = {}
        for w in keywords:
            # 1. Update State
            self.index_counters[w] += 1
            curr_count = self.index_counters[w]
            
            # 2. Generate Trapdoor for this specific instance
            trapdoor = self._hash_keyword_with_count(w, curr_count)
            
            # 3. Create Entry 
            # (In a full scheme, the doc_id is encrypted. Here we focus on the index key)
            index_entries[trapdoor] = [doc_id]
            
        return index_entries

    def generate_search_tokens(self, keyword: str) -> list:
        """
        Generates all valid trapdoors for a keyword up to the current counter.
        This allows the server to find all previous occurrences.
        """
        tokens = []
        count = self.index_counters.get(keyword, 0)
        for i in range(1, count + 1):
            tokens.append(self._hash_keyword_with_count(keyword, i))
        return tokens

    @staticmethod
    def search(index: dict, trapdoors: list) -> list:
        """
        Server-side operation.
        Checks all provided trapdoors (historical variants) against the index.
        """
        results = []
        for t in trapdoors:
            if t in index:
                results.extend(index[t])
        return results
