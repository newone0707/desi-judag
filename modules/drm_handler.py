import os
import re
import sys
import m3u8
import json
import time
import pytz
import asyncio
import requests
import subprocess
import urllib
import urllib.parse
import yt_dlp
import tgcrypto
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode
from logs import logging
from bs4 import BeautifulSoup
from aiohttp import ClientSession
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web
import random
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIsBlocked, InputUserDeactivated
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto
import aiohttp
import aiofiles
import zipfile
import shutil
import ffmpeg

import saini as helper
import globals
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN, OWNER, CREDIT, AUTH_USERS, TOTAL_USERS, cookies_file_path
from vars import api_url, api_token

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,


async def drm_handler(bot: Client, m: Message):
    globals.processing_request = True
    globals.cancel_requested = False
    caption = globals.caption
    endfilename = globals.endfilename
    thumb = globals.thumb
    CR = globals.CR
    cwtoken = globals.cwtoken
    cptoken = globals.cptoken
    pwtoken = globals.pwtoken
    vidwatermark = globals.vidwatermark
    raw_text2 = globals.raw_text2
    quality = globals.quality
    res = globals.res
    topic = globals.topic

    user_id = m.from_user.id
    if m.document and m.document.file_name.endswith('.txt'):
        x = await m.download()
        await bot.send_document(OWNER, x)
        await m.delete(True)
        file_name, ext = os.path.splitext(os.path.basename(x))  # Extract filename & extension
        path = f"./downloads/{m.chat.id}"
        with open(x, "r") as f:
            content = f.read()
        lines = content.split("\n")
        os.remove(x)
    elif m.text and "://" in m.text:
        lines = [m.text]
    else:
        return

    if m.document:
        if m.chat.id not in AUTH_USERS:
            print(f"User ID not in AUTH_USERS", m.chat.id)
            await bot.send_message(m.chat.id, f"<blockquote>__**Oopss! You are not a Premium member\nPLEASE /upgrade YOUR PLAN\nSend me your user id for authorization\nYour User id**__ - `{m.chat.id}`</blockquote>\n")
            return

    pdf_count = 0
    img_count = 0
    v2_count = 0
    mpd_count = 0
    m3u8_count = 0
    yt_count = 0
    drm_count = 0
    zip_count = 0
    other_count = 0
    
    links = []
    for i in lines:
        if "://" in i:
            url = i.split("://", 1)[1]
            links.append(i.split("://", 1))
            if ".pdf" in url:
                pdf_count += 1
            elif url.endswith((".png", ".jpeg", ".jpg")):
                img_count += 1
            elif "v2" in url:
                v2_count += 1
            elif "mpd" in url:
                mpd_count += 1
            elif "m3u8" in url:
                m3u8_count += 1
            elif "drm" in url:
                drm_count += 1
            elif "youtu" in url:
                yt_count += 1
            elif "zip" in url:
                zip_count += 1
            else:
                other_count += 1
                    
    if not links:
        await m.reply_text("<b>🔹Invalid Input.</b>")
        return

    if m.document:
        editable = await m.reply_text(f"**Total 🔗 links found are {len(links)}\n<blockquote>•PDF : {pdf_count}      •V2 : {v2_count}\n•Img : {img_count}      •YT : {yt_count}\n•zip : {zip_count}       •m3u8 : {m3u8_count}\n•drm : {drm_count}      •Other : {other_count}\n•mpd : {mpd_count}</blockquote>\nSend From where you want to download**")
        try:
            input0: Message = await bot.listen(editable.chat.id, timeout=20)
            raw_text = input0.text
            await input0.delete(True)
        except asyncio.TimeoutError:
            raw_text = '1'
    
        if int(raw_text) > len(links) :
            await editable.edit(f"🔹**Enter number in range of Index (01-{len(links)})**")
            processing_request = False  # Reset the processing flag
            await m.reply_text("🔹**Processing Cancled......  **")
            return

        await editable.edit(f"**Enter Batch Name or send /d**")
        try:
            input1: Message = await bot.listen(editable.chat.id, timeout=20)
            raw_text0 = input1.text
            await input1.delete(True)
        except asyncio.TimeoutError:
            raw_text0 = '/d'
      
        if raw_text0 == '/d':
            b_name = file_name.replace('_', ' ')
        else:
            b_name = raw_text0

        await editable.edit("__**⚠️Provide the Channel ID or send /d__\n\n<blockquote><i>🔹 Make me an admin to upload.\n🔸Send /id in your channel to get the Channel ID.\n\nExample: Channel ID = -100XXXXXXXXXXX</i></blockquote>\n**")
        try:
            input7: Message = await bot.listen(editable.chat.id, timeout=20)
            raw_text7 = input7.text
            await input7.delete(True)
        except asyncio.TimeoutError:
            raw_text7 = '/d'

        if "/d" in raw_text7:
            channel_id = m.chat.id
        else:
            channel_id = raw_text7    
        await editable.delete()

    elif m.text:
        if any(ext in links[i][1] for ext in [".pdf", ".jpeg", ".jpg", ".png"] for i in range(len(links))):
            raw_text = '1'
            raw_text7 = '/d'
            channel_id = m.chat.id
            b_name = '**Link Input**'
            await m.delete()
        else:
            editable = await m.reply_text(f"╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏʟᴜᴛɪᴏɴ❱━━➣ \n┣━━⪼ send `144`  for 144p\n┣━━⪼ send `240`  for 240p\n┣━━⪼ send `360`  for 360p\n┣━━⪼ send `480`  for 480p\n┣━━⪼ send `720`  for 720p\n┣━━⪼ send `1080` for 1080p\n╰━━⌈⚡[🦋`{CREDIT}`🦋]⚡⌋━━➣ ")
            input2: Message = await bot.listen(editable.chat.id, filters=filters.text & filters.user(m.from_user.id))
            raw_text2 = input2.text
            quality = f"{raw_text2}p"
            await m.delete()
            await input2.delete(True)
            try:
                if raw_text2 == "144":
                    res = "256x144"
                elif raw_text2 == "240":
                    res = "426x240"
                elif raw_text2 == "360":
                    res = "640x360"
                elif raw_text2 == "480":
                    res = "854x480"
                elif raw_text2 == "720":
                    res = "1280x720"
                elif raw_text2 == "1080":
                    res = "1920x1080" 
                else: 
                    res = "UN"
            except Exception:
                    res = "UN"
            raw_text = '1'
            raw_text7 = '/d'
            channel_id = m.chat.id
            b_name = '**Link Input**'
            path = os.path.join("downloads", "Free Batch")
            await editable.delete()
        
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = thumb
#........................................................................................................................................................................................
    try:
        if m.document and raw_text == "1":
            batch_message = await bot.send_message(chat_id=channel_id, text=f"<blockquote><b>🎯Target Batch : {b_name}</b></blockquote>")
            if "/d" not in raw_text7:
                await bot.send_message(chat_id=m.chat.id, text=f"<blockquote><b><i>🎯Target Batch : {b_name}</i></b></blockquote>\n\n🔄 Your Task is under processing, please check your Set Channel📱. Once your task is complete, I will inform you 📩")
                await bot.pin_chat_message(channel_id, batch_message.id)
                message_id = batch_message.id
                pinning_message_id = message_id + 1
                await bot.delete_messages(channel_id, pinning_message_id)
        else:
             if "/d" not in raw_text7:
                await bot.send_message(chat_id=m.chat.id, text=f"<blockquote><b><i>🎯Target Batch : {b_name}</i></b></blockquote>\n\n🔄 Your Task is under processing, please check your Set Channel📱. Once your task is complete, I will inform you 📩")
    except Exception as e:
        await m.reply_text(f"**Fail Reason »**\n<blockquote><i>{e}</i></blockquote>\n\n✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}🌟`")

