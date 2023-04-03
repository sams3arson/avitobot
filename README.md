# avitobot
You can see a demo [here](https://j.gifs.com/16vMDj.mp4).
## Description
avitobot is a bot with the help of which you can track advertisements on [Avito](https://www.avito.ru): 
- the appearance of new ones,
- price changes on old ones, 
- general statistics on advertisements \
(for specific queries).
> Avito is a Russian platform for selling and buying used things.

With the help of this bot you can run a resale business.

It's done using async libraries Pyrogram (tg bot), aiosqlite (db), pyppeteer (webdriver).

## Installation
You need to have Python with pip installed (3.10+ recommended, not tested on lower).

1. Install requirements:
```
$ pip3 install -r requirements.txt
```
2. Create your own bot and get the bot token.

3. Get Telegram app API keys at [my.telegram.org/apps](https://my.telegram.org/apps).

4. Get ID of your telegram account with [userinfobot](https://t.me/userinfobot).

5. Set environment variables `API_ID`, `API_HASH`, `BOT_TOKEN` and `OWNER_ID` or
fill them in `config.ini` file inside `avitobot` package.

6. Go to `avitobot` package, create an SQLite database named `avitobot.db` and use content 
inside `avitobot.sql` file to create all required tables. You can run this command on Linux or macOS:
```
$ cat avitobot.sql | sqlite3 avitobot.db
```
7. Finally, run the bot (in repo folder, not in `avitobot` package):
```
$ python3 -m avitobot
```
If you experience any problems or bugs, feel free to create an issue.

## Usage
Commands:
- `help` - get help info
- `city` - set the city where bot will look for ads
- `interval` - set interval of checking your tracked requests
- `status` - get all info about your current settings and status
- `ping` - bot will send you message every 4 hours if he's alive
- `request` - look for ads on specific query (later, you can turn on tracking all ads on that request)
- `stop` - stop tracking a request

## Plans
- add poetry as package manager for project
- add English language (for experience, no idea why English would use this bot)
- probably add some handling of exceptions that may occur
