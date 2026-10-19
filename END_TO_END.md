# 视频到核验版 PDF：实际运行说明

本次使用 B 站课程 `BV1kybV6DE47`，按“完整媒体采集 → 本地音频转录 → 画面筛选 → Agent 重写讲义 → 主题和出处核验 → PDF 生成与逐页检查 → GitHub 发布”执行。

## 哪些部分已经自动化

`acquire_video.py` 使用 yt-dlp 采集选定单讲，保存视频和音轨，使用 PyAV 核对时长，并记录 SHA-256。FFmpeg 来自 imageio-ffmpeg，不再要求先在系统中安装 ffprobe。它每 15 秒提取一张候选帧。

`transcribe_sensevoice.py` 在本地用 SenseVoice 处理完整音轨，每 20 秒一个真实输入窗口，输出 SRT、索引文本、原始识别记录与转录报告。窗口级时间戳用于定位片段，不能被宣传为逐字准确的字幕。

`verify_source.py` 核对媒体、完整时间范围、图像哈希、配图出处、讲义版本与主题覆盖审查。它读取已完成的审阅记录，不会自动把“模型写了一段话”判作正确。

`run_lecture.py` 串联上述采集、转录、检查与 PDF 导出，并支持从已经完成的阶段继续。缺少正文或语义审查记录时会停止并说明下一步，不生成一个假装核验通过的成品。

## 为什么正文仍由 Agent 编写和审查

用户要求的是可独立学习的讲义。它需要判断教学主线、把相邻解释组合起来、区别讲师观点与参考补充，还要确认截图能支持图注。当前会话中的 Agent 完成这一步，`TASK.md` 是复用的执行任务书。

脚本的自动检查和 Agent 的语义审查共同构成这条流程；本项目没有伪造一个无需模型调用、仅凭脚本就能理解任意课程的“一键写作器”。处理新课时需要让 Agent 接手写作和审阅阶段。

## 本地复现

推荐 Python 3.12。先按 [LATEX.md](LATEX.md) 安装 Pandoc 和 Tectonic；PDF 已默认使用 LaTeX。在仓库根目录准备依赖与模型：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-latex.txt -r requirements-video.txt
.\.venv\Scripts\python.exe download_sensevoice.py work/models
```

采集和转录：

```powershell
.\.venv\Scripts\python.exe acquire_video.py 'https://www.bilibili.com/video/BV1kybV6DE47/?p=1' work/nju-gse-03-verified
.\.venv\Scripts\python.exe transcribe_sensevoice.py work/nju-gse-03-verified/audio.m4a work/nju-gse-03-verified work/models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17
```

音轨扩展名以采集结果为准。本例为 `audio.m4a`；其他平台可能是 WebM 等格式。

让 Agent 依据 TASK.md 阅读时间轴、检查候选帧、编写讲义及审查记录。`prepare_evidence.py` 中的选帧和分栏只适用于本节课程，**处理新视频必须重新选择帧并测量裁剪区域**。

本节课在审阅记录齐备后，可以执行统一入口：

```powershell
.\.venv\Scripts\python.exe run_lecture.py 'https://www.bilibili.com/video/BV1kybV6DE47/?p=1' --workdir work/nju-gse-03-verified --notes notes/software-repository-management.md --evidence evidence --output output/pdf/software-repository-management.pdf --modeldir work/models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17
```

如下载器能够读取本机浏览器登录态，可通过采集入口的 `--browser chrome` 等选项请求字幕。本次完整流程使用未登录下载器可取得的公开视频和音轨，并在本地转录，未导出内嵌浏览器 Cookies。

## 核验与发布边界

原视频媒体全部下载、转录窗口处理到音轨末尾，与“每一字都人工听写”和“每一帧都人工检查”是不同要求。本次按每 5 分钟窗口抽查转录内容并核对章节覆盖；12 张配图逐张打开检查，同时参考候选帧缩略图定位演示。

自动识别的英语术语可能不准确，讲义统一术语时结合原画面、官方讲义和公开整理稿。讲师的模型体验被保留为个人观察，“快一千倍”保留为思想实验，未当作测量结果。

GitHub 的 PDF Actions 负责从仓库中已完成的 Markdown 与配图重新生成 PDF，不会在每次提交时重新下载 100 分钟的视频或重新运行写作模型。源媒体核验记录另见 [evidence/README.md](evidence/README.md)。
