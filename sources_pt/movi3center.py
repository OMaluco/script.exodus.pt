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

from resources.lib.modules import cleantitle
from resources.lib.modules import client

import random
import urlresolver
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
from urlresolver.plugins.lib import helpers


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pt']
        self.domains = ['movi3center.net']
        
        self.base_link = 'http://movi3center.net'
        self.search_link = '/?s='


    def movie(self, imdb, title, localtitle, year):
        try:

            query = self.base_link+self.search_link+str(title.replace(' ','+'))

            try: result = client.request(query)
            except: result = ''

            result = client.parseDOM(result, 'div', attrs = {'class': 'boxinfo'})#'movie'})

            urls = ''
            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                try: resultado = client.request(result_url)
                except: resultado = ''
                try:result_imdb = re.compile('imdb.com/title/(.+?)/" target="_blank">').findall(resultado)[0]
                except:result_imdb=''                
                if imdb == result_imdb:                                
                        urls = urls+result_url+'|'
            if urls != '': url = urls+'IMDB'+imdb+'IMDB'
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, year):
        try:

            query = self.base_link+self.search_link+str(tvshowtitle.replace(' ','+'))

            try: result = self.abrir_url(query)
            except: result = ''
            result = re.compile('<h2 class="title post-title">(.+?)</h2>').findall(result)
            
            a = str(len(result))
            
            for results in result:
                result_url = re.compile('href="(.+?)"').findall(results)[0]
                try: result = self.abrir_url(result_url)
                except: result = ''
                try:result_imdb = re.compile('imdb.com/title/(.+?)/').findall(result)[0]
                except:result_imdb='result_imdb'                
                if imdb == result_imdb:                                
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
        try:
            sources = []
            
            leg = []
            
            if url == None: return sources

            idb = re.compile('IMDB(.+?)IMDB').findall(url)[0]
            url = re.compile('(.+?)IMDB.+?IMDB').findall(url)[0]
            
            result = re.compile('(.+?)[|]').findall(url)
            for url in result:
                legendas = ''
                lele = ''
                try:
                    try: result = client.request(url)
                    except: result = ''

                    result = client.parseDOM(result, 'div', attrs = {'class': 'movieplay'})#'player-content'})
                    result = str(result)
                    result = client.parseDOM(result, 'iframe', ret='src')

                    for host_url in result:

                        try:
                            quality = url.strip().upper()
                            if '1080P' in quality: quality = '1080p'
                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality: quality = 'HD'
                            elif 'SCREENER' in quality: quality = 'SCR'
                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                            else: quality = 'SD'
                        except: quality = 'HD'

                        audio_filme = ''
                        try:
                            audio = url.upper()
                            if 'PT-PT' in audio or 'PORTUGU' in audio or '-PT' in audio:
                                audio_filme = ' | PT-PT'
                                legendas = 'AUDIO PT'
                            else:
                                audio_filme = ''
                                legendas = lele
                        except:
                            audio_filme = ''
                            legendas = lele
            
                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')

                        if 'rapidvideo' in host:
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
                                    if l[i]:legendas = l[i]
                                    else:legendas = lele
                                    try:
                                        quality = quality.upper()
                                        if '1080P' in quality: quality = '1080p'
                                        elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                                        elif 'SCREENER' in quality: quality = 'SCR'
                                        elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                                        else: quality = 'SD'
                                    except: quality = 'SD'
                                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'provider': 'Movi3center'+audio_filme, 'url': ru, 'direct': True, 'debridonly': False, 'legendas': legendas})
                                    if len(leg) == 1: i = 0
                                    else: i = i + 1
                                    lele = legendas
                            except: pass

                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'provider': 'Movi3center'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False})
                    
                except: pass

            
            return sources
        except:
            return sources
        


    def resolve(self, url):
        return url
        

    def abrir_url(self, url):            
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link





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


                

