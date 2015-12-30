# -*- coding: utf-8 -*-

from .. import pmeventparser
import unittest
import datetime
import pytz

class Test8to5Calendar(unittest.TestCase):
    """
    Tests the 8 to 5 calendar rules
    """
    def test_1_min_after_5pm(self):
        input_date = datetime.datetime(2015, 12, 29, 17, 1, 0,
                                      tzinfo=pytz.timezone("US/Eastern"))
        # Next day. 8:00 AM
        expected_date = datetime.datetime(2015, 12, 30, 8, 0, 0,
                                          tzinfo=pytz.timezone("US/Eastern"))
        output_date = pmeventparser.restrict_to_standard_calendar(input_date)
        self.assertTrue(expected_date == output_date)

    def test_at_5pm(self):
        input_date = datetime.datetime(2015, 12, 29, 17, 0, 0,
                                      tzinfo=pytz.timezone("US/Eastern"))
        # Same day. 5:00 PM
        expected_date = datetime.datetime(2015, 12, 29, 17, 0, 0,
                                          tzinfo=pytz.timezone("US/Eastern"))
        output_date = pmeventparser.restrict_to_standard_calendar(input_date)
        self.assertTrue(expected_date == output_date)

    def test_at_459pm(self):
        input_date = datetime.datetime(2015, 12, 29, 16, 59, 0,
                                      tzinfo=pytz.timezone("US/Eastern"))
        # Same day. 4:59 PM
        expected_date = datetime.datetime(2015, 12, 29, 16, 59, 0,
                                          tzinfo=pytz.timezone("US/Eastern"))
        output_date = pmeventparser.restrict_to_standard_calendar(input_date)
        self.assertTrue(expected_date == output_date)

    def test_at_759pm(self):
        input_date = datetime.datetime(2015, 12, 29, 7, 59, 0,
                                      tzinfo=pytz.timezone("US/Eastern"))
        # Same day. 8 AM
        expected_date = datetime.datetime(2015, 12, 29, 8, 0, 0,
                                          tzinfo=pytz.timezone("US/Eastern"))
        output_date = pmeventparser.restrict_to_standard_calendar(input_date)
        self.assertTrue(expected_date == output_date)

    def test_at_midnight(self):
        input_date = datetime.datetime(2015, 12, 29, 0, 0, 0,
                                      tzinfo=pytz.timezone("US/Eastern"))
        # Same day. 8 AM
        expected_date = datetime.datetime(2015, 12, 29, 8, 0, 0,
                                          tzinfo=pytz.timezone("US/Eastern"))
        output_date = pmeventparser.restrict_to_standard_calendar(input_date)
        self.assertTrue(expected_date == output_date)

    def test_at_2359(self):
        input_date = datetime.datetime(2015, 12, 29, 23, 59, 0,
                                      tzinfo=pytz.timezone("US/Eastern"))
        # Next day. 8 AM
        expected_date = datetime.datetime(2015, 12, 30, 8, 0, 0,
                                          tzinfo=pytz.timezone("US/Eastern"))

        output_date = pmeventparser.restrict_to_standard_calendar(input_date)

        print(output_date)

        self.assertTrue(expected_date == output_date)

if __name__ == '__main__':
    unittest.main()
