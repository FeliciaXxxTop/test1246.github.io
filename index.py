import asyncio
from aiohttp import ClientSession
import re
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import time
from discord_webhook import DiscordWebhook, DiscordEmbed
import requests
import json

app = Flask(__name__)

# Discord webhook URL for logging
WEBHOOK_URL = 'https://discord.com/api/webhooks/1243423826981945345/Je-jvTHii02JPxN6ei7jjPQN5MhGeKBKFGJYjc1rHZqAmIV50w-SfrUm0SpNZGzYBROs'

# Common cookie and header setup for bypass
commoncookie = 'Anti-Bypass=BypassersKHTTP_VERSION5069e4e61337c2fbea2368f9da1a07725f2a65bb1eab2d8de6dc9cf83e7a683e; .pipe=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiJLMGc4SjNsRmY1TW43UWw4bVh5bytpNnVBeGh4aWFSYTU2bldDZEcxQnlNPSIsImUiOjE2ODkyNTAyODEsImlzc3VlZCI6MTY4OTI0NjY4MS4zMzksInNhbHQiOiJzYWx0eSIsImNvbm5lY3RvciI6LTF9.tHnUGnosgCctAafGTgta4F1_1KQezhvdIATrj9YwQU0'

commonheader = {
    'Referer': 'https://work.ink/',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Cookie': commoncookie
}

# Function to send log to Discord webhook
def send_discord_log(url, response_json):
    webhook = DiscordWebhook(url=WEBHOOK_URL)
    embed = DiscordEmbed(title='API Request and Response', color=242424)
    embed.add_embed_field(name='URL Requested', value=url, inline=False)
    embed.add_embed_field(name='API Response', value=response_json, inline=False)
    webhook.add_embed(embed)
    response = webhook.execute()
    print(f'Discord webhook response: {response}')

# Function to fetch the URL content with headers
def fetch(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch URL: {url}. Error: {e}")

# Function to handle the banana bypass logic
def bypass_banana():
    try:
        response = fetch('https://banana-hub.xyz/getkey', commonheader)
        soup = BeautifulSoup(response, 'html.parser')
        url = soup.find('a')['href']

        res_key_url = fetch(url, commonheader)
        parsed = BeautifulSoup(res_key_url, 'html.parser')
        key_url = parsed.find('a')['href']

        key_pol = fetch(key_url, commonheader)
        soup = BeautifulSoup(key_pol, 'html.parser')
        script = soup.find(class_='box').text.strip()
        script = re.sub(r'\s+', ' ', script)  # Replace multiple whitespaces with a single space

        ambil_key = r'getgenv\(\)\.Key\s*=\s*"([^"]+)"'
        hasil_key = re.search(ambil_key, script)

        key = hasil_key.group(1) if hasil_key else None

        return key
    except Exception as e:
        raise Exception(f"Failed to bypass: {str(e)}")

# Function to handle the fluxus bypass logic
key_regex = r'let content = \("([^"]+)"\);'

def bypass_fluxus(url):
    try:
        hwid = url.split("HWID=")[-1]
        if not hwid:
            raise Exception("Invalid HWID in URL")

        start_time = time.time()
        endpoints = [
            {
                "url": f"https://flux.li/android/external/start.php?HWID={hwid}",
                "referer": ""
            },
            {
                "url": f"https://flux.li/android/external/check1.php?hash={hash}",
                "referer": "https://linkvertise.com"
            },
            {
                "url": f"https://flux.li/android/external/main.php?hash={hash}",
                "referer": "https://linkvertise.com"
            }
        ]

        for endpoint in endpoints:
            url = endpoint["url"]
            referer = endpoint["referer"]
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',  # Do Not Track Request Header
                'Connection': 'close',
                'Referer': referer,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x66) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
            response_text = fetch(url, headers)
            if endpoint == endpoints[-1]:  # End of the bypass
                match = re.search(key_regex, response_text)
                if match:
                    end_time = time.time()
                    time_taken = end_time - start_time
                    return match.group(1), time_taken
                else:
                    raise Exception("Failed to find content key")
    except Exception as e:
        raise Exception(f"Failed to bypass link. Error: {e}")

