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


import os,sys,re,json,urllib,urllib2,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import jsunpack

import random
import urlresolver
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
from urlresolver.plugins.lib import helpers


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pt']
        self.domains = ['toppt.net']
        
        self.base_link = 'http://toppt.net'
        self.search_movie_link = '/?s=%s'#'/category/filmes/?s=%s'
        self.search_serie_link = '/?s=%s'#'/category/series/?s=%s'
        

    def movie(self, imdb, title, localtitle, year):
        try:

            titulo = title
            genero = ''
            try: genero = self.get_genre(imdb)                
            except: pass
            if genero == 'Animation':
                try: titulo = self.get_portuguese_name(imdb)                
                except: titulo = title
            
            query = self.search_movie_link % (urllib.quote_plus(titulo))
            query = urlparse.urljoin(self.base_link, query)

            result = client.request(query)
            result = client.parseDOM(result, 'div', attrs = {'id': 'main.+?'})[0]            
            result = client.parseDOM(result, 'div', attrs = {'class': 'post clearfix.+?'})

            urls = ''
            for results in result:
                result_url = re.compile('<h2 class="title"><a href="(.+?)" title').findall(results.replace('\n',''))[0]
                try:
                    result_imdb = re.compile('imdb.com/title/(.+?)/"').findall(results.replace('\n',''))[0]
                except:
                    result_imdb='result_imdb'
                if imdb == result_imdb:                                
                        urls = urls+result_url+'|'
            if urls != '': url = urls+'IMDB'+imdb+'IMDB'
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, year):
        try:
            query = self.search_serie_link % (urllib.quote_plus(tvshowtitle))
            query = urlparse.urljoin(self.base_link, query)

            result = client.request(query)
            result = client.parseDOM(result, 'div', attrs = {'id': 'main.+?'})[0]            
            result = client.parseDOM(result, 'div', attrs = {'class': 'post clearfix.+?'})

            urls = ''
            for results in result:
                result_url = re.compile('<h2 class="title"><a href="(.+?)" title').findall(results.replace('\n',''))[0]
                try:
                    result_imdb = re.compile('imdb.com/title/(.+?)/"').findall(results.replace('\n',''))[0]
                except:
                    result_imdb='result_imdb'
                if imdb == result_imdb:                                
                        urls = urls+result_url+'|'
            if urls != '': url = urls+'IMDB'+imdb+'IMDB'
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            #url = '%s S%02dE%02d' % (url, int(season), int(episode))
            url = url + 'EPISODIO'+episode+'EPISODIOIMDB'+imdb+'IMDB'
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
##        sources = []
##        sources.append({'source': 'TopPt', 'quality': 'HD', 'provider': 'TopPt'+url, 'url': url, 'direct': True, 'debridonly': False})

        try:
            sources = []

            leg = []

            legendas = ''
            
            if url == None: return sources

            idb = re.compile('IMDB(.+?)IMDB').findall(url)[0]
            url = re.compile('(.+?)IMDB.+?IMDB').findall(url)[0]

            procura = 'FILME'
            
            if 'EPISODIO' in url:
                procura = 'EPISODIO'
                url = re.compile('(.+?)EPISODIO(\d+)EPISODIO').findall(url)
                episodio = str(url[0][1])
                url = url[0][0]+'|'

            result = re.compile('(.+?)[|]').findall(url)

            for url in result:
                result = client.request(url)
                
                try:audiopt = re.compile('<b>AUDIO:</b>(.+?)<br/>').findall(result.replace(" ",''))[0]
                except:audiopt = 'audio'
                if 'PT' in audiopt.upper():
                    audio_filme = ' | PT-PT'
                    legendas = 'AUDIO PT'
                    audio = 'pt'
                else:
                    audio_filme = ''
                    legendas = ''
                    audio = 'en'

                try:
                    try:quality = re.compile('<b>VERS.+?:</b>(.+?)<br/>').findall(result.replace(' ',''))[0]
                    except:quality = re.compile('<b>RELEASE:</b>(.+?)<br/>').findall(result.replace(' ',''))[0]
                    quality = quality.strip().upper()
                    if 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                    elif 'SCREENER' in quality: quality = 'SCR'
                    elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or 'HDTV' in quality or '720P' in quality: quality = 'HD'
                    elif '1080P' in quality: quality = '1080p'
                    else: quality = 'SD'
                except: quality = 'SD'

                if procura == 'EPISODIO':
                    result = re.compile('</span>'+str(episodio)+'º EPISODIO(.+?)DOWNLOAD').findall(result.replace('\n',''))[0]
                    
                result = result.replace('\n','')
                
                try:
                    resultado = re.compile('<spanclass="su-lightbox"data-mfp-src="(.+?)".+?;-webkit-text-shadow:none">.+?</span></a></span>').findall(result.replace(' ',''))
                except: pass
                if len(resultado) == 1 and 'youtube' in resultado[0]:
                    try:
                        resultado = re.compile('<iframesrc="(.+?)"scrolling').findall(result.replace(' ',''))
                        outras = re.compile('<strong>VERONLINE[(]outras(.+?)<strong>LINKSPARADOWNLOAD').findall(result.replace(' ',''))[0]
                        resultado += re.compile('href="(.+?)"target=').findall(outras.replace(' ',''))
                    except: pass
                
                for host_url in resultado:
                                        
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    if 'rapidvideo' in host.lower():
                        try:
                            padrao = re.compile('(?://|\.)(rapidvideo\.com)/(?:embed/|\?v=)?([0-9A-Za-z]+)').findall(host_url)
                            rapidurl = []
                            l = []
                            rapidurl,l = RapidVideoResolver().get_media_url(padrao[0][0],padrao[0][1])
                            if l != []:
                                for ll in l:
                                    leg.append(str(ll))
                            i = 0
                            for rl in rapidurl:
                                quality = rl[0]
                                ru = rl[1]
                                if l[i]: legendas = l[i]
                                else:legendas = legendas
                                try:
                                    quality = quality.upper()
                                    if '1080P' in quality: quality = '1080p'
                                    elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                                    elif 'SCREENER' in quality: quality = 'SCR'
                                    elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                                    else: quality = 'SD'
                                except: quality = 'SD'
                                sources.append({'source': host, 'quality': quality, 'language': audio, 'provider': 'TopPt'+audio_filme, 'url': ru, 'direct': True, 'debridonly': False, 'legendas': legendas})
                                if len(leg) == 1: i = 0
                                else: i = i + 1
                        except: pass
                        
                    elif 'vidzi' in host:
                        try:
                            vidzi = Vidzi(host_url)
                            urli = vidzi.getMediaUrl()
                            lege = vidzi.getSubtitle()
                            if lege: legendas = lege.replace('\/','/')
                            else: legendas = legendas
                            leg.append(str(legendas))
                        except: pass

                    if 'youtube' not in host_url and 'rapidvideo' not in host_url:
                        sources.append({'source': host, 'quality': quality, 'language': audio, 'provider': 'TopPt'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False, 'legendas': legendas})
            
            return sources
        except:
            return sources


    def resolve(self, url):
