# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest
from presence_analyzer.utils import seconds_since_midnight, mean, interval
from presence_analyzer.utils import group_by_weekday_start_end, \
    group_by_weekday
from presence_analyzer import main, utils



TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)
TEST_USERS_NAMES = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_users.xml'
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
        main.app.config.update({'USERS_NAMES': TEST_USERS_NAMES})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page view.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<html lang=en>', resp.data)
        self.assertIn('<h2>Presence by weekday</h2>', resp.data)

    def test_mean_time(self):
        """
        Test mean_time_weekday view.
        """
        resp = self.client.get('/mean_time_weekday')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<html lang=en>', resp.data)
        self.assertIn('<h2>Presence mean time by weekday</h2>', resp.data)

    def test_start_end(self):
        """
        Test presence_start_end view.
        """
        resp = self.client.get('/presence_start_end')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<html lang=en>', resp.data)
        self.assertIn('<h2>Presence start-end weekday</h2>', resp.data)

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], {u'user_id': u'141',
                                       u'name': u'Adam Pieśkiewicz'})
        #self.assertEqual(len(data), 2)
        #self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_avatar_view(self):
        """
        Test avatar viewing
        """
        resp = self.client.get('/api/v1/get_avatar/141')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(data,
                         'https://intranet.stxnext.pl/api/images/users/141')

    def test_mean_time_weekday_view(self):
        """
        Test day abbr
        """
        resp = self.client.get('api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertEqual('pon', data[0][0])
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
        self.assertEqual('pon', data[1][0])
        self.assertEqual(0, data[1][1])
        self.assertEqual(23705, data[4][1])

    def test_presence_start_end_view(self):
        """
        Test presence start end views
        """
        resp = self.client.get('api/v1/presence_start_end/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual('pon', data[0][0])
        self.assertEqual(33134, data[0][1])
        self.assertEqual(57257, data[0][2])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'USERS_NAMES': TEST_USERS_NAMES})

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

    def test_get_users(self):
        """
        Test getting users
        """
        data = utils.get_users()
        self.assertIsInstance(data, dict)
        self.assertEqual(data.keys(), ['141'])
        self.assertEqual(data['141'], u'Adam Pieśkiewicz')

    def test_get_avatars(self):
        """
        Test getting avatar
        """
        data = utils.get_avatars()
        self.assertEqual(data.keys(), ['141'])
        self.assertEqual(data['141'],
                         'https://intranet.stxnext.pl/api/images/users/141')

    def test_group_by_weekday(self):
        """
        Test group by weekday
        """
        data = utils.get_data()
        weekdays = group_by_weekday(data[11])
        self.assertEqual([24123], weekdays[0])
        self.assertEqual([22969, 22999], weekdays[3])

    def test_seconds_since_midnight(self):
        """
        Test calculate to seconds
        """
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
        start = datetime.time(2, 3, 2)
        end = datetime.time(3, 2, 3)
        result = interval(start, end)
        self.assertEqual(3541, result)

    def test_mean(self):
        """
        Test mean
        """
        items = [2, 3, 5, 10]
        result = mean(items)
        self.assertEqual(5, result)

    def test_group_by_weekday_start_end(self):
        """
        Test group by weekdat start end
        """
        data = utils.get_data()
        result_start, result_stop = group_by_weekday_start_end(data[11])
        self.assertEqual([33134], result_start[0])
        self.assertEqual([57257], result_stop[0])
        self.assertEqual([37116, 34088], result_start[3])
        self.assertEqual([60085, 57087], result_stop[3])


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
