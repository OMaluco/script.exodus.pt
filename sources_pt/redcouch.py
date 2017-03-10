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


import re,urllib,urllib2,urlparse,xbmc

from resources.lib.modules import cleantitle
from resources.lib.modules import client
#from resources.lib.modules import openload

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pt']
        self.domains = ['redcouch.xyz']
        
        self.base_link = 'http://www.redcouch.xyz'
        self.search_link = '/index.php?do=search&subaction=search&catlist[]=1&story='
        self.searchSeries_link = '/index.php?do=search&subaction=search&catlist[]=2&story='


    def movie(self, imdb, title, localtitle, year):
        try:
##            titulo = title
##            genero = ''
##            try: genero = self.get_genre(imdb)                
##            except: pass
##            if genero == 'Animation':
##                try: titulo = self.get_portuguese_name(imdb)                
##                except: titulo = title

            query = self.base_link+self.search_link+str(title.replace(' ','+'))

            try: result = client.request(query)
            except: result = ''

            result = client.parseDOM(result, 'div', attrs = {'class': 'short-film'})
            result = str(result)
            result = client.parseDOM(result, 'div', attrs = {'class': 'img-block border-2'})
            result = client.parseDOM(result, 'a', ret='href')
            
            urls = ''
            for result_url in result:
                xbmc.log(str(result_url))
                try: result_title = client.request(result_url)
                except: result_title = ''
                try: result_title = re.compile('tulooriginal.+?/span><pclass="text"><strong>(.+?)</strong></p>').findall(result_title.replace('\n','').replace(' ',''))[0]
                except: result_title = ''
                if result_title == title:                                
                    urls = urls+result_url+'|'
                    #break
            if urls != '': url = urls

            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, year):
        try:

            query = self.base_link+self.searchSeries_link+str(tvshowtitle.replace(' ','+'))

            try: result = client.request(query)
            except: result = ''
            result = result.replace('\n','')
            result = re.compile('<div class="short-film">(.+?)<img src').findall(result)
            
            for results in result:
                try: result_url = re.compile('href="(.+?)"').findall(results)[0]
                except: result_url = ''
                try: result_title = client.request(result_url)
                except: result_title = ''
                try: result_title = re.compile('tulooriginal.+?/span><pclass="text"><strong>(.+?)</strong></p>').findall(result_title.replace('\n','').replace(' ',''))[0]
                except: result_title = ''
                if cleantitle.movie(result_title) == cleantitle.movie(tvshowtitle):                                
                    url = result_url
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
##        sources.append({'source': 'Redcouch', 'quality': 'HD', 'provider': 'Redcouch'+url, 'url': url, 'direct': False, 'debridonly': False})

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
                try:
                    result = client.request(url)
                    ifr = re.compile('<iframe(.+?)</iframe').findall(result.replace('\n',''))[0]
                    ifr = re.compile('src="(.+?)"').findall(ifr)[0]
                    result = self.abrir_url(ifr)
                except: result = ''
                #print result

                ifr = re.compile('<div id="tabs'+season+'-'+episodio+'">(.+?)</div>').findall(result.replace('\n',''))[0]
                ifr = re.compile('<iframe(.+?)</iframe').findall(ifr.replace('\n',''))
                for hosts in ifr:
##                    if S_E in hosts.upper() and 'data-src' in hosts:
                    if hosts != '':
                        host_url = re.compile('data-src="(.+?)"').findall(hosts)[0]
                        audio_filme = ''
                        audio = 'en'
                        try:
                            if 'PT-PT' in host_url.upper() or 'PORTUGU' in host_url.upper():
                                audio_filme = ' | PT-PT'
                                audio = 'pt'
                            else:
                                audio_filme = ''
                                audio = 'en'
                        except: audio_filme = ''
                        try:
                            quality = host_url.strip().upper()
                            if '1080P' in quality: quality = '1080p'
                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or 'HDTV' in quality or '720P' in quality: quality = 'HD'
                            elif 'SCREENER' in quality: quality = 'SCR'
                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                            else: quality = 'SD'
                        except: quality = 'SD'

                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')

                        sources.append({'source': host, 'quality': quality, 'language': audio, 'provider': 'Redcouch'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False})
   
                
            if procura == 'FILME':
                
                result = re.compile('(.+?)[|]').findall(url)

                for url in result:

                    try: result = client.request(url)
                    except: result = ''
                    
                    audio_filme = ''
                    audio = 'en'
                    try:
                        titulo = re.compile('<h1 class="title">(.+?)</h1>').findall(result)[0]
                        if 'PT-PT' in titulo.upper() or 'PORTUGU' in titulo.upper():
                            audio_filme = ' | PT-PT'
                            audio = 'pt'
                        else:
                            audio_filme = ''
                            audio = 'en'
                    except: audio_filme = ''
                    try:
                        quality = url.strip().upper()
                        if '1080P' in quality: quality = '1080p'
                        elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality: quality = 'HD'
                        elif 'SCREENER' in quality: quality = 'SCR'
                        elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                        else: quality = 'SD'
                    except: quality = 'SD'

                    hosts = re.compile('<iframe(.+?)</iframe>').findall(result.replace('\n',''))
                    for host_urls in hosts:
                       # print '#################'+host_urls
                        host_url = re.compile('src="(.+?)"').findall(host_urls)[0]
                        
                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')

                        sources.append({'source': host, 'quality': quality, 'language': audio, 'provider': 'Redcouch'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False})
               
                        
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


                

