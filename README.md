# Mastodon2TG

Sync mastodon toot and telegram channel or group in both direction.

Using mastodon websocket API to fetch statuses update.

## Functions

### Mastodon to Telegram

- [x] Text only message
- [x] Text with photo
- [ ] Poll...


### Telegram to Mastodon

- [x] Text only message
- [ ] Photo
- [ ] Medias...

(Video and other media type may not working...)

## Usage

Modify your `config.sample.json` to `config.json` with your own information.

All keys except chat_id is necessary.

Get your telegram bot token from telegram: @botfather.

Get your mastodon api token from your mastodon server.

You can fork this project and modify the source code as you want.
## Todo

- [x] Sync telegram channel message to mastodon.
- [ ] Support other message type. (Maybe poll?)