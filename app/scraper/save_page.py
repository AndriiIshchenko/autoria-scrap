import requests

URL = "https://auto.ria.com/uk/auto_volkswagen_tiguan_38285805.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/114.0.0.0 Safari/537.36"
}

response = requests.get(URL, headers=HEADERS)

if response.status_code == 200:
    with open("auto_ria_tiguan.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Page saved")
else:
    print(f"Failed to fetch page: {response.status_code}")
