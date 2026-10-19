# 自动讲义生成工作流

把课程视频整理为可以独立阅读、能回查来源的中文 Markdown 讲义，并按需生成 PDF。

**视频来源核验与 PDF 导出已接通。** [直接阅读图文核验版 PDF](software-repository-management.pdf)，或查看 [本地一键导出与 GitHub 自动构建](PDF.md)。

视频来源核验流程与复现命令见 [END_TO_END.md](END_TO_END.md)，本次原始窗口字幕、配图来源和审查范围见 [evidence/README.md](evidence/README.md)。

- [全流程操作手册](WORKFLOW.md)：环境准备、采集、编写、核验和上传。
- [Agent 执行任务书](TASK.md)：替换输入后交给编码 Agent 使用。
- [示例讲义：软件仓库管理](notes/software-repository-management.md)：根据完整原视频、本地转录、课堂画面与官方讲义整理。
- `prepare.ps1`：下载选定视频及字幕，提取候选画面；不会自动生成讲义。
- `validate_markdown.py`：检查 Markdown 交付的基本结构、链接与来源记录。

## 本次交付状态

| 项目 | 状态 |
| --- | --- |
| 参考网页与仓库 | 已阅读，脚本参数已静态核对 |
| 全流程文档、任务书、示例讲义 | 已编写 |
| 示例依据 | 完整原视频、本地窗口字幕、选定画面、官方讲义与公开整理稿 |
| 本地原视频下载、时间轴与画面核验 | 完整媒体、401 张候选帧、12 张原图审查；结果见 evidence/source-verification.json |
| PDF | 图文讲义由 ReportLab 导出；检查范围与结果见随附 JSON 记录 |
| 自动导出 | 提供 build_pdf.ps1、Python 转换器与 GitHub Actions；LaTeX 路线未部署 |
| GitHub 目标 | https://github.com/zettarnc/- ，上传结果以远端实际提交为准 |

`prepare.ps1` 是本项目新增的采集脚本，不是上游项目的一键生成入口。正文重组与语义核验需要具备读图能力的 Agent 或人工完成，下载成功不代表讲义可信。

## 参考与版本

- 展示页面：<https://blog.simona.plus/lecture-to-notes/>
- 上游项目：<https://github.com/ysyecust/lecture-to-notes>
- 本次核对的上游 commit：`880f11c53c3abf65d01a643d895e04e56344b06f`
- 原课程：蒋炎岩，南京大学《生成式软件工程》2026 年第 3 讲。
- 视频：<https://www.bilibili.com/video/BV1kybV6DE47/>

本项目文档是面向 Markdown 的流程改编，没有复制上游站点或安装上游 Skill。引用和改编的课程内容遵循原课程及字幕整理来源的 CC BY-NC 4.0 条件；参见示例讲义末尾的署名与许可说明。