##        if 'openload' in url:
##            url = openload.OpenLoad(url).getMediaUrl()
        #if 'videowood' in url: url = resolversSdP.videowood(url)
        return url


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
            #print t
            
            genre = re.compile('<span class="itemprop" itemprop="genre">(.+?)</span></a>').findall(result.replace('\n',''))
            for i in genre:
                #print i
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

class RapidVideoResolver(UrlResolver):
    name = "rapidvideo.com"
    domains = ["rapidvideo.com"]
    pattern = '(?://|\.)(rapidvideo\.com)/(?:embed/|\?v=)?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        #print web_url
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        data = helpers.get_hidden(html)
        data['confirm.y'] = random.randint(0, 120)
        data['confirm.x'] = random.randint(0, 120)
        headers['Referer'] = web_url
        post_url = web_url + '#'
        html = self.net.http_POST(post_url, form_data=data, headers=headers).content.encode('utf-8')
##        sources = helpers.parse_sources_list(html)
##        try: sources.sort(key=lambda x: x[0], reverse=True)
##        except: pass
##        return helpers.pick_source(sources)

        sourc = []
        legenda = []
        try:
            le = re.compile('"file":"([^"]+)","label":".+?","kind":"captions"').findall(html)
            for l in le:
                legenda.append(l.replace('\/', '/'))
        except: pass
        match = re.search('''['"]?sources['"]?\s*:\s*\[(.*?)\]''', html, re.DOTALL)
        if match:
            sourc = [(match[1], match[0].replace('\/', '/')) for match in re.findall('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([^'"]*)''', match.group(1), re.DOTALL)]        
        return sourc,legenda

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://www.rapidvideo.com/embed/{media_id}')

class Vidzi():
	def __init__(self, url):
		self.url = url
		#self.net = Net()
		self.id = str(self.getId())
		#self.messageOk = xbmcgui.Dialog().ok
		self.site = 'http://vidzi.tv'
		self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}
		self.subtitle = ''

	def getId(self):
		return re.compile('http\:\/\/vidzi.tv\/embed-(.+?)-').findall(self.url)[0]

	def getNewHost(self):
		return 'http://vidzi.tv/embed-%s.html' % (self.id)

	def getMediaUrl(self):
		sourceCode = client.request(self.getNewHost(), headers=self.headers)#.content

		match = re.search('file\s*:\s*"([^"]+)', sourceCode)
		if match:
			return match.group(1) + '|Referer=http://vidzi.tv/nplayer/jwpayer.flash.swf'
		else:
			for pack in re.finditer('(eval\(function.*?)</script>', sourceCode, re.DOTALL):
				dataJs = jsunpack.unpack(pack.group(1)) # Unpacker for Dean Edward's p.a.c.k.e.r | THKS

				##print dataJs
				#pprint.pprint(dataJs)

				stream = re.search('file\s*:\s*"([^"]+)', dataJs)
				try:
					subtitle = re.compile('tracks:\[\{file:"(.+?)\.srt"').findall(dataJs)[0]
					subtitle += ".srt"
				except:
					try:
						subtitle = re.compile('tracks:\[\{file:"(.+?)\.vtt"').findall(dataJs)[0]
						subtitle += ".vtt"
					except:
						subtitle = ''
				self.subtitle = subtitle

				if stream:
					return stream.group(1)


	def getSubtitle(self):
		return self.subtitle


