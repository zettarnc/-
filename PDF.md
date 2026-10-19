# 中文 PDF：LaTeX 默认路线

本项目默认使用 Markdown → Pandoc → LaTeX（ctexart）→ PDF。本地引擎为 Tectonic，GitHub Actions 引擎为 XeLaTeX，均使用开源 Fandol 宋体正文、黑体标题与 TeX Gyre Pagella 西文正文。

## 本次成品

- [第二讲：提示词与上下文工程（15 页）](prompt-context-engineering.pdf)
- [第二讲 TeX 源码](prompt-context-engineering.tex) · [检查记录](prompt-context-engineering.verification.json)
- [第三讲：软件仓库管理（14 页）](software-repository-management.pdf)
- [编译与检查记录](software-repository-management.verification.json)
- [讲义 Markdown](notes/software-repository-management.md)
- [LaTeX 环境、字体与复现命令](LATEX.md)

第二讲保留 14 张视频原图，第三讲保留 12 张，均给出可回查的时间段。原视频、完整音轨转录与主题审查见 [来源记录](evidence/README.md)，与排版引擎无关。

## 本地与云端

安装步骤见 LATEX.md，然后运行：

```powershell
python build_latex.py notes/software-repository-management.md output/pdf/software-repository-management.pdf
```

也可以执行 build_pdf.ps1。GitHub Actions 自动安装 Pandoc 与 XeLaTeX，检查来源哈希后导出 PDF、TeX 源码、编译日志和 JSON，可在 Actions 的 lecture-pdfs 产物中下载。

仓库根目录 PDF 是本次逐页审阅的成品。后续重建的 JSON 将 visual_review 设为 pending，避免把编译通过误当作人工版式检查通过。

本仓库接入 LaTeX 排版，未执行或冒充上游项目独有的生产门禁。旧 ReportLab 转换器保留为兼容实现，默认入口与 CI 已改用 LaTeX。
