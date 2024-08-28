import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
import pandas as pd
from collections import defaultdict
from tagmatch.synonym_manager import SynonymManager 

class TestSynonymManager(unittest.TestCase):
    def setUp(self):
        self.names_storage = ["Moon", "Apollo 11", "Moon Mission", "Mars", "Venus"]
        self.sm = SynonymManager(self.names_storage)
        self.sample_df = pd.DataFrame({
            'word': ['Moon', 'Moon', 'Mars', 'Mars'],
            'synonym': ['Apollo 11', 'Moon Mission', 'Red Planet', 'Venus']
        })

    def test_init(self):
        self.assertEqual(self.sm.names_storage, self.names_storage)
        self.assertTrue(self.sm.synonym_csv.empty)
        self.assertEqual(len(self.sm.synonym_dict), 0)

    def test_set_names_storage(self):
        new_storage = ["Earth", "Sun", "Jupiter"]
        self.sm.set_names_storage(new_storage)
        self.assertEqual(self.sm.names_storage, new_storage)

    def test_set_synonym_csv(self):
        self.sm.set_synonym_csv(self.sample_df)
        self.assertFalse(self.sm.synonym_csv.empty)
        self.assertEqual(len(self.sm.synonym_dict), 5)  

    def test_remove_synonym_csv(self):
        self.sm.set_synonym_csv(self.sample_df)
        self.sm.remove_synonym_csv()
        self.assertTrue(self.sm.synonym_csv.empty)
        self.assertEqual(len(self.sm.synonym_dict), 0)

    def test_synonyms_exist(self):
        self.assertFalse(self.sm.synonyms_exist())
        self.sm.set_synonym_csv(self.sample_df)
        self.assertTrue(self.sm.synonyms_exist())

    def test_get_synonym_count(self):
        self.assertEqual(self.sm.get_synonym_count(), -1)
        self.sm.set_synonym_csv(self.sample_df)
        self.assertEqual(self.sm.get_synonym_count(), 4)

    def test_create_synonym_dict(self):
        self.sm.set_synonym_csv(self.sample_df)
        expected_dict = defaultdict(set, {
            'moon': {'apollo 11', 'moon mission'},
            'apollo 11': {'moon', 'moon mission'},
            'moon mission': {'moon', 'apollo 11'},
            'mars' : {'venus'},
            'venus' : {'mars'}
        })
        self.assertEqual(dict(self.sm.synonym_dict), dict(expected_dict))

    def test_apply_transitivity(self):
        df = pd.DataFrame({
            'word': ['A', 'B', 'C'],
            'synonym': ['B', 'C', 'D']
        })
        self.sm.names_storage = ['A', 'B', 'C', 'D']
        self.sm.set_synonym_csv(df)
        expected_dict = defaultdict(set, {
            'a': {'b', 'c', 'd'},
            'b': {'a', 'c', 'd'},
            'c': {'a', 'b', 'd'},
            'd': {'a', 'b', 'c'}
        })
        self.assertEqual(dict(self.sm.synonym_dict), dict(expected_dict))

    def test_get_synonym(self):
        self.sm.set_synonym_csv(self.sample_df)
        self.assertEqual(self.sm.get_synonym('moon'), {'apollo 11', 'moon mission'})
        self.assertEqual(self.sm.get_synonym('apollo 11'), {'moon', 'moon mission'})
        self.assertEqual(self.sm.get_synonym('mars'), {'venus'})
        self.assertEqual(self.sm.get_synonym('venus'), {'mars'})
        self.assertIsNone(self.sm.get_synonym('nonexistent'))

    def test_nonexistent_names(self):
        df = pd.DataFrame({
            'word': ['Moon', 'Jupiter'],
            'synonym': ['Apollo 11', 'Gas Giant']
        })
        self.sm.set_synonym_csv(df)
        self.assertNotIn('jupiter', self.sm.synonym_dict)
        self.assertNotIn('gas giant', self.sm.synonym_dict)

if __name__ == '__main__':
    unittest.main()