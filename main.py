import requests
import time
import json
import os
import re

def validateTitle(title):
    string = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(string, "_", title)
    return new_title

url = input("请输入视频地址：")
cookie = input("请输入cookie：")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 "
                  "Safari/537.36 Edg/126.0.0.0",
    "Referer": "https://www.bilibili.com/"
}
key = "window.__EduPlayPiniaState__"
html_str = ""
start = -1
count = 0
while True:
    html_str = requests.get(url, headers=headers).text
    start = html_str.find(key)
    if start > 0:
        start += len(key) + 2
        break
    else:
        count += 1
        if count > 15:
            print("未找到播放信息，请稍后再试")
            exit()
        time.sleep(1)
end = html_str.find("</script>", start) - 1
json_str = html_str[start:end]
my_json = json.loads(json_str.replace("\\", ""))
ep_list = my_json['index']['epList']
headers["Cookie"] = cookie
play_url = "https://api.bilibili.com/pugv/player/web/playurl?avid=%s&cid=%s&qn=0&fnver=0&fnval=16&fourk=1&gaia_source=&from_client=BROWSER&is_main_page=true&need_fragment=false&season_id=19591&isGaiaAvoided=false&ep_id=%s&session=ed1c4795e01bf762f6d1dbefc27379ef&voice_balance=1&drm_tech_type=2"
count = 1
title = my_json['index']['viewInfo']['title']
tmp = 1
tmp_str = title
while os.path.exists(tmp_str):
    tmp_str = title + "（" + str(tmp) + "）"
    tmp += 1
title = tmp_str
os.mkdir(title)
os.chdir(title)
print("检测到" + str(len(ep_list)) + "集视频")
for ep in ep_list:
    print('正在下载第' + str(count) + '集')
    try:
        ep_url = play_url % (ep['aid'], ep['cid'], ep['id'])
        ep_json = requests.get(ep_url, headers=headers).json()
        v_url = ep_json['data']['dash']['video'][0]['base_url']
        v_content = requests.get(v_url, headers=headers, timeout=120).content
        with open(str(count) + ".mp4", "wb") as f:
            f.write(v_content)
        a_url = ep_json['data']['dash']['audio'][0]['base_url']
        a_content = requests.get(a_url, headers=headers, timeout=120).content
        with open(str(count) + ".mp3", "wb") as f:
            f.write(a_content)
    except Exception as e:
        print(e)
        if e.args[0] == 'dash':
            print("第" + str(count) + "集下载失败，可能是无效的Cookie或课程未购买")
            exit()
        if e.args[0] == 'data':
            print("第" + str(count) + "集尚未更新")
            exit()
        print("第" + str(count) + "集下载失败")
        count += 1
        continue
    try:
        cmd = "..\\ffmpeg.exe -i " + str(count) + ".mp4 -i " + str(count) + ".mp3 -vcodec copy -acodec copy \"" + str(count) + "." + validateTitle(ep['title']) + ".mp4\" 1>nul 2>nul"
        result = os.system(cmd)
        if result != 0:
            raise Exception("合并失败")
    except Exception as e:
        print("第" + str(count) + "集合并失败")
        count += 1
        continue
    os.remove(str(count) + ".mp4")
    os.remove(str(count) + ".mp3")
    count += 1
print("下载完成")