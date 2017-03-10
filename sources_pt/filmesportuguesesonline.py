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


import re,urllib,urllib2,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import jsunpack

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pt']
        self.domains = ['www.filmesportuguesesonline.com']
        
        self.base_link = 'http://www.filmesportuguesesonline.com'
        self.search_link = '/search?q='


    def movie(self, imdb, title, localtitle, year):
        try:
            titulo = title
            genero = ''
            try: genero = self.get_genre(imdb)                
            except: pass
            if genero == 'Animation':
                try: titulo = self.get_portuguese_name(imdb)                
                except: titulo = title

            query = self.base_link+self.search_link+str(imdb)#+str(titulo.replace(' ','+'))

            result = client.request(query)

            result = str(result.replace('\n',''))
            result = client.parseDOM(result, 'div', attrs = {'class': 'post-body entry-content'})

            urls = ''
            for results in result:
                result_url = re.compile('y="(.+?)"').findall(results)[0]
                try: result_imdb = client.request(result_url)
                except: result_imdb = ''
                try: result_imdb = re.compile('http://www.imdb.com/title/(.+?)/').findall(results)[0]
                except: result_imdb = ''
                if imdb in result_imdb:                                
                    urls = urls+result_url+'|'
            if urls != '': url = urls

            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, year):
        try:

            query = self.base_link+self.search_link+str(tvshowtitle.replace(' ','+'))

            result = client.request(query)

            result = str(result.replace('\n',''))
            #result = client.parseDOM(result, 'div', attrs = {'class': 'image'})
            result = re.compile('<div class="image">(.+?)<div class="imdb_r').findall(result)
            
            urls = ''
            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                try:
                    result_title = re.compile('<span class="titulo_o">(.+?)</span>').findall(results)[0]
                except: result_title = 'result_title'
                if tvshowtitle.upper() in result_title.upper():                                
                    urls = urls+result_url+'|'
            if urls != '': url = urls

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
##        sources.append({'source': 'FilmesPortuguesesOnline', 'quality': 'HD', 'provider': 'FilmesPortuguesesOnline'+url, 'url': url, 'direct': False, 'debridonly': False})

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
                url = url[0][0].replace('tvshows','episode')+'=='
                url = url.replace('/|==','')+'-'+season+'x'+episodio
                try: result = client.request(url)
                except: result = ''
                
                hosts = client.parseDOM(result, 'div', attrs = {'class': 'streaming'})
                hosts = client.parseDOM(result, 'iframe', ret='src')
                
                for host_url in hosts:

                    audio_filme = ''
                    try:
                        titulo = re.compile("<h1 class='post-title entry-title'><a href='.+?'>(.+?)</a></h1>").findall(result.replace('\n',''))[0]
                        if 'PT-PT' in titulo.upper() or 'PORTUGU' in titulo.upper(): audio_filme = ' | PT-PT'
                        else: audio_filme = ''
                    except: audio_filme = ''
                    try:
                        quality = host_url.strip().upper()
                        if '1080P' in quality: quality = '1080p'
                        elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality: quality = 'HD'
                        elif 'SCREENER' in quality: quality = 'SCR'
                        elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                        else: quality = 'SD'
                    except: quality = 'SD'
                        
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'provider': 'FilmesPortuguesesOnline'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False})
   
                
            if procura == 'FILME':
                
                resultado = re.compile('(.+?)[|]').findall(url)

                for url in resultado:

                    try: result = client.request(url)
                    except: result = ''

##                    hosts = client.parseDOM(result, 'div', attrs = {'class': 'post bar hentry'})
##                    hosts = str(hosts)
                    hosts = re.compile("<div class='postmeta'>(.+?)<div style='clear: both;'></div>").findall(result.replace('\n',''))[0]
                    hosts = re.compile("Ver o Filme(.*)").findall(hosts)
                    print hosts
                    
                    for host_urls in hosts:
                        
                        host_url = re.compile('href="(.+?)"').findall(host_urls)[0]

                        audio_filme = ' | PT-PT'
##                        try:
##                            titulo = re.compile('<div class="icon"><img src=".+?" alt=""></div>(.+?)</div>').findall(result.replace('\n',''))[0]
##                            if 'PT-PT' in titulo.upper() or 'PORTUGU' in titulo.upper(): audio_filme = ' | PT-PT'
##                            else: audio_filme = ''
##                        except: audio_filme = ''
                        try:
                            quality = host_url.strip().upper()
                            if '1080P' in quality: quality = '1080p'
                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or 'HD' in quality: quality = 'HD'
                            elif 'SCREENER' in quality: quality = 'SCR'
                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                            else: quality = 'SD'
                        except: quality = 'SD'
                        
                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')

                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'provider': 'FilmesPortuguesesOnline'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False})
               
                        
            return sources
        except:
            return sources
        

    def get_portuguese_name(self, imdb):

        titulo = ''

        query = 'http://www.imdb.com/title/'+str(imdb)
       
        try:
            req = urllib2.Request(query)
            req.add_header('User-Agent','Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko')
            response = urllib2.urlopen(req)
            result=response.read()
            response.close()

            t = re.compile('<title>(.+?)</title>').findall(result.replace('\n',''))[0]
            t = str(re.compile('(.+?)[(]').findall(t)[0])
            t = t.replace('í','i')
            print t
            
            genre = re.compile('<span class="itemprop" itemprop="genre">(.+?)</span></a>').findall(result.replace('\n',''))
            for i in genre:
                print i
                if 'Animation' in i:
                    titulo = t
                    break
              
            return urllib.quote_plus(titulo)
        except:
            return

    def get_genre(self, imdb):

        genero = ''

        query = 'http://www.imdb.com/title/'+str(imdb)
       
        try:
            req = urllib2.Request(query)
            req.add_header('User-Agent','Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko')
            response = urllib2.urlopen(req)
            result=response.read()
            response.close()
            
            genre = re.compile('<span class="itemprop" itemprop="genre">(.+?)</span></a>').findall(result.replace('\n',''))
            for i in genre:
                if 'Animation' in i:
                    genero = 'Animation'
                    break
              
            return urllib.quote_plus(genero)
        except:
            return


    def resolve(self, url):
##        if 'openload' in url:
##            url = openload.OpenLoad(url).getMediaUrl()
        return url
        

    def abrir_url(self, url):            
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link


                

