#!/bin/env python
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)
EVENT_LINK_HREF_RE = re.compile(r'^/events/view/(?P<id>\d+)$')
APP_URL = 'https://calendar.dallasmakerspace.org'

def grab_event_info_from_link(link):
    href = link['href']

    res = requests.get(APP_URL + href)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    eid = EVENT_LINK_HREF_RE.match(href).group('id')
    einfo = None
    return eid, einfo

@app.route("/")
def todays_events_info():
    today = datetime.today()
    current_year = today.year
    current_date = today.date()

    res = requests.get(APP_URL + '/events/embed')
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    grab_events = False
    event_links = []
    # Get today's events
    for child in soup.find(True, 'event-list')(True, recursive=False):
        if 'date-break' in child['class']:
            listing_date = datetime.strptime('{} {}'.format(child.string.strip(), current_year), '%A, %B %d %Y').date()
            grab_events = listing_date == current_date
        elif grab_events:
            event_links.append(child.find('a', href=EVENT_LINK_HREF_RE))
    # return '<br>'.join(APP_URL + link['href'] for link in event_links)
    d = { '1-2-3': {'foo': 'bar'}}
    return jsonify(date=current_date,
                   events=dict(map(grab_event_info_from_link, event_links)))

if __name__ == '__main__':
    # app.run()
    return_info()
