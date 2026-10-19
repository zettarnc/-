"""Compile reviewed Markdown through Pandoc -> LaTeX -> Tectonic/XeLaTeX."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent

def find_tool(name, supplied=None):
    candidates = [supplied, shutil.which(name), ROOT / '.latex-tools' / (name + '.exe')]
    if name == 'pandoc':
        candidates.append(ROOT / '.latex-tools/python/pypandoc/files/pandoc.exe')
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    raise SystemExit(f'Missing {name}; see LATEX.md for installation.')

def build(args):
    source, output = args.source.resolve(), args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    pandoc = find_tool('pandoc', args.pandoc)
    engine = find_tool(args.engine, args.engine_path)
    text = source.read_text(encoding='utf-8')
    title, body = text.split('\n', 1)
    title = title.lstrip('# ').strip()
    input_md = output.with_suffix('.input.md')
    tex = output.with_suffix('.tex')
    input_md.write_text(body, encoding='utf-8')
    subprocess.run([pandoc, str(input_md), '-f', 'markdown-implicit_figures',
                    '-t', 'latex', '--standalone', '--shift-heading-level-by=-1', '--resource-path', str(source.parent),
                    '--lua-filter', str(ROOT / 'latex-figures.lua'),
                    '--include-in-header', str(ROOT / 'latex-header.tex'),
                    '-V', 'documentclass=ctexart', '-V', 'classoption=fontset=fandol',
                    '-V', 'fontsize=11pt', '-V', 'mainfont=TeX Gyre Pagella',
                    '-V', 'sansfont=TeX Gyre Heros', '-V', 'monofont=Latin Modern Mono',
                    '-V', 'colorlinks=true', '-M', 'title='+title, '-M', 'date=',
                    '--output', str(tex)], check=True)
    # Pandoc retains relative images; absolute paths keep compilation independent of cwd.
    latex = tex.read_text(encoding='utf-8')
    for image in source.parent.glob('*.jpg'):
        latex = latex.replace('{'+image.name+'}', '{'+image.resolve().as_posix()+'}')
    tex.write_text(latex, encoding='utf-8')
    if args.engine == 'tectonic':
        command = [engine, '--keep-logs', '--keep-intermediates', '--outdir', str(output.parent), str(tex)]
        subprocess.run(command, check=True, cwd=ROOT)
    else:
        command = [engine, '-interaction=nonstopmode', '-halt-on-error', '-no-shell-escape',
                   '-output-directory='+str(output.parent), str(tex)]
        for _ in range(2):
            subprocess.run(command, check=True, cwd=ROOT)
    reader = PdfReader(output)
    if not reader.pages or any(not (page.extract_text() or '').strip() for page in reader.pages):
        raise SystemExit('PDF has empty/unsearchable pages')
    report = {
        'engine': args.engine, 'pipeline': 'Pandoc -> LaTeX (ctexart) -> '+args.engine,
        'fonts': {'CJK_body':'FandolSong', 'CJK_headings':'FandolHei', 'Latin_body':'TeX Gyre Pagella'},
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'pdf_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'pages': len(reader.pages), 'format_check':'PASS', 'visual_review':'pending',
        'source_verification_report':'evidence/source-verification.json',
    }
    output.with_suffix('.verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    input_md.unlink()
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--engine', choices=['tectonic','xelatex'], default='tectonic')
    parser.add_argument('--pandoc')
    parser.add_argument('--engine-path')
    build(parser.parse_args())
