import _thread
import json
import logging

import requests
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
mastodon_app_name = config['mastodon_app_name']
mastodon_username = config['mastodon_username']
add_link_in_telegram = config['add_link_in_telegram']
add_link_in_mastodon = config['add_link_in_mastodon']

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[
                        logging.FileHandler('main.log'),
                        logging.StreamHandler()
                    ])

bot = telebot.TeleBot(tg_bot_token, parse_mode="MARKDOWN")


@bot.channel_post_handler(func=lambda message: message.chat.id != channel_chat_id)
def wrong_channel(message):
    logging.warning(f'Received message from wrong channel id: {message.chat.id}')
    bot.reply_to(message, "This bot is only for specific channel.")


@bot.channel_post_handler(func=lambda message: message.chat.id == channel_chat_id)
def send_message_to_mastodon(message):
    logging.info(f'Received channel message from chatid: {message.chat.id} message: {message}')
    try:
        text = message.text
        if "#noforward" in text:
            logging.info('Do not forward this channel message to mastodon.')
            return
        if add_link_in_mastodon:
            link = f'from: https://t.me/c/{str(message.chat.id)[4:]}/{message.message_id}'
            text += f'\n\n{link}'
        header = {
            'Authorization': f'Bearer {mastodon_api_access_token}'
        }
        data = {
            'status': text,
            'media_ids': [],
            'poll': [],
            'visibility': 'public',
        }
        requests.post(f"https://{mastodon_host}/api/v1/statuses", headers=header, data=data)
        logging.info(f'Message:{text}\nforwarded to mastodon.')
        bot.send_message(pm_chat_id, f"{text}\nforwarded to mastodon.")
    except Exception as e:
        logging.warning(e)
        bot.send_message(pm_chat_id, f"Exception: {e}")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    logging.info(f'Received channel message from chatid: {message.chat.id} message: {message}')
    bot.reply_to(message, "Welcome to my bot!")


def send_message_to_channel(content):
    try:
        toot = json.loads(content['payload'])
        logging.info('Received mastodon toot:\n' + json.dumps(toot, ensure_ascii=False, indent=2))
        if toot['account']['username'] == mastodon_username and \
                toot['application']['name'] != mastodon_app_name and \
                toot['in_reply_to_id'] is None and \
                toot['visibility'] in config['scope']:
            logging.info(f'Forwarding message from mastodon to telegram.')
            txt = markdownify(toot['content'])
            if add_link_in_telegram:
                txt += 'from: ' + toot['url']
            logging.info(f'Text sending to telegram: {txt}')
            if len(toot['media_attachments']) != 0:
                medias = []
                for i in toot['media_attachments']:
                    if i['type'] == 'image':
                        medias.append(types.InputMediaPhoto(i['url']))
                    elif i['type'] == 'video':
                        medias.append(types.InputMediaVideo(i['url']))
                medias[0].caption = txt
                logging.info('Sending media group to telegram channel.')
                bot.send_media_group(channel_chat_id, medias)
            else:
                logging.info('Sending pure-text message to telegram channel.')
                bot.send_message(channel_chat_id, txt, disable_web_page_preview=True)
    except Exception as e:
        logging.warning(e)
        bot.send_message(pm_chat_id, f"Exception: {e}")


def on_message(ws, message):
    logging.info(f'Websocket: {message}')
    content = json.loads(message)
    if content['event'] == 'update':
        send_message_to_channel(content)


def on_error(ws, error):
    logging.warning(f'Websocket Error: {error}')


def websocketTest():
    # websocket.enableTrace(True)
    websocket.setdefaulttimeout(10)
    ws = websocket.WebSocketApp(
        f"wss://{mastodon_host}/api/v1/streaming?access_token={mastodon_api_access_token}&stream=user",
        on_message=on_message,
        on_error=on_error)
    ws.run_forever()


if __name__ == '__main__':
    _thread.start_new_thread(websocketTest, ())
    bot.infinity_polling()
