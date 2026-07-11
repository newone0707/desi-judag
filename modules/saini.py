import os
import re
import time
import mmap
import datetime
import aiohttp
import aiofiles
import asyncio
import logging
import requests
import tgcrypto
import subprocess
import concurrent.futures
from math import ceil
from utils import progress_bar
from pyrogram import Client, filters
from pyrogram.types import Message
from io import BytesIO
from pathlib import Path  
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

# ------------------------------------------------------------
# ✅ NEW: Caption truncator (Telegram limit = 1024 chars)
# ------------------------------------------------------------
def truncate_caption(caption: str, max_len: int = 1000) -> str:
    """Safely truncate caption to max_len characters."""
    if caption is None:
        return ""
    if len(caption) <= max_len:
        return caption
    # Simple truncation – breaks HTML tags if any, but avoids API error
    return caption[:max_len-3] + "..."
# ------------------------------------------------------------

def duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

def get_mps_and_keys(api_url):
    response = requests.get(api_url)
    response_json = response.json()
    mpd = response_json.get('MPD')
    keys = response_json.get('KEYS')
    return mpd, keys
   
def exec(cmd):
        process = subprocess.run(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = process.stdout.decode()
        print(output)
        return output
        #err = process.stdout.decode()

def pull_run(work, cmds):
    with concurrent.futures.ThreadPoolExecutor(max_workers=work) as executor:
        print("Waiting for tasks to complete")
        fut = executor.map(exec,cmds)
        
async def aio(url,name):
    k = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(k, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return k


async def download(url,name):
    ka = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(ka, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return ka


def parse_vid_info(info):
    info = info.strip()
    info = info.split("\n")
    new_info = []
    temp = []
    for i in info:
        i = str(i)
        if "[" not in i and '---' not in i:
            while "  " in i:
                i = i.replace("  ", " ")
            i.strip()
            i = i.split("|")[0].split(" ",2)
            try:
                if "RESOLUTION" not in i[2] and i[2] not in temp and "audio" not in i[2]:
                    temp.append(i[2])
                    new_info.append((i[0], i[2]))
            except:
                pass
    return new_info

def vid_info(info):
    info = info.strip()
    info = info.split("\n")
    new_info = dict()
    temp = []
    for i in info:
        i = str(i)
        if "[" not in i and '---' not in i:
            while "  " in i:
                i = i.replace("  ", " ")
            i.strip()
            i = i.split("|")[0].split(" ",3)
            try:
                if "RESOLUTION" not in i[2] and i[2] not in temp and "audio" not in i[2]:
                    temp.append(i[2])
                    
                    # temp.update(f'{i[2]}')
                    # new_info.append((i[2], i[0]))
                    #  mp4,mkv etc ==== f"({i[1]})" 
                    
                    new_info.update({f'{i[2]}':f'{i[0]}'})

            except:
                pass
    return new_info


def get_keys_from_mp4(mp4_path, license_url, token, mpd_url=None):
    import subprocess
    import requests
    import re
    import base64
    from pywidevine.cdm import Cdm
    from pywidevine.device import Device
    from pywidevine.pssh import PSSH

    pssh_hex = None
    
    if mpd_url:
        try:
            manifest = requests.get(mpd_url).text
            match = re.search(r'<cenc:pssh[^>]*>([^<]+)</cenc:pssh>', manifest)
            if match:
                pssh_hex = base64.b64decode(match.group(1)).hex()
        except Exception:
            pass
            
    if not pssh_hex and mp4_path:
        result = subprocess.run(["mp4dump", mp4_path], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for i, line in enumerate(lines):
            if "[system id] = [ed ef 8b a9 79 d6 4a ce a3 c8 27 dc d5 1d 21 ed]" in line:
                for j in range(i+1, min(i+10, len(lines))):
                    if "[data] = " in lines[j]:
                        pssh_hex = lines[j].split("[data] = ")[1].replace("[", "").replace("]", "").replace(" ", "").strip()
                        break
                if pssh_hex:
                    break
    
    if not pssh_hex:
        print("No Widevine PSSH found in mp4 or mpd")
        return ""
    
    pssh_bytes = bytes.fromhex(pssh_hex)
    pssh_obj = PSSH(pssh_bytes)
    
    device_args = {
        "client_id": open("device_client_id_blob", "rb").read(),
        "private_key": open("device_private_key.txt", "rb").read()
    }
    
    try:
        from pywidevine.device import DeviceTypes
        device_args["type_"] = DeviceTypes.ANDROID
    except ImportError:
        device_args["type_"] = 2

    try:
        device = Device(**device_args, security_level=3, flags=None)
    except TypeError as e:
        print(f"Device init error: {e}")
        device_args.pop("type_", None)
        device = Device(**device_args, flags=None)
    cdm = Cdm.from_device(device)
    session_id = cdm.open()
    challenge = cdm.get_license_challenge(session_id, pssh_obj)
    
    headers = {
        'host': 'api.classplusapp.com',
        'x-access-token': token,
        'user-agent': 'Mobile-Android',
        'content-type': 'application/json'
    }
    r = requests.post(license_url, data=challenge, headers=headers)
    if r.status_code != 200:
        cdm.close(session_id)
        print(f"License API failed: {r.status_code} {r.text}")
        return ""
        
    cdm.parse_license(session_id, r.content)
    keys = []
    for key in cdm.get_keys(session_id):
        if key.type == 'CONTENT':
            keys.append(f"--key {key.kid.hex}:{key.key.hex()}")
    cdm.close(session_id)
    return " ".join(keys)


async def decrypt_and_merge_video(url, keys_string, path, name, raw_text2, license_url, cptoken):
    import subprocess
    import shutil
    import os
    from pathlib import Path
    import asyncio
    output_path = Path(path) / "downloads" / name
    output_path.mkdir(parents=True, exist_ok=True)
    output_name = name.split(".mp4")[0]

    cmd1 = f'yt-dlp -f "bv[height<=480]+ba/b" -o "{output_path}/file.%(ext)s" --allow-unplayable-format --no-check-certificate --external-downloader aria2c "{url}"'
    print(f"Running command: {cmd1}", flush=True)
    os.system(cmd1)

    avDir = list(output_path.glob("file.*"))
    print(f"Downloaded files: {avDir}", flush=True)

    if ("classplusapp" in url or license_url) and not keys_string:
        print("Extracting Widevine keys...", flush=True)
        for data in avDir:
            if data.suffix in [".mp4", ".m4a"]:
                try:
                    keys_string = get_keys_from_mp4(str(data), license_url, cptoken, mpd_url=url)
                    if keys_string:
                        print(f"Extracted keys: {keys_string}", flush=True)
                        break
                except Exception as e:
                    print(f"Failed to extract keys: {e}", flush=True)

    video_decrypted = False
    audio_decrypted = False

    for data in avDir:
        if data.suffix == ".mp4" and not video_decrypted:
            if keys_string:
                cmd2 = f'mp4decrypt {keys_string} --show-progress "{data}" "{output_path}/video.mp4"'
            else:
                cmd2 = f'cp "{data}" "{output_path}/video.mp4"'
            print(f"Running command: {cmd2}", flush=True)
            os.system(cmd2)
            if (output_path / "video.mp4").exists():
                video_decrypted = True
            data.unlink()
        elif data.suffix == ".m4a" and not audio_decrypted:
            if keys_string:
                cmd3 = f'mp4decrypt {keys_string} --show-progress "{data}" "{output_path}/audio.m4a"'
            else:
                cmd3 = f'cp "{data}" "{output_path}/audio.m4a"'
            print(f"Running command: {cmd3}", flush=True)
            os.system(cmd3)
            if (output_path / "audio.m4a").exists():
                audio_decrypted = True
            data.unlink()

    if not video_decrypted:
        raise FileNotFoundError("Decryption failed: video file not found.")

    if audio_decrypted:
        cmd4 = f'ffmpeg -i "{output_path}/video.mp4" -i "{output_path}/audio.m4a" -c copy "{output_path}/{output_name}.mp4"'
        print(f"Running command: {cmd4}", flush=True)
        os.system(cmd4)
        if (output_path / "video.mp4").exists():
            (output_path / "video.mp4").unlink()
        if (output_path / "audio.m4a").exists():
            (output_path / "audio.m4a").unlink()
    else:
        cmd4 = f'cp "{output_path}/video.mp4" "{output_path}/{output_name}.mp4"'
        print(f"Running command: {cmd4}", flush=True)
        os.system(cmd4)
        if (output_path / "video.mp4").exists():
            (output_path / "video.mp4").unlink()
            
    res_file = str(output_path / f"{output_name}.mp4")
    return res_file


