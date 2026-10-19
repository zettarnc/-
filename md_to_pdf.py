"""Render the project's Markdown lecture notes to a searchable Chinese PDF.

Supported: headings, paragraphs, fenced code, pipe tables, lists, links, images.
Mermaid blocks are printed as source; diagrams require pre-rendered image assets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from html import escape
from pathlib import Path
from urllib.parse import unquote

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    KeepTogether, HRFlowable,
)
from pypdf import PdfReader


def find_font(explicit=None):
    candidates = [explicit, os.environ.get('LECTURE_PDF_FONT'),
                  'C:/Windows/Fonts/simhei.ttf',
                  '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                  '/usr/share/fonts/truetype/arphic/ukai.ttc']
    for value in candidates:
        if value and Path(value).is_file():
            return str(value)
    raise SystemExit('No CJK TrueType font. Pass --font PATH or install fonts-wqy-zenhei.')


def inline(text):
    # Work with escaped text so input cannot inject ReportLab paragraph markup.
    value = escape(text)
    value = re.sub(r'`([^`]+)`', r'<font color="#225e7a">\1</font>', value)
    value = re.sub(r'\*\*([^*]+)\*\*', r'\1', value)
    value = re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',
                   r'<a href="\2" color="#225e7a">\1</a>', value)
    value = re.sub(r'&lt;(https?://[^&\s]+)&gt;',
                   r'<a href="\1" color="#225e7a">\1</a>', value)
    return value


def render(source, destination, font_path):
    text = source.read_text(encoding='utf-8-sig')
    pdfmetrics.registerFont(TTFont('LectureCJK', font_path, subfontIndex=0))
    base = dict(fontName='LectureCJK', wordWrap='CJK', textColor=colors.HexColor('#20313e'),
                alignment=TA_LEFT, splitLongWords=True)
    styles = {
        'body': ParagraphStyle('body', fontSize=10.5, leading=17, spaceAfter=7,
                               allowWidows=0, allowOrphans=0, **base),
        'title': ParagraphStyle('title', fontSize=23, leading=32, spaceAfter=17, **base),
        'h2': ParagraphStyle('h2', fontSize=15, leading=23, spaceBefore=16, spaceAfter=9,
                             keepWithNext=True, **base),
        'h3': ParagraphStyle('h3', fontSize=12, leading=19, spaceBefore=9, spaceAfter=6,
                             keepWithNext=True, **base),
        'cell': ParagraphStyle('cell', fontSize=9, leading=14, **base),
        'code': ParagraphStyle('code', fontSize=8.5, leading=13, spaceAfter=0, **base),
        'bullet': ParagraphStyle('bullet', fontSize=10.5, leading=17, leftIndent=13,
                                firstLineIndent=-10, spaceAfter=5, **base),
    }
    width, height = 595.276, 841.89
    usable = width - 104
    story = []
    title = next((s[2:].strip() for s in text.splitlines() if s.startswith('# ')), source.stem)
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith('```') or line.startswith('~~~'):
            fence = line[:3]
            code = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith(fence):
                code.append(lines[index])
                index += 1
            if index == len(lines):
                raise ValueError('Unclosed code fence')
            for code_line in code:
                value = escape(code_line).replace(' ', '&#160;') or '&#160;'
                block = Table([[Paragraph(value, styles['code'])]], colWidths=[usable])
                block.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4f6')),
                    ('LEFTPADDING', (0, 0), (-1, -1), 9),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 9),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                story.append(block)
            story.append(Spacer(1, 10))
        elif line.startswith('|') and index + 1 < len(lines) and re.match(r'^\s*\|?\s*:?-{3,}', lines[index + 1]):
            rows = []
            while index < len(lines) and lines[index].strip().startswith('|'):
                values = [v.strip() for v in lines[index].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', v) for v in values):
                    rows.append([Paragraph(inline(v), styles['cell']) for v in values])
                index += 1
            index -= 1
            count = max(len(row) for row in rows)
            for row in rows:
                row.extend([''] * (count - len(row)))
            proportions = [0.27, 0.73] if count == 2 else [1 / count] * count
            table = Table(rows, colWidths=[usable * p for p in proportions], repeatRows=1,
                          hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5eef3')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7f9fa')]),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 9),
                ('RIGHTPADDING', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.HexColor('#bfd0da')),
            ]))
            story.extend([table, Spacer(1, 10)])
        elif re.match(r'^#{1,6}\s', line):
            level = len(line) - len(line.lstrip('#'))
            heading = line[level:].strip()
            story.append(Paragraph(inline(heading), styles['title' if level == 1 else 'h2' if level == 2 else 'h3']))
        elif re.fullmatch(r'[-*_]{3,}', line):
            story.append(HRFlowable(width='100%', color=colors.HexColor('#d3dfe5')))
        elif re.fullmatch(r'!\[[^\]]*\]\([^)]+\)', line):
            match = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            image_path = (source.parent / unquote(match[2])).resolve()
            if not image_path.is_file():
                raise ValueError(f'Image missing: {image_path}')
            iw, ih = ImageReader(str(image_path)).getSize()
            scale = min(usable / iw, 370 / ih)
            image_block = [Image(str(image_path), width=iw * scale, height=ih * scale),
                           Paragraph(inline(match[1]), styles['cell'])]
            caption_index = index + 1
            while caption_index < len(lines) and not lines[caption_index].strip():
                caption_index += 1
            if caption_index < len(lines) and lines[caption_index].strip().startswith('画面证据：'):
                caption = []
                while caption_index < len(lines) and lines[caption_index].strip():
                    caption.append(lines[caption_index].strip())
                    caption_index += 1
                image_block.append(Paragraph(inline(' '.join(caption)), styles['cell']))
                index = caption_index - 1
            image_block.append(Spacer(1, 10))
            story.append(KeepTogether(image_block))
        elif re.match(r'^(?:[-*+] |\d+\. )', line):
            content = re.sub(r'^(?:[-*+] |\d+\. )', '', line)
            story.append(Paragraph('· ' + inline(content), styles['bullet']))
        else:
            paragraph = [line]
            while index + 1 < len(lines) and lines[index + 1].strip():
                following = lines[index + 1].strip()
                if re.match(r'^(?:#|```|~~~|\||[-*+] |\d+\. |!\[)', following):
                    break
                index += 1
                paragraph.append(following)
            story.append(Paragraph(inline(' '.join(paragraph)), styles['body']))
        index += 1

    destination.parent.mkdir(parents=True, exist_ok=True)
    def page_chrome(canvas, doc):
        canvas.saveState()
        canvas.setFont('LectureCJK', 8)
        canvas.setFillColor(colors.HexColor('#607583'))
        canvas.drawString(52, height - 31, title[:38])
        canvas.drawRightString(width - 52, 29, str(doc.page))
        canvas.setStrokeColor(colors.HexColor('#d7e1e6'))
        canvas.line(52, 43, width - 52, 43)
        canvas.restoreState()
    document = SimpleDocTemplate(str(destination), pagesize=(width, height),
                                 leftMargin=52, rightMargin=52, topMargin=53, bottomMargin=57,
                                 title=title, author='Lecture Notes', pageCompression=1)
    document.build(story, onFirstPage=page_chrome, onLaterPages=page_chrome)
    reader = PdfReader(destination)
    extracted = '\n'.join(page.extract_text() or '' for page in reader.pages)
    if not reader.pages or title not in extracted:
        raise ValueError('PDF verification failed: missing pages or searchable Chinese title')
    if any(not (page.extract_text() or '').strip() for page in reader.pages):
        raise ValueError('PDF verification failed: empty page')
    report = {
        'source': source.name, 'output': destination.name,
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'pdf_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
        'pages': len(reader.pages), 'searchable_title': True,
        'format_check': 'PASS', 'visual_review': 'pending',
        'video_evidence_review': 'not_performed_by_this_converter',
    }
    destination.with_suffix('.verification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--font', help='CJK TrueType TTF/TTC font')
    args = parser.parse_args()
    render(args.source.resolve(), args.output.resolve(), find_font(args.font))
