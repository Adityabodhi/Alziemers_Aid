import requests
import os

os.makedirs("fonts", exist_ok=True)
url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"

print(f"Downloading font from {url}...")
try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        with open("fonts/noto.ttf", "wb") as f:
            f.write(response.content)
        print("Font downloaded successfully: fonts/noto.ttf")
    else:
        print(f"Failed to download. Status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
