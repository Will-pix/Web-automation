from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def extract_keyword_blocks_from_docx(docx_path: str | Path) -> list[dict[str, str]]:
    path = Path(docx_path)
    paragraphs = _read_docx_paragraphs(path)
    classes = []

    for index, line in enumerate(paragraphs):
        match = re.match(r"class\s+([A-Za-z_][A-Za-z0-9_]*)\s*:", line.strip())
        if match:
            classes.append((index, match.group(1)))

    blocks: list[dict[str, str]] = []
    for idx, (start, class_name) in enumerate(classes):
        end = classes[idx + 1][0] if idx + 1 < len(classes) else len(paragraphs)
        code = "\n".join(paragraphs[start:end]).strip() + "\n"
        blocks.append(
            {
                "name": class_name,
                "keyword_fun_name": class_name,
                "keyword_value": code,
                "keyword_desc": "[]",
            }
        )
    return blocks


def _read_docx_paragraphs(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        xml_data = archive.read("word/document.xml")

    root = ET.fromstring(xml_data)
    body = root.find("w:body", WORD_NS)
    if body is None:
        return []

    paragraphs: list[str] = []
    for child in body:
        if child.tag.split("}")[-1] != "p":
            continue
        texts = [node.text for node in child.findall(".//w:t", WORD_NS) if node.text is not None]
        text = "".join(texts)
        if text:
            paragraphs.append(text.rstrip())
    return paragraphs

