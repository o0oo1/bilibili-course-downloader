# bilibili-course-downloader

BiliBili 课堂视频下载器

# 预置条件

课程已购买

## 依赖组件

- Python 环境
- alive_progress
- simplejson
- requests
- ffmpeg-python

```shell
yes | python3 -m pip uninstall ffmpeg python-ffmpeg
yes | python3 -m pip install alive_progress simplejson requests ffmpeg-python
```

## 使用方法

运行 main.py，输入课程网页播放链接和 Cookie，视频下载到 main.py 同级目录。
