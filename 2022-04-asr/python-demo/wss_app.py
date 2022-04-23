#/usr/bin/python
#-*- coding: utf-8 -*-
import ssl
import urllib
from html.parser import HTMLParser
import sys,os,string
import requests
import time
import datetime
import websocket
import hashlib
import json
import uuid
from optparse import OptionParser

try:
    import thread
except ImportError:
    import _thread as thread
import time

parser = OptionParser()

def Usage():
    parser.add_option("-u", "--url", help="asr ws/wss url", action="store", type="string", dest="wsurl", default="wss://speech-test.ainirobot.com/ws/streaming-asr")
    parser.add_option("-a", "--auth_url", help="auth url", action="store", type="string", dest="authurl", default="https://speech-test.ainirobot.com/asr-auth/token/apply")
    parser.add_option("-p", "--pid",  help="product id", action="store", type="int", dest="pid", default=7001)
    parser.add_option("-f", "--file",  help="audio file", action="store", type="string", dest="pcmfile", default="1.pcm")

    parser.add_option("--client_id",  help="auth paramter client id", action="store", type="string", dest="acid", default="")
    parser.add_option("--client_secret",   help="auth paramter client secret", action="store",  type="string", dest="asecret", default="")

    parser.add_option("--protocol",  help="protocol,(0,307,400,200 eg)", action="store", type="string", dest="protocol", default="0")
    parser.add_option("--lang",  help="lang:1 chinese, 2 english", action="store", type="int", dest="lang", default=1)
    parser.add_option("--trans",  help="trans lang:0 chinese, 1 englist", action="store", type="int", dest="trans", default=2)
    parser.add_option("--type",  help="audio type:0 16kpcm, 1:16kopus, 2:g722", action="store", type="int", dest="audio_type", default=0)

    parser.add_option("--uclientid",  help="user_semantics client_id, protocol=307", action="store", type="string", dest="ucid", default="c_00000001")
    parser.add_option("--usecret",  help="user_semantics client_secret, protocol=307", action="store", type="string", dest="usecret", default="CF5E4E2C28478C7526211DDCD1E0BD67")
    parser.add_option("--utoken",  help="user_semantics union access token, protocol=307", action="store", type="string", dest="utoken", default="eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vYXBpLmNoaWxkLmNtY20uY29tIiwiaWF0IjoxNTExMTgxNzc3LCJ1c2VySWQiOjY3fQ.egXSXeynzewxIRdgTXvPPf495A_EdJyHlpSKb6r6sfw")

    parser.add_option("--enter",  help="enterprise id", action="store", type="string", dest="enterid", default="")

    #others
    parser.add_option("--sepa",  help="out log with html separator", action="store", type="string", dest="sepa", default="")

#auth
def authVerify(url, id, secret):
    filename = "tts.token." + id
    token=""
    if os.path.exists(filename) :
        #read local token and expire
        fd = open(filename,"r")
        line = fd.readline()
        info = line.split(":")
        token = info[0]
        etime = info[1]
        ctime = int(time.time())
        if int(etime) > ctime :
            print("local token valid, etime:" + str(etime) + ", ctime:" + str(ctime) + options.sepa)
            fd.close()
            return token
        token=""
        fd.close()
    print("local token expire, apply again !" + options.sepa)
    headers = {}
    payload = {'client_id':id, 'client_secret':secret}
    print(payload)
    resp = requests.post(url, data=payload, headers=headers, timeout=3)
    if resp.status_code == 200 :
        headjson = resp.text
        headdict = json.loads(headjson)
        ret = headdict['code']
        if ret == "success" :
            token = headdict['token']
            utime = headdict['expire']
            #write to local
            with open(filename, "w+") as fd :
                fd.write(token + ":" + utime)
    return token

#websocket
def on_message(ws, message):
    print("接收包  " + message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("##close##")

def on_open(ws):
    def run(*args):
        pkg = {}
        pkg["sid"] = str(uuid.uuid1()) + "-wss_app-test";
        pkg["pid"] = options.pid
        pkg["devid"] = "wss-app-test-1234567890"
        pkg["protocol"] = options.protocol
        pkg["lang"] = options.lang
        pkg["audio_type"] = options.audio_type

        if options.protocol == "400" : #translate paramter
            mt = {}
            mt["range"] = [options.lang, options.trans]
            pkg["mt"] = json.dumps(mt)

        elif options.protocol == "307" : #nlu paramter
            #307
            us = {}
            us["client_id"] = options.ucid
            us["user_id"] = "wss_test_uid"
            us["device_type"] = "2"
            us["deviceid"] = "wss-app-test-1234567890"
            us["imei"] = "012345678912345"
            us["lat"] = "30.678124"
            us["lng"] = "104.09434"
            us["os_type"] = "linux"
            us["union_access_token"] = options.utoken
            us["os_version"] = 19
            us["date"] = int(round(time.time()*1000))
            us["version"] = 10509
            us["enterprise_id"] = options.enterid
            #sign
            allvalue = ""
            for k,v in us.items():
                if type(v) == str :
                    allvalue += v
                else :
                    allvalue += str(v)
            allvalue += options.usecret
            sallvalue = sorted(allvalue)
            #md5
            md = hashlib.md5()
            md.update(str(sallvalue))
            sign=md.hexdigest()
            pkg["user_semantics"] = json.dumps(us) + "&sign=" + sign
        #first
        firstpkg = json.dumps(pkg)
        print("发送包  " + firstpkg)
        ws.send(firstpkg, 0x1);
        pkg_num=1
        #middle
        fd = open(options.pcmfile, "rb")
        try:
            while True:
                chunk = fd.read(1024)
                if not chunk:
                    break
                ws.send(chunk, 0x2)
                pkg_num+=1
                #print "send %d:binary data" % (pkg_num)
                time.sleep(0.03)
        finally:
            fd.close()
        #last
        pkg = {}
        pkg["pkgnum"] = pkg_num + 1
        lastpkg=json.dumps(pkg)
        print("发送包  %s" % (lastpkg))
        ws.send(lastpkg, 0x1);
        #print("thread terminating...")
    thread.start_new_thread(run, ())


def wssasr(token):
    websocket.enableTrace(False)
    headers=["Authorization: Bearer " + token]
    ws = websocket.WebSocketApp(options.wsurl, on_message = on_message, on_error = on_error, on_close = on_close, header=headers)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

if __name__ == "__main__":
    #参数
    Usage()
    (options, args) = parser.parse_args(sys.argv)
    if options.wsurl == None:
        print ("paramter error, url is null" + "<br>")
        exit(-1)
    if options.authurl == None:
        print ("paramter error, url is null" + "<br>")
        exit(-1)
    if options.acid == None:
        print ("paramter error, client_id is null" + "<br>")
        exit(-1)
    if options.asecret == None:
        print ("paramter error, client_secret is null" + "<br>")
        exit(-1)

    #1-鉴权
    token = authVerify(options.authurl, options.acid, options.asecret)
    if token == "" :
        print ("auth verify error" + "<br>")
        exit(-2)

    #2-识别
    wssasr(token)

    exit(0)
