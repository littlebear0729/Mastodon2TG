# Mastodon2TG

Sync mastodon toot and telegram channel or group in both direction.

Using mastodon websocket API to fetch statuses update.

## Functions

### Mastodon to Telegram

- [x] Text only message
- [x] Text with photo
- [x] Text with video
- [ ] Poll...


### Telegram to Mastodon

- [x] Text only message
- [ ] Photo
- [ ] Medias...

(Video and other media type may not working...)

### Tag #noforward

Add tag `#noforward` if you don't want to forward messages.

## Usage

Copy .env.example

```shell
cp .env.example .env
```

Edit it with your values

### Docker-compose

```shell
docker-compose up -d --build
```

### Standalone

```shell
python main.py
```

|Key|Explaination
|:-:|:-:
|add_link_in_mastodon|Decides whether to add a link in Telegram Channel Messages forwarded to your Mastodon Instance.
|add_link_in_telegram|Decides whether to add a link in Toots forwarded to Telegram Channel.
|channel_chat_id|Forward a message from your channel to [@GetIDs Bot](https://t.me/getidsbot) to get it. Should start with `-100`.
|mastodon_api_access_token|See [How to configure your Mastodon Instance?](#how-to-configure-your-mastodon-instance).
|mastodon_app_name|See [How to configure your Mastodon Instance?](#how-to-configure-your-mastodon-instance).
|mastodon_host|Your mastodon host. e.g. `hub.example.com` from `@alice@hub.example.com`
|mastodon_username|Your mastodon username. e.g. `alice` from `@alice@hub.example.com`
|pm_chat_id|Your Account's ID. You will get it by forwarding a message to [@GetIDs Bot](https://t.me/getidsbot).
|scope|Determines whether a toot should be forwarded to Telegram Channel. Possible values: public, unlisted, private, direct with `,` delimeter
|tg_bot_token|Create a bot in Telegram using [@BotFather](https://t.me/BotFather)

### How to configure your Mastodon Instance?

1. Navigate to `Settings`.
2. In `Settings` find the `Development` section.
3. Click on `New Application`
4. Fill in `Application Name`. e.g. `Mastodon2TG`. This will be displayed when a message is forwarded.**Leave everything else default.**
5. You have finished creating an application. Click its name to grab the required access token. Copy the value in the field `Your access token` and paste it into `mastodon_api_access_token` in `config.json`.
6. In `config.json`, fill in `mastodon_app_name`. e.g. `Mastodon2TG`
7. In `config.json`, fill in `mastodon_username`. e.g. `yourusername`
8. You're done!

## Code License

You have to use the source code under license.

## Todo

- [x] Sync telegram channel message to mastodon.
- [ ] Support other message type. (Maybe poll?)
- [ ] Support reply message. (Maybe in both direction?)
