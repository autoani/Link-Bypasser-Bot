from base64 import standard_b64encode, standard_b64decode
import pytz
from datetime import datetime
import requests

def str_to_b64(__str: str) -> str:
    str_bytes = __str.encode('ascii')
    bytes_b64 = standard_b64encode(str_bytes)
    b64 = bytes_b64.decode('ascii')
    return b64

def b64_to_str(b64: str) -> str:
    bytes_b64 = b64.encode('ascii')
    bytes_str = standard_b64decode(bytes_b64)
    __str = bytes_str.decode('ascii')
    return __str

def get_current_time():
    tz = pytz.timezone('Asia/Kolkata')
    return int(datetime.now(tz).timestamp())

def get_readable_time(seconds):
    dt = datetime.fromtimestamp(int(seconds))
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def shorten_url(url):
    #site_url = f"https://atglinks.com/api?api=36b6661ad0b4ceeb21c980d665e8159e4e88d622&url={url}&format=text"
    site_url = f"{url}"
    #return str(requests.get(site_url).text)
    return site_url
