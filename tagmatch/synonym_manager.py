from typing import Dict, List, Set
import pandas as pd
from collections import defaultdict

class SynonymManager:
    def __init__(self, names_storage: List[str]):
        self.names_storage = names_storage
        self.synonym_csv: pd.DataFrame = pd.DataFrame()
        self.synonym_dict: defaultdict[str, Set[str]] = defaultdict(set)

    def set_names_storage(self, names_storage: List[str]):
        self.names_storage = names_storage

    def set_synonym_csv(self, synonym_csv: pd.DataFrame):
        self.synonym_csv = synonym_csv
        self._create_synonym_dict()

    def remove_synonym_csv(self):
        self.synonym_csv = pd.DataFrame()
        self.synonym_dict = defaultdict(set)
    
    def synonyms_exist(self):
        if not self.synonym_csv.empty:
            return True
        return False
    
    def get_synonym_count(self) -> int:
        nb_points = len(self.synonym_csv) if not self.synonym_csv.empty else None
        if nb_points is None:
            return -1
        return nb_points

    def _create_synonym_dict(self):      
        for _, row in self.synonym_csv.iterrows():
            if row['word'] in self.names_storage and row['synonym'] in self.names_storage:
                self.synonym_dict[row['word'].lower()].add(row['synonym'].lower())
                self.synonym_dict[row['synonym'].lower()].add(row['word'].lower())
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

    def get_synonym(self, word: str) -> Set[str]:
        return self.synonym_dict.get(word)
    
    
    