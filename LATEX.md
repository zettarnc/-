# LaTeX 中文讲义排版

默认输出链已切换为 **Markdown → Pandoc → LaTeX（ctexart）→ Tectonic / XeLaTeX → PDF**。

正文采用开源 FandolSong 宋体，标题采用 FandolHei 黑体，西文正文采用 TeX Gyre Pagella。字体来自 TeX 字体包，不依赖 Windows 专有字体；本地和 GitHub 都使用相同字体配置。

## Windows 安装

安装 Python、[Pandoc](https://pandoc.org/installing.html) 和 [Tectonic 官方 Windows 版本](https://tectonic-typesetting.github.io/book/latest/installation/)，将两个可执行文件加入 PATH。也可以将 `tectonic.exe`、`pandoc.exe` 放在仓库的 `.latex-tools/` 目录中。Tectonic 首次运行会联网下载 TeX 宏包和字体。

```powershell
python -m pip install -r requirements-latex.txt
python verify_published.py
python build_latex.py notes/software-repository-management.md output/pdf/software-repository-management.pdf
```

也可以用 `build_pdf.ps1 -Python python`。已经安装 TeX Live 或 MiKTeX 的机器可传入 `--engine xelatex`（PowerShell 入口为 `-Engine xelatex`），所需包包括 ctex、Fandol、fontspec、xeCJK、fvextra 和 titling。

## Linux / GitHub

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends pandoc texlive-xetex texlive-lang-chinese texlive-latex-extra texlive-fonts-recommended tex-gyre lmodern fonts-texgyre fonts-texgyre-math fonts-lmodern
python -m pip install -r requirements-latex.txt
python verify_published.py
python build_latex.py notes/software-repository-management.md output/pdf/software-repository-management.pdf --engine xelatex
```

仓库 Actions 使用上述 XeLaTeX 路线，先检查已审阅的讲义、字幕与配图哈希，再生成 PDF、TeX 源码、编译日志和 JSON。更换字体与版式不会改动已经核验的 Markdown 正文。

## 版式与复核

`latex-header.tex` 控制 A4 页边距、11pt 字号、1.42 倍行距、标题层级与页眉页码；`latex-figures.lua` 把视频截图与出处说明放在同一个版面块中。

自动检查只确认编译、页数和可提取文字；JSON 中的 `visual_review` 默认是 pending，仍需将最终 PDF 渲染后逐页检查。媒体与内容核验范围见 [来源记录](evidence/README.md)。

旧 `md_to_pdf.py` 为 ReportLab 兼容实现，默认入口和 CI 已使用 LaTeX。这里接入的是本仓库的 LaTeX 导出，不声称执行了上游项目独有的校验脚本。
