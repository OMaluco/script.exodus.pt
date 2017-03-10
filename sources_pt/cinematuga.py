# -*- coding: utf-8 -*-

'''
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
'''


import re, urllib, urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client

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
            result = client.parseDOM(result, 'div', attrs={'id': 'content'})
            result = client.parseDOM(result, 'div', attrs={'class': 'item'})
            result = [(client.parseDOM(i, 'div', attrs={'class': 'thumb'}), client.parseDOM(i, 'div', attrs={'class': 'imdb'})) for i in result]
            result = [(client.parseDOM(i[0], 'a', ret='href'), client.parseDOM(i[1], 'a', attrs={'href': '[^\'"]+/%s[^\'"]+' % imdb}, ret='href')) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [i[0][0] for i in result if len(i[0]) > 0 and len(i[1]) > 0][0]

            url = re.findall('(?://.+?|)(/.+)', result)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if url is None:
                return sources

            url = urlparse.urljoin(self.base_link, url)

            result = client.request(url)
            result = client.parseDOM(result, 'div', attrs={'id': 'player\d+'})
            result = [client.parseDOM(i, 'iframe', ret='src') for i in result]
            result = [i[0] for i in result if i]

            for host_url in result:
                host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                if not host in hostDict: continue

                fmt = re.sub('(.+)(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*)(\.|\)|\]|\s)', '', host_url.upper())
                fmt = re.split('\.|\(|\)|\[|\]|\s|\-', fmt)
                fmt = [i.lower() for i in fmt]

                if '1080p' in fmt: quality = '1080p'
                elif '720p' in fmt: quality = 'HD'
                else: quality = 'SD'
                if any(i in ['dvdscr', 'r5', 'r6'] for i in fmt): quality = 'SCR'
                elif any(i in ['camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'telesync', 'ts'] for i in fmt): quality = 'CAM'

                info = []
                if '3d' in fmt or any(i.endswith('3d') for i in fmt): info.append('3D')
                if any(i in ['hevc', 'h265', 'x265'] for i in fmt): info.append('HEVC')
                if not any(i in ['pt-pt', 'portugu'] for i in fmt): info.append('subbed')

                info = ' | '.join(info)

                sources.append({'source': host, 'quality': quality, 'language': 'pt', 'url': host_url, 'info': info, 'direct': False, 'debridonly': False, 'checkquality': True})

            return sources
        except:
            return sources


    def resolve(self, url):
        return url
                

