import unittest
from src.feature_extraction.extract_features import *
from src.training.train_and_test import *

class TestFeatureExtraction(unittest.TestCase):
    def test(self):
        feature_extractor('/home/lhh/Learning-based-QPP/test_files_open_source/plans.json', '/home/lhh/Learning-based-QPP/test_files_open_source/plans_seq.json')
if __name__ == '__main__':
    unittest.main()