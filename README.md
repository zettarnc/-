# 自动讲义生成工作流

把课程视频整理为可以独立阅读、能回查来源的中文 Markdown 讲义，并按需生成 PDF。

- [全流程操作手册](WORKFLOW.md)：环境准备、采集、编写、核验和上传。
- [Agent 执行任务书](TASK.md)：替换输入后交给编码 Agent 使用。
- [示例讲义：软件仓库管理](notes/software-repository-management.md)：根据本次课程的公开字幕整理稿和官方讲义编写。
- `prepare.ps1`：下载选定视频及字幕，提取候选画面；不会自动生成讲义。
- `validate_markdown.py`：检查 Markdown 交付的基本结构、链接与来源记录。

## 本次交付状态

| 项目 | 状态 |
| --- | --- |
| 参考网页与仓库 | 已阅读，脚本参数已静态核对 |
| 全流程文档、任务书、示例讲义 | 已编写 |
| 示例依据 | 公开字幕整理稿及官方讲义；字幕尚未完成人工校对 |
| 本地原视频下载、完整时间轴字幕和画面核验 | 尚未完成，不能视为已跑通视频流水线 |
| LaTeX / PDF | 本次未生成 |
| GitHub 目标 | https://github.com/zettarnc/- ，上传结果以远端实际提交为准 |

`prepare.ps1` 是本项目新增的采集脚本，不是上游项目的一键生成入口。正文重组与语义核验需要具备读图能力的 Agent 或人工完成，下载成功不代表讲义可信。

## 参考与版本

- 展示页面：<https://blog.simona.plus/lecture-to-notes/>
- 上游项目：<https://github.com/ysyecust/lecture-to-notes>
- 本次核对的上游 commit：`880f11c53c3abf65d01a643d895e04e56344b06f`
- 原课程：蒋炎岩，南京大学《生成式软件工程》2026 年第 3 讲。
- 视频：<https://www.bilibili.com/video/BV1kybV6DE47/>

本项目文档是面向 Markdown 的流程改编，没有复制上游站点或安装上游 Skill。引用和改编的课程内容遵循原课程及字幕整理来源的 CC BY-NC 4.0 条件；参见示例讲义末尾的署名与许可说明。
