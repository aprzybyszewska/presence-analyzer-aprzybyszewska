# -*- coding: utf-8 -*-
"""
Defines views.
"""
import calendar
import locale
from flask import render_template

from presence_analyzer.main import app
from presence_analyzer.utils import jsonify, get_data, mean, group_by_weekday
from presence_analyzer.utils import group_by_weekday_start_end
from presence_analyzer.utils import get_users, get_avatars

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103

locale.setlocale(locale.LC_ALL, "pl_PL.UTF-8")


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return render_template('presence_weekday.html')


@app.route('/mean_time_weekday')
def mean_time():
    """
    Redirects to mean_time_weekday page.
    """
    return render_template('mean_time_weekday.html')


@app.route('/presence_start_end')
def start_end():
    """
    Redirects to presence_start_end page.
    """
    return render_template('presence_start_end.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    users = get_users()
    data = get_data()
    result = [{'user_id': i, 'name': users[i]}
        for i in users.keys() if int(i) in data.keys()]

    result.sort(key=lambda item: item['name'], cmp=locale.strcoll)
    return result


@app.route('/api/v1/get_avatar/<int:user_id>', methods=['GET'])
@jsonify
def avatar_view(user_id):
    """
    Viewing avatars
    """
    avatars = get_avatars()
    user_id = str(user_id)
    return avatars[user_id]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    #import pdb; pdb.set_trace()
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns mean start and end hours grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    result_start, result_stop = group_by_weekday_start_end(data[user_id])
    result = []
    for i in range(7):
        result.append((
            calendar.day_abbr[i], mean(result_start[i]), mean(result_stop[i])))

    return result
