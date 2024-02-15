
import os
import requests
import logging
from flask import Flask, request, make_response
import hashlib
import xml.etree.ElementTree as ET
import time
import json

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.DEBUG)  # 设置日志等级为 DEBUG

# 使用 os.environ.get('环境变量名称') 来获取环境变量
WEIXIN_TOKEN = os.environ.get('WEIXIN_TOKEN')
WEIXIN_APPID = os.environ.get('WEIXIN_APPID')
WEIXIN_APPSECRET = os.environ.get('WEIXIN_APPSECRET')
WEBSERVICE_TOKEN = os.environ.get('WEBSERVICE_TOKEN')
WEBSERVICE_URL = os.environ.get('WEBSERVICE_URL')
PROXY_SECRET = os.environ.get('PROXY_SECRET')  # 从环境变量获取 PROXY_SECRET

@app.route('/weixin', methods=['GET', 'POST'])
def weixin():
    if request.method == 'GET':
        # 微信公众号接入验证
        token = WEIXIN_TOKEN
        data = request.args
        signature = data.get('signature', '')
        timestamp = data.get('timestamp', '')
        nonce = data.get('nonce', '')
        echostr = data.get('echostr', '')
        s = [timestamp, nonce, token]
        s.sort()
        s = ''.join(s).encode('utf-8')
        if hashlib.sha1(s).hexdigest() == signature:
            return make_response(echostr)
        else:
            return make_response("Verification failed")
    else:
        # 处理接收到的用户消息
        xml_rec = request.stream.read()
        xml_rec = ET.fromstring(xml_rec)
        to_user = xml_rec.find('ToUserName').text
        from_user = xml_rec.find('FromUserName').text
        msg_type = xml_rec.find('MsgType').text
        
        # 根据消息类型进行处理
        if msg_type == 'text':
            content = xml_rec.find('Content').text
            print(content)
            headers = {
                'accept': 'application/json',
                'Authorization': PROXY_SECRET,  # 使用环境变量中的 PROXY_SECRET
                'Content-Type': 'application/json'
            }
            data = {
                "messages": [
                    {
                        "content": content,  # 微信消息作为内容发送
                        "role": "user"
                    }
                ],
                "model": "gpt-4",
                "stream": False
            }
            print(data)
            response = requests.post(WEBSERVICE_URL+"/v1/chat/completions", headers=headers, data=json.dumps(data))  # 使用环境变量中的 WEBSERVICE_URL
            print(json.dumps(response))
            # step 3 和 step 4: 接收 webservice 的响应并返回给微信服务器...   
            if response.status_code == 200:
                reply = f"<xml><ToUserName><![CDATA[{from_user}]]></ToUserName><FromUserName><![CDATA[{to_user}]]></FromUserName><CreateTime>{int(time.time())}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[你好，你发送的消息是: {content}]]></Content></xml>"
                print(reply)
                response = make_response(reply)
                response.content_type = 'application/xml'
                return response
            else:
                return "success"

if __name__ == '__main__':
    app.run()
