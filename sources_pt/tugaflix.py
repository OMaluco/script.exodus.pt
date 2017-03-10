# -*- coding: utf-8 -*-

'''
    Genesis Add-on
    Copyright (C) 2015 lambda

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


import os,re,urllib,urllib2,urlparse,xbmc

import urlresolver
from urlresolver.plugins.lib import recaptcha_v2

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import client_genesis
from resources.lib.modules import jsunpack

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pt']
        self.domains = ['tugaflix.com']
        
        self.base_link = 'http://tugaflix.com'
        self.search_link = '/Filmes?G=&O=1&T='
        self.searchSeries_link = '/Series?G=&O=1&T='


    def movie(self, imdb, title, localtitle, year):
        try:
            
            query = self.base_link+self.search_link+str(title.replace(' ','+'))

            result = client.request(query)
            
            result = client.parseDOM(result, 'div', attrs = {'class': 'browse-movie-bottom'})
            result = str(result)
            result = client.parseDOM(result, 'a', ret='href')
            #result = re.compile('<div class="browse-movie-wrap.+?"> <a href="(.+?)" class="browse-movie-link"> <figure>').findall(result)
            
            for result_url in result:
                try:result_imdb = re.compile('=(.*)').findall(result_url)[0]
                except:result_imdb='result_imdb'                
                if imdb == 'tt'+result_imdb:                                
                        url = self.base_link+'/Filme?F='+result_imdb
                        break
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, year):
        try:
            query = self.base_link+self.searchSeries_link+str(tvshowtitle.replace(' ','+'))

            result = client.request(query)
            result = client.parseDOM(result, 'div', attrs = {'class': 'browse-movie-bottom'})
            result = str(result)
            result = client.parseDOM(result, 'a', ret='href')
            #result = re.compile('<div class="browse-movie-wrap.+?"> <a href="(.+?)" class="browse-movie-link"> <figure>').findall(result)
            
            for result_url in result:
                try:result_imdb = re.compile('=(.*)').findall(result_url)[0]
                except:result_imdb='result_imdb'                
                if imdb == 'tt'+result_imdb:                                
                        url = self.base_link+'/Serie?S='+result_imdb
                        break
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            #url = '%s S%02dE%02d' % (url, int(season), int(episode))
            url = url + 'EPISODIO'+episode+'EPISODIOSEASON'+season+'SEASON'
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):

##        sources = []
##        sources.append({'source': 'TugaFlix', 'quality': 'HD', 'provider': 'TugaFlix'+url, 'url': url, 'direct': False, 'debridonly': False})

        try:
            sources = []
            
            if url == None: return sources

            referer_url = url

            procura = 'FILME'
            
            if 'EPISODIO' in url:
                procura = 'EPISODIO'
                url = re.compile('(.+?)EPISODIO(\d+)EPISODIOSEASON(\d+)SEASON').findall(url)
                episodio = str(url[0][1])
                season = str(url[0][2])
                if int(episodio) < 10: e = 'E0'+episodio
                else: e = 'E'+episodio
                if int(season) < 10: t = 'S0'+season
                else: t = 'S'+season
                S_E = t+e
                url = url[0][0]

            try: result = client.request(url)
            except: result = ''
            
            audio_filme = ''
            audio = 'en'
            try:
                titulo = client.parseDOM(result, 'h1', attrs = {'class': 'title'})[0]
                if 'PT-PT' in titulo or 'PORTUGU' in titulo:
                    audio_filme = ' | PT-PT'
                    audio = 'pt'
                else:
                    audio_filme = ''
                    audio = 'en'
            except: audio_filme = ''
            try:
                quality = url.strip().upper()
                if '1080P' in quality: quality = '1080p'
                elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or 'HDTV' in quality or '720P' in quality: quality = 'HD'
                elif 'SCREENER' in quality: quality = 'SCR'
                elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                else: quality = 'SD'
            except: quality = 'SD'

            if procura == 'EPISODIO':
                #result = client.parseDOM(result, 'a', attrs = {'class': 'browse-movie-link'})
                result = re.compile('<a class="browse-movie-link"(.+?)<h6 class="gridepisode2">').findall(result)
                for results in result:
                    if S_E in results.upper():
                        url = re.compile('href="(.+?)"><figure>').findall(results)[0]
                        url = self.base_link+url
                        sources.append({'source': 'TugaFlix', 'quality': 'HD', 'provider': 'TugaFlix', 'url': url, 'direct': False, 'debridonly': False})
            elif procura == 'FILME':
                sources.append({'source': 'TugaFlix', 'quality': 'HD', 'language': audio, 'provider': 'TugaFlix', 'url': url, 'direct': False, 'debridonly': False})
            
            return sources
        except:
            return sources
        

    def resolve(self, url):
        try:cookie = client.request(url+'&HD', output='cookie')
        except:cookie = client.request(url, output='cookie')
        xbmc.log('COOKIE -++++++++++++++++++++++ '+str(cookie))
        
        try: result = client.request(url)
        except: result = ''
        
        key=re.compile('data-sitekey="(.+?)" data-callback="onSubmit').findall(result)[0]
        xbmc.log('KEY -++++++++++++++++++++++ '+str(key))
        
        token=recaptcha_v2.UnCaptchaReCaptcha().processCaptcha(key, lang='en')
        xbmc.log('TOKEN +++++++++++++++++++++ '+str(token))
        
        post = urllib.urlencode({'g-recaptcha-response': token})
        try:result = client.request(url+'&HD', post=post, cookie=cookie)
        except:result = client.request(url, post=post, cookie=cookie)

        url = re.compile('<iframe src="(.+?)" scrolling="no"').findall(result)[0]
        xbmc.log('URL -++++++++++++++++++++++ '+str(url))

        return url

