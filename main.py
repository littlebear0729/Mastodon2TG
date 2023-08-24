from dotenv import load_dotenv
from markdownify import markdownify
from telebot import types
import json
import logging
import os
import rel
import requests
import telebot
import threading
import websocket

import threading

# Load environment variables from .env file
load_dotenv()

# Fetch variables from environment or .env file
tg_bot_token = os.getenv('TG_BOT_TOKEN')
channel_chat_id = int(os.getenv('CHANNEL_CHAT_ID'))
pm_chat_id = int(os.getenv('PM_CHAT_ID'))
mastodon_host = os.getenv('MASTODON_HOST')
mastodon_api_access_token = os.getenv('MASTODON_API_ACCESS_TOKEN')
mastodon_app_name = os.getenv('MASTODON_APP_NAME')
mastodon_username = os.getenv('MASTODON_USERNAME')
add_link_in_telegram = os.getenv('ADD_LINK_IN_TELEGRAM') == 'True'
add_link_in_mastodon = os.getenv('ADD_LINK_IN_MASTODON') == 'True'
scope = os.getenv('SCOPE', 'public')  # Default to 'public' if not provided

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
            logging.info('Tag #noforward detected, aborting forwarding this channel message to mastodon.')
            return
        if add_link_in_mastodon:
            link = f'Forwarded From: https://t.me/c/{str(message.chat.id)[4:]}/{message.message_id}'
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
    bot.reply_to(message, "Welcome to my bot! If you want the same one for yourself, check this: https://github.com/littlebear0729/Mastodon2TG")


def send_message_to_channel(content):
    try:
        toot = json.loads(content['payload'])
        if toot['account']['username'] != mastodon_username:
            logging.info('Mastodon username does not match, skipping forwarding to Telegram.')
            return
        if toot['application']['name'] == mastodon_app_name:
            logging.info('Mastodon app name matches, skipping forwarding to Telegram.')
            return
        if toot['in_reply_to_id'] is not None:
            logging.info('Toot is a reply, skipping forwarding to Telegram.')
            return
        if toot['visibility'] not in scope:
            logging.info('Toot visibility is not in scope, skipping forwarding to Telegram.')
            return
        logging.info(f'Forwarding message from mastodon to telegram.')
        txt = markdownify(toot['content'])
        if "#noforward" in txt:
            logging.info(f'Tag #noforward detected, aborting forwarding this mastodon toot to telegram channel.')
            return
        if add_link_in_telegram:
            txt += 'Forwarded From: ' + toot['url']
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


def start_polling():
    bot.infinity_polling()

if __name__ == '__main__':
    threading.Thread(target=start_polling).start()

    # websocket.enableTrace(True)
    websocket.setdefaulttimeout(10)
    ws = websocket.WebSocketApp(
        f"wss://{mastodon_host}/api/v1/streaming?access_token={mastodon_api_access_token}&stream=user",
        on_message=on_message,
        on_error=on_error)
    ws.run_forever(dispatcher=rel, reconnect=5)
    rel.signal(2, rel.abort)
    rel.dispatch()

