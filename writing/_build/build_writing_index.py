#!/usr/bin/env python3
"""Build writing/index.html from writing/_data YAML. Stdlib only."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKS_PATH = ROOT / "_data" / "works.yml"
PROFILES_PATH = ROOT / "_data" / "profiles.yml"
OUT_PATH = ROOT / "index.html"

STATUS_NOTE = {
    "in_press": "(in press)",
    "under_contract": "Under contract.",
    "conditionally_accepted": "Conditionally accepted.",
    "under_review": "Under review.",
    "submitted": "Submitted.",
}


def load_yaml_maps(path: Path, list_key: str) -> list[dict[str, str]]:
    """Load a list of maps emitted with JSON-quoted scalars."""
    rows: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    in_list = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line == f"{list_key}:":
            in_list = True
            continue
        if not in_list:
            continue
        if line.startswith("  - "):
            if current is not None:
                rows.append(current)
            current = {}
            line = "    " + line[4:]
        if current is None:
            raise SystemExit(f"FAIL: scalar before first item in {path}")
        if ": " not in line:
            raise SystemExit(f"FAIL: cannot parse {path}: {line}")
        key, value = line.strip().split(": ", 1)
        current[key] = json.loads(value)
    if current is not None:
        rows.append(current)
    if not rows:
        raise SystemExit(f"FAIL: no rows in {path} under {list_key}")
    return rows


def locator_text(row: dict[str, str]) -> str:
    volume = row.get("volume") or ""
    issue = row.get("issue") or ""
    pages = row.get("pages") or ""
    if volume and issue and pages:
        return (
            f"{html.escape(volume, quote=False)}"
            f"({html.escape(issue, quote=False)}):"
            f"{html.escape(pages, quote=False)}"
        )
    if volume and issue:
        return f"{html.escape(volume, quote=False)}({html.escape(issue, quote=False)})"
    if volume and pages:
        return f"{html.escape(volume, quote=False)}:{html.escape(pages, quote=False)}"
    if volume:
        return html.escape(volume, quote=False)
    if issue and pages:
        return f"{html.escape(issue, quote=False)}:{html.escape(pages, quote=False)}"
    if pages:
        return html.escape(pages, quote=False)
    return ""


def citation_core(row: dict[str, str]) -> str:
    authors = html.escape(row.get("authors", ""), quote=False).rstrip(".")
    year = html.escape(row.get("year", ""), quote=False)
    title = html.escape(row.get("title", ""), quote=False)
    venue = html.escape(row.get("venue", ""), quote=False)
    extra = html.escape((row.get("extra") or "").strip(), quote=False)
    isbn = (row.get("isbn") or "").strip()
    locator = locator_text(row)
    status_note = STATUS_NOTE.get(row.get("status") or "", "")
    year_bit = f". {year}." if year else "."
    if row.get("section") == "books":
        core = f"{authors}{year_bit} <em>{title}</em>."
        if venue:
            core = f"{core} {venue}."
        if extra:
            core = f"{core} {extra}"
        if isbn:
            core = f"{core} ISBN: {html.escape(isbn, quote=False)}"
        if status_note:
            core = f"{core} {html.escape(status_note, quote=False)}"
        return core
    if venue:
        core = f"{authors}{year_bit} “{title}.” <em>{venue}</em>"
        if locator:
            core = f"{core} {locator}."
        else:
            core = f"{core}."
    else:
        core = f"{authors}{year_bit} “{title}.”"
        if locator:
            core = f"{core} {locator}."
    if extra:
        core = f"{core} {extra}"
    if status_note:
        core = f"{core} {html.escape(status_note, quote=False)}"
    return core


def _append_link(bits: list[str], seen: set[str], href: str, label: str = "") -> None:
    key = href.rstrip("/")
    if not href or key in seen:
        return
    text = label or href
    bits.append(
        f'<a href="{html.escape(href, quote=True)}">{html.escape(text, quote=False)}</a>'
    )
    seen.add(key)


def link_bits(row: dict[str, str]) -> str:
    bits: list[str] = []
    seen: set[str] = set()
    doi = (row.get("doi") or "").strip()
    if doi:
        _append_link(bits, seen, f"https://doi.org/{doi}")
    url = (row.get("url") or "").strip()
    if url and "doi.org/" not in url:
        _append_link(bits, seen, url)
    alt = (row.get("alt_url") or "").strip()
    if alt and "doi.org/" not in alt:
        _append_link(bits, seen, alt)
    hosted = (row.get("hosted_path") or "").strip()
    if hosted:
        href = (
            hosted
            if hosted.startswith("http")
            else f"https://computationalethnography.org{hosted}"
        )
        _append_link(bits, seen, href)
    podcast = (row.get("podcast_url") or "").strip()
    if podcast:
        _append_link(bits, seen, podcast, "Podcast")
    accolade = (row.get("accolade_url") or "").strip()
    if accolade:
        label = (row.get("accolade_label") or "").strip() or accolade
        _append_link(bits, seen, accolade, label)
    if not bits:
        return ""
    return " " + " ".join(bits)


def render_item(row: dict[str, str]) -> str:
    work_id = (row.get("id") or "").strip()
    id_attr = f' id="{html.escape(work_id, quote=True)}"' if work_id else ""
    return f"<li{id_attr}>{citation_core(row)}{link_bits(row)}</li>"


def sort_rows(
    rows: list[dict[str, str]],
    ascending: bool = False,
) -> list[dict[str, str]]:
    def key(row: dict[str, str]) -> tuple:
        title = row.get("title", "")
        year = int(row.get("year") or 0)
        if ascending:
            return (year, title)
        return (-year, title)

    return sorted(rows, key=key)


def render_list(
    rows: list[dict[str, str]],
    ascending: bool = False,
) -> str:
    items = "\n".join(render_item(r) for r in sort_rows(rows, ascending=ascending))
    return f'<ul class="works">\n{items}\n</ul>'


CULTURE_SEE_ALSO = (
    ("rsf-pain-2024", "Abramson et al. 2024"),
    ("asr-2026", "Li, Dohan, and Abramson 2026"),
    ("end-game-2015", "Abramson 2015"),
    ("who-are-the-clients-2009", "Abramson 2009"),
)


def culture_see_also_html(works: list[dict[str, str]]) -> str:
    known = {row.get("id") for row in works}
    bits: list[str] = []
    for work_id, label in CULTURE_SEE_ALSO:
        if work_id not in known:
            raise SystemExit(f"FAIL: see-also missing work {work_id}")
        bits.append(
            f'<a href="#{html.escape(work_id, quote=True)}">'
            f"{html.escape(label, quote=False)}</a>"
        )
    return f'<p class="see-also">See also {"; ".join(bits)}.</p>'


def footer_html(profiles: list[dict[str, str]]) -> str:
    links = []
    for row in profiles:
        href = (row.get("href") or "").strip()
        label = row.get("label") or ""
        if not href:
            continue
        rel = (row.get("rel") or "").strip()
        rel_attr = f' rel="{html.escape(rel, quote=True)}"' if rel else ""
        links.append(
            f'<a href="{html.escape(href, quote=True)}"{rel_attr}>{html.escape(label, quote=False)}</a>'
        )
    inner = " · ".join(links)
    return f'<footer class="hub-foot">{inner}</footer>'


def page_html(works: list[dict[str, str]], profiles: list[dict[str, str]]) -> str:
    books = [r for r in works if r.get("section") == "books"]
    health = [
        r
        for r in works
        if r.get("section") == "articles" and r.get("topic") == "health_inequality"
    ]
    culture = [
        r
        for r in works
        if r.get("section") == "articles" and r.get("topic") == "culture"
    ]
    ai_ml = [
        r
        for r in works
        if r.get("section") == "articles"
        and r.get("topic") == "methods"
        and r.get("method_group") == "ai_ml"
    ]
    other = [
        r
        for r in works
        if r.get("section") == "articles"
        and r.get("topic") == "methods"
        and r.get("method_group") == "other"
    ]
    commentary = [r for r in works if r.get("section") == "commentary"]
    curricula = [r for r in works if r.get("section") == "curricula"]
    software = [r for r in works if r.get("section") == "software"]
    required = {
        "books": books,
        "health_inequality": health,
        "culture": culture,
        "ai_ml": ai_ml,
        "other": other,
        "commentary": commentary,
        "curricula": curricula,
        "software": software,
    }
    for key, rows in required.items():
        if not rows:
            raise SystemExit(f"FAIL: missing section {key}")
    body = "\n\n".join(
        [
            f"<h2>Books</h2>\n{render_list(books, ascending=True)}",
            "<h2>Articles</h2>",
            f"<h3>Health and Inequality</h3>\n{render_list(health)}",
            (
                "<h3>Theory (Culture and Action)</h3>\n"
                f"{culture_see_also_html(works)}\n"
                f"{render_list(culture)}"
            ),
            "<h3>Methods</h3>",
            f"<h4>AI and Machine Learning</h4>\n{render_list(ai_ml)}",
            (
                "<h4>Comparative Ethnography and Logics of Inquiry</h4>\n"
                f"{render_list(other)}"
            ),
            f"<h2>Blogs and Commentary</h2>\n{render_list(commentary)}",
            f"<h2>Public Methods Resources</h2>\n{render_list(curricula)}",
            f"<h2>Software and Code</h2>\n{render_list(software)}",
        ]
    )
    return f"""---
