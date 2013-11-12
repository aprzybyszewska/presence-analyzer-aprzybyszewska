# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest
import calendar
from utils import seconds_since_midnight, mean, interval, group_by_weekday, start_end
from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday_view(self):
        """
        Test day abbr
        """
        resp = self.client.get('api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertEqual('Mon', data[0][0])
        self.assertEqual(0, data[0][1])
        self.assertEqual(30047.0, data[1][1])

    def test_presence_weekday_view(self):
        """
        Test day abbr
        """
        resp = self.client.get('api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertEqual('Mon', data[1][0])
        self.assertEqual(0, data[1][1])
        self.assertEqual(23705, data[4][1])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_group_by_weekday(self):
        """
        Test weekday
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 11)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 19, 52))
        sample_weekday = 2
        self.assertEqual(sample_date.weekday(), sample_weekday)
        print data[10]

    def test_seconds_since_midnight(self):
        """
        Test calculate to seconds
        """
        from presence_analyzer.utils import seconds_since_midnight
        start = datetime.time(2, 3, 2)
        end = datetime.time(3, 2, 3)
        result_start = seconds_since_midnight(start)
        self.assertEqual(7382, result_start)
        result_end = seconds_since_midnight(end)
        self.assertEqual(10923, result_end)

    def test_interval(self):
        """
        Test interval
        """
        from presence_analyzer.utils import interval
        start = datetime.time(2, 3, 2)
        end = datetime.time(3, 2, 3)
        result = interval(start, end)
        self.assertEqual(3541, result)

    def test_mean(self):
        """
        Test mean
        """
        from presence_analyzer.utils import mean
        items = [2, 3, 5, 10]
        result = mean(items)
        self.assertEqual(5, result)

    def test_start_end(self):
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                        datetime.time(9, 39, 5))

        result_start = {i: [] for i in range(7)}
        result_stop = {i: [] for i in range(7)}
        items = data[11]
        mean_weekday = []
        for date in items:
            start = items[date]['start']
            end = items[date]['end']
            result_start[date.weekday()].append(seconds_since_midnight(start))
            result_stop[date.weekday()].append(seconds_since_midnight(end))
        for i in range(7):
            mean_weekday.append((mean(result_start[i]), mean(result_stop[i])))
        return mean_weekday


def suite():
    """
    Default test suite.B
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
