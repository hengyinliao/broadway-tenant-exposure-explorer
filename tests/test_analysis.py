import unittest

from scripts.analysis import calculate_land_improvement_ratio, calculate_redevelopment_activity
from scripts.analysis import calculate_redevelopment_pressure, classify_exposure_matrix
from scripts.analysis import normalize_indicator, validate_missing_data


class AnalysisTests(unittest.TestCase):
    def test_indicator_direction_and_bounds(self):
        self.assertEqual(normalize_indicator(10, 0, 20), 50)
        self.assertEqual(normalize_indicator(30, 0, 20), 100)
        self.assertEqual(normalize_indicator(5, 0, 20, reverse=True), 75)

    def test_land_ratio_and_activity_direction(self):
        self.assertEqual(calculate_land_improvement_ratio(900, 100), .9)
        self.assertGreater(calculate_redevelopment_activity(demolitions=1),
                           calculate_redevelopment_activity(major_alterations=1))

    def test_required_missing_component_never_becomes_zero(self):
        values = {'activity': 80, 'policy': None, 'land': 60}
        self.assertIsNone(calculate_redevelopment_pressure(
            values, {'activity': 30, 'policy': 25, 'land': 20}))
        self.assertEqual(calculate_redevelopment_pressure(
            values, {'activity': 30, 'policy': 0, 'land': 20}), 72)

    def test_missing_renter_data_blocks_matrix_classification(self):
        self.assertIsNone(classify_exposure_matrix(80, None))
        self.assertEqual(validate_missing_data({'renter_share': None}, ['renter_share']),
                         ['renter_share'])


if __name__ == '__main__':
    unittest.main()
