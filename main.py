from alive_progress import alive_bar
import simplejson as json
import requests
import ffmpeg
import time
import os
import re


def validateTitle(title):
    string = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(string, "_", title)
    return new_title


def mergeAudioVideo(mp4_file, mp3_file, output_file):
    try:
        (
            ffmpeg.input(mp4_file)
            .output(ffmpeg.input(mp3_file), output_file, vcodec="copy", acodec="copy")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(f"合并失败: {e.stderr.decode('utf8')}")
        raise Exception("合并失败")


url = input("请输入视频地址：")
cookie = input("请输入Cookie：")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 "
    "Safari/537.36 Edg/126.0.0.0",
    "Referer": "https://www.bilibili.com/",
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
ep_list = my_json["index"]["epList"]
headers["Cookie"] = cookie.encode("utf_8").decode("latin1")
play_url = "https://api.bilibili.com/pugv/player/web/playurl?avid=%s&cid=%s&qn=0&fnver=0&fnval=16&fourk=1&gaia_source=&from_client=BROWSER&is_main_page=true&need_fragment=false&season_id=19591&isGaiaAvoided=false&ep_id=%s&session=ed1c4795e01bf762f6d1dbefc27379ef&voice_balance=1&drm_tech_type=2"
count = 1
title = my_json["index"]["viewInfo"]["title"]
orign_title = title
title = validateTitle(title)
tmp = 1
tmp_str = title
while os.path.exists(tmp_str):
    tmp_str = title + "（" + str(tmp) + "）"
    tmp += 1
title = validateTitle(tmp_str)
os.mkdir(title)
os.chdir(title)
print("发现课程：" + orign_title)
print("共检测到" + str(len(ep_list)) + "集视频")
for ep in ep_list:
    print(f"\n正在下载第{count}集: {ep['title']}")

    try:
        ep_url = play_url % (ep["aid"], ep["cid"], ep["id"])
        ep_json = requests.get(ep_url, headers=headers).json()
        v_url = ep_json["data"]["dash"]["video"][0]["base_url"]
        a_url = ep_json["data"]["dash"]["audio"][0]["base_url"]

        with alive_bar(1, title="下载视频") as video_bar:
            v_content = requests.get(v_url, headers=headers, timeout=120).content
            with open(f"{count}.mp4", "wb") as f:
                f.write(v_content)
            video_bar()

        with alive_bar(1, title="下载音频") as audio_bar:
            a_content = requests.get(a_url, headers=headers, timeout=120).content
            with open(f"{count}.mp3", "wb") as f:
                f.write(a_content)
            audio_bar()

        with alive_bar(1, title="合并音视频") as merge_bar:
            try:
                mp4_file = f"{count}.mp4"
                mp3_file = f"{count}.mp3"
                output_file = f"{count}.{validateTitle(ep['title'])}.mp4"
                mergeAudioVideo(mp4_file, mp3_file, output_file)
                os.remove(mp4_file)
                os.remove(mp3_file)
                merge_bar()
            except Exception as e:
                print(e)
                print(f"第{count}集合并失败")
                count += 1
                continue
        count += 1
    except Exception as e:
        print(e)
        if e.args[0] == "dash":
            print(f"第{count}集下载失败，可能是无效的Cookie或课程未购买")
            exit()
        if e.args[0] == "data":
            print(f"第{count}集尚未更新")
            exit()
        print(f"第{count}集下载失败")
        count += 1
        continue

print("下载完成")