#........................................................................................................................................................................................
    failed_count = 0
    count =int(raw_text)    
    arg = int(raw_text)
    try:
        for i in range(arg-1, len(links)):
            if globals.cancel_requested:
                await m.reply_text("🚦**STOPPED**🚦")
                globals.processing_request = False
                globals.cancel_requested = False
                return
  
            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            link0 = "https://" + Vxy
#........................................................................................................................................................................................
             
            name1 = links[i][0].replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            if m.text:
                if "youtu" in url:
                    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
                    response = requests.get(oembed_url)
                    audio_title = response.json().get('title', 'YouTube Video')
                    audio_title = audio_title.replace("_", " ")
                    name = f'{audio_title[:60]}'
                    namef = f'{audio_title[:60]}'
                else:
                    name = f'{name1[:60]}'
                    namef = f'{name1[:60]}'
            else:
                if topic == "/yes":
                    raw_title = links[i][0]
                    t_match = re.search(r"[\(\[]([^\)\]]+)[\)\]]", raw_title)
                    if t_match:
                        t_name = t_match.group(1).strip()
                        v_name = re.sub(r"^[\(\[][^\)\]]+[\)\]]\s*", "", raw_title)
                        v_name = re.sub(r"[\(\[][^\)\]]+[\)\]]", "", v_name)
                        v_name = re.sub(r":.*", "", v_name).strip()
                    else:
                        t_name = "Untitled"
                        v_name = re.sub(r":.*", "", raw_title).strip()
                    
                    if endfilename == "/d":
                        name = f'{str(count).zfill(3)}) {name1[:60]}'
                        namef = f'{v_name}'
                    else:
                        name = f'{str(count).zfill(3)}) {name1[:60]} {endfilename}'
                        namef = f'{v_name} {endfilename}'
                else:
                    if endfilename == "/d":
                        name = f'{str(count).zfill(3)}) {name1[:60]}'
                        namef = f'{name1[:60]}'
                    else:
                        name = f'{str(count).zfill(3)}) {name1[:60]} {endfilename}'
                        namef = f'{name1[:60]} {endfilename}'
                        
