from __future__ import unicode_literals

import os
import sys
import redis
import requests

from argparse import ArgumentParser
from linebot.models import FlexSendMessage
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoMessage, FileMessage, StickerMessage, StickerSendMessage,TemplateSendMessage,ButtonsTemplate,ImageSendMessage
)
from linebot.utils import PY3

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# obtain the port that heroku assigned to this app.
heroku_port = os.getenv('PORT', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if isinstance(event.message, TextMessage):
            handle_Confirmed(event)
        #if isinstance(event.message, ButtonsTemplate):
            #handle_News(event)
        if isinstance(event.message, ImageMessage):
            handle_image(event)
        if isinstance(event.message, StickerMessage):
            handle_News(event)
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

    return 'OK'

# Handler function for Text Message


def handle_Confirmed(event):
    input_text = event.message.text
    # 请求地址
    url = 'http://www.dzyong.top:3005/yiqing/area'
    # 发送get请求
    r = requests.get(url)
    t = r.json()

    if input_text == '疫情信息':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='请输入要查询的城市:'))
    input_text_1 = event.message.text
    for item in t['data']:
        if item['cityName'] == input_text_1:
            confirm = item['confirmedCount']
            suspect = item['suspectedCount']
            dead = item['deadCount']
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f'{input_text_1}的肺炎感染人数为:{confirm}人,\n{input_text_1}的疑似感染肺炎人数为:{suspect}人,\n{input_text_1}因肺炎死亡的人数为:{dead}人'))


def handle_News(event):
    #input_text = event.message.text
    #if input_text == "疫情新闻":
    print("successfully operate handle_News function")
    flex = make_flex()
    line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text = "疫情播报",
                    contents = flex
                )
            )


def make_flex():

    contents ={"type": "bubble",
               "header": {
                   "type": "box",
                   "layout": "horizontal",
                   "contents": [
                       {"type": "text", "text": "疫情新闻", "size": "xl", "weight": "bold"},
                   ]
               },
               "hero": {
                   "type": "image",
                   "url": "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1586910091544&di=e1676a22ba60d21bbd925b0e9ed4767f&imgtype=0&src=http%3A%2F%2Fwww.e4221.com%2Fuploads%2Fallimg%2F2003%2F2-20031212533c27.jpg",
                   "size": "full",
                   "aspect_ratio": "20:13",
                   "aspect_mode": "cover"
               },
               "footer": {
                   "type": "box",
                   "layout": "vertical",
                   "contents": [
                       {"type": "spacer", "size": "md"},
                       {"type": "button", "style": "primary", "color": "#1DB352",
                        "action": {"type": "uri", "label": "国内疫情新闻", "uri": 'https://news.qq.com/zt2020/page/feiyan.htm#/?nojump=1'}},
                        {"type": "button", "style": "primary", "color": "#1DB352",
                        "action": {"type": "uri", "label": "香港疫情新闻", "uri": 'https://www.coronavirus.gov.hk/chi/'}}
                   ]
               }
              }


    return contents

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)
