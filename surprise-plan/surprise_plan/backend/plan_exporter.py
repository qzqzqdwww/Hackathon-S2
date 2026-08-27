"""Plan export — multiple formats, filename auto-detection."""
import json
import os
from pathlib import Path


SUPPORTED_FORMATS = {
    ".json": "json",
    ".md": "md",
    ".txt": "txt",
    ".html": "html",
}


def detect_format(filepath: str) -> str:
    """Detect format from file extension.

    Returns one of: json, md, txt, html
    """
    ext = Path(filepath).suffix.lower()
    return SUPPORTED_FORMATS.get(ext, "txt")


def export_plan(plan_data: dict, filepath: str) -> str:
    """Export plan to file. Format is auto-detected from extension.

    Supported extensions: .json, .md, .txt, .html

    Returns the absolute path of the written file.
    """
    fmt = detect_format(filepath)
    path = Path(filepath).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    plan = plan_data.get("plan", {})
    domain = plan.get("domain", plan_data.get("picked_domain", "?"))
    tagline = plan.get("tagline", "")
    why = plan.get("why_interesting", "")
    key_terms = plan.get("key_terms", [])
    fun_fact = plan.get("fun_fact", "")
    connections = plan.get("connections", [])
    learning_path = plan.get("learning_path", [])
    surprise = plan.get("surprise_factor", "")

    content = ""
    if fmt == "json":
        content = json.dumps(plan_data, ensure_ascii=False, indent=2)
    elif fmt == "html":
        content = _format_html(domain, tagline, why, key_terms, fun_fact,
                               connections, learning_path, surprise)
    elif fmt == "md":
        content = _format_markdown(domain, tagline, why, key_terms, fun_fact,
                                   connections, learning_path, surprise)
    else:  # plain text
        content = _format_plain(domain, tagline, why, key_terms, fun_fact,
                                connections, learning_path, surprise)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(path)


def _format_plain(domain, tagline, why, key_terms, fun_fact,
                  connections, learning_path, surprise) -> str:
    lines = [
        "=" * 60,
        f"  {domain}",
        "=" * 60,
        "",
    ]
    if tagline:
        lines += [tagline, ""]
    lines += [
        "为什么学这个",
        "-" * 40,
        why,
        "",
    ]
    if key_terms:
        lines += ["关键概念", "-" * 40]
        for t in key_terms:
            lines.append(f"  * {t}")
        lines.append("")
    if fun_fact:
        lines += ["冷知识", "-" * 40, fun_fact, ""]
    if connections:
        lines += ["与你兴趣的意外关联", "-" * 40]
        for c in connections:
            lines.append(f"  -> {c}")
        lines.append("")
    if learning_path:
        lines += ["四周学习路径", "-" * 40]
        for w in learning_path:
            lines.append(f"  第 {w.get('week', '?')} 周：{w.get('theme', '')}")
            for a in w.get("activities", []):
                lines.append(f"    - {a}")
            for r in w.get("resources", []):
                lines.append(f"    [BOOK] {r}")
            lines.append("")
    if surprise:
        lines += ["意外之喜", "-" * 40, surprise, ""]
    lines.append("=" * 60)
    return "\n".join(lines)


def _format_markdown(domain, tagline, why, key_terms, fun_fact,
                     connections, learning_path, surprise) -> str:
    lines = [f"# {domain}", ""]
    if tagline:
        lines += [f"*{tagline}*", ""]
    lines += ["## 为什么学这个", "", why, ""]
    if key_terms:
        lines += ["## 关键概念", ""]
        for t in key_terms:
            lines.append(f"- {t}")
        lines.append("")
    if fun_fact:
        lines += ["## 冷知识", "", f"> {fun_fact}", ""]
    if connections:
        lines += ["## 与你兴趣的意外关联", ""]
        for c in connections:
            lines.append(f"- {c}")
        lines.append("")
    if learning_path:
        lines += ["## 四周学习路径", ""]
        for w in learning_path:
            lines.append(f"### 第 {w.get('week', '?')} 周：{w.get('theme', '')}")
            lines.append("")
            for a in w.get("activities", []):
                lines.append(f"- {a}")
            lines.append("")
            for r in w.get("resources", []):
                lines.append(f"  *资源*: {r}")
            lines.append("")
    if surprise:
        lines += ["## 意外之喜", "", f"*{surprise}*", ""]
    return "\n".join(lines)


def _format_html(domain, tagline, why, key_terms, fun_fact,
                 connections, learning_path, surprise) -> str:
    def p(text): return f"<p>{text}</p>"
    def h2(text): return f"<h2>{text}</h2>"
    def h3(text): return f"<h3>{text}</h3>"

    body = f"<h1>{domain}</h1>"
    if tagline:
        body += f'<p class="tagline"><em>{tagline}</em></p>'
    body += h2("为什么学这个") + p(why.replace("\n", "<br>"))
    if key_terms:
        body += h2("关键概念") + "<ul>"
        for t in key_terms:
            body += f"<li>{t}</li>"
        body += "</ul>"
    if fun_fact:
        body += h2("冷知识") + f'<blockquote>{fun_fact}</blockquote>'
    if connections:
        body += h2("与你兴趣的意外关联") + "<ul>"
        for c in connections:
            body += f"<li>{c}</li>"
        body += "</ul>"
    if learning_path:
        body += h2("四周学习路径")
        for w in learning_path:
            body += h3(f"第 {w.get('week', '?')} 周：{w.get('theme', '')}")
            body += "<ul>"
            for a in w.get("activities", []):
                body += f"<li>{a}</li>"
            body += "</ul>"
            for r in w.get("resources", []):
                body += f'<p class="resource">资源: {r}</p>'
    if surprise:
        body += h2("意外之喜") + f'<p class="surprise"><em>{surprise}</em></p>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{domain} - Surprise-Plan</title>
<style>
body {{ max-width: 720px; margin: 0 auto; padding: 2rem;
       font-family: system-ui, -apple-system, sans-serif; line-height: 1.8; color: #222; }}
h1 {{ color: #e65100; border-bottom: 2px solid #e65100; padding-bottom: 0.5rem; }}
h2 {{ color: #f57c00; margin-top: 2rem; }}
h3 {{ color: #fb8c00; }}
.tagline {{ font-size: 1.1rem; color: #555; }}
blockquote {{ border-left: 4px solid #ffb74d; padding: 0.5rem 1rem;
             background: #fff3e0; margin: 1rem 0; }}
.resource {{ color: #666; font-size: 0.9rem; }}
.surprise {{ font-size: 1.05rem; color: #6a1b9a; }}
</style>
</head>
<body>
{body}
</body>
</html>"""
