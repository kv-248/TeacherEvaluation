from __future__ import annotations

import argparse
from pathlib import Path

import markdown
from weasyprint import CSS, HTML


def _css() -> str:
    return """
    @page {
      size: A4;
      margin: 18mm 16mm 18mm 16mm;
      @bottom-center {
        content: counter(page);
        font-family: "DejaVu Sans", Arial, sans-serif;
        font-size: 9pt;
        color: #5f6b73;
      }
    }

    body {
      font-family: "DejaVu Serif", Georgia, serif;
      color: #16242d;
      font-size: 10.5pt;
      line-height: 1.5;
      hyphens: auto;
    }

    h1, h2, h3, h4 {
      font-family: "DejaVu Sans", Arial, sans-serif;
      color: #16384d;
      page-break-after: avoid;
    }

    h1 {
      font-size: 22pt;
      margin: 0 0 4mm 0;
      text-align: center;
      line-height: 1.18;
      border-bottom: none;
    }

    h2 {
      font-size: 14pt;
      margin: 16pt 0 6pt 0;
      padding-bottom: 2pt;
      border-bottom: 1px solid #d3dde4;
    }

    h3 {
      font-size: 11.5pt;
      margin: 12pt 0 4pt 0;
    }

    p {
      margin: 0 0 8pt 0;
      text-align: justify;
      orphans: 2;
      widows: 2;
    }

    ul, ol {
      margin-top: 4pt;
      margin-bottom: 8pt;
    }

    code {
      font-family: "DejaVu Sans Mono", monospace;
      font-size: 9pt;
      background: #f4f7f9;
      padding: 1px 3px;
      border-radius: 3px;
    }

    pre {
      font-family: "DejaVu Sans Mono", monospace;
      font-size: 8.8pt;
      background: #f7fafb;
      border: 1px solid #d6e0e6;
      padding: 10px 12px;
      white-space: pre-wrap;
      page-break-inside: avoid;
    }

    a {
      color: #1f5e89;
      text-decoration: none;
    }

    img {
      display: block;
      max-width: 100%;
      margin: 10pt auto 6pt auto;
      page-break-inside: avoid;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin: 6pt 0 10pt 0;
      font-size: 9pt;
      page-break-inside: avoid;
    }

    th, td {
      border: 1px solid #c7d2d9;
      padding: 5px 6px;
      vertical-align: top;
    }

    th {
      background: #edf3f7;
      font-family: "DejaVu Sans", Arial, sans-serif;
      text-align: left;
      font-weight: 600;
    }

    .manuscript-label {
      text-align: center;
      font-family: "DejaVu Sans", Arial, sans-serif;
      font-size: 9pt;
      color: #52636f;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 12pt;
    }

    .abstract {
      border: 1px solid #cad6dd;
      background: #fbfcfd;
      padding: 10pt 12pt;
      margin: 0 0 8pt 0;
      page-break-inside: avoid;
    }

    .abstract p:last-child {
      margin-bottom: 0;
    }

    .keywords {
      font-family: "DejaVu Sans", Arial, sans-serif;
      font-size: 9pt;
      color: #324550;
      margin-bottom: 14pt;
    }

    .figure-caption,
    .table-caption {
      font-family: "DejaVu Sans", Arial, sans-serif;
      font-size: 8.9pt;
      color: #243742;
      margin: 3pt 0 11pt 0;
      text-align: left;
    }

    .references {
      margin: 6pt 0 0 0;
      padding-left: 1.2em;
    }

    .references li {
      margin: 0 0 6pt 0;
      padding-left: 0.2em;
      text-indent: -1.15em;
    }

    .appendix-note {
      font-size: 9.2pt;
      color: #415560;
    }
    """


def _build_html(title: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
  </head>
  <body>
    {body_html}
  </body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a journal-style markdown manuscript to PDF.")
    parser.add_argument("--input", type=Path, required=True, help="Path to the markdown manuscript.")
    parser.add_argument("--output", type=Path, required=True, help="Path to the output PDF.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = args.input.read_text(encoding="utf-8")
    body_html = markdown.markdown(
        text,
        extensions=[
            "tables",
            "fenced_code",
            "sane_lists",
        ],
        output_format="html5",
    )
    html = _build_html(args.input.stem, body_html)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html, base_url=str(args.input.parent.resolve())).write_pdf(
        str(args.output),
        stylesheets=[CSS(string=_css())],
    )
    print(f"PDF written to {args.output}")


if __name__ == "__main__":
    main()
