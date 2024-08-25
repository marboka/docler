import json
from typing import Dict, List, Set
import pandas as pd
from collections import defaultdict

class TagOverrideManager:
    def __init__(self, names_storage: List[str]):
        self.names_storage = names_storage
        self.synonym_dict: Dict[str, Set[str]] = defaultdict(set)

    def load_overrides(self, override_json_path: str):
        file = open(override_json_path)
        overrides = json.load(file)
        for pair in overrides["synonyms"]:
            if pair[0] in self.names_storage and pair[1] in self.names_storage:
                self.synonym_dict[pair[0]].add(pair[1])
                self.synonym_dict[pair[1]].add(pair[0])
        self._apply_transitivity()
        
    def _apply_transitivity(self):
        changed = True
        while changed:
            changed = False
            for word in list(self.synonym_dict.keys()):
                synonyms = set(self.synonym_dict[word])
                for synonym in list(synonyms):
                    if self.synonym_dict[synonym] - synonyms:
                        self.synonym_dict[word].update(self.synonym_dict[synonym])
                        changed = True
        for word in self.synonym_dict:
            self.synonym_dict[word].discard(word)

    def get_synonyms(self, tag: str) -> Set[str]:
        return self.synonym_dict.get(tag)
    
    
    