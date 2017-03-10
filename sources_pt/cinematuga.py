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


import re,urllib,urllib2,urlparse,xbmc

from resources.lib.modules import cleantitle
from resources.lib.modules import client

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pt']
        self.domains = ['cinematuga.rocks']
        
        self.base_link = 'http://cinematuga.rocks'
        self.search_link = '/?s='

    def movie(self, imdb, title, localtitle, year):
        try:
            query = self.base_link+self.search_link+str(title.replace(' ','+'))+'&submit=Search'

            result = client.request(query)
            result = client.parseDOM(result, 'div', attrs = {'class': 'item'})

            for results in result:
                try:result_imdb = re.compile('imdb.com/title/(.+?)/"').findall(results)[0]
                except:result_imdb = 'result_imdb'
                try:result_url = client.parseDOM(results, 'a', ret='href')[0]
                except:result_url = 'result_url'
                if imdb == result_imdb:                                
                        url = result_url
                        break
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            
            if url == None: return sources

            result = client.request(url)
            result = client.parseDOM(result, 'div', attrs = {'class': 'movieplay'})
            
            for results in result:
                
                host_url = client.parseDOM(results, 'iframe', ret='src')[0]
                
                try:
                    quality = host_url.strip().upper()
                    if '1080P' in quality: quality = '1080p'
                    elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality: quality = 'HD'
                    elif 'SCREENER' in quality: quality = 'SCR'
                    elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                    else: quality = 'SD'
                except: quality = 'HD'
                
                audio_filme = ''
                audio = 'en'
                try:
                    if 'PT-PT' in host_url.upper() or 'PORTUGU' in host_url.upper():
                        audio_filme = ' | PT-PT'
                        audio = 'pt'
                    else:
                        audio_filme = ''
                        audio = 'en'
                except:
                    audio_filme = ''
                    audio = 'en'
                
                if 'http' not in host_url: host_url = 'http:'+host_url
                
                host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                if not host in hostDict: raise Exception()
                host = client.replaceHTMLCodes(host)
                host = host.encode('utf-8')

                sources.append({'source': host+audio_filme, 'quality': quality, 'language': audio, 'provider': 'Cinematuga', 'url': host_url, 'direct': False, 'debridonly': False})                
                
            return sources
        except:
            return sources


    def resolve(self, url):
        return url
                

