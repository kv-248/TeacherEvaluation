"""Render a thesis-quality PDF from a markdown source with mermaid diagrams.

Pre-renders mermaid code blocks to PNG via mmdc, converts the resulting
markdown to HTML with the report stylesheet, then prints to PDF with
Microsoft Edge in headless mode. Designed to work on Windows without
WeasyPrint / GTK3 runtime dependencies.

Usage:
    python docs/render_thesis_pdf.py \\
        --input docs/thesis_research_report.md \\
        --output docs/thesis_research_report.pdf
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import markdown


MMDC_CMD = "mmdc.cmd" if Path("C:/Windows").exists() else "mmdc"
EDGE_CANDIDATES = [
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
]


def _find_edge() -> Path:
    for candidate in EDGE_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Microsoft Edge not found in standard locations.")


def _find_mmdc() -> str:
    for name in ("mmdc.cmd", "mmdc"):
        located = shutil.which(name)
        if located:
            return located
    npm_prefix = Path.home() / "AppData" / "Roaming" / "npm" / "mmdc.cmd"
    if npm_prefix.exists():
        return str(npm_prefix)
    raise FileNotFoundError("mmdc (mermaid-cli) not found. Install with: npm i -g @mermaid-js/mermaid-cli")


MERMAID_BLOCK = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)


def _render_mermaid_blocks(markdown_text: str, figures_dir: Path) -> str:
    figures_dir.mkdir(parents=True, exist_ok=True)
    mmdc = _find_mmdc()
    blocks = list(MERMAID_BLOCK.finditer(markdown_text))
    if not blocks:
        return markdown_text

    config_file = figures_dir / "mmdc_config.json"
    config_file.write_text('{"theme":"default","themeVariables":{"fontFamily":"Arial, sans-serif"}}', encoding="utf-8")

    replacements: list[tuple[int, int, str]] = []
    for idx, match in enumerate(blocks, start=1):
        mmd_source = match.group(1)
        mmd_path = figures_dir / f"figure_{idx:02d}.mmd"
        png_path = figures_dir / f"figure_{idx:02d}.png"
        mmd_path.write_text(mmd_source, encoding="utf-8")
        cmd = [
            mmdc,
            "-i", str(mmd_path),
            "-o", str(png_path),
            "-c", str(config_file),
            "-b", "white",
            "-s", "3",
            "-w", "1400",
        ]
        print(f"[mermaid] rendering figure {idx}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[mermaid] FAILED figure {idx}: {result.stderr}")
            raise RuntimeError(f"mmdc failed on figure {idx}")
        rel = png_path.relative_to(figures_dir.parent).as_posix()
        replacement = f'<div class="figure-wrapper"><img src="{rel}" alt="Figure {idx}" class="mermaid-figure" /></div>'
        replacements.append((match.start(), match.end(), replacement))

    out = []
    cursor = 0
    for start, end, repl in replacements:
        out.append(markdown_text[cursor:start])
        out.append(repl)
        cursor = end
    out.append(markdown_text[cursor:])
    return "".join(out)


def _css() -> str:
    return """
    @page {
      size: A4;
      margin: 20mm 18mm 22mm 18mm;
    }

    @page :not(:first) {
      @top-center {
        content: "AUTOMATED NONVERBAL TEACHER EVALUATION";
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 7.5pt;
        font-weight: 400;
        letter-spacing: 0.18em;
        color: #999999;
      }
    }

    body {
      font-family: "Palatino Linotype", "Book Antiqua", "Palatino", Georgia, serif;
      color: #2c3e50;
      font-size: 11pt;
      line-height: 1.60;
      max-width: 170mm;
      margin: 0 auto;
    }

    h1, h2, h3, h4 {
      font-family: "Palatino Linotype", "Book Antiqua", "Palatino", Georgia, serif;
      color: #1a252f;
      page-break-after: avoid;
    }

    h1 {
      font-size: 24pt;
      font-weight: 800;
      letter-spacing: -0.01em;
      border-bottom: 2.5px solid #1f4068;
      padding-bottom: 12px;
      margin-bottom: 26px;
      margin-top: 0;
    }

    h2 {
      font-size: 14pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-top: 28px;
      margin-bottom: 4px;
      padding-bottom: 0;
      border-bottom: none;
    }

    h2::after {
      content: "";
      display: block;
      margin-top: 6px;
      border-bottom: 1.5px solid #dce0e4;
    }

    h3 {
      font-size: 12pt;
      font-weight: 700;
      font-style: italic;
      margin-top: 18px;
      margin-bottom: 6px;
      color: #1a252f;
    }

    h4 {
      font-size: 11pt;
      font-weight: 700;
      font-style: normal;
      margin-top: 14px;
      margin-bottom: 4px;
      color: #1a252f;
    }

    p {
      margin: 0 0 10px 0;
      text-align: justify;
    }

    ul, ol {
      margin: 6px 0 12px 0;
      padding-left: 26px;
    }

    li {
      margin-bottom: 3px;
    }

    p, li, table, figure, pre {
      page-break-inside: avoid;
    }

    tr.signal-desc-row td {
      background: #f8f9fa;
      color: #5e6d7a;
      font-size: 8.5pt;
      font-style: italic;
      padding: 3px 10px 8px 10px;
      border-top: none;
    }

    code {
      font-family: "Consolas", "DejaVu Sans Mono", monospace;
      font-size: 9.5pt;
      background: #f4f6f8;
      padding: 1px 4px;
      border-radius: 2px;
      color: #1f4068;
    }

    pre {
      background: #f8f9fa;
      border: 1px solid #dce0e4;
      border-left: 3px solid #1f4068;
      padding: 10px 14px;
      margin: 10px 0 14px 0;
      overflow: hidden;
      white-space: pre-wrap;
      font-size: 9.5pt;
      line-height: 1.4;
    }

    pre code {
      background: transparent;
      color: inherit;
      padding: 0;
      border-radius: 0;
    }

    a {
      color: #1f4068;
      text-decoration: none;
    }

    blockquote {
      border-left: 4px solid #1f4068;
      background: #f0f4f8;
      margin: 12px 0;
      padding: 10px 16px;
      color: #1a252f;
      font-style: italic;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin: 10px 0 18px 0;
      font-size: 10pt;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
    }

    th, td {
      border: 1px solid #dce0e4;
      padding: 7px 10px;
      vertical-align: top;
      text-align: left;
    }

    th {
      background: #f8f9fa;
      font-weight: 700;
      color: #1a252f;
      border-top: 2px solid #1f4068;
    }

    tr:nth-child(even) td {
      background: #f4f6f8;
    }

    .figure-wrapper {
      text-align: center;
      margin: 18px 0;
      page-break-inside: avoid;
    }

    img.mermaid-figure {
      max-width: 90%;
      max-height: 120mm;
      display: inline-block;
      border: 1px solid #dce0e4;
      padding: 6px;
      background: #ffffff;
      box-sizing: border-box;
    }

    /* Inline keyframe images (not from mermaid) — §6 qualitative-validation frames */
    img[src^="accurate_frames/"] {
      display: block;
      max-width: 115mm;
      width: 115mm;
      height: auto;
      margin: 12px auto 4px auto;
      border: 1px solid #dce0e4;
      padding: 3px;
      background: #ffffff;
      page-break-inside: avoid;
    }

    /* Full-width landmark overlay illustration in §4.4 */
    img[src$="mediapipe_overlay_example.jpg"] {
      max-width: 148mm;
      width: 148mm;
    }

    /* UI screenshot figures in §5.7 — wider to preserve dashboard legibility */
    img[src$="ui_demo_upload.png"],
    img[src$="ui_results_scorecard.png"],
    img[src$="ui_detailed_coaching.png"] {
      max-width: 148mm;
      width: 148mm;
    }

    /* The italicised caption paragraph immediately after a keyframe */
    img[src^="accurate_frames/"] + em,
    p > img[src^="accurate_frames/"] + em {
      display: block;
      text-align: center;
      font-size: 9pt;
      font-family: "Segoe UI", Arial, sans-serif;
      color: #5e6d7a;
      margin-top: 0;
    }

    /* Table of contents */
    .toc {
      background: #f8f9fa;
      border: 1px solid #dce0e4;
      border-left: 3px solid #1f4068;
      padding: 14px 18px 14px 22px;
      margin: 14px 0 24px 0;
      page-break-inside: avoid;
    }

    .toc ul {
      margin: 4px 0;
      padding-left: 18px;
    }

    .toc li {
      margin-bottom: 4px;
      font-family: "Segoe UI", Arial, sans-serif;
      font-size: 9.5pt;
      color: #2c3e50;
    }

    .toc a {
      color: #1f4068;
      text-decoration: none;
    }

    /* Zero-height block to break .figure-wrapper + p caption selector */
    .section-break {
      display: block;
      height: 0;
      margin: 0;
      padding: 0;
    }

    /* Figure caption paragraph after mermaid wrapper */
    .figure-wrapper + p {
      text-align: center;
      font-size: 9pt;
      font-family: "Segoe UI", Arial, sans-serif;
      color: #5e6d7a;
      margin-top: -6px;
      margin-bottom: 18px;
    }
    """


def _build_html(title: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>{_css()}</style>
  </head>
  <body>
    {body_html}
  </body>
</html>
"""


