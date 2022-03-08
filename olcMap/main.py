
# https://www.onlinecontest.org/olc-3.0/gliding/finder.html?aa=&cc=&sedte=-1&filter=&st=olc&sdt=2022-02-08&sedts=-1&mp=0&edt=2022-02-21&pi=&ap=&c=TS&sc=

# class div
# "smallmap"



import requests
from bs4 import BeautifulSoup


date_min = "2022-02-10"
date_max = "2022-02-21"

url = "https://www.onlinecontest.org/olc-3.0/gliding/finder.html?aa=&cc=&sedte=-1&filter=&st=olc&sdt={}&sedts=-1&mp=0&edt={}&pi=&ap=&c=TS&sc=".format(date_min, date_max)
print(url)
html_content = requests.get(url).text

soup = BeautifulSoup(html_content, "html.parser")


addr_list = soup.find_all("td", attrs={"class": "notwrappable"})
print(addr_list)
ids = set()
for s in addr_list:
    _, ex = str(s).split("dsId")
    ids.add(ex[1:8])

print(ids)

download_addr = set()

for id in ids:
    download_url = "https://www.onlinecontest.org/olc-3.0/gliding/flightinfo.html?dsId={}".format(id)
    html_content = requests.get(download_url).text

    soup = BeautifulSoup(html_content, "html.parser")

    btn = soup.find_all("div", attrs={"class": "btn-group"})

    for txt in btn:
        if "download.html?flightId" in str(txt):

            _, t, *_ = str(txt).split("download.html?flightId=")
            t, *_ = t.split("&")
            href = "https://www.onlinecontest.org/olc-3.0/gliding/download.html?flightId=" + t

            download_addr.add(href)
            print(href)


payload = {
    'Username': 'TH40X',
    'Password': 'Megawack3'
}

with requests.Session() as s:
    p = s.post("https://www.onlinecontest.org/olc-3.0/secure/login.html", data=payload)