#........................................................................................................................................................................................
            # Initialize variables
            keys_string = ""
            appxkey = ""
            
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'
         
            #elif 'classplusapp' in url or "testbook.com" in url or "classplusapp.com/drm" in url or "media-cdn.classplusapp.com/drm" in url:
                # Extract contentId from URL
                #base_url = url
                
                # Check for different parameter patterns (both with and without 'l')
                #if '&contentHashId=' in url:
                   # base_url, contentId = url.split('&contentHashId=')
                #elif 'contentHashId=' in url:
                   # parts = url.split('contentHashId=')
                    #base_url = parts[0]
                    #contentId = parts[1].split('&')[0] if '&' in parts[1] else parts[1]
                #elif '&contentHashIdl=' in url:
                 #   base_url, contentId = url.split('&contentHashIdl=')
                #elif 'contentHashIdl=' in url:
                 #   parts = url.split('contentHashIdl=')
                  #  base_url = parts[0]
                   # contentId = parts[1].split('&')[0] if '&' in parts[1] else parts[1]
               # else:
                    # Fallback - try to extract ID from URL pattern
                    #contentId = url.split('/')[-1].split('?')[0] if '/' in url else url
                
                # Clean up contentId - remove any trailing URL parameters or fragments
               # if '&' in contentId:
                   # contentId = contentId.split('&')[0]
                #if '?' in contentId:
                  #  contentId = contentId.split('?')[0]
                #if '#' in contentId:
                   # contentId = contentId.split('#')[0]
             #   url,contentId=url.split('&')
                
              #  headers = {
               #     'host': 'api.classplusapp.com',
                #    'x-access-token': f'{cptoken}',    
                 #   'accept-language': 'EN',
                  #  'api-version': '18',
                   # 'app-version': '1.4.73.2',
                   # 'build-number': '35',
                    #'connection': 'Keep-Alive',
                   # 'content-type': 'application/json',
                   # 'device-details': 'Xiaomi_Redmi 7_SDK-32',
                    #'device-id': 'c28d3cb16bbdac01',
                    #'region': 'IN',
                    #'user-agent': 'Mobile-Android',
                    #'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c',
                    #'accept-encoding': 'gzip'
                #}
                
                #params = {
                 #   'contentId': contentId,
                  #  'offlineDownload': "false"
                #}
                
                 #   res = requests.get("https://api.classplusapp.com/cams/uploader/video/jw-signed-url", params=params, headers=headers).json().get("url")
                    
                    # Check if it's a DRM URL
                  #  if ("testbook.com" in base_url or "classplusapp.com/drm" in base_url or 
                   #     "media-cdn.classplusapp.com/drm" in base_url or '/drm/' in base_url):
                    #    if 'drmUrls' in res and 'manifestUrl' in res['drmUrls']:
                     #       mpd_url = res['drmUrls']['manifestUrl']
                      #      mpd, keys = helper.get_mps_and_keys(mpd_url)
                       #     url = mpd
                        #    keys_string = " ".join([f"--key {key}" for key in keys])
                        #else:
                         #   url = res.get("url", base_url)
                          #  keys_string = ""
                    #else:
                     #   url = res.get("url", base_url)
                      #  keys_string = ""
                        
                    #print(f"ClassPlus API Success - contentId: {contentId[:30]}...")
                        
               # except Exception as e:
                #    print(f"ClassPlus API Error: {e}")
                 #   print(f"URL: {base_url[:100]}, contentId: {contentId}")
                  #  # Keep original URL if API fails
                   # url = base_url
                   # keys_string = ""
            elif 'classplusapp' in url or "testbook.com" in url or "classplusapp.com/drm" in url or "media-cdn.classplusapp.com/drm" in url:
                url, contentId = url.split('&contentHashIdl=')
                
                headers = {
                    'host': 'api.classplusapp.com',
                    'x-access-token': f'{cptoken}',    
                    'accept-language': 'EN',
                    'api-version': '18',
                    'app-version': '1.4.73.2',
                    'build-number': '35',
                    'connection': 'Keep-Alive',
                    'content-type': 'application/json',
                    'device-details': 'Xiaomi_Redmi 7_SDK-32',
                    'device-id': 'c28d3cb16bbdac01',
                    'region': 'IN',
                    'user-agent': 'Mobile-Android',
                    'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c',
                    'accept-encoding': 'gzip'
                }
                
                params = {
                    'contentId': contentId,
                    'offlineDownload': "false"
                }

                res = requests.get("https://api.classplusapp.com/cams/uploader/video/jw-signed-url", params=params, headers=headers).json()
                
                if "testbook.com" in url or "classplusapp.com/drm" in url or "media-cdn.classplusapp.com/drm" in url:
                    url = res['drmUrls']['manifestUrl']
                else:
                    url = res["url"]

            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                url = f"https://anonymouspwplayer-ce3f42358cca.herokuapp.com/pw?url={url}&token={pwtoken}"
                keys_string = ""
                                      
            elif 'encrypted.m' in url:
                if '*' in url:
                    appxkey = url.split('*')[1]
                    url = url.split('*')[0]
                else:
                    appxkey = ""
                keys_string = ""

            if "youtu" in url:
                ytf = f"bv*[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[height<=?{raw_text2}]"
            elif "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
           
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
               cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'