def _print_with_edge(html_path: Path, pdf_path: Path) -> None:
    edge = _find_edge()
    url = html_path.resolve().as_uri()
    if pdf_path.exists():
        try:
            pdf_path.unlink()
        except PermissionError:
            raise RuntimeError(
                f"Cannot overwrite {pdf_path} — close any PDF viewer holding the file open and retry."
            )
    user_data_dir = tempfile.mkdtemp(prefix="edge_headless_")
    cmd = [
        str(edge),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--user-data-dir={user_data_dir}",
        f"--print-to-pdf={pdf_path.resolve()}",
        url,
    ]
    print(f"[edge] printing {html_path.name} -> {pdf_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if not pdf_path.exists():
        print(f"[edge] stdout: {result.stdout}")
        print(f"[edge] stderr: {result.stderr}")
        raise RuntimeError("Edge headless print did not produce a PDF")
    shutil.rmtree(user_data_dir, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a markdown thesis report to PDF (mermaid-aware).")
    parser.add_argument("--input", type=Path, required=True, help="Markdown source file.")
    parser.add_argument("--output", type=Path, required=True, help="Destination PDF path.")
    parser.add_argument(
        "--keep-html",
        action="store_true",
        help="Keep the intermediate HTML next to the PDF for debugging.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    src_text = args.input.read_text(encoding="utf-8")

    work_dir = args.output.parent / "_thesis_pdf_build"
    work_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = work_dir / "figures"

    # Sync any checked-in image dirs referenced by the markdown (relative to docs/)
    # into the build dir so their relative paths resolve from the rendered HTML.
    for named in ("accurate_frames",):
        src_dir = args.input.parent / named
        if src_dir.is_dir():
            dst_dir = work_dir / named
            if dst_dir.exists():
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)

    preprocessed = _render_mermaid_blocks(src_text, figures_dir)
    body_html = markdown.markdown(
        preprocessed,
        extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list", "md_in_html"],
        output_format="html5",
    )
    html = _build_html(args.input.stem, body_html)

    html_path = work_dir / f"{args.input.stem}.html"
    html_path.write_text(html, encoding="utf-8")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    _print_with_edge(html_path, args.output)

    if not args.keep_html:
        pass
    print(f"PDF written to {args.output.resolve()}")


if __name__ == "__main__":
    main()
