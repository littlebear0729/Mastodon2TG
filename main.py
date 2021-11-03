import _thread
import json

import telebot
import websocket
from markdownify import markdownify
from telebot import types

# Read Config
with open('config.json', 'r') as f:
    config = json.load(f)

tg_bot_token = config['tg_bot_token']
channel_chat_id = config['channel_chat_id']
pm_chat_id = config['pm_chat_id']
mastodon_host = config['mastodon_host']
mastodon_api_secret = config['mastodon_api_secret']
mastodon_username = config['mastodon_username']

bot = telebot.TeleBot(tg_bot_token, parse_mode=None)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(message.chat.id, message)
    bot.reply_to(message, "Welcome to my bot!")


def send_message(content):
    try:
        toot = json.loads(content['payload'])
        if toot['account']['username'] == mastodon_username and toot['in_reply_to_id'] is None:
            txt = markdownify(toot['content'])
            if len(toot['media_attachments']) != 0:
                medias = []
                for i in toot['media_attachments']:
                    medias.append(types.InputMediaPhoto(i['url']))
                bot.send_media_group(channel_chat_id, medias)
            txt += 'from: ' + toot['url']
            print(txt)
            bot.send_message(channel_chat_id, txt, disable_web_page_preview=True)
    except Exception as e:
        print(e)


def on_message(ws, message):
    print("ws:", message)
    content = json.loads(message)
    if content['event'] == 'update':
        send_message(content)


def on_error(ws, error):
    print(error)


def websocketTest():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "wss://{host}/api/v1/streaming?access_token={token}&stream=user".format(host=mastodon_host,
                                                                                token=mastodon_api_secret),
        on_message=on_message,
        on_error=on_error)
    ws.run_forever()


if __name__ == '__main__':
    _thread.start_new_thread(websocketTest, ())
    bot.infinity_polling()
