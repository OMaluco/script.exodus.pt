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


import re,urllib,urllib2,urlparse,xbmcaddon,xbmc,xbmcplugin,xbmcgui,xbmcvfs

import os, json
import traceback

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import jsunpack
from resources.lib.modules import resolversSdP
from resources.lib.modules import control

addon_id = 'plugin.video.exodus'
selfAddon = xbmcaddon.Addon(id=addon_id)

import random
import urlresolver
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
from urlresolver.plugins.lib import helpers

import base64
import binascii
import cookielib
import string
from StringIO import StringIO



class source:
    def __init__(self):        
        self.tralhas = "http://tralhas.xyz/geturl/url.txt"
        self.base_link = self.rato_base_url()
        self.search_link = '?do=search&subaction=search&search_start=1&story='
        self.user = selfAddon.getSetting('ratotv_user')
        self.password = selfAddon.getSetting('ratotv_password')

        self.priority = 1
        self.language = ['pt']
        self.domains = [self.base_link]

    def rato_base_url(self):
        request = urllib2.Request(self.tralhas)
        request.add_header("User-Agent", "Wget/1.15 (linux-gnu)")
        try:
            response =  urllib2.urlopen(request)
            base_url = response.read()
            response.close()
        except:
            traceback.print_exc()
            return
        return base_url


    def movie(self, imdb, title, localtitle, year):
        try:
            
            if (self.user == '' or self.password == ''): raise Exception()

            query = self.base_link
            post = urllib.urlencode({'login': 'submit', 'login_name': self.user, 'login_password': self.password})
            cookie = client.request(query, post=post, output='cookie')

            query = self.base_link+self.search_link+str(title.replace(' ','+'))
            result = client.request(query, post=post, cookie=cookie, referer=self.base_link)
            
            result = client.parseDOM(result, 'div', attrs = {'class': 'shortpost'})
            urls = ''
            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                try:
                    result_imdb = re.compile('imdb.com/title/(.+?)/"').findall(results.replace(' ',''))[0]
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
            if (self.user == '' or self.password == ''): raise Exception()

            query = self.base_link
            post = urllib.urlencode({'login': 'submit', 'login_name': self.user, 'login_password': self.password})
            cookie = client.request(query, post=post, output='cookie')
            
            query = self.base_link+self.search_link+str(tvshowtitle.replace(' ','+'))
            result = client.request(query, post=post, cookie=cookie, referer=self.base_link)

            if cookie: a = cookie
            else: a = 'nao'
            
            result = client.parseDOM(result, 'div', attrs = {'class': 'shortpost'})
            
            urls = ''
            for results in result:                
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                try:
                    result_imdb = re.compile('imdb.com/title/(.+?)/"').findall(results.replace(' ',''))[0]
                except:
                    result_imdb='result_imdb'
                if imdb == result_imdb:                                
                        urls = urls+result_url+'|'
            if urls != '': url = urls
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = url.replace('|','')
            #url = '%s S%02dE%02d' % (url, int(season), int(episode))
            url = url + 'EPISODIO'+episode+'EPISODIOSEASON'+season+'SEASONIMDB'+imdb+'IMDB'
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
##        sources = []
##        sources.append({'source': 'gdrive', 'quality': 'HD', 'provider': 'RatoTV', 'url': 'https://drive.google.com/file/d/0B8kCEtrnzKhDUzJrckloQURXVDA/edit', 'direct': False, 'debridonly': False})
        try:
            sources = []

            if url == None: return sources

            options = []
            leg = []
            legendas = ''

            idb = re.compile('IMDB(.+?)IMDB').findall(url)[0]
            url = re.compile('(.+?)IMDB.+?IMDB').findall(url)[0]

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

                options = series_seasons(url,season,episodio,self.user,self.password)
                for i in options:
                    nome_source = str(i['source'])
                    try:leg.append(str(i['subs']))
                    except: pass
                    try:legendas = str(i['subs'])
                    except:legendas = ''
                    if nome_source == 'NONE':
                        host_url = i['url']
                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')

                        sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'provider': 'RatoTV', 'url': host_url, 'direct': False, 'debridonly': False, 'legendas': legendas})
                    else:
                        quality = str(i['quality'])
                        try:
                            quality = quality.strip().upper()
                            if '1080P' in quality: quality = '1080p'
                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                            elif 'SCREENER' in quality: quality = 'SCR'
                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                            else: quality = 'SD'
                        except: quality = 'SD'
                        sources.append({'source': str(i['source']), 'quality': quality, 'language': 'en', 'provider': 'RatoTV', 'url': str(i['url']), 'direct': True, 'debridonly': False, 'legendas': legendas})
            else:
                result = re.compile('(.+?)[|]').findall(url)
                for url in result:
                    options = self.get_host_options(url)
                    #if options == '': break
                    
                    for i in options:
                        print 'legendas------------------'+str(i['subs'])
                        if i['subs']:
                            leg.append(str(i['subs']))
                            legendas = str(i['subs'])
                        else: legendas = legendas
                        nome_source = str(i['source'])
                        if nome_source == 'NONE':
                            host_url = i['url']
                            host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                            host = client.replaceHTMLCodes(host)
                            host = host.encode('utf-8')
                            
                            sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'provider': 'RatoTV', 'url': host_url, 'direct': False, 'debridonly': False, 'legendas': legendas})
                        else:
                            quality = str(i['quality'])
                            try:
                                quality = quality.upper()
                                if '1080P' in quality: quality = '1080p'
                                elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                                elif 'SCREENER' in quality: quality = 'SCR'
                                elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                                else: quality = 'SD'
                            except: quality = 'SD'
                            sources.append({'source': str(i['source']), 'quality': quality, 'language': 'en', 'provider': 'RatoTV', 'url': str(i['url']), 'direct': True, 'debridonly': False, 'legendas': legendas})
            
            return sources
        except:
            return sources
        

    def get_host_options(self, url):#, sourc=None):
        opcoes = []
        try:
            opcoes = get_options(url, self.user, self.password)#, sourc)
        except: pass
        return opcoes
    

    def resolve(self, url):