layout: null
---
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Writing</title>
<link rel="canonical" href="https://computationalethnography.org/writing/">
<meta name="author" content="Corey M. Abramson">
<style>
  body {{
    font-family: sans-serif;
    background-color: #0d1117;
    color: #c9d1d9;
    padding: 2em;
    line-height: 1.55;
    max-width: 52rem;
  }}
  a {{ color: #58a6ff; }}
  h1 {{ font-size: 1.7rem; margin: 0.4rem 0 1rem; }}
  h2 {{ font-size: 1.2rem; margin: 1.8rem 0 0.7rem; }}
  h3 {{ font-size: 1.05rem; margin: 1.2rem 0 0.5rem; }}
  h4 {{ font-size: 1rem; margin: 1rem 0 0.4rem; font-weight: 600; }}
  ul.works {{ padding-left: 1.2rem; }}
  ul.works li {{ margin: 0 0 0.85rem; }}
  .see-also {{ color: #8b949e; font-size: 0.95rem; margin: 0 0 0.6rem; }}
  .hub-foot {{ margin-top: 2rem; color: #8b949e; font-size: 0.85rem; }}
  .hub-foot a {{ color: #8b949e; }}
  .lab-nav {{ margin: 0 0 1rem; }}
</style>
</head>
<body>
<p class="lab-nav"><a href="https://computationalethnography.org/">The Computational Ethnography Lab (CEL)</a></p>
<h1>Writing</h1>
{body}
{footer_html(profiles)}
</body>
</html>
"""


def main() -> None:
    works = load_yaml_maps(WORKS_PATH, "works")
    profiles = load_yaml_maps(PROFILES_PATH, "profiles")
    for work_id in (
        "ai-wiki-2026",
        "opensource-teaching",
        "methods-blog-coding-simplified-2022",
        "methods-blog-subsetting-2022",
    ):
        rows = [r for r in works if r.get("id") == work_id]
        if len(rows) != 1 or rows[0].get("section") != "curricula":
            raise SystemExit(f"FAIL: {work_id} must be section curricula, not articles")
    text = page_html(works, profiles)
    if not text.startswith("---\nlayout: null\n---\n"):
        raise SystemExit("FAIL: hub missing layout: null")
    if 'href=""' in text:
        raise SystemExit("FAIL: empty href")
    if "reporter.nih.gov" in text.lower():
        raise SystemExit("FAIL: NIH RePORTER link in hub")
    allowed_myncbi = (
        "https://www.ncbi.nlm.nih.gov/myncbi/corey.abramson.1/bibliography/public/"
    )
    if "ncbi.nlm.nih.gov/myncbi" in text.lower() and allowed_myncbi not in text:
        raise SystemExit("FAIL: unexpected NCBI My Bibliography URL")
    locked = [
        "https://www.linkedin.com/in/corey-m-abramson-328926153",
        "https://cmabramson.com",
        "https://github.com/Computational-Ethnography-Lab",
        "user=vBMsaYwAAAAJ",
        allowed_myncbi,
        "/writing/qualitative-research-in-an-era-of-ai/",
        "/writing/from-carbon-paper-to-code/",
        ">Books<",
        ">Articles<",
        ">Health and Inequality<",
        ">Theory (Culture and Action)<",
        ">Methods<",
        ">AI and Machine Learning<",
        ">Comparative Ethnography and Logics of Inquiry<",
        ">Blogs and Commentary<",
        ">Public Methods Resources<",
        ">Software and Code<",
        "https://github.com/Computational-Ethnography-Lab/ai-wiki",
        "https://github.com/Computational-Ethnography-Lab/teaching",
        "https://aihorizons.io/qualitative-coding-simplified/",
        "https://aihorizons.io/sub-setting-qualitative-data-for-machine-learning-or-export/",
        "Everything You Wanted to Know About AI (in social science)",
        "Qualitative Coding Simplified",
        "Sub-setting Qualitative Data for Machine Learning",
        "Guidelines for Conducting and Presenting Qualitative Research in PCOR",
        'href="#rsf-pain-2024"',
        'href="#asr-2026"',
        'href="#end-game-2015"',
        'href="#who-are-the-clients-2009"',
        "sagesociology.libsyn.com",
        "cmap_qdpx_converter",
        "ASA2022_Workshop",
        "https://doi.org/10.1146/annurev-soc-011824-104836",
        "https://doi.org/10.1177/00031224261448220",
        "https://doi.org/10.7758/RSF.2024.10.5.02",
        "9780674979680",
        "9780190608491",
        "Unequal Until the End",
        "cmabramson.com/resources",
    ]
    for needle in locked:
        if needle == "cmabramson.com/resources":
            if needle in text:
                raise SystemExit("FAIL: personal-site Resources chrome on hub")
            continue
        if needle not in text:
            raise SystemExit(f"FAIL: missing {needle}")
    if ">Other methods<" in text:
        raise SystemExit("FAIL: residual Other methods heading")
    if ">Software<" in text:
        raise SystemExit("FAIL: residual Software heading")
    if ">Featured<" in text:
        raise SystemExit("FAIL: Featured heading should not appear")
    if ">In progress<" in text or "Unequal Anatomies" in text:
        raise SystemExit("FAIL: In progress section should not appear")
    if "Citations follow the 2026 CV" in text:
        raise SystemExit("FAIL: cut intro still present")
    if text.count("From Carbon Paper to Code") != 1:
        raise SystemExit("FAIL: Contexts should appear once")
    articles_block = text.split("<h2>Blogs and Commentary</h2>")[0]
    if "ai-wiki" in articles_block or "Everything You Wanted to Know About AI" in articles_block:
        raise SystemExit("FAIL: wiki listed under Articles")
    if "Computational Analysis for Qualitative Data" in articles_block:
        raise SystemExit("FAIL: teaching repo listed under Articles")
    if "Qualitative Coding Simplified" in articles_block:
        raise SystemExit("FAIL: methods blog listed under Articles")
    OUT_PATH.write_text(text, encoding="utf-8")
    print(f"wrote {OUT_PATH} bytes={OUT_PATH.stat().st_size} works={len(works)}")


if __name__ == "__main__":
    main()
