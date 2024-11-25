from django.test import TestCase
from datetime import datetime
from tutorials.views import combine_date_and_time  # Import the helper function

class CombineDateAndTimeTests(TestCase):
    def test_valid_date_and_time(self):
        """Test with valid date and time"""
        date_str = "2024-11-25"
        time_str = "14:30"
        
        result = combine_date_and_time(date_str, time_str)
        
        # Expected result: datetime object for '2024-11-25 14:30:00'
        expected = datetime(2024, 11, 25, 14, 30)
        
        self.assertEqual(result, expected)

    def test_valid_date_with_time_at_midnight(self):
        """Test with valid date and time of '00:00' (midnight)"""
        date_str = "2024-11-25"
        time_str = "00:00"
        
        result = combine_date_and_time(date_str, time_str)
        
        # Expected result: datetime object for '2024-11-25 00:00:00'
        expected = datetime(2024, 11, 25, 0, 0)
        
        self.assertEqual(result, expected)

    def test_invalid_date_format(self):
        """Test with invalid date format"""
        date_str = "25-11-2024"  # Invalid format
        time_str = "14:30"
        
        result = combine_date_and_time(date_str, time_str)
        
        self.assertIsNone(result)

    def test_invalid_time_format(self):
        """Test with invalid time format"""
        date_str = "2024-11-25"
        time_str = "14:60"  # Invalid time
        
        result = combine_date_and_time(date_str, time_str)
        
        self.assertIsNone(result)

    def test_missing_date(self):
        """Test with missing date"""
        date_str = ""
        time_str = "14:30"
        
        result = combine_date_and_time(date_str, time_str)
        
        self.assertIsNone(result)

    def test_missing_time(self):
        """Test with missing time"""
        date_str = "2024-11-25"
        time_str = ""
        
        result = combine_date_and_time(date_str, time_str)
        
        self.assertIsNone(result)

    def test_both_missing(self):
        """Test with both date and time missing"""
        date_str = ""
        time_str = ""
        
        result = combine_date_and_time(date_str, time_str)
        
        self.assertIsNone(result)
