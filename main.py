# -*- coding=utf-8 -*-
from bs4 import BeautifulSoup
from xpinyin import Pinyin
import requests
import json
from tqdm import tqdm
from urllib import parse
import re

p = Pinyin()

f = open("wiki.html", 'rb')
soup = BeautifulSoup(f, 'lxml')
f.close()
tables = soup.find_all("table", class_="data-table")

li = {}

def get_data(text):
    js = json.loads(requests.get(f"https://mcid.ipacel.cc/api.list/?l=zh_cn&q=" + parse.quote(text)).text)
    try:
        return js['list'][0]['key'], js['list'][0]['id'], js['list'][0]['type'], js['list'][0]['VerMax'], js['list'][0][
            'VerMin']
    except Exception:
        return 'none', 0, 'none', 'none', 'none'


trs = []
for t in tables:
    tr = t.find_next('tbody').find_all("tr")
    for i in tr:
        trs.append(i)

for t in range(1):
    for tr in tqdm(trs):
        try:
            if tr.find_next("span")['style']:
                tr.find_all_next('td')

                if tr.find_next("span")['class'][1].rstrip('-spirit') not in li:
                    li[tr.find_next("span")['class'][1].rstrip('-spirit')] = []
                apy = p.get_pinyin(tr.find_all_next('td')[2].text, '')
                ipy = p.get_initials(tr.find_all_next('td')[2].text, '')

                key, uid, utype, verMax, verMin = get_data(tr.find_all_next('td')[2].text)

                li[tr.find_next("span")['class'][1].rstrip('-spirit')].append({
                    "name_en": tr.find_all_next('td')[1].text,
                    "name_zh": tr.find_all_next('td')[2].text,
                    "name_cn": apy,
                    "name_cn_initials": ipy,
                    "spirit": tr.find_next("span")['class'][1].rstrip('-spirit'),
                    "position": tr.find_next("span")['style'].lstrip('background-position:'),
                    'key': key,
                    'id': uid,
                    'type': utype,
                    'verMax': verMax,
                    'verMin': verMin
                })
                print(tr.find_all_next('td')[2].text, apy, key)
        except KeyError as e:
            print('error', e)

# ========= get effect ==========
url = "https://minecraft.fandom.com/zh/wiki/%E7%8A%B6%E6%80%81%E6%95%88%E6%9E%9C#%E5%85%8D%E7%96%AB%E7%8A%B6%E6%80%81%E6%95%88%E6%9E%9C"
soup = BeautifulSoup(requests.get(url).text, 'lxml')
p = Pinyin()

li['effect-sprite'] = []
for tr in soup.find_all('table')[6].find_all_next('tr'):
    try:
        tds = tr.find_all_next('td')
        in_td = tds[0]
        code_td = tds[1]
        id_td = tds[2]

        image_url = in_td.find_next('span', class_='sprite')['style']
        image = re.match(r".*;background-position:(.*);height:.*", image_url).group(1)
        name = in_td.find_next('span', class_='sprite-text').text
        code = code_td.text.rstrip('\n')
        uid = id_td.text.lstrip(' ').rstrip('\n')
        print(name, code, uid, image)
        apy = p.get_pinyin(name, '')
        ipy = p.get_initials(name, '')
        li['effect-sprite'].append(
            {
                "name": name,
                "code": code,
                "id": uid,
                "position": image,
                "name_cn": apy,
                "name_cn_initials": ipy,
            }
        )
    except Exception as e:
        pass

# ========= get enchant ==========
url = 'https://minecraft.fandom.com/zh/wiki/%E9%99%84%E9%AD%94'
soup = BeautifulSoup(requests.get(url).text, 'lxml')
trs_ = None
p = Pinyin()
for i in soup.find_all('table'):
    if i['data-description'] == '魔咒概述':
        trs_ = i

li['enchant-sprite'] = []
trs = trs_.find_all_next('tr')
for tr in trs:
    try:
        tds = tr.find_all_next('td')
        name = tds[0].find_next('a').text.rstrip('\n')
        code = tds[1].find_next('code').text
        uid = tds[2].text.rstrip('\n')
        print(name, code, uid)
        apy = p.get_pinyin(name, '')
        ipy = p.get_initials(name, '')
        li['enchant-sprite'].append({'name': name, "code": code, "id": uid, "name_cn": apy, "name_cn_initials": ipy})
        if name == "耐久": break
    except Exception as e:
        pass

with open('index.bak', "w") as f:
    f.write(json.dumps(li).encode('utf-8').decode('unicode-escape'))
