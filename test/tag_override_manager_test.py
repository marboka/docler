import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import unittest
from tag_override_manager import TagOverrideManager


class TestTagOverrideManager(unittest.TestCase):
    def test_read_json(self):
        #arrange
        csv_tags = pd.read_csv("./tags/dummy_tags.csv", sep=None, header=0, engine="python")
        names_storage = csv_tags["name"].dropna().unique().tolist()
        tag_override_manager = TagOverrideManager(names_storage)
        #act
        tag_override_manager.load_overrides("test/manual_tags_test1.json")
        processed_dict = tag_override_manager.synonym_dict
        #assert
        expected_dict = {"Moon": {"Apollo 11", "Landing", "Spacecraft", "Moon Mission"}, 
                         "Moon Mission": {"Apollo 11", "Landing", "Spacecraft", "Moon"}, 
                         "Apollo 11": {"Landing", "Spacecraft", "Moon", "Moon Mission"}, 
                         "Spacecraft": {"Apollo 11", "Landing", "Moon", "Moon Mission"}, 
                         "Landing": {"Apollo 11", "Spacecraft", "Moon", "Moon Mission"}, 
                         "NASA": {"ESA"}, 
                         "ESA": {"NASA"}}
        self.assertDictEqual(dict(processed_dict), expected_dict)

    def test_get_synonyms(self):
        #arrange
        csv_tags = pd.read_csv("./tags/dummy_tags.csv", sep=None, header=0, engine="python")
        names_storage = csv_tags["name"].dropna().unique().tolist()
        tag_override_manager = TagOverrideManager(names_storage)
        #act
        tag_override_manager.load_overrides("test/manual_tags_test1.json")
        #assert
        self.assertEqual(tag_override_manager.get_synonyms("abc"), None)

        self.assertEqual(tag_override_manager.get_synonyms("ESA"), {"NASA"})
        self.assertEqual(tag_override_manager.get_synonyms("NASA"), {"ESA"})

        self.assertEqual(tag_override_manager.get_synonyms("Landing"), {"Apollo 11", "Spacecraft", "Moon", "Moon Mission"})
        self.assertEqual(tag_override_manager.get_synonyms("Spacecraft"), {"Apollo 11", "Landing", "Moon", "Moon Mission"})
    

if __name__ == "__main__":
    test_class = TestTagOverrideManager()
    test_class.test_read_json()
    test_class.test_get_synonyms()