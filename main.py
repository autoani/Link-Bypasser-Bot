import pyrogram
from pyrogram import Client,filters
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton
from os import environ, remove
from threading import Thread
from json import load
from re import search

from texts import HELP_TEXT
import bypasser
import freewall
from time import time

import psutil
from datetime import datetime

botStartTime = time()


# bot
with open('config.json', 'r') as f: DATA = load(f)
def getenv(var): return environ.get(var) or DATA.get(var, None)

bot_token = getenv("TOKEN")
api_hash = getenv("HASH") 
api_id = getenv("ID")

app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)  




# stats command
@app.on_message(filters.command(["stats"]))
async def stats_command(_, message):
    def get_readable_time(seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

    def get_readable_file_size(size, decimal_places=2):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                break
            size /= 1024.0
        return f"{size:.{decimal_places}f} {unit}"

    def get_progress_bar_string(percent, length=10):
        progress = int(length * percent / 100.0)
        return "[" + "#" * progress + "-" * (length - progress) + "]"

    def boot_time():
        return psutil.boot_time()

    sys_time = get_readable_time(time() - boot_time())
    bot_time = get_readable_time(time() - botStartTime)

    cpu_usage = psutil.cpu_percent(interval=1)
    v_core = psutil.cpu_count(logical=True) - psutil.cpu_count(logical=False)
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    total, used, free, disk = psutil.disk_usage('/')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)

    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv())

    stats = f'**Your Bot Statistics**\n\n' \
            f'**System Uptime:** `{sys_time}`\n' \
            f'**Bot Uptime:** `{bot_time}`\n\n' \
            f'**CPU:** `{get_progress_bar_string(cpu_usage)} {cpu_usage}%`\n' \
            f'**CPU Total Core(s):** `{psutil.cpu_count(logical=True)}`\n' \
            f'**P-Core(s):** `{psutil.cpu_count(logical=False)}` | **V-Core(s):** `{v_core}`\n' \
            f'**Frequency:** `{psutil.cpu_freq(percpu=False).current} Mhz`\n\n' \
            f'**RAM:** `{get_progress_bar_string(memory.percent)} {memory.percent}%`\n' \
            f'**RAM In Use:** `{get_readable_file_size(memory.used)}` [{memory.percent}%]\n' \
            f'**Total:** `{get_readable_file_size(memory.total)}` | **Free:** `{get_readable_file_size(memory.available)}`\n\n' \
            f'**SWAP:** `{get_progress_bar_string(swap.percent)} {swap.percent}%`\n' \
            f'**SWAP In Use:** `{get_readable_file_size(swap.used)}` [{swap.percent}%]\n' \
            f'**Allocated:** `{get_readable_file_size(swap.total)}` | **Free:** `{get_readable_file_size(swap.free)}`\n\n' \
            f'**DISK:** `{get_progress_bar_string(disk)} {disk}%`\n' \
            f'**Drive In Use:** `{used}` [{disk}%]\n' \
            f'**Total:** `{total}` | **Free:** `{free}`\n\n' \
            f'**UL:** `{sent}` | **DL:** `{recv}`'

    await app.send_message(
        chat_id=message.chat.id,
        text=stats
    )


# handle ineex
def handleIndex(ele,message,msg):
    result = bypasser.scrapeIndex(ele)
    try: app.delete_messages(message.chat.id, msg.id)
    except: pass
    for page in result: app.send_message(message.chat.id, page, reply_to_message_id=message.id, disable_web_page_preview=True)