##        u = url
##        if 'openload' in url:
##            try:
##                url = openload.OpenLoad(url).getMediaUrl()
##            except: url = u
        return url



########################################## RESOLVER RATOTV #####################################################
#base_url = rato_base_url()"http://ratotv.win"#"http://ratotv.xyz"

def rato_base_url():
    tralhas = "http://tralhas.xyz/geturl/url.txt"
    request = urllib2.Request(tralhas)
    request.add_header("User-Agent", "Wget/1.15 (linux-gnu)")
    try:
        response =  urllib2.urlopen(request)
        base_url = response.read()
        response.close()
    except:
        traceback.print_exc()
        return
    return base_url

class LoginError(Exception):
    pass


def json_get(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    data = json.load(urllib2.urlopen(req))
    return data


def post_page(url, user, password):
    mydata = [('login_name', user), ('login_password', password), ('login', 'submit')]
    mydata = urllib.urlencode(mydata)
    req = urllib2.Request(url, mydata)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    page = urllib2.urlopen(req).read()
    return page


def post_page_free(url, mydata, headers=None):
    mydata = urllib.urlencode(mydata)
    req = urllib2.Request(url, mydata)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    if headers:
        for header in headers:
            req.add_header(header[0],header[1])
    page = urllib2.urlopen(req).read()
    return page


def abrir_url(url, encoding='utf-8'):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    if encoding != 'utf-8': link = link.decode(encoding).encode('utf-8')
    return link


def xmlhttp_request(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header('Accept', 'text/html, */*')
    req.add_header('X-Requested-With', '    XMLHttpRequest')
    response = urllib2.urlopen(req)
    data = response.read()
    response.close()
    return data


def resolve_vmail(url):
    base_url = rato_base_url()
    # http://my.mail.ru/mail/rishuam/video/_myvideo/5404.html
    base_profile_url = url.split("/video/")[0]
    video_id = url.split("/")[-1][:-5]
    ajax_url = base_profile_url + "/ajax?ajax_call=1&func_name=video.get_item&mna=&mnb=&arg_id=" + video_id
    #print "[vmail] ajax_url:", ajax_url
    ajax_resp = urllib2.urlopen(ajax_url)
    api_url = re.compile(r'\\"signVideoUrl\\"\:\ \\"(.+?)\\"', re.DOTALL).findall(ajax_resp.read())[0]
    #print "[vmail] api_url:", api_url
    api_resp = urllib2.urlopen(api_url)
    video_key = re.compile('(video_key=[^\;]+)').findall(api_resp.headers.get('Set-Cookie', ''))[0]
    #print "[vmail] Cookie:", video_key
    video_json = json.load(api_resp)
    result = []
    for v in video_json["videos"]:
        headers = {"Cookie":video_key}
        result.append({"provider":"videomail.ru", "quality":v['key'], "url": v['url'], "headers":headers})
    return result


def resolve_vkcom(url):
    base_url = rato_base_url()
    rato_vk_url = base_url + "zencrypt/pluginsw/plugins_vk.php"
    user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3"
    post_data1 = [
        ("iagent", user_agent),
        ("url", url),
        ("ihttpheader", "true"),
        ("icookie", ""),
        ("iheader", "true")
    ]
    #print "[vk.com] post_data:", post_data1
    data1 = post_page_free(rato_vk_url, post_data1)
    #print "[vk.com] data1 line1:", data1.split("\n")[0]
    data2 = post_page_free(rato_vk_url, [("checkcookie", "true")])
    # #print "[vk] data2:", data2
    cookie = data2.replace("&cookie=", "")
    #print "[vk,com] cookie:", cookie
    oid_part, vid = url.split("/")[-1].split("_")
    oid = oid_part.replace("video", "")
    #print "[vk.com] oid:", oid
    #print "[vk.com] vid:", vid
    post_data3 = [
        ("iheader", "true"),
        ("url", "https://vk.com/al_video.php"),
        ("ipost", "true"),
        ("iagent", user_agent),
        ("ipostfield", "oid=" + oid + "&act=video_embed_box&al=1&vid=" + vid),
        ("ihttpheader", "true"),
        ("icookie", "remixlang=3; remixsid=" + cookie),
        ("isslverify", "true")
    ]
    data3 = post_page_free(rato_vk_url, post_data3)
    #print "[vk.com] data3 line1", data3.split("\n")[0]
    # #print "[vk] data3", data3
    embed_hash = re.search(r"vk\.com/video_ext\.php\?oid=%s\&id=%s\&hash=([^\"\']+)" % (oid, vid), data3, re.DOTALL).group(1)
    # #print "[vk] embed_hash:", embed_hash
    api_url = "http://api.vk.com/method/video.getEmbed?oid=%s&video_id=%s&embed_hash=%s" % (oid, vid, embed_hash)
    #print "[vk.com] api_url:", api_url
    video_json = json_get(api_url)["response"]
    result = []
    url240 = video_json.get("url240")
    url360 = video_json.get("url360")
    url480 = video_json.get("url480")
    url720 = video_json.get("url720")
    url1080 = video_json.get("url1080")
    if url240:
        result.append({"provider":"vk.com", "quality":"240p", "url":url240})
    if url360:
        result.append({"provider":"vk.com", "quality":"360p", "url":url360})
    if url480:
        result.append({"provider":"vk.com", "quality":"480p", "url":url480})
    if url720:
        result.append({"provider":"vk.com", "quality":"720p", "url":url720})
    if url1080:
        result.append({"provider":"vk.com", "quality":"1080p", "url":url1080})
    return result


def resolve_ok(url):
    base_url = rato_base_url()
    accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3"
    vid = url
    vid = url.split("/")[-1]
    #print "[ok.ru] vid:", vid
    api_url = 'http://ok.ru/dk?cmd=videoPlayerMetadata&mid=' + vid
    api_req = urllib2.Request(api_url)
    api_req.add_header('User-Agent', user_agent)
    api_req.add_header('Accept', accept)
    api_req.add_header('Cache-Control', 'no-transform')
    video_json = json.load(urllib2.urlopen(api_req))
    result = []
    for v in video_json["videos"]:
        if v['name'] == "lowest":
            quality = "240p"
        elif v['name'] == "low":
            quality = "360p"
        elif v['name'] == "sd":
            quality = "480p"
        elif v['name'] == "hd":
            quality = "720p"
        elif v['name'] == "full":
            quality = "1080p"
        else:
            continue
        vurl = v['url'].decode("unicode-escape")
        headers = {
            "User-Agent":user_agent,
            "Accept":accept,
            "Referer":base_url
        }
        result.append({"provider":"ok.ru", "quality":quality, "url":vurl, "headers":headers})
    return result


def resolve_upstream(url):
    base_url = rato_base_url()
    video_req = urllib2.Request(url)
    video_req.add_header("User-Agent", "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3")
    video_page = urllib2.urlopen(video_req).read()
    ##print "[upstream] html = ", video_page
    video_data = re.search(r"(<video).+?(</video>)", video_page, re.DOTALL).group()
    result = []
    for source in re.finditer("<source src=\'(.+?)\'.+?data-res=\'(.+?)\'", video_data, re.DOTALL):
        url = source.group(1)
        if url.startswith("//"):
            url = "http:" + url
        result.append({"provider":"upstream.com", "url":url, "quality":source.group(2)})
    return result


def resolve_gdrive(url):
##    vid = urlparse.urlparse(url).path.split("/")[-2]
##    host = urlparse.urlparse(url).path.split("/")[-3]
##    #print "[gdrive] vid = %s" % vid
##    #print "[gdrive] host = %s" % host
    links = []
    result = []
    resposta, links = GoogleResolver()._parse_google(url)
##    #print 'links------------------'
##    #print links
    for i in links:
        try:result.append({"provider":"gdrive", "url":i[1], "quality": i[0]+"p"})
        except:pass
    return result

                    
def resolve_gdrive_original(url):    
    base_url = rato_base_url()
    # https://drive.google.com/file/d/0B8kCEtrnzKhDLTNmYzZBSnpPeEE/edit?pli=1
    vid = urlparse.urlparse(url).path.split("/")[-2]
    #print "[gdrive] vid = %s" % vid
    # direct link for uploaded video, non-seekable..
    # return [{"provider":"gdrive", "url":"https://googledrive.com/host/%s"% vid, "quality":"???"}]

    # ydl gdrive, seekable urls..
    video_req = urllib2.Request(url)
    video_req.add_header("User-Agent", "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3")
    video_data = urllib2.urlopen(video_req).read().decode('unicode_escape')
    # #print "[gdrive]", video_data
    formats = {
        '5': {'ext': 'flv'},
        '6': {'ext': 'flv'},
        '13': {'ext': '3gp'},
        '17': {'ext': '3gp'},
        '18': {'ext': 'mp4'},
        '22': {'ext': 'mp4'},
        '34': {'ext': 'flv'},
        '35': {'ext': 'flv'},
        '36': {'ext': '3gp'},
        '37': {'ext': 'mp4'},
        '38': {'ext': 'mp4'},
        '43': {'ext': 'webm'},
        '44': {'ext': 'webm'},
        '45': {'ext': 'webm'},
        '46': {'ext': 'webm'},
        '59': {'ext': 'mp4'}
    }
    fmt_list = re.search(r'"fmt_list"\s*,\s*"([^"]+)', video_data).group(1)
    fmt_list = fmt_list.split(',')
    #print "[gdrive] fmt_list = %r" % fmt_list
    fmt_stream_map = re.search(r'"fmt_stream_map"\s*,\s*"([^"]+)', video_data).group(1)
    fmt_stream_map = fmt_stream_map.split(',')
    ##print "[gdrive] fmt_stream_map = %r, len=%d" % (fmt_stream_map, len(fmt_stream_map))
    result = []
    for i in range(len(fmt_stream_map)):
        fmt_id, fmt_url = fmt_stream_map[i].split('|')
        fmt = formats.get(fmt_id)
        extension = fmt and fmt['ext']
        resolution = fmt_list[i].split('/')[1]
        width, height = resolution.split('x')
        result.append({"provider":"gdrive", "url":fmt_url, "quality": height+"p", "ext":extension})
    return result

def resolver_externos(link_data):
    base_url = rato_base_url()
    videos = []
    decoded_url = link_data['link']
    ##print link_data
    try:
        request = link_data['request']
        if request['method'] == 'POST':
            headers = []
            if 'referer' in request:
                headers.append(('Referer', request['referer']))
            if 'cookie' in request:
                headers.append(('Cookie', request['cookie']))
            data = json.loads(post_page_free(link_data['request']['url'], request['data'], headers))
            ##print '[resolve_externos] data = ', data
            request_data = {}
            request_data['link'] = link_data['link']
            request_data['poscom'] = link_data['poscom']
            request_data['response'] = data
            post_data = [('data', base64.encodestring(json.dumps(request_data)))]
            data2 = json.loads(post_page_free(base_url + '/newplay/gkpluginsphp.php', post_data))
            ##print '[resolve_externos] data2 = ', data2
            decoded_url = data2['link']
    except:
        traceback.print_exc()
    ##print "decoded url = ", decoded_url
    #print 'DECODED URL----------------'+decoded_url
    if "my.mail.ru/mail/" in decoded_url:
        #print "___resolving videomail.ru url___"
        try:
            videos = resolve_vmail(decoded_url)
        except:
            videos.append({'provider': "NONE", 'url': decoded_url, 'quality': "NONE"})
            traceback.print_exc()
    elif "vk.com/video" in  decoded_url:
        #print "___resolving vk.com url___"
        try:
            videos = resolve_vkcom(decoded_url)
        except:
            videos.append({'provider': "NONE", 'url': decoded_url, 'quality': "NONE"})
            traceback.print_exc()
    elif "odnoklassniki.ru/video/" in decoded_url or "ok.ru" in decoded_url:
        #print "___resolving ok.ru url___"
        try:
            videos = resolve_ok(decoded_url)
        except:
            videos.append({'provider': "NONE", 'url': decoded_url, 'quality': "NONE"})
            traceback.print_exc()
    elif "uptostream.com/" in decoded_url:
        #print "___resolving uptostream.com url___"
        videos.append({'provider': "NONE", 'url': decoded_url, 'quality': "NONE"})
        traceback.print_exc()
##        try:
##            videos = resolve_upstream(decoded_url)
##        except:
##            videos.append({'provider': "NONE", 'url': decoded_url, 'quality': "NONE"})
##            traceback.print_exc()
    elif "drive.google.com/file/d/" in decoded_url:
        #print "___resolving drive.google.com url___"
        try:
            videos = resolve_gdrive(decoded_url)
        except:
            videos.append({'provider': "NONE", 'url': decoded_url, 'quality': "NONE"})
            traceback.print_exc()
    else:
        try:videos.append({'provider': "NONE", 'url': decoded_url, 'quality': "NONE"})
        except:pass
        #print "not supported host!"
    return videos

def rm(m, u, p):
    base_url = rato_base_url()
    #if m in [1,2,3,4,5,6,8,10,16,26,36,39,40,42,45,59]:
        #data = post_page(base_url+"/user/"+u, u, p)
        #groupo_li = re.search("Tehcb:(.+?)</yv>".decode("rot13"), data).group(1)
        #if not ("Nqzvavfgenqbe".decode("rot13") in groupo_li or
            #"Zbqrenqbe".decode("rot13") in groupo_li or
            #"Hcybnqref".decode("rot13") in groupo_li or
            #"Qbangbe".decode("rot13") in groupo_li): dw().doModal()
    return m



def _get_gks_data(html_source):
    base_url = rato_base_url()
    ##print html_source
    mstr_match = re.compile('var a = \d+').findall(html_source)
    mstr_match = mstr_match[0].replace('var a = ','')
    #print "mstr_match:", mstr_match
    if len(mstr_match) == 0:
        #print "mstr_match vazio!"
        return
    gks_match = re.compile('"(/gks2.php\?id=.+?\&a=)"').findall(html_source)
    #print "gks_match:", gks_match
    if len(gks_match) == 0:
        #print "gks_match vazio!!"
        return
    gks_url = base_url + gks_match[0] + urllib.quote_plus(mstr_match)
    #print "gks_url:", gks_url
    gks_data = xmlhttp_request(gks_url)
    ##print "gks_data:", gks_data
    return gks_data


def list_tvshow(url, username, password):
    base_url = rato_base_url()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
    urllib2.install_opener(opener)
    #print "Lista: %s" % (url)
    try:
        html_source = post_page(url, username, password)
    except:
        raise LoginError()
    gks_data = _get_gks_data(html_source)
    if gks_data is None:
        #print "Nenhuma série encontrada!"
        return result
    ##print gks_data
    dp_data = json.loads(re.search(r'var display_data = (\[.+?\])</script>', gks_data).group(1))[0]
    dp_link = json.loads(re.search(r'var display_links = (\[.+?\])</script>', gks_data).group(1))[0]
    ##print "dp_data =", dp_data
    ##print "dp_link =", dp_link
    result = {}
    for season in dp_data.keys():
        result[season] = {}
        if isinstance(dp_data[season], list):
            season_episodes_list = True
            episodes_list = (str(i) for i in range(1, len(dp_data[season])))
        else:
            season_episodes_list = False
            episodes_list = dp_data[season].keys()

        for episode in episodes_list:
            if season_episodes_list:
                result[season][episode] = dp_data[season][int(episode)-1]
            else:
                result[season][episode] = dp_data[season][episode]
            result[season][episode]['options'] = []
            for option in sorted(dp_link.keys()):
                if season not in dp_link[option]:
                    #print '[list_tv_show] missing links for season %s!' % season
                    continue
                if isinstance(dp_link[option][season], list):
                    try:
                        result[season][episode]['options'].append({'subtitle':result[season][episode].get('subtitle'), 'link': dp_link[option][season][int(episode)-1]})
                    except IndexError:
                        #print '[list_tv_show] missing links for season %s episode %s!' % (season, episode)
                        continue
                else:
                    if episode not in dp_link[option][season]:
                        #print '[list_tv_show] missing links for season %s episode %s!' % (season, episode)
                        continue
                    result[season][episode]['options'].append({'subtitle':result[season][episode].get('subtitle'),'link':dp_link[option][season][episode]})
    return result

def list_episodes(url, username, password, season, tvshow_dict, progress_hook=None):
    base_url = rato_base_url()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
    urllib2.install_opener(opener)
    try:
        html_source = post_page(url, username, password)
    except:
        raise LoginError()
    result = tvshow_dict[season]
    for episode in result.keys():
        result[episode]['watched'] = False
    for m in re.finditer(r'<div data-sid="(?P<sid>\d+)" data-eid="(?P<eid>\d+)" data-watch="(?P<watch>\d+)"', html_source):
        if m.group('sid') == season:
            if m.group('eid') not in result:
                continue
            result[m.group('eid')]['watched'] = bool(int(m.group('watch')))
    return result

def get_quality_key(video_item):
    base_url = rato_base_url()
    try:
        return int(video_item['quality'][:-1])
    except:
        pass
    return video_item['quality']

def get_options(url, username, password, flashvar_list=None, progress_hook=None):
    base_url = rato_base_url()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
    urllib2.install_opener(opener)
    options = []
    progress_type = 0
    if flashvar_list is None:
        flashvar_list = []
        progress_type = 1
        try: 
            html_source = post_page(url, username, password)
        except:
            raise LoginError()
        gks_data = _get_gks_data(html_source)
        dp_data = json.loads(re.search(r'var dp_data = (\[[^\]]+\]);', gks_data).group(1))[0]
        dp_link = json.loads(re.search(r'var dp_link = (\[[^\]]+\]);', gks_data).group(1))[0]
        ##print "dp_data = ", dp_data
        ##print "dp_link = ", dp_link
        for idx, key in enumerate(sorted(dp_data)):
            dp_data[key]['link'] = dp_link[key]
            flashvar_list.append(dp_data[key])
            if progress_hook:
                progress_hook(int((idx + 1) / float(len(dp_data.keys())) * 50))
        #print "flashvar_list = ", flashvar_list

    #print "__found %d options__\n\n" % len(flashvar_list)
    for idx, f in enumerate(flashvar_list):
        #print "__processing %d option__\n" % idx
        f['link_data'] = json.loads(post_page_free(base_url + "/newplay/gkpluginsphp.php", [("link", f["link"])]))
        videos = resolver_externos(f['link_data'])
        if len(videos) == 0:
            #print "no videos resolved!"
            continue
        else:
            #print "%d videos resolved" % len(videos)
            for v in videos:
                #######
                subs = []
                if f.get('subtitle'):
                    subs = []
                    for sub_path in f['subtitle'].split(','):
                        subs.append(base_url + sub_path)
                    #print 'subs:', subs
                if subs != []: l = subs[0]
                else: l= 'NONE'
                #######
                #print v
                try:
                    headers = v['headers']
                    ul = v['url']
                    ul+="|" + "&".join("%s=%s"%(k,urllib.quote(l)) for k,l in headers.iteritems())
                    ##print '1RATOTV======================'+ul
                except: ul = str(v['url'])
                #print "video_url[%s] : %s" % (v['quality'], v['url'])
                options.append({'source': str(v['provider']), 'quality': str(v['quality']), 'provider': 'RatoTV', 'url': ul, 'subs': str(l)})
##        if f.get('subtitle'):
##            subs = []
##            for sub_path in f['subtitle'].split(','):
##                subs.append(base_url + sub_path)
##            #print 'subs:', subs
##            for v in videos:
##                v['subs'] = subs
        videos.sort(key=get_quality_key, reverse=True)
        #options.append(videos)
        if progress_hook:
            if progress_type == 0:
                progress_hook(int((idx + 1) / float(len(flashvar_list)) * 100))
            else:
                progress_hook(50 + int((idx + 1) / float(len(flashvar_list)) * 50))
        #print '\n'
    return options

#########################################################################################################################


def series_seasons_get_dictionary(url,username,password):#2
    #print url+username+password
    tvshow_dict = list_tvshow(url, username, password)
    return tvshow_dict

def series_seasons(url, num_season, num_episode, username, password):#1

    serie_dict_temporadas = series_seasons_get_dictionary(url,username,password)
    for season in sorted(serie_dict_temporadas.iterkeys(),key=int):
        if str(season) == str(num_season):
            serie_dict_temporadas = serie_dict_temporadas[str(season)]
            print str(len(serie_dict_temporadas))
            break
            
    
    episodios_dict = {}
    for episode in sorted(serie_dict_temporadas.iterkeys(),key=int):
        episodios_dict[episode] = {}
        episodios_dict[episode]['source'] = [eop for eop in serie_dict_temporadas[episode]['options']]
        
    for episodio in sorted(episodios_dict.iterkeys(), key=keyfunc):
        if str(episodio) == str(num_episode):
            episodios_dict = str(episodios_dict[episodio]["source"])
            break
        
    options = get_options(url, username, password, eval(episodios_dict))
        
    return options


def keyfunc(key): return float(key.replace(" e ","."))



################ para episosios RatoTV ##########################
def rato_season_episodes(url, num_season, username, password):

    serie_dict_temporadas = series_seasons_get_dictionary(url,username,password)
    for season in sorted(serie_dict_temporadas.iterkeys(),key=int):
        if str(season) == str(num_season):
            serie_dict_temporadas = serie_dict_temporadas[str(season)]
            break
    return str(len(serie_dict_temporadas))


###############################################################################################################




class GoogleResolver(UrlResolver):
    name = "googlevideo"
    domains = ["googlevideo.com", "googleusercontent.com", "get.google.com",
               "plus.google.com", "googledrive.com", "drive.google.com", "docs.google.com"]
    pattern = 'https?://(.*?(?:\.googlevideo|(?:plus|drive|get|docs)\.google|google(?:usercontent|drive))\.com)/(.*?(?:videoplayback\?|[\?&]authkey|host/)*.+)'

    def __init__(self):
        self.net = common.Net()
        self.itag_map = {'5': '240', '6': '270', '17': '144', '18': '360', '22': '720', '34': '360', '35': '480',
                         '36': '240', '37': '1080', '38': '3072', '43': '360', '44': '480', '45': '720', '46': '1080',
                         '82': '360 [3D]', '83': '480 [3D]', '84': '720 [3D]', '85': '1080p [3D]', '100': '360 [3D]',
                         '101': '480 [3D]', '102': '720 [3D]', '92': '240', '93': '360', '94': '480', '95': '720',
                         '96': '1080', '132': '240', '151': '72', '133': '240', '134': '360', '135': '480',
                         '136': '720', '137': '1080', '138': '2160', '160': '144', '264': '1440',
                         '298': '720', '299': '1080', '266': '2160', '167': '360', '168': '480', '169': '720',
                         '170': '1080', '218': '480', '219': '480', '242': '240', '243': '360', '244': '480',
                         '245': '480', '246': '480', '247': '720', '248': '1080', '271': '1440', '272': '2160',
                         '302': '2160', '303': '1080', '308': '1440', '313': '2160', '315': '2160', '59': '480'}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        response, video_urls = self._parse_google(web_url)
        if video_urls:
            video = helpers.pick_source(video_urls)
        else:
            video = None

        headers = {'User-Agent': common.FF_USER_AGENT}
        if response is not None:
            res_headers = response.get_headers(as_dict=True)
            if 'Set-Cookie' in res_headers:
                headers['Cookie'] = res_headers['Set-Cookie']

        if not video:
            if ('redirector.' in web_url) or ('googleusercontent' in web_url):
                video = urllib2.urlopen(web_url).geturl()
            elif 'googlevideo.' in web_url:
                video = web_url + helpers.append_headers(headers)
        else:
            if ('redirector.' in video) or ('googleusercontent' in video):
                video = urllib2.urlopen(video).geturl()

        if video:
            if 'plugin://' in video:  # google plus embedded videos may result in this
                return video
            else:
                return video + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'https://%s/%s' % (host, media_id)

    def _parse_google(self, link):
        sources = []
        response = None
        if re.match('https?://get[.]', link):
            if link.endswith('/'): link = link[:-1]
            vid_id = link.split('/')[-1]
            response = self.net.http_GET(link)
            sources = self.__parse_gget(vid_id, response.content)
        elif re.match('https?://plus[.]', link):
            response = self.net.http_GET(link)
            sources = self.__parse_gplus(response.content)
        elif 'drive.google' in link or 'docs.google' in link:
            response = self.net.http_GET(link)
            sources = self._parse_gdocs(response.content)
##############################
        headers = {'User-Agent': common.FF_USER_AGENT}
        if response is not None:
            res_headers = response.get_headers(as_dict=True)
            if 'Set-Cookie' in res_headers:
                headers['Cookie'] = res_headers['Set-Cookie']
        sources_final = []
        for i in sources:
            if 'plugin://' in i[1]:  # google plus embedded videos may result in this
                break
            else:
                sources_final.append((i[0],i[1] + helpers.append_headers(headers)))
###################################            
##        print '_parse_google------------------------'
####        print response
##        print sources
##        print sources_final
        return response, sources_final#sources

    def __parse_gplus(self, html):
        sources = []
        match = re.search('<c-wiz.+?track:impression,click".*?jsdata\s*=\s*".*?(http[^"]+)"', html, re.DOTALL)
        if match:
            source = match.group(1).replace('&amp;', '&').split(';')[0]
            resolved = hmf.HostedMediaFile(url=source).resolve()
            if resolved:
                sources.append(('Unknown Quality', resolved))
##        print '__parse_gplus------------------------'
##        print sources
        return sources

    def __parse_gget(self, vid_id, html):
        sources = []
        match = re.search('.+return\s+(\[\[.*?)\s*}}', html, re.DOTALL)
        if match:
            try:
                js = self.parse_json(match.group(1))
                for top_item in js:
                    if isinstance(top_item, list):
                        for item in top_item:
                            if isinstance(item, list):
                                for item2 in item:
                                    if isinstance(item2, list):
                                        for item3 in item2:
                                            if vid_id in str(item3):
                                                sources = self.__extract_video(item2)
                                                if sources:
                                                    return sources
            except Exception as e:
                pass
##        print '__parse_gget------------------------'
##        print sources
        return sources

    def __extract_video(self, item):
        sources = []
        for e in item:
            if isinstance(e, dict):
                for key in e:
                    for item2 in e[key]:
                        if isinstance(item2, list):
                            for item3 in item2:
                                if isinstance(item3, list):
                                    for item4 in item3:
                                        if isinstance(item4, unicode):
                                            item4 = item4.encode('utf-8')
                                            
                                        if isinstance(item4, basestring):
                                            item4 = urllib2.unquote(item4).decode('unicode_escape')
                                            for match in re.finditer('url=(?P<link>[^&]+).*?&itag=(?P<itag>[^&]+)', item4):
                                                link = match.group('link')
                                                itag = match.group('itag')
                                                quality = self.itag_map.get(itag, 'Unknown Quality [%s]' % itag)
                                                sources.append((quality, link))
                                            if sources:
                                                return sources
##        print '__extract_video------------------------'
##        print sources
        return sources

    def _parse_gdocs(self, html):
        urls = []
        for match in re.finditer('\[\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]', html):
            key, value = match.groups()
            if key == 'fmt_stream_map':
                items = value.split(',')
                for item in items:
                    _source_itag, source_url = item.split('|')
                    if isinstance(source_url, unicode):
                        source_url = source_url.encode('utf-8')
                        
                    source_url = source_url.decode('unicode_escape')
                    quality = self.itag_map.get(_source_itag, 'Unknown Quality [%s]' % _source_itag)
                    source_url = urllib2.unquote(source_url)
                    urls.append((quality, source_url))
                return urls
##        print 'urls------------------------'
##        print urls
        return urls

    @staticmethod
    def parse_json(html):
        if html:
            try:
                if not isinstance(html, unicode):
                    if html.startswith('\xef\xbb\xbf'):
                        html = html[3:]
                    elif html.startswith('\xfe\xff'):
                        html = html[2:]
                js_data = json.loads(html)
                if js_data is None:
                    return {}
                else:
                    return js_data
            except ValueError:
                return {}
        else:
            return {}


                

