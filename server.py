#!/bin/env python
import re
import requests
from collections import OrderedDict, namedtuple
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template

app = Flask(__name__)
EVENT_LINK_HREF_RE = re.compile(r'^/events/view/(?P<id>\d+)$')
APP_URL = 'https://calendar.dallasmakerspace.org'
EventInfo = namedtuple('EventInfo', 'id title start_time end_time where info_html')

def grab_event_info_from_link(link, time_re):
    href = link['href']

    res = requests.get(APP_URL + href)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser").find(True, 'events')
    time_match = time_re.match(soup.find('td', string=time_re).string)
    where = soup.find('td', string='Where').find_next_sibling('td')

    return EventInfo(id=EVENT_LINK_HREF_RE.match(href).group('id'),
                     title=soup.find(True, 'page-header').find('h1').string.strip(),
                     start_time=time_match.group('start_time'),
                     end_time=time_match.group('end_time'),
                     where=next(where.stripped_strings),
                     info_html=str(soup))

@app.route("/")
def todays_events_info():
    today = datetime.today()
    current_year = today.year
    current_date = today.date()

    time_re = re.compile(r'\s*%s\s+%d\s+(?P<start_time>[\w:]+)\s+—\s+(?P<end_time>[\w:]+)' % (current_date.strftime(r'%a\s+%b'), current_date.day), re.M)

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
    return render_template('index.html', date=current_date,
                                         events=[grab_event_info_from_link(l, time_re) for l in event_links])

if __name__ == '__main__':
    # app.run()
    pass
