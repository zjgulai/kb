#!/usr/bin/env python3
"""Generate a single-file HTML PRD with a sidebar table of contents."""

from __future__ import annotations

import argparse
import hashlib
import html
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


def slugify(text: str, used: set[str]) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    base = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text.lower()).strip("-")
    base = base or "section"
    slug = base
    index = 2
    while slug in used:
        slug = f"{base}-{index}"
        index += 1
    used.add(slug)
    return slug


def render_inline(text: str) -> str:
    code_tokens: list[str] = []

    def code_repl(match: re.Match[str]) -> str:
        code_tokens.append(f"<code>{html.escape(match.group(1))}</code>")
        return f"@@CODE{len(code_tokens) - 1}@@"

    text = re.sub(r"`([^`]+)`", code_repl, text)
    text = html.escape(text, quote=False)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    for index, token in enumerate(code_tokens):
        text = text.replace(f"@@CODE{index}@@", token)
    return text


def split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def is_table_start(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    current = lines[index].strip()
    divider = lines[index + 1].strip()
    return (
        current.startswith("|")
        and current.endswith("|")
        and divider.startswith("|")
        and re.fullmatch(r"\|?[\s:\-\|]+\|?", divider) is not None
        and "---" in divider
    )


def render_table(lines: list[str], start: int) -> tuple[str, int]:
    headers = split_table_row(lines[start])
    rows: list[list[str]] = []
    index = start + 2
    while index < len(lines):
        line = lines[index]
        if not line.strip().startswith("|"):
            break
        rows.append(split_table_row(line))
        index += 1

    thead = "".join(f"<th>{render_inline(cell)}</th>" for cell in headers)
    body_rows = []
    for row in rows:
        padded = row + [""] * max(0, len(headers) - len(row))
        body_rows.append(
            "<tr>" + "".join(f"<td>{render_inline(cell)}</td>" for cell in padded[: len(headers)]) + "</tr>"
        )
    table_html = (
        '<div class="table-wrap"><table><thead><tr>'
        + thead
        + "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table></div>"
    )
    return table_html, index


def classify_code_block(language: str, code_lines: list[str]) -> str:
    code = "\n".join(code_lines)
    normalized_language = language.strip().lower()
    if normalized_language == "mermaid":
        return "mermaid"
    if normalized_language not in {"", "text", "txt"}:
        return "code"
    tree_like = any(token in code for token in ["├─", "├──", "└─", "└──"]) or re.search(
        r"^[\w\u4e00-\u9fff.-]+/\s*$", code, re.MULTILINE
    )
    architecture_like = any(token in code for token in ["┌", "┐", "┘", "║", "╔", "╚", "╠", "═"])
    component_architecture = all(
        token in code
        for token in [
            "多模态知识库训练平台  (详细组件)",
            "【数据摄取与解析层】",
            "【知识构建层】",
            "【存储层】",
            "【服务与调用层】",
        ]
    )
    if component_architecture:
        return "component_architecture"
    if tree_like and not architecture_like:
        return "tree"
    if architecture_like:
        return "architecture"
    if any(token in code for token in ["──►", "──>", "-->", "->", "→"]) and len([line for line in code_lines if line.strip()]) <= 8:
        return "flow"
    return "code"


def split_flow_nodes(line: str) -> list[str]:
    parts = re.split(r"\s*(?:──►|──>|-->|->|→)\s*", line.strip())
    return [part.strip() for part in parts if part.strip()]


def render_flow_diagram(code_lines: list[str]) -> str:
    rows: list[str] = []
    fallback: list[str] = []
    for line in code_lines:
        if not line.strip():
            continue
        nodes = split_flow_nodes(line)
        if len(nodes) < 2:
            fallback.append(line)
            continue
        row_parts: list[str] = []
        for index, node in enumerate(nodes):
            row_parts.append(f'<span class="flow-node">{render_inline(node)}</span>')
            if index < len(nodes) - 1:
                row_parts.append('<span class="flow-arrow" aria-hidden="true"></span>')
        rows.append('<div class="flow-row">' + "".join(row_parts) + "</div>")
    if not rows:
        return render_ascii_diagram("flow", code_lines)
    fallback_html = ""
    if fallback:
        fallback_html = '<pre class="diagram-pre">' + html.escape("\n".join(fallback)) + "</pre>"
    return (
        '<figure class="diagram-block diagram-flow" data-diagram-kind="flow">'
        '<figcaption>流程图</figcaption>'
        '<div class="flow-canvas">'
        + "".join(rows)
        + fallback_html
        + "</div></figure>"
    )


def parse_mermaid_node(expression: str) -> tuple[str, str]:
    expression = expression.strip().rstrip(";")
    match = re.match(r"^([A-Za-z0-9_]+)\s*(.*)$", expression)
    if not match:
        return expression, expression

    node_id = match.group(1)
    label = match.group(2).strip() or node_id
    label = label.replace("\\n", "\n")
    for _ in range(3):
        stripped = label.strip()
        pairs = [("[", "]"), ("(", ")"), ("{", "}"), ('"', '"')]
        for start, end in pairs:
            if stripped.startswith(start) and stripped.endswith(end):
                label = stripped[1:-1].strip()
                break
        else:
            break
    return node_id, label or node_id


def render_node_label(label: str) -> str:
    parts = [part.strip() for part in label.splitlines() if part.strip()]
    if not parts:
        parts = [label.strip()]
    return "<br>".join(render_inline(part) for part in parts)


def render_mermaid_diagram(code_lines: list[str]) -> str:
    nodes: dict[str, str] = {}
    edges: list[tuple[str, str, str]] = []
    direction = "TD"

    def remember_node(node_id: str, label: str) -> None:
        if label != node_id or node_id not in nodes:
            nodes[node_id] = label

    for line in code_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("%%"):
            continue
        direction_match = re.match(r"flowchart\s+([A-Z]+)", stripped, re.IGNORECASE)
        if direction_match:
            direction = direction_match.group(1).upper()
            continue
        edge_match = re.match(r"(?P<source>.+?)\s*[-.=]+>\s*(?P<target>.+)$", stripped)
        if not edge_match:
            continue
        source_id, source_label = parse_mermaid_node(edge_match.group("source"))
        target_expr = edge_match.group("target").strip()
        edge_label = ""
        if target_expr.startswith("|"):
            label_end = target_expr.find("|", 1)
            if label_end != -1:
                edge_label = target_expr[1:label_end].strip()
                target_expr = target_expr[label_end + 1 :].strip()
        target_id, target_label = parse_mermaid_node(target_expr)
        remember_node(source_id, source_label)
        remember_node(target_id, target_label)
        edges.append((source_id, edge_label, target_id))

    if not edges:
        return render_ascii_diagram("flow", code_lines)

    rows: list[str] = []
    for source_id, edge_label, target_id in edges:
        label = f'<span class="mermaid-edge-label">{render_inline(edge_label)}</span>' if edge_label else ""
        rows.append(
            '<div class="mermaid-row">'
            f'<span class="mermaid-node">{render_node_label(nodes.get(source_id, source_id))}</span>'
            f'<span class="mermaid-connector"><span class="flow-arrow" aria-hidden="true"></span>{label}</span>'
            f'<span class="mermaid-node">{render_node_label(nodes.get(target_id, target_id))}</span>'
            "</div>"
        )
    return (
        f'<figure class="diagram-block diagram-mermaid" data-diagram-kind="mermaid-flow" data-direction="{html.escape(direction)}">'
        '<figcaption>Mermaid 流程图</figcaption>'
        '<div class="mermaid-canvas">'
        + "".join(rows)
        + "</div></figure>"
    )


def render_component_card(title: str, subtitle: str, details: list[str], tone: str = "") -> str:
    detail_html = "".join(f"<li>{render_inline(detail)}</li>" for detail in details)
    tone_class = f" {html.escape(tone, quote=True)}" if tone else ""
    return (
        f'<article class="component-card{tone_class}">'
        f"<h4>{render_inline(title)}</h4>"
        f"<p>{render_inline(subtitle)}</p>"
        f"<ul>{detail_html}</ul>"
        "</article>"
    )


def render_component_architecture(code_lines: list[str]) -> str:
    layers = [
        {
            "number": "01",
            "title": "数据摄取与解析层",
            "summary": "按模态路由原始内容，产出统一 content_list 与元数据。",
            "tone": "ingestion",
            "cards": [
                ("Format Router", "格式/模态路由", ["识别 PDF、Office、图片、音频、视频", "决定解析链路与后续质量门禁"]),
                ("MinerU 2.5", "PDF / Office 解析", ["两阶段 VLM 解析", "保留版面、表格、图片边界"]),
                ("VLM 图像描述引擎", "图片语义化", ["图像描述 + OCR", "为多模态检索生成文本代理"]),
                ("Whisper ASR", "音频语音转写", ["语音转写 + 时间戳", "支撑视频和音频证据回溯"]),
                ("VideoRAG 双通道", "长视频 > 5min", ["视觉通道：抽帧 -> VLM 描述 + 时间戳", "音频通道：Whisper 转写 + 时间戳"]),
                ("Unified content_list", "标准化输出", ["content_list Format", "Metadata Schema 统一封装"]),
            ],
        },
        {
            "number": "02",
            "title": "知识构建层",
            "summary": "将标准化内容转换为可检索、可追溯、可增量维护的知识结构。",
            "tone": "knowledge",
            "cards": [
                ("RAG-Anything", "多模态编排引擎", ["调度文本、图像、表格、视频解析结果", "组织跨模态知识构建流程"]),
                ("实体/关系抽取", "LLM 驱动", ["抽取实体、关系、业务事件", "形成图谱节点和边"]),
                ("跨模态关系映射", "图谱连边", ["连接图片、表格、文本和视频证据", "减少单模态召回断裂"]),
                ("语义分块", "MinerU 解析边界", ["overlap 15%", "保留章节、表格、图片上下文"]),
                ("向量化", "Qwen3 Embedding", ["生成检索向量", "支撑语义召回和重排"]),
                ("LightRAG 增量 merge", "零停机并入", ["新节点/边 union 并入", "保留历史连接和证据链"]),
            ],
        },
        {
            "number": "03",
            "title": "存储层",
            "summary": "按知识形态拆分存储责任，兼顾 PoC 起步和规模化扩展。",
            "tone": "storage",
            "cards": [
                ("图存储", "关系与路径推理", ["起步：PG + AGE", "规模：Neo4j"]),
                ("向量存储", "语义召回", ["起步：pgvector", "规模：Milvus"]),
                ("KV / 文档状态", "任务与索引状态", ["PostgreSQL", "版本、任务、审计元数据"]),
                ("对象存储", "原始证据归档", ["MinIO / OSS / S3", "文件、图片、视频、解析产物"]),
            ],
        },
        {
            "number": "04",
            "title": "服务与调用层",
            "summary": "把知识库能力暴露给 AI 智能体和业务系统，并保留路由、权限与溯源边界。",
            "tone": "service",
            "cards": [
                ("LightRAG Server", "FastAPI REST", ["/query /insert", "BGE-Reranker"]),
                ("MCP Server", "智能体工具入口", ["P1 只读 MCP 工具", "stdio / http + namespace 路由"]),
                ("Agentic Router", "查询规划与多源调用", ["A2A / 集体记忆", "可观测、权限、证据溯源"]),
            ],
        },
    ]

    layer_html: list[str] = []
    connectors = [
        "标准化内容与元数据进入知识构建",
        "图谱、向量、状态与原始证据分库存储",
        "检索、MCP 工具与智能体路由对外提供能力",
    ]
    for index, layer in enumerate(layers):
        cards = "".join(
            render_component_card(title, subtitle, details, f"is-{layer['tone']}")
            for title, subtitle, details in layer["cards"]
        )
        layer_html.append(
            f'<section class="architecture-layer is-{html.escape(str(layer["tone"]), quote=True)}">'
            '<div class="layer-heading">'
            f'<span class="layer-number">{html.escape(str(layer["number"]))}</span>'
            "<div>"
            f'<h3>{render_inline(str(layer["title"]))}</h3>'
            f'<p>{render_inline(str(layer["summary"]))}</p>'
            "</div>"
            "</div>"
            f'<div class="component-grid layer-{html.escape(str(layer["tone"]), quote=True)}">{cards}</div>'
            "</section>"
        )
        if index < len(connectors):
            layer_html.append(
                '<div class="architecture-connector" aria-hidden="true">'
                f"<span>{render_inline(connectors[index])}</span>"
                "</div>"
            )

    source = html.escape("\n".join(code_lines))
    return (
        '<figure class="diagram-block component-architecture" data-diagram-kind="component-architecture">'
        "<figcaption>C4 L2 组件架构图</figcaption>"
        '<div class="architecture-board">'
        '<div class="architecture-head">'
        "<span>C4 L2 · 详细组件</span>"
        "<strong>多模态知识库训练平台</strong>"
        "<p>读图顺序：数据摄取 -> 知识构建 -> 存储 -> 服务与智能体调用。</p>"
        "</div>"
        '<div class="architecture-layers">'
        + "".join(layer_html)
        + "</div>"
        '<details class="architecture-source">'
        "<summary>查看原始 ASCII 源</summary>"
        f'<pre class="diagram-pre"><code>{source}</code></pre>'
        "</details>"
        "</div>"
        "</figure>"
    )


def render_ascii_diagram(kind: str, code_lines: list[str]) -> str:
    labels = {
        "architecture": "架构图",
        "tree": "结构图",
        "flow": "流程图",
    }
    label = labels.get(kind, "图示")
    code = html.escape("\n".join(code_lines))
    return (
        f'<figure class="diagram-block diagram-{kind}" data-diagram-kind="{kind}">'
        f"<figcaption>{label}</figcaption>"
        f'<pre class="diagram-pre"><code>{code}</code></pre>'
        "</figure>"
    )


def collect_block(lines: list[str], start: int, predicate) -> tuple[list[str], int]:
    block: list[str] = []
    index = start
    while index < len(lines) and predicate(lines[index]):
        block.append(lines[index])
        index += 1
    return block, index


def render_markdown(markdown: str) -> tuple[str, list[dict[str, str | int]]]:
    lines = markdown.splitlines()
    html_parts: list[str] = []
    nav: list[dict[str, str | int]] = []
    used_ids: set[str] = set()
    pending_anchor: str | None = None
    index = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        anchor_match = re.fullmatch(r'<a\s+name="([^"]+)"></a>', stripped)
        if anchor_match:
            pending_anchor = anchor_match.group(1)
            used_ids.add(pending_anchor)
            index += 1
            continue

        if not stripped:
            index += 1
            continue

        if stripped == "---":
            html_parts.append("<hr>")
            index += 1
            continue

        if stripped.startswith("```"):
            language = stripped[3:].strip()
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            block_kind = classify_code_block(language, code_lines)
            if block_kind == "flow":
                html_parts.append(render_flow_diagram(code_lines))
                continue
            if block_kind == "mermaid":
                html_parts.append(render_mermaid_diagram(code_lines))
                continue
            if block_kind == "component_architecture":
                html_parts.append(render_component_architecture(code_lines))
                continue
            if block_kind in {"architecture", "tree"}:
                html_parts.append(render_ascii_diagram(block_kind, code_lines))
                continue
            code = html.escape("\n".join(code_lines))
            lang_label = html.escape(language or "text")
            html_parts.append(
                f'<figure class="codeblock"><figcaption>{lang_label}'
                f'<button type="button" class="copy-code">复制</button></figcaption>'
                f'<pre><code>{code}</code></pre></figure>'
            )
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            section_id = pending_anchor or slugify(title, used_ids)
            pending_anchor = None
            html_parts.append(
                f'<h{level} id="{html.escape(section_id, quote=True)}">'
                f'<a class="heading-anchor" href="#{html.escape(section_id, quote=True)}" aria-label="Link to section">#</a>'
                f"{render_inline(title)}</h{level}>"
            )
            if level <= 3:
                nav.append({"level": level, "title": re.sub(r"<[^>]+>", "", title), "id": section_id})
            index += 1
            continue

        if is_table_start(lines, index):
            table_html, index = render_table(lines, index)
            html_parts.append(table_html)
            continue

        if stripped.startswith(">"):
            block, index = collect_block(lines, index, lambda item: item.strip().startswith(">"))
            quote_lines = [item.strip().lstrip(">").strip() for item in block]
            quote_lines = [item for item in quote_lines if item]
            html_parts.append(
                "<blockquote>"
                + "".join(f"<p>{render_inline(item)}</p>" for item in quote_lines)
                + "</blockquote>"
            )
            continue

        if re.match(r"^\s*[-*]\s+", line):
            block, index = collect_block(lines, index, lambda item: re.match(r"^\s*[-*]\s+", item) is not None)
            items = [re.sub(r"^\s*[-*]\s+", "", item) for item in block]
            html_parts.append("<ul>" + "".join(f"<li>{render_inline(item)}</li>" for item in items) + "</ul>")
            continue

        if re.match(r"^\s*\d+\.\s+", line):
            block, index = collect_block(lines, index, lambda item: re.match(r"^\s*\d+\.\s+", item) is not None)
            items = [re.sub(r"^\s*\d+\.\s+", "", item) for item in block]
            html_parts.append("<ol>" + "".join(f"<li>{render_inline(item)}</li>" for item in items) + "</ol>")
            continue

        paragraph_lines: list[str] = [line]
        index += 1
        while index < len(lines):
            next_line = lines[index]
            next_stripped = next_line.strip()
            if (
                not next_stripped
                or next_stripped == "---"
                or next_stripped.startswith("```")
                or re.match(r"^(#{1,6})\s+", next_line)
                or re.fullmatch(r'<a\s+name="([^"]+)"></a>', next_stripped)
                or is_table_start(lines, index)
                or next_stripped.startswith(">")
                or re.match(r"^\s*[-*]\s+", next_line)
                or re.match(r"^\s*\d+\.\s+", next_line)
            ):
                break
            paragraph_lines.append(next_line)
            index += 1
        html_parts.append(f"<p>{render_inline(' '.join(item.strip() for item in paragraph_lines))}</p>")

    return "\n".join(html_parts), nav


def nav_html(nav: Iterable[dict[str, str | int]]) -> str:
    links = []
    for item in nav:
        level = int(item["level"])
        title = html.escape(str(item["title"]))
        section_id = html.escape(str(item["id"]), quote=True)
        links.append(
            f'<a class="toc-link level-{level}" href="#{section_id}" data-title="{title.lower()}">'
            f"<span>{title}</span></a>"
        )
    return "\n".join(links)


def build_html(markdown: str, source_path: Path) -> str:
    body, nav = render_markdown(markdown)
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>多模态企业知识库平台 PRD</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f7fb;
      --surface: #ffffff;
      --surface-soft: #f8fafc;
      --ink: #172033;
      --muted: #667085;
      --line: #d9e0eb;
      --accent: #0f6b5f;
      --accent-2: #285a9b;
      --accent-soft: #e6f4f1;
      --warning: #a15c00;
      --code-bg: #111827;
      --code-ink: #e5e7eb;
      --sidebar: #111827;
      --sidebar-ink: #dbe4f0;
      --sidebar-muted: #8fa3bf;
      --shadow: 0 18px 45px rgba(15, 23, 42, 0.10);
      --shadow-soft: 0 10px 24px rgba(15, 23, 42, 0.08);
      --radius: 8px;
      --content-width: 1120px;
      --measure: 76ch;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      background: var(--bg);
      color: var(--ink);
      font-size: 15.5px;
      line-height: 1.74;
      letter-spacing: 0;
      text-rendering: optimizeLegibility;
      -webkit-font-smoothing: antialiased;
    }}
    a {{ color: var(--accent); text-decoration: none; text-underline-offset: 3px; }}
    a:hover {{ text-decoration: underline; }}
    .layout {{ display: grid; grid-template-columns: 330px minmax(0, 1fr); min-height: 100vh; }}
    .sidebar {{
      position: sticky;
      top: 0;
      height: 100vh;
      overflow: auto;
      background: var(--sidebar);
      color: var(--sidebar-ink);
      border-right: 1px solid rgba(255,255,255,0.08);
      padding: 22px 18px;
    }}
    .brand {{ padding: 4px 4px 18px; border-bottom: 1px solid rgba(255,255,255,0.10); }}
    .brand h1 {{ margin: 0 0 8px; font-size: 18px; line-height: 1.35; color: white; }}
    .brand p {{ margin: 0; color: var(--sidebar-muted); font-size: 12px; line-height: 1.55; }}
    .toolbox {{ display: grid; gap: 10px; margin: 16px 0; }}
    .search {{
      width: 100%;
      border: 1px solid rgba(255,255,255,0.14);
      background: rgba(255,255,255,0.07);
      color: white;
      border-radius: var(--radius);
      padding: 10px 11px;
      font-size: 14px;
      outline: none;
    }}
    .search::placeholder {{ color: var(--sidebar-muted); }}
    .actions {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
    .actions button, .mobile-toggle {{
      border: 1px solid rgba(255,255,255,0.14);
      background: rgba(255,255,255,0.08);
      color: white;
      border-radius: var(--radius);
      padding: 8px 10px;
      cursor: pointer;
      font-size: 13px;
    }}
    .toc {{ display: grid; gap: 2px; padding-bottom: 24px; }}
    .toc-link {{
      display: block;
      color: var(--sidebar-ink);
      border-radius: 6px;
      padding: 7px 9px;
      font-size: 13px;
      line-height: 1.35;
      border-left: 3px solid transparent;
    }}
    .toc-link:hover {{ background: rgba(255,255,255,0.07); text-decoration: none; }}
    .toc-link.active {{
      background: rgba(15, 107, 95, 0.28);
      border-left-color: #4dd0bd;
      color: white;
    }}
    .toc-link.level-2 {{ padding-left: 22px; color: #c8d4e3; }}
    .toc-link.level-3 {{ padding-left: 36px; color: var(--sidebar-muted); font-size: 12px; }}
    .document {{ min-width: 0; padding: 34px clamp(22px, 4vw, 64px) 80px; }}
    .doc-shell {{ max-width: var(--content-width); margin: 0 auto; }}
    .meta-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 0 0 18px;
      color: var(--muted);
      font-size: 12px;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--surface);
      padding: 4px 10px;
    }}
    .content {{
      background: var(--surface);
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
      border-radius: var(--radius);
      padding: clamp(24px, 4vw, 48px);
      font-size: 15.5px;
      line-height: 1.76;
    }}
    .content h1, .content h2, .content h3, .content h4, .content h5, .content h6 {{
      color: #101828;
      line-height: 1.28;
      letter-spacing: 0;
      scroll-margin-top: 22px;
      text-wrap: balance;
    }}
    .content h1 {{
      margin: 42px 0 22px;
      max-width: 26ch;
      font-size: 32px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--line);
      position: relative;
    }}
    .content h1::after {{
      content: "";
      position: absolute;
      left: 0;
      bottom: -1px;
      width: 112px;
      height: 3px;
      background: var(--accent);
      border-radius: 999px;
    }}
    .content h1:first-child {{ margin-top: 0; }}
    .content h2 {{
      margin: 42px 0 16px;
      max-width: 34ch;
      font-size: 23px;
      padding-left: 12px;
      border-left: 4px solid var(--accent);
    }}
    .content h3 {{
      margin: 30px 0 10px;
      max-width: 46ch;
      font-size: 18px;
      color: #263247;
    }}
    .content h4 {{ margin: 22px 0 8px; max-width: 56ch; font-size: 16px; color: #344054; }}
    .heading-anchor {{
      opacity: 0;
      margin-right: 8px;
      color: var(--accent);
      font-weight: 600;
    }}
    h1:hover .heading-anchor, h2:hover .heading-anchor, h3:hover .heading-anchor,
    h4:hover .heading-anchor, h5:hover .heading-anchor, h6:hover .heading-anchor {{ opacity: 1; }}
    .content p {{
      max-width: var(--measure);
      margin: 12px 0;
      color: #263247;
      line-height: 1.78;
      overflow-wrap: anywhere;
    }}
    .content p + p {{ margin-top: 14px; }}
    .content h1 + p,
    .content h2 + p,
    .content h3 + p,
    .content h4 + p {{ margin-top: 8px; }}
    .content strong {{ color: #111827; font-weight: 700; }}
    .content em {{ color: #475467; }}
    .content a {{ font-weight: 560; }}
    blockquote {{
      max-width: calc(var(--measure) + 8ch);
      margin: 18px 0 22px;
      padding: 14px 18px;
      border-left: 4px solid var(--accent);
      background: var(--accent-soft);
      color: #18443e;
      line-height: 1.74;
      border-radius: 0 var(--radius) var(--radius) 0;
    }}
    .content blockquote p {{
      max-width: none;
      margin: 0;
      color: inherit;
      line-height: 1.72;
    }}
    .content blockquote p + p {{ margin-top: 7px; }}
    hr {{ border: 0; border-top: 1px solid var(--line); margin: 32px 0; }}
    code {{
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      font-size: 0.9em;
      background: #eef2f7;
      border: 1px solid #dce3ed;
      border-radius: 5px;
      padding: 1px 5px 2px;
      white-space: normal;
      word-break: break-word;
    }}
    .codeblock {{
      margin: 18px 0;
      background: var(--code-bg);
      border-radius: var(--radius);
      overflow: hidden;
      border: 1px solid #1f2937;
    }}
    .codeblock figcaption {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      min-height: 36px;
      padding: 8px 12px;
      color: #9ca3af;
      font-size: 12px;
      border-bottom: 1px solid #1f2937;
    }}
    .copy-code {{
      border: 1px solid #374151;
      background: #1f2937;
      color: #e5e7eb;
      border-radius: 6px;
      padding: 4px 8px;
      cursor: pointer;
      font-size: 12px;
    }}
    pre {{ margin: 0; overflow: auto; padding: 16px; }}
    pre code {{ background: transparent; border: 0; color: var(--code-ink); padding: 0; font-size: 13px; line-height: 1.6; }}
    .diagram-block {{
      margin: 22px 0;
      border: 1px solid #cdd8e6;
      border-radius: var(--radius);
      background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
      box-shadow: var(--shadow-soft);
      overflow: hidden;
    }}
    .diagram-block figcaption {{
      min-height: 38px;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 9px 14px;
      border-bottom: 1px solid #d9e2ef;
      color: #203047;
      font-size: 13px;
      font-weight: 700;
      background: #eef4fb;
    }}
    .diagram-block figcaption::before {{
      content: "";
      width: 9px;
      height: 9px;
      border-radius: 999px;
      background: var(--accent);
      box-shadow: 14px 0 0 #4f8fd9, 28px 0 0 #d29b2d;
      margin-right: 28px;
    }}
    .diagram-pre {{
      margin: 0;
      padding: 18px;
      background:
        linear-gradient(90deg, rgba(15,107,95,.06) 1px, transparent 1px),
        linear-gradient(180deg, rgba(15,107,95,.05) 1px, transparent 1px),
        #fbfdff;
      background-size: 28px 28px;
      color: #172033;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      font-size: 13px;
      line-height: 1.68;
      overflow: auto;
      white-space: pre;
    }}
    .diagram-pre code {{
      color: inherit;
      background: transparent;
      border: 0;
      padding: 0;
      white-space: inherit;
      word-break: normal;
      overflow-wrap: normal;
    }}
    .diagram-architecture .diagram-pre {{
      background:
        linear-gradient(90deg, rgba(40,90,155,.07) 1px, transparent 1px),
        linear-gradient(180deg, rgba(40,90,155,.06) 1px, transparent 1px),
        #f8fbff;
      background-size: 32px 32px;
    }}
    .diagram-tree .diagram-pre {{
      background: #fbfcfe;
      border-left: 4px solid var(--accent);
    }}
    .component-architecture {{
      border-color: #bdcadb;
      background: #f7f9fc;
    }}
    .architecture-board {{
      padding: 18px;
      background:
        linear-gradient(90deg, rgba(40,90,155,.05) 1px, transparent 1px),
        linear-gradient(180deg, rgba(40,90,155,.045) 1px, transparent 1px),
        #f8fbff;
      background-size: 30px 30px;
    }}
    .architecture-head {{
      display: grid;
      gap: 6px;
      max-width: 760px;
      margin: 0 0 16px;
      padding: 14px 16px;
      border: 1px solid #cbd8e8;
      border-left: 5px solid var(--accent);
      border-radius: var(--radius);
      background: rgba(255,255,255,.92);
      box-shadow: 0 10px 20px rgba(15, 23, 42, .06);
    }}
    .architecture-head span {{
      color: var(--accent-2);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .04em;
      text-transform: uppercase;
    }}
    .architecture-head strong {{
      color: #101828;
      font-size: 22px;
      line-height: 1.25;
    }}
    .architecture-head p {{
      max-width: none;
      margin: 0;
      color: #536178;
      font-size: 13px;
      line-height: 1.55;
    }}
    .architecture-layers {{
      display: grid;
      gap: 0;
    }}
    .architecture-layer {{
      display: grid;
      grid-template-columns: minmax(210px, .72fr) minmax(0, 2.6fr);
      gap: 16px;
      align-items: stretch;
      padding: 16px;
      border: 1px solid #cad7e7;
      border-radius: var(--radius);
      background: rgba(255,255,255,.94);
      box-shadow: 0 8px 20px rgba(15, 23, 42, .055);
      position: relative;
      overflow: hidden;
    }}
    .architecture-layer::before {{
      content: "";
      position: absolute;
      inset: 0 auto 0 0;
      width: 5px;
      background: var(--accent);
    }}
    .architecture-layer.is-knowledge::before {{ background: #285a9b; }}
    .architecture-layer.is-storage::before {{ background: #7a5a16; }}
    .architecture-layer.is-service::before {{ background: #7b3f63; }}
    .layer-heading {{
      display: grid;
      grid-template-columns: 44px minmax(0, 1fr);
      gap: 12px;
      align-content: start;
      padding-left: 2px;
    }}
    .layer-number {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 42px;
      height: 42px;
      border-radius: 50%;
      background: #eef5f3;
      color: var(--accent);
      border: 1px solid #bfd8d3;
      font-weight: 850;
      font-size: 13px;
    }}
    .is-knowledge .layer-number {{
      background: #eef4fb;
      color: #285a9b;
      border-color: #c8d8ec;
    }}
    .is-storage .layer-number {{
      background: #fff7e6;
      color: #7a5a16;
      border-color: #ead7a8;
    }}
    .is-service .layer-number {{
      background: #fbf0f7;
      color: #7b3f63;
      border-color: #e6c4d8;
    }}
    .layer-heading h3 {{
      margin: 1px 0 5px;
      max-width: none;
      color: #172033;
      font-size: 17px;
      line-height: 1.28;
    }}
    .layer-heading p {{
      max-width: none;
      margin: 0;
      color: #5f6f86;
      font-size: 13px;
      line-height: 1.58;
    }}
    .component-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      align-items: stretch;
    }}
    .component-grid.layer-storage {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .component-grid.layer-service {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .component-card {{
      min-height: 132px;
      padding: 12px 12px 11px;
      border: 1px solid #cbd8e8;
      border-top: 4px solid var(--accent);
      border-radius: var(--radius);
      background: #ffffff;
      box-shadow: 0 8px 18px rgba(40, 90, 155, .07);
    }}
    .component-card.is-knowledge {{ border-top-color: #285a9b; }}
    .component-card.is-storage {{ border-top-color: #b47b1c; }}
    .component-card.is-service {{ border-top-color: #9b527c; }}
    .component-card h4 {{
      margin: 0 0 5px;
      max-width: none;
      color: #132033;
      font-size: 14px;
      line-height: 1.3;
    }}
    .component-card p {{
      max-width: none;
      margin: 0 0 8px;
      color: #285a9b;
      font-size: 12px;
      line-height: 1.35;
      font-weight: 700;
    }}
    .component-card.is-storage p {{ color: #8b6418; }}
    .component-card.is-service p {{ color: #85476c; }}
    .component-card ul,
    .content .component-card ul {{
      max-width: none;
      margin: 0;
      padding-left: 16px;
    }}
    .component-card li,
    .content .component-card li {{
      margin: 3px 0;
      padding-left: 0;
      color: #344054;
      font-size: 12px;
      line-height: 1.45;
    }}
    .architecture-connector {{
      display: flex;
      justify-content: center;
      min-height: 44px;
      position: relative;
    }}
    .architecture-connector::before {{
      content: "";
      width: 2px;
      background: #8da7c5;
    }}
    .architecture-connector::after {{
      content: "";
      position: absolute;
      top: 27px;
      width: 10px;
      height: 10px;
      border-right: 2px solid #8da7c5;
      border-bottom: 2px solid #8da7c5;
      transform: rotate(45deg);
      background: transparent;
    }}
    .architecture-connector span {{
      position: absolute;
      top: 10px;
      padding: 3px 10px;
      border: 1px solid #cdd9e8;
      border-radius: 999px;
      background: #ffffff;
      color: #52657d;
      font-size: 12px;
      line-height: 1.35;
      box-shadow: 0 5px 12px rgba(15, 23, 42, .06);
    }}
    .architecture-source {{
      margin-top: 16px;
      border: 1px solid #d5dfec;
      border-radius: var(--radius);
      background: #ffffff;
      overflow: hidden;
    }}
    .architecture-source summary {{
      cursor: pointer;
      padding: 10px 12px;
      color: #475467;
      font-size: 13px;
      font-weight: 700;
      background: #f4f7fb;
    }}
    .architecture-source .diagram-pre {{
      box-shadow: none;
      border-top: 1px solid #d5dfec;
    }}
    .flow-canvas {{
      display: grid;
      gap: 14px;
      padding: 18px;
      overflow-x: auto;
      background:
        radial-gradient(circle at 1px 1px, rgba(15,107,95,.16) 1px, transparent 0),
        #fbfdff;
      background-size: 22px 22px;
    }}
    .flow-row {{
      display: inline-flex;
      align-items: center;
      min-width: max-content;
      gap: 10px;
    }}
    .flow-node {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 42px;
      max-width: 260px;
      padding: 9px 13px;
      border: 1px solid #b7c8dc;
      border-radius: var(--radius);
      background: #ffffff;
      color: #172033;
      font-weight: 650;
      line-height: 1.35;
      box-shadow: 0 8px 18px rgba(40, 90, 155, .10);
      white-space: normal;
      text-align: center;
    }}
    .flow-arrow {{
      display: inline-flex;
      align-items: center;
      width: 42px;
      height: 2px;
      background: var(--accent-2);
      position: relative;
      flex: 0 0 42px;
    }}
    .flow-arrow::after {{
      content: "";
      position: absolute;
      right: -1px;
      width: 9px;
      height: 9px;
      border-top: 2px solid var(--accent-2);
      border-right: 2px solid var(--accent-2);
      transform: rotate(45deg);
    }}
    .diagram-mermaid .mermaid-canvas {{
      display: grid;
      gap: 10px;
      padding: 18px;
      overflow-x: auto;
      background:
        linear-gradient(90deg, rgba(40,90,155,.06) 1px, transparent 1px),
        linear-gradient(180deg, rgba(40,90,155,.05) 1px, transparent 1px),
        #fbfdff;
      background-size: 30px 30px;
    }}
    .mermaid-row {{
      display: grid;
      grid-template-columns: minmax(190px, 1fr) 112px minmax(190px, 1fr);
      align-items: center;
      gap: 10px;
      min-width: 620px;
    }}
    .mermaid-node {{
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 48px;
      padding: 10px 12px;
      border: 1px solid #b8cbe2;
      border-radius: var(--radius);
      background: rgba(255, 255, 255, .94);
      color: #172033;
      font-weight: 650;
      line-height: 1.35;
      text-align: center;
      box-shadow: 0 8px 18px rgba(40, 90, 155, .10);
    }}
    .mermaid-connector {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
      min-height: 32px;
    }}
    .mermaid-connector .flow-arrow {{
      flex-basis: 38px;
      width: 38px;
    }}
    .mermaid-edge-label {{
      max-width: 72px;
      padding: 2px 6px;
      border: 1px solid #d5e0ec;
      border-radius: 999px;
      background: #ffffff;
      color: #285a9b;
      line-height: 1.25;
      text-align: center;
    }}
    .table-wrap {{
      overflow: auto;
      margin: 22px 0 26px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    }}
    table {{ width: 100%; border-collapse: collapse; min-width: 720px; background: white; font-size: 14px; line-height: 1.62; }}
    th, td {{ padding: 11px 13px; border-bottom: 1px solid var(--line); vertical-align: top; text-align: left; }}
    th {{ position: sticky; top: 0; background: var(--surface-soft); color: #263247; font-weight: 700; line-height: 1.45; }}
    td {{ color: #27364a; }}
    tbody tr:nth-child(even) td {{ background: #fbfdff; }}
    tbody tr:hover td {{ background: #f1f7f6; }}
    tr:last-child td {{ border-bottom: 0; }}
    .content ul, .content ol {{
      max-width: calc(var(--measure) + 8ch);
      margin: 13px 0 18px;
      padding-left: 26px;
    }}
    .content li {{
      margin: 6px 0;
      padding-left: 2px;
      color: #263247;
      line-height: 1.74;
    }}
    .content li::marker {{ color: var(--accent); font-weight: 700; }}
    .content li code, .content td code {{ font-size: 0.88em; }}
    .mobile-toggle {{ display: none; position: fixed; right: 16px; bottom: 16px; z-index: 20; background: var(--sidebar); box-shadow: var(--shadow); }}
    .progress {{ position: fixed; top: 0; left: 0; height: 3px; width: 0; background: var(--accent); z-index: 30; }}
    @media (max-width: 980px) {{
      .layout {{ display: block; }}
      .sidebar {{
        position: fixed;
        inset: 0 auto 0 0;
        z-index: 15;
        width: min(86vw, 340px);
        transform: translateX(-105%);
        transition: transform 0.2s ease;
      }}
      body.nav-open .sidebar {{ transform: translateX(0); }}
      .document {{ padding: 22px 16px 72px; }}
      .content {{ padding: 24px 18px; font-size: 15px; line-height: 1.74; }}
      .content h1 {{ max-width: none; font-size: 24px; margin-bottom: 18px; }}
      .content h2 {{ max-width: none; font-size: 20px; margin-top: 34px; }}
      .content h3 {{ max-width: none; font-size: 17px; }}
      .content p, .content ul, .content ol, blockquote {{ max-width: none; }}
      .content p {{ line-height: 1.76; }}
      table {{ font-size: 13.5px; }}
      .flow-node {{ max-width: 210px; }}
      .mermaid-row {{
        grid-template-columns: minmax(170px, 1fr) 74px minmax(170px, 1fr);
        min-width: 470px;
      }}
      .mermaid-edge-label {{ display: none; }}
      .architecture-board {{ padding: 12px; }}
      .architecture-head {{
        padding: 12px 13px;
        margin-bottom: 12px;
      }}
      .architecture-head strong {{ font-size: 19px; }}
      .architecture-layer {{
        grid-template-columns: 1fr;
        gap: 12px;
        padding: 14px;
      }}
      .layer-heading {{
        grid-template-columns: 38px minmax(0, 1fr);
        gap: 10px;
      }}
      .layer-number {{
        width: 36px;
        height: 36px;
      }}
      .component-grid,
      .component-grid.layer-storage,
      .component-grid.layer-service {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .component-card {{ min-height: 124px; }}
      .architecture-connector span {{
        max-width: min(78vw, 360px);
        text-align: center;
      }}
      .mobile-toggle {{ display: block; }}
    }}
    @media (max-width: 640px) {{
      .component-grid,
      .component-grid.layer-storage,
      .component-grid.layer-service {{
        grid-template-columns: 1fr;
      }}
      .component-card {{ min-height: auto; }}
    }}
    @media print {{
      .sidebar, .mobile-toggle, .progress, .heading-anchor, .copy-code {{ display: none !important; }}
      .layout {{ display: block; }}
      .document {{ padding: 0; }}
      .content {{ box-shadow: none; border: 0; padding: 0; }}
      body {{ background: white; }}
      .content p, .content li {{ color: #111827; }}
      .architecture-board {{ padding: 10pt; }}
      .architecture-layer {{ break-inside: avoid; box-shadow: none; }}
      .component-card {{ box-shadow: none; }}
      table {{ font-size: 10.5pt; }}
      a {{ color: inherit; }}
    }}
  </style>
</head>
<body>
  <div class="progress" id="progress"></div>
  <div class="layout">
    <aside class="sidebar" aria-label="PRD navigation">
      <div class="brand">
        <h1>多模态企业知识库平台 PRD</h1>
        <p>单文件 HTML · 侧边目录 · 由 <code>KB_Platform_PRD.md</code> 生成</p>
      </div>
      <div class="toolbox">
        <input class="search" id="tocSearch" type="search" placeholder="搜索目录">
        <div class="actions">
          <button type="button" id="expandTop">顶部</button>
          <button type="button" id="printDoc">打印</button>
        </div>
      </div>
      <nav class="toc" id="toc">
        {nav_html(nav)}
      </nav>
    </aside>
    <main class="document">
      <div class="doc-shell">
        <div class="meta-strip">
          <span class="badge">Generated: {generated_at}</span>
          <span class="badge">Source SHA256: {source_hash}</span>
          <span class="badge">Boundary: docs-only draft · no provider call</span>
        </div>
        <article class="content" id="content">
          {body}
        </article>
      </div>
    </main>
  </div>
  <button type="button" class="mobile-toggle" id="mobileToggle">目录</button>
  <script>
    const links = Array.from(document.querySelectorAll('.toc-link'));
    const sections = links.map(link => document.getElementById(link.getAttribute('href').slice(1))).filter(Boolean);
    const search = document.getElementById('tocSearch');
    const progress = document.getElementById('progress');

    function updateProgress() {{
      const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      progress.style.width = height > 0 ? `${{(scrollTop / height) * 100}}%` : '0';
    }}

    const observer = new IntersectionObserver((entries) => {{
      const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!visible) return;
      links.forEach(link => link.classList.toggle('active', link.getAttribute('href') === `#${{visible.target.id}}`));
    }}, {{ rootMargin: '-10% 0px -80% 0px', threshold: [0, 1] }});
    sections.forEach(section => observer.observe(section));
    window.addEventListener('scroll', updateProgress, {{ passive: true }});
    updateProgress();

    search.addEventListener('input', () => {{
      const q = search.value.trim().toLowerCase();
      links.forEach(link => {{
        link.style.display = !q || link.dataset.title.includes(q) ? '' : 'none';
      }});
    }});

    document.getElementById('expandTop').addEventListener('click', () => window.scrollTo({{ top: 0, behavior: 'smooth' }}));
    document.getElementById('printDoc').addEventListener('click', () => window.print());
    document.getElementById('mobileToggle').addEventListener('click', () => document.body.classList.toggle('nav-open'));
    links.forEach(link => link.addEventListener('click', () => document.body.classList.remove('nav-open')));
    document.querySelectorAll('.copy-code').forEach(button => {{
      button.addEventListener('click', async () => {{
        const code = button.closest('.codeblock').querySelector('code').innerText;
        try {{
          await navigator.clipboard.writeText(code);
          const original = button.textContent;
          button.textContent = '已复制';
          setTimeout(() => button.textContent = original, 1200);
        }} catch (error) {{
          button.textContent = '复制失败';
        }}
      }});
    }});
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="KB_Platform_PRD.md")
    parser.add_argument("--output", default="KB_Platform_PRD.html")
    args = parser.parse_args()

    source = Path(args.input)
    output = Path(args.output)
    markdown = source.read_text(encoding="utf-8")
    output.write_text(build_html(markdown, source), encoding="utf-8")
    print(f"generated {output} from {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
