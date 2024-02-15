import os
import requests
from flask import Flask, request, make_response
import hashlib
import xml.etree.ElementTree as ET
import time

app = Flask(__name__)

# 使用 os.environ.get('环境变量名称') 来获取环境变量
WEIXIN_TOKEN = os.environ.get('WEIXIN_TOKEN')
WEIXIN_APPID = os.environ.get('WEIXIN_APPID')
WEIXIN_APPSECRET = os.environ.get('WEIXIN_APPSECRET')
WEBSERVICE_TOKEN = os.environ.get('WEBSERVICE_TOKEN')
WEBSERVICE_URL = os.environ.get('WEBSERVICE_URL')

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
    """
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
            reply = f"<xml><ToUserName><![CDATA[{from_user}]]></ToUserName><FromUserName><![CDATA[{to_user}]]></FromUserName><CreateTime>{int(time.time())}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[你好，你发送的消息是: {content}]]></Content></xml>"
            
            response = make_response(reply)
            response.content_type = 'application/xml'
            return response
        # 可以添加更多消息类型的处理逻辑
        # ...

    return "success"  
    """
    else:
        # step 1: 接收微信消息
        data = request.get_data()
        
        # step 2: 将消息和token发送到指定的 webservice
        headers = {
            'Content-Type': 'application/xml',
            'Authorization': f'Bearer {WEBSERVICE_TOKEN}'  # 假设 webservice 使用 Bearer token 认证
        }
        response = requests.post(WEBSERVICE_URL, data=data, headers=headers)
        
        # step 3: 接收 webservice 的响应
        # 确保 webservice 返回的是微信期望的 XML 格式
        
        # step 4: 将这个响应返回给微信服务器
        if response.status_code == 200:
            return response.text, 200, {'Content-Type': 'application/xml'}
        else:
            # 如果 webservice 响应错误，你可以决定如何处理
            return "success"

if __name__ == '__main__':
    app.run()