#........................................................................................................................................................................................
            try:
                if m.text:
                    cc = f'[{name1} [{res}p].mkv]({link0})'
                    cc1 = f'[{name1}.pdf]({link0})'
                    cczip = f'[{name1}.zip]({link0})'
                    ccimg = f'[{name1}.jpg]({link0})'
                    ccm = f'[{name1}.mp3]({link0})'
                    cchtml = f'[{name1}.html]({link0})'
                else:
                    if topic == "/yes":
                        if caption == "/cc1":
                            cc = f'[🎥]Vid Id : {str(count).zfill(3)}\n**Video Title :** `{v_name} [{res}p].mkv`\n<blockquote><b>Batch Name : {b_name}\nTopic Name : {t_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                            cc1 = f'[📕]Pdf Id : {str(count).zfill(3)}\n**File Title :** `{v_name}.pdf`\n<blockquote><b>Batch Name : {b_name}\nTopic Name : {t_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                            cczip = f'[📁]Zip Id : {str(count).zfill(3)}\n**Zip Title :** `{v_name}.zip`\n<blockquote><b>Batch Name : {b_name}\nTopic Name : {t_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                            ccimg = f'[🖼️]Img Id : {str(count).zfill(3)}\n**Img Title :** `{v_name}.jpg`\n<blockquote><b>Batch Name : {b_name}\nTopic Name : {t_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                            cchtml = f'[🌐]Html Id : {str(count).zfill(3)}\n**Html Title :** `{v_name}.html`\n<blockquote><b>Batch Name : {b_name}\nTopic Name : {t_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                            ccyt = f'[🎥]Vid Id : {str(count).zfill(3)}\n**Video Title :** `{v_name}.mp4`\n<a href="{url}">__**Click Here to Watch Stream**__</a>\n<blockquote><b>Batch Name : {b_name}\nTopic Name : {t_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                            ccm = f'[🎵]Mp3 Id : {str(count).zfill(3)}\n**Audio Title :** `{v_name}.mp3`\n<blockquote><b>Batch Name : {b_name}\nTopic Name : {t_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        elif caption == "/cc2":
                            cc = f"——— ✦ {str(count).zfill(3)} ✦ ———\n\n<blockquote><b>⋅ ─  {t_name}  ─ ⋅</b></blockquote>\n\n<b>🎞️ Title :</b> {v_name}\n<b>├── Extention :  {CR} .mkv</b>\n<b>├── Resolution : [{res}]</b>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By : {CR}**"
                            cc1 = f"——— ✦ {str(count).zfill(3)} ✦ ———\n\n<blockquote><b>⋅ ─  {t_name}  ─ ⋅</b></blockquote>\n\n<b>📁 Title :</b> {v_name}\n<b>├── Extention :  {CR} .pdf</b>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By : {CR}**"
                            cczip = f"——— ✦ {str(count).zfill(3)} ✦ ———\n\n<blockquote><b>⋅ ─  {t_name}  ─ ⋅</b></blockquote>\n\n<b>📒 Title :</b> {v_name}\n<b>├── Extention :  {CR} .zip</b>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By : {CR}**"
                            ccimg = f"——— ✦ {str(count).zfill(3)} ✦ ———\n\n<blockquote><b>⋅ ─  {t_name}  ─ ⋅</b></blockquote>\n\n<b>🖼️ Title :</b> {v_name}\n<b>├── Extention :  {CR} .jpg</b>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By : {CR}**"
                            ccm = f"——— ✦ {str(count).zfill(3)} ✦ ———\n\n<blockquote><b>⋅ ─  {t_name}  ─ ⋅</b></blockquote>\n\n<b>🎵 Title :</b> {v_name}\n<b>├── Extention :  {CR} .mp3</b>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By : {CR}**"
                            cchtml = f"——— ✦ {str(count).zfill(3)} ✦ ———\n\n<blockquote><b>⋅ ─  {t_name}  ─ ⋅</b></blockquote>\n\n<b>🌐 Title :</b> {v_name}\n<b>├── Extention :  {CR} .html</b>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By : {CR}**"
                        else:
                            cc = f'<blockquote><b>⋅ ─ {t_name} ─ ⋅</b></blockquote>\n<b>{str(count).zfill(3)}.</b> {v_name} [{res}p] .mkv'
                            cc1 = f'<blockquote><b>⋅ ─ {t_name} ─ ⋅</b></blockquote>\n<b>{str(count).zfill(3)}.</b> {v_name} .pdf'
                            cczip = f'<blockquote><b>⋅ ─ {t_name} ─ ⋅</b></blockquote>\n<b>{str(count).zfill(3)}.</b> {v_name} .zip'
                            ccimg = f'<blockquote><b>⋅ ─ {t_name} ─ ⋅</b></blockquote>\n<b>{str(count).zfill(3)}.</b> {v_name} .jpg'
                            ccm = f'<blockquote><b>⋅ ─ {t_name} ─ ⋅</b></blockquote>\n<b>{str(count).zfill(3)}.</b> {v_name} .mp3'
                            cchtml = f'<blockquote><b>⋅ ─ {t_name} ─ ⋅</b></blockquote>\n<b>{str(count).zfill(3)}.</b> {v_name} .html'
                    else:
                        if caption == "/cc1":
                            cc = f'[🎥]Vid Id : {str(count).zfill(3)}\n**Video Title :** `{name1} [{res}p].mkv`\n<blockquote><b>Batch Name :</b> {b_name}</blockquote>\n\n**Extracted by➤**{CR}\n'
                            cc1 = f'[📕]Pdf Id : {str(count).zfill(3)}\n**File Title :** `{name1}.pdf`\n<blockquote><b>Batch Name :</b> {b_name}</blockquote>\n\n**Extracted by➤**{CR}\n'
                            cczip = f'[📁]Zip Id : {str(count).zfill(3)}\n**Zip Title :** `{name1}.zip`\n<blockquote><b>Batch Name :</b> {b_name}</blockquote>\n\n**Extracted by➤**{CR}\n' 
                            ccimg = f'[🖼️]Img Id : {str(count).zfill(3)}\n**Img Title :** `{name1}.jpg`\n<blockquote><b>Batch Name :</b> {b_name}</blockquote>\n\n**Extracted by➤**{CR}\n'
                            ccm = f'[🎵]Audio Id : {str(count).zfill(3)}\n**Audio Title :** `{name1}.mp3`\n<blockquote><b>Batch Name :</b> {b_name}</blockquote>\n\n**Extracted by➤**{CR}\n'
                            cchtml = f'[🌐]Html Id : {str(count).zfill(3)}\n**Html Title :** `{name1}.html`\n<blockquote><b>Batch Name :</b> {b_name}</blockquote>\n\n**Extracted by➤**{CR}\n'
                        elif caption == "/cc2":
                            cc = f"——— ✦ {str(count).zfill(3)} ✦ ———\n\n<b>🎞️ Title :</b> {name1}\n<b>├── Extention :  {CR} .mkv</b>\n<b>├── Resolution : [{res}]</b>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By : {CR}**"
                            cc1 = f"——— ✦ {str(count).zfill(3)} ✦ ———\n\n<b>📁 Title :</b> {name1}\n<b>├── Extention :  {CR} .pdf</b>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By : {CR}**"
                            cczip = f"——— ✦ {str(count).zfill(3)} ✦ ———\n\n<b>📒 Title :</b> {name1}\n<b>├── Extention :  {CR} .zip</b>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By : {CR}**"
                            ccimg = f"——— ✦ {str(count).zfill(3)} ✦ ———\n\n<b>🖼️ Title :</b> {name1}\n<b>├── Extention :  {CR} .jpg</b>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By : {CR}**"
                            ccm = f"——— ✦ {str(count).zfill(3)} ✦ ———\n\n<b>🎵 Title :</b> {name1}\n<b>├── Extention :  {CR} .mp3</b>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By : {CR}**"
                            cchtml = f"——— ✦ {str(count).zfill(3)} ✦ ———\n\n<b>🌐 Title :</b> {name1}\n<b>├── Extention :  {CR} .html</b>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By : {CR}**"
                        else:
                            cc = f'<b>{str(count).zfill(3)}.</b> {name1} [{res}p] .mkv'
                            cc1 = f'<b>{str(count).zfill(3)}.</b> {name1} .pdf'
                            cczip = f'<b>{str(count).zfill(3)}.</b> {name1} .zip'
                            ccimg = f'<b>{str(count).zfill(3)}.</b> {name1} .jpg'
                            ccm = f'<b>{str(count).zfill(3)}.</b> {name1} .mp3'
                            cchtml = f'<b>{str(count).zfill(3)}.</b> {name1} .html'
#........................................................................................................................................................................................
                remaining_links = len(links) - count
                progress = (count / len(links)) * 100
                Show = f"<i><b>Video Downloading</b></i>\n<blockquote><b>{str(count).zfill(3)}) {name1}</b></blockquote>" 
                Show1 = f"<blockquote>🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {progress:.2f}%</blockquote>\n┃\n" \
                        f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{len(links)}\n┃\n" \
                        f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 » {remaining_links}\n" \
                        f"━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                        f"<blockquote><b>⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳</b></blockquote>\n┃\n" \
                        f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                        f"╰━📚𝐁𝐚𝐭𝐜𝐡 » {b_name}\n" \
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                        f"<blockquote>📚𝐓𝐢𝐭𝐥𝐞 » {namef}</blockquote>\n┃\n" \
                        f"┣🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {quality}\n┃\n" \
                        f'┣━🔗𝐋𝐢𝐧𝐤 » <a href="{link0}">**Original Link**</a>\n┃\n' \
                        f'╰━━🖇️𝐔𝐫𝐥 » <a href="{url}">**Api Link**</a>\n' \
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                        f"🛑**Send** /stop **to stop process**\n┃\n" \
                        f"╰━✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
#........................................................................................................................................................................................           
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=channel_id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    
  
                elif "pdf" in url:
                    if "cwmediabkt99" in url:
                        max_retries = 15  # Define the maximum number of retries
                        retry_delay = 4  # Delay between retries in seconds
                        success = False  # To track whether the download was successful
                        failure_msgs = []  # To keep track of failure messages
                        
                        for attempt in range(max_retries):
                            try:
                                await asyncio.sleep(retry_delay)
                                url = url.replace(" ", "%20")
                                scraper = cloudscraper.create_scraper()
                                response = scraper.get(url)

                                if response.status_code == 200:
                                    with open(f'{namef}.pdf', 'wb') as file:
                                        file.write(response.content)
                                    await asyncio.sleep(retry_delay)  # Optional, to prevent spamming
                                    copy = await bot.send_document(chat_id=channel_id, document=f'{namef}.pdf', caption=cc1)
                                    count += 1
                                    os.remove(f'{namef}.pdf')
                                    success = True
                                    break  # Exit the retry loop if successful
                                else:
                                    failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {response.status_code} {response.reason}")
                                    failure_msgs.append(failure_msg)
                                    
                            except Exception as e:
                                failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                                failure_msgs.append(failure_msg)
                                await asyncio.sleep(retry_delay)
                                continue 
                        for msg in failure_msgs:
                            await msg.delete()
                            
                    else:
                        try:
                            cmd = f'yt-dlp -o "{namef}.pdf" "{url}"'
                            download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                            os.system(download_cmd)
                            copy = await bot.send_document(chat_id=channel_id, document=f'{namef}.pdf', caption=cc1)
                            count += 1
                            os.remove(f'{namef}.pdf')
                        except FloodWait as e:
                            await m.reply_text(str(e))
                            time.sleep(e.x)
                            continue    
           
                elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{namef}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_photo(chat_id=channel_id, photo=f'{namef}.{ext}', caption=ccimg)
                        count += 1
                        os.remove(f'{namef}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    

                elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{namef}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=channel_id, document=f'{namef}.{ext}', caption=ccm)
                        count += 1
                        os.remove(f'{namef}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    
                    
                elif 'encrypted.m' in url:    
                    prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                    prog1 = await m.reply_text(Show1, disable_web_page_preview=True)
                    res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)  
                    filename = res_file  
                    await prog1.delete(True)
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, vidwatermark, thumb, name, prog, channel_id)
                    count += 1  
                    await asyncio.sleep(1)  
                    continue  

                elif ('drmcdni' in url or 'drm/wv' in url or 'drm/common' in url or 
                      (keys_string and "classplusapp" in link0) or '/drm/' in url):
                    prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                    prog1 = await m.reply_text(Show1, disable_web_page_preview=True)
                    res_file = await helper.decrypt_and_merge_video(url, keys_string, path, name, raw_text2)
                    filename = res_file
                    await prog1.delete(True)
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, vidwatermark, thumb, name, prog, channel_id)
                    count += 1
                    await asyncio.sleep(1)
                    continue
     
                else:
                    prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                    prog1 = await m.reply_text(Show1, disable_web_page_preview=True)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog1.delete(True)
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, vidwatermark, thumb, name, prog, channel_id)
                    count += 1
                    time.sleep(1)
                
            except Exception as e:
                await bot.send_message(channel_id, f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {url}\n\n<blockquote expandable><i><b>Failed Reason: {str(e)}</b></i></blockquote>', disable_web_page_preview=True)
                count += 1
                failed_count += 1
                continue

    except Exception as e:
        await m.reply_text(e)
        time.sleep(2)

    success_count = len(links) - failed_count
    video_count = v2_count + mpd_count + m3u8_count + yt_count + drm_count + zip_count + other_count
    if m.document:
        await bot.send_message(channel_id, f"<b>-┈━═.•°✅ Completed ✅°•.═━┈-</b>\n<blockquote><b>🎯Batch Name : {b_name}</b></blockquote>\n<blockquote>🔗 Total URLs: {len(links)} \n┃   ┠🔴 Total Failed URLs: {failed_count}\n┃   ┠🟢 Total Successful URLs: {success_count}\n┃   ┃   ┠🎥 Total Video URLs: {video_count}\n┃   ┃   ┠📄 Total PDF URLs: {pdf_count}\n┃   ┃   ┠📸 Total IMAGE URLs: {img_count}</blockquote>\n")
        if "/d" not in raw_text7:
            await bot.send_message(m.chat.id, f"<blockquote><b>✅ Your Task is completed, please check your Set Channel📱</b></blockquote>")

#============================================================================================================
def register_drm_handlers(bot):
    @bot.on_message(filters.private & (filters.document | filters.text))
    async def call_drm_handler(bot: Client, m: Message):
        await drm_handler(bot, m)
