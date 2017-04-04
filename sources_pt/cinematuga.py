# -*- coding: utf-8 -*-

"""
    Exodus Add-on
    Copyright (C) 2016 Exodus

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import urllib
import urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pt']
        self.domains = ['cinematuga.rocks']

        self.base_link = 'http://cinematuga.rocks'
        self.search_link = '/?s=%s&submit=Search'

    def movie(self, imdb, title, localtitle, year):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query(title)))
            query = urlparse.urljoin(self.base_link, query)

            result = client.request(query)
            result = dom_parser.parse_dom(result, 'div', attrs={'id': 'content'})
            result = dom_parser.parse_dom(result, 'div', attrs={'class': 'item'})
            result = [(dom_parser.parse_dom(i, 'div', attrs={'class': 'thumb'}), dom_parser.parse_dom(i, 'div', attrs={'class': 'imdb'})) for i in result]
            result = [(dom_parser.parse_dom(i[0], 'a', req='href'), dom_parser.parse_dom(i[1], 'a', attrs={'href': re.compile('.*/%s.*' % imdb)}, req='href')) for i in result if i[0] and i[1]]
            result = [i[0][0].attrs['href'] for i in result if i[0] and i[1]][0]

            return source_utils.strip_domain(result)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            url = urlparse.urljoin(self.base_link, url)

            result = client.request(url)
            result = dom_parser.parse_dom(result, 'div', attrs={'id': re.compile('player\d+')})
            result = dom_parser.parse_dom(result, 'iframe', req='src')
            result = [i.attrs['src'] for i in result if i]

            for host_url in result:
                valid, hoster = source_utils.is_host_valid(host_url, hostDict)
                if not valid: continue

                quality, info = source_utils.get_release_quality(host_url)

                info = ' | '.join(info)

                sources.append({'source': hoster, 'quality': quality, 'language': 'pt', 'url': host_url, 'info': info, 'direct': False, 'debridonly': False, 'checkquality': True})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url