# loop thread
def loopthread(message,otherss=False):

    urls = []
    if otherss: texts = message.caption
    else: texts = message.text

    if texts in [None,""]: return
    for ele in texts.split():
        if "http://" in ele or "https://" in ele:
            urls.append(ele)
    if len(urls) == 0: return

    if bypasser.ispresent(bypasser.ddl.ddllist,urls[0]):
        msg = app.send_message(message.chat.id, "⚡ __generating...__", reply_to_message_id=message.id)
    elif freewall.pass_paywall(urls[0], check=True):
        msg = app.send_message(message.chat.id, "🕴️ __jumping the wall...__", reply_to_message_id=message.id)
    else:
        if "https://olamovies" in urls[0] or "https://psa.wf/" in urls[0]:
            msg = app.send_message(message.chat.id, "⏳ __this might take some time...__", reply_to_message_id=message.id)
        else:
            msg = app.send_message(message.chat.id, "🔎 __bypassing...__", reply_to_message_id=message.id)

    strt = time()
    links = ""
    temp = None
    for ele in urls:
        if search(r"https?:\/\/(?:[\w.-]+)?\.\w+\/\d+:", ele):
            handleIndex(ele,message,msg)
            return
        elif bypasser.ispresent(bypasser.ddl.ddllist,ele):
            try: temp = bypasser.ddl.direct_link_generator(ele)
            except Exception as e: temp = "**Error**: " + str(e)
        elif freewall.pass_paywall(ele, check=True):
            freefile = freewall.pass_paywall(ele)
            if freefile:
                try: 
                    app.send_document(message.chat.id, freefile, reply_to_message_id=message.id)
                    remove(freefile)
                    app.delete_messages(message.chat.id,[msg.id])
                    return
                except: pass
            else: app.send_message(message.chat.id, "__Failed to Jump", reply_to_message_id=message.id)
        else:    
            try: temp = bypasser.shortners(ele)
            except Exception as e: temp = "**Error**: " + str(e)
        print("bypassed:",temp)
        if temp != None: links = links + temp + "\n"
    end = time()
    print("Took " + "{:.2f}".format(end-strt) + "sec")

    if otherss:
        try:
            app.send_photo(message.chat.id, message.photo.file_id, f'__{links}__', reply_to_message_id=message.id)
            app.delete_messages(message.chat.id,[msg.id])
            return
        except: pass

    try: 
        final = []
        tmp = ""
        for ele in links.split("\n"):
            tmp += ele + "\n"
            if len(tmp) > 4000:
                final.append(tmp)
                tmp = ""
        final.append(tmp)
        app.delete_messages(message.chat.id, msg.id)
        tmsgid = message.id
        for ele in final:
            tmsg = app.send_message(message.chat.id, f'__{ele}__',reply_to_message_id=tmsgid, disable_web_page_preview=True)
            tmsgid = tmsg.id
    except Exception as e:
        app.send_message(message.chat.id, f"__Failed to Bypass : {e}__", reply_to_message_id=message.id)
        


# start command
@app.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id, f"__👋 Hi **{message.from_user.mention}**, i am Link Bypasser Bot, just send me any supported links and i will you get you results.\nCheckout /help to Read More__",
    reply_markup=InlineKeyboardMarkup([
        [ InlineKeyboardButton("🌐 Source Code", url="https://github.com/bipinkrish/Link-Bypasser-Bot")],
        [ InlineKeyboardButton("Replit", url="https://replit.com/@bipinkrish/Link-Bypasser#app.py") ]]), 
        reply_to_message_id=message.id)


# help command
@app.on_message(filters.command(["help"]))
def send_help(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id, HELP_TEXT, reply_to_message_id=message.id, disable_web_page_preview=True)


# links
@app.on_message(filters.text)
def receive(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    bypass = Thread(target=lambda:loopthread(message),daemon=True)
    bypass.start()


# doc thread
def docthread(message):
    msg = app.send_message(message.chat.id, "🔎 __bypassing...__", reply_to_message_id=message.id)
    print("sent DLC file")
    file = app.download_media(message)
    dlccont = open(file,"r").read()
    links = bypasser.getlinks(dlccont)
    app.edit_message_text(message.chat.id, msg.id, f'__{links}__', disable_web_page_preview=True)
    remove(file)


# files
@app.on_message([filters.document,filters.photo,filters.video])
def docfile(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    
    try:
        if message.document.file_name.endswith("dlc"):
            bypass = Thread(target=lambda:docthread(message),daemon=True)
            bypass.start()
            return
    except: pass

    bypass = Thread(target=lambda:loopthread(message,True),daemon=True)
    bypass.start()


# server loop
print("Bot Starting")
app.run()
