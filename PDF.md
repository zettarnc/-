# PDF 生成：已接通的路径

本项目现在支持 Markdown → 中文 PDF，不需要安装 LaTeX。它与上游 LaTeX 生产流程是两条不同的输出路径，不执行或冒充上游的 PDF 门禁。

## 查看本次成品

- [《软件仓库管理》PDF](software-repository-management.pdf)
- [生成与检查记录](software-repository-management.verification.json)
- [讲义 Markdown](notes/software-repository-management.md)

本次更新为带 12 张视频原图的讲义，中文可搜索；最终页数和 PDF 检查结果见随附 JSON。原视频完整采集、窗口转录及主题覆盖审查结果另见 evidence/source-verification.json，它们与 PDF 格式检查是独立的检查项。

仓库根目录提供本次核验后的成品；本地脚本和 Actions 后续生成的文件位于 `output/pdf/`。

## Windows 本地一键导出

在仓库目录首次准备依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-pdf.txt
```

随后运行：

```powershell
.\build_pdf.ps1 -Python .\.venv\Scripts\python.exe
```

转换其他讲义时指定文件：

```powershell
.\build_pdf.ps1 -Python .\.venv\Scripts\python.exe -Source notes/my-lecture.md -Output output/pdf/my-lecture.pdf
```

Windows 默认读取系统 `simhei.ttf`。其他系统可以设置 `LECTURE_PDF_FONT` 或传入 `-Font` 指定支持中文的 TrueType 字体；缺字体时会明确报错，不静默生成乱码。

## 跨平台 Python 入口

```bash
python validate_markdown.py notes/software-repository-management.md
python md_to_pdf.py notes/software-repository-management.md output/pdf/software-repository-management.pdf --font /path/to/chinese-font.ttf
```

Ubuntu 可以安装 `fonts-wqy-zenhei`，转换器会自动识别其默认字体路径。依赖版本固定在 `requirements-pdf.txt`，使用 Python 3.12 为推荐环境。

## GitHub 自动构建

`.github/workflows/build-pdf.yml` 在 main 分支的讲义或转换代码变化时运行，也可以在 Actions 页手动启动。

流程安装 Python、中文字体及依赖，逐份检查 `notes/*.md`，导出 PDF 和 JSON 检查记录，最后上传名为 `lecture-pdfs` 的构建产物。进入 Actions → Build lecture PDFs → 成功的运行 → Artifacts 下载。

自动构建只需要仓库只读权限，不写回分支、不调用模型、不读取浏览器登录态。它把已经写好的讲义自动排版，不会从视频自动写出新讲义。视频采集及证据核验按 WORKFLOW.md 执行，正文写作使用 TASK.md。

自动报告保留 `visual_review: pending`，因为脚本不会假装自己做过视觉审查。本次随仓库提供的 PDF 会在逐页审查后将相应交付记录标注为 PASS。未来每次新构建应重新检查页面。

## 支持范围与限制

支持中文正文、多级标题、链接、项目列表、围栏代码块、管道表格和单独一行的本地图片。表格有重复表头，长正文自动分页，PDF 提供页眉与页码。

这不是完整的通用 Markdown / LaTeX 引擎：复杂嵌套表格、数学公式排版和 Mermaid 图形不自动渲染。含公式的正式课程应采用上游 LaTeX 路线，Mermaid 则先导出为图片再引用。当前课程样例没有依赖这些能力。

## 来源

- 原视频：<https://www.bilibili.com/video/BV1kybV6DE47/>
- [参考项目](https://github.com/ysyecust/lecture-to-notes)
- [本项目工作流](WORKFLOW.md)
