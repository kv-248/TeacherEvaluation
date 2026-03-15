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
    }

    body {
      font-family: "DejaVu Serif", Georgia, serif;
      color: #17202a;
      font-size: 11pt;
      line-height: 1.45;
    }

    h1, h2, h3, h4 {
      font-family: "DejaVu Sans", Arial, sans-serif;
      color: #0b3954;
      page-break-after: avoid;
    }

    h1 {
      font-size: 24pt;
      border-bottom: 3px solid #0b3954;
      padding-bottom: 8px;
      margin-bottom: 20px;
    }

    h2 {
      font-size: 17pt;
      margin-top: 24px;
      border-bottom: 1px solid #b8c6d1;
      padding-bottom: 4px;
    }

    h3 {
      font-size: 13.5pt;
      margin-top: 16px;
    }

    p, ul, ol, table, figure, pre {
      page-break-inside: avoid;
    }

    code {
      font-family: "DejaVu Sans Mono", monospace;
      font-size: 9.5pt;
      background: #f4f7f9;
      padding: 1px 3px;
      border-radius: 3px;
    }

    pre {
      background: #f4f7f9;
      border: 1px solid #d7e0e6;
      padding: 10px;
      overflow: hidden;
      white-space: pre-wrap;
    }

    a {
      color: #0b5394;
      text-decoration: none;
    }

    img {
      max-width: 100%;
      display: block;
      margin: 10px auto 16px auto;
      border: 1px solid #d7e0e6;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin: 10px 0 16px 0;
      font-size: 9.6pt;
    }

    th, td {
      border: 1px solid #c8d4dc;
      padding: 6px 7px;
      vertical-align: top;
    }

    th {
      background: #eaf2f8;
      font-family: "DejaVu Sans", Arial, sans-serif;
      text-align: left;
    }

    blockquote {
      border-left: 4px solid #9fb3c8;
      margin-left: 0;
      padding-left: 12px;
      color: #3e5164;
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
    parser = argparse.ArgumentParser(description="Render a markdown research report to PDF.")
    parser.add_argument("--input", type=Path, required=True, help="Path to the markdown report.")
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
            "toc",
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
