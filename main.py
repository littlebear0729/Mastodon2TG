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
mastodon_api_access_token = config['mastodon_api_access_token']
mastodon_username = config['mastodon_username']

bot = telebot.TeleBot(tg_bot_token, parse_mode=None)

@bot.message_handler()
def log(message):
    print(message.chat.id, message)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(message.chat.id, message)
    bot.reply_to(message, "Welcome to my bot!")


def send_message(content):
    try:
        toot = json.loads(content['payload'])
        print(json.dumps(toot, ensure_ascii=False, indent=2))
        if toot['account']['username'] == mastodon_username and toot['in_reply_to_id'] is None and toot['visibility'] in config['scope']:
            txt = markdownify(toot['content'])
            txt += 'from: ' + toot['url']
            print(txt)
            if len(toot['media_attachments']) != 0:
                medias = []
                for i in toot['media_attachments']:
                    if i['type'] == 'image':
                        medias.append(types.InputMediaPhoto(i['url']))
                    elif i['type'] == 'video':
                        medias.append(types.InputMediaVideo(i['url']))
                medias[0].caption = txt
                bot.send_media_group(channel_chat_id, medias)
            else:
                bot.send_message(channel_chat_id, txt, disable_web_page_preview=True)
    except Exception as e:
        print(e)
        bot.send_message(pm_chat_id, f"Exception: {e}")


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
        f"wss://{mastodon_host}/api/v1/streaming?access_token={mastodon_api_access_token}&stream=user",
        on_message=on_message,
        on_error=on_error)
    ws.run_forever()


if __name__ == '__main__':
    _thread.start_new_thread(websocketTest, ())
    bot.infinity_polling()