# Function to handle the Pastebin bypass logic
def bypass_pastebin(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://pastebin.com/'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

# Function to handle the Mediafire bypass logic
def bypass_mediafire(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            download_button = soup.find('a', {'id': 'downloadButton'})
            if download_button:
                direct_link = download_button.get('href')
                return direct_link
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f'Error: {e}')
        return None

# Function to create a paste on Pastebin
key = "PVhNDTLkAK9JEY_8YyBKHSMZ3Ke94Tsd"

def create_paste(text):
    try:
        if not text:
            return {'error': 'No text provided'}, 400
        paste_data = {
            'api_dev_key': key,
            'api_option': 'paste',
            'api_paste_code': text,
            'api_paste_private': 0,  # 0=public, 1=unlisted, 2=private
            'api_paste_name': 'New Paste',
            'api_paste_expire_date': 'N',
        }

        response = requests.post('https://pastebin.com/api/api_post.php', data=paste_data)
        if response.status_code == 200:
            response_data = {'result': response.text}
            send_discord_log('https://pastebin.com', jsonify(response_data).get_data(as_text=True))
            return response_data, 200
        else:
            error_message = {'error': 'Failed to create paste'}
            send_discord_log('https://pastebin.com', jsonify(error_message).get_data(as_text=True))
            return error_message, 500
    except Exception as e:
        error_message = {'error': f'Failed to create paste: {str(e)}'}
        send_discord_log('https://pastebin.com', jsonify(error_message).get_data(as_text=True))
        return error_message, 500

# Function to extract target URL for mboost
def mboost(url):
    try:
        response = requests.get(url)
        html_content = response.text
    except requests.RequestException as e:
        return str(e)

    targeturl_regex = r'"targeturl":\s*"(.*?)"'
    match = re.search(targeturl_regex, html_content, re.MULTILINE)

    if match and len(match.groups()) > 0:
        return match.group(1)
    else:
        return "Please try again later"

# Function to handle Delta bypass logic
API_KEY = "E99l9NOctud3vmu6bPne"
BASE_URL = "https://stickx.top/api-delta/"

def bypass_delta(url):
    hwid = url.split("id=")[-1]
    api_url = f"{BASE_URL}?hwid={hwid}&api_key={API_KEY}"

    start_time = time.time()
    response = requests.get(api_url)
    end_time = time.time()
    time_taken = end_time - start_time

    try:
        data = response.json()
        return {
            "key": data.get("key"),
            "time_taken": time_taken,
            "discord": "discord.gg/feliciaxxx"
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed To Bypass")
    except json.JSONDecodeError:
        raise Exception("Invalid JSON response")
    except Exception as e:
        raise Exception("An unexpected error occurred")

@app.route('/api/bypass', methods=['GET'])
def bypass():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is missing"}), 400

    try:
        if "banana-hub.xyz" in url:
            key = bypass_banana()
            response_json = jsonify({"key": key}).get_data(as_text=True)
            send_discord_log(url, response_json)
            return jsonify({"key": key})

        elif url.startswith("https://flux.li/android/external/start.php?HWID="):
            content, time_taken = bypass_fluxus(url)
            response_json = jsonify({"key": content, "time_taken": time_taken, "credit": "FeliciaXxx"}).get_data(as_text=True)
            send_discord_log(url, response_json)
            return jsonify({"key": content, "time_taken": time_taken, "credit": "FeliciaXxx"})

        elif "pastebin.com" in url:
            raw_url = url.replace('pastebin.com', 'pastebin.com/raw')
            content = bypass_pastebin(raw_url)
            if content:
                response_json = jsonify({"status": "success", "result": content}).get_data(as_text=True)
                send_discord_log(url, response_json)
                return jsonify({"status": "success", "result": content})
            else:
                error_message = "Failed to fetch content"
                send_discord_log(url, error_message)
                return jsonify({"status": "fail", "message": error_message}), 500

        elif "mediafire.com" in url:
            direct_link = bypass_mediafire(url)
            if direct_link:
                response_json = jsonify({"status": "success", "result": direct_link}).get_data(as_text=True)
                send_discord_log(url, response_json)
                return jsonify({"status": "success", "result": direct_link})
            else:
                error_message = "Failed to fetch direct link"
                send_discord_log(url, error_message)
                return jsonify({"status": "fail", "message": error_message}), 500

        elif "pastebin.com" in url:
            text = request.args.get('text')
            response_data, status_code = create_paste(text)
            return jsonify(response_data), status_code

        elif "mboost" in url:
            result = mboost(url)
            response_json = jsonify({"status": "success", "result": result}).get_data(as_text=True)
            send_discord_log(url, response_json)
            return jsonify({"result": result})

        elif url.startswith("https://gateway.platoboost.com/a/8?id="):
            data = bypass_delta(url)
            return jsonify(data)

        else:
            error_message = "Invalid URL or Unsupported Link!"
            send_discord_log(url, error_message)
            return jsonify({"error": error_message}), 400

    except Exception as e:
        error_message = str(e)
        send_discord_log(url, error_message)
        return jsonify({"error": error_message}), 500

@app.route("/")
def home():
    return jsonify({"message": "Invalid Endpoint"})
