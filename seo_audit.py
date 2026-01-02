#!/usr/bin/env python3
"""Simple SEO audit tool that fetches a URL and generates a PDF report."""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
from fpdf import FPDF


@dataclass
class Issue:
    severity: str
    title: str
    details: str
    recommendation: str


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme:
        return f"https://{url}"
    return url


def fetch_page(url: str) -> tuple[requests.Response, float]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        )
    }
    start = time.perf_counter()
    response = requests.get(url, headers=headers, timeout=15)
    elapsed = time.perf_counter() - start
    return response, elapsed


def is_internal_link(base_netloc: str, href: str) -> bool:
    parsed = urlparse(href)
    if not parsed.netloc:
        return True
    return parsed.netloc == base_netloc


def gather_links(soup: BeautifulSoup, base_url: str) -> tuple[list[str], list[str]]:
    base_netloc = urlparse(base_url).netloc
    internal: list[str] = []
    external: list[str] = []
    for link in soup.find_all("a", href=True):
        href = link["href"].strip()
        if href.startswith("#") or href.lower().startswith("javascript:"):
            continue
        absolute = urljoin(base_url, href)
        if is_internal_link(base_netloc, absolute):
            internal.append(absolute)
        else:
            external.append(absolute)
    return internal, external


def visible_text_word_count(soup: BeautifulSoup) -> int:
    text = " ".join(soup.stripped_strings)
    return len(text.split())


def add_issue(issues: list[Issue], severity: str, title: str, details: str, recommendation: str) -> None:
    issues.append(Issue(severity, title, details, recommendation))


def analyze_seo(url: str, response: requests.Response, elapsed: float) -> tuple[dict, list[Issue]]:
    issues: list[Issue] = []
    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.title.string.strip() if soup.title and soup.title.string else ""
    meta_desc = soup.find("meta", attrs={"name": "description"})
    meta_desc_content = meta_desc.get("content", "").strip() if meta_desc else ""

    h1_tags = soup.find_all("h1")
    images = soup.find_all("img")
    missing_alt = [img for img in images if not img.get("alt") or not img.get("alt").strip()]

    canonical = soup.find("link", rel=lambda value: value and "canonical" in value.lower())
    viewport = soup.find("meta", attrs={"name": "viewport"})
    robots = soup.find("meta", attrs={"name": "robots"})
    html_lang = soup.find("html").get("lang") if soup.find("html") else ""

    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")
    structured_data = soup.find("script", type="application/ld+json")

    internal_links, external_links = gather_links(soup, url)
    word_count = visible_text_word_count(soup)

    summary = {
        "status_code": response.status_code,
        "load_time": elapsed,
        "title": title_tag,
        "meta_description": meta_desc_content,
        "h1_count": len(h1_tags),
        "image_count": len(images),
        "missing_alt_count": len(missing_alt),
        "canonical": canonical.get("href") if canonical else "",
        "viewport": bool(viewport),
        "robots": robots.get("content") if robots else "",
        "html_lang": html_lang,
        "internal_links": len(internal_links),
        "external_links": len(external_links),
        "word_count": word_count,
        "og_title": og_title.get("content") if og_title else "",
        "og_description": og_desc.get("content") if og_desc else "",
        "structured_data": bool(structured_data),
    }

    if response.status_code >= 400:
        add_issue(
            issues,
            "Critical",
            "Page returned an error status",
            f"HTTP status code: {response.status_code}",
            "Ensure the URL returns a 200 status code for crawlers.",
        )

    if elapsed > 3:
        add_issue(
            issues,
            "Warning",
            "Slow page response time",
            f"Load time is {elapsed:.2f} seconds.",
            "Optimize server response time and page assets.",
        )

    if not title_tag:
        add_issue(
            issues,
            "High",
            "Missing title tag",
            "No <title> tag found.",
            "Add a descriptive title between 50-60 characters.",
        )
    elif not 50 <= len(title_tag) <= 60:
        add_issue(
            issues,
            "Medium",
            "Title length outside best-practice range",
            f"Title length is {len(title_tag)} characters.",
            "Keep the title around 50-60 characters for optimal display.",
        )

    if not meta_desc_content:
        add_issue(
            issues,
            "High",
            "Missing meta description",
            "No meta description found.",
            "Add a concise meta description between 120-160 characters.",
        )
    elif not 120 <= len(meta_desc_content) <= 160:
        add_issue(
            issues,
            "Medium",
            "Meta description length outside best-practice range",
            f"Meta description length is {len(meta_desc_content)} characters.",
            "Aim for 120-160 characters for better search snippets.",
        )

    if len(h1_tags) == 0:
        add_issue(
            issues,
            "High",
            "Missing H1 heading",
            "No H1 heading found on the page.",
            "Add a single, descriptive H1 tag to clarify page topic.",
        )
    elif len(h1_tags) > 1:
        add_issue(
            issues,
            "Medium",
            "Multiple H1 headings",
            f"Found {len(h1_tags)} H1 headings.",
            "Limit to one H1 per page to avoid topic dilution.",
        )

    if missing_alt:
        add_issue(
            issues,
            "Medium",
            "Images missing alt text",
            f"{len(missing_alt)} images without alt attributes.",
            "Provide descriptive alt text to improve accessibility and SEO.",
        )

    if not canonical:
        add_issue(
            issues,
            "Medium",
            "Missing canonical tag",
            "No canonical link tag found.",
            "Add a canonical URL to prevent duplicate content issues.",
        )

    if robots and any(value in robots.get("content", "").lower() for value in ["noindex", "nofollow"]):
        add_issue(
            issues,
            "High",
            "Robots directive blocks indexing",
            f"Robots meta tag content: {robots.get('content')}",
            "Remove noindex/nofollow unless intentional.",
        )

    if not html_lang:
        add_issue(
            issues,
            "Low",
            "Missing html lang attribute",
            "<html> tag missing lang attribute.",
            "Add a language declaration, e.g., <html lang=\"en\">.",
        )

    if not viewport:
        add_issue(
            issues,
            "High",
            "Missing viewport meta tag",
            "No viewport meta tag detected.",
            "Add a viewport tag to ensure mobile-friendly rendering.",
        )

    if word_count < 300:
        add_issue(
            issues,
            "Low",
            "Low word count",
            f"Only {word_count} words of visible text found.",
            "Add more relevant content to improve topic depth.",
        )

    if not og_title or not og_desc:
        add_issue(
            issues,
            "Low",
            "Open Graph tags missing",
            "Missing og:title or og:description tags.",
            "Add Open Graph tags to improve social sharing previews.",
        )

    if not structured_data:
        add_issue(
            issues,
            "Low",
            "Structured data not detected",
            "No application/ld+json script found.",
            "Add structured data to enhance rich results eligibility.",
        )

    return summary, issues


def render_issue_list(pdf: FPDF, issues: Iterable[Issue]) -> None:
    for issue in issues:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"{issue.severity}: {issue.title}", ln=1)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, f"Details: {issue.details}")
        pdf.multi_cell(0, 6, f"Recommendation: {issue.recommendation}")
        pdf.ln(1)


def create_pdf_report(output_path: str, url: str, summary: dict, issues: list[Issue]) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "SEO Audit Report", ln=1)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"URL: {url}", ln=1)
    pdf.cell(0, 8, f"HTTP Status: {summary['status_code']}", ln=1)
    pdf.cell(0, 8, f"Load Time: {summary['load_time']:.2f}s", ln=1)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Summary Metrics", ln=1)

    pdf.set_font("Helvetica", "", 11)
    for label, value in [
        ("Title", summary["title"] or "(missing)"),
        ("Meta Description", summary["meta_description"] or "(missing)"),
        ("H1 Count", summary["h1_count"]),
        ("Images", summary["image_count"]),
        ("Images Missing Alt", summary["missing_alt_count"]),
        ("Canonical", summary["canonical"] or "(missing)"),
        ("Viewport Tag", "Yes" if summary["viewport"] else "No"),
        ("Robots Meta", summary["robots"] or "(missing)"),
        ("HTML Lang", summary["html_lang"] or "(missing)"),
        ("Internal Links", summary["internal_links"]),
        ("External Links", summary["external_links"]),
        ("Word Count", summary["word_count"]),
        ("OG Title", summary["og_title"] or "(missing)"),
        ("OG Description", summary["og_description"] or "(missing)"),
        ("Structured Data", "Yes" if summary["structured_data"] else "No"),
    ]:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(45, 6, f"{label}:")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, str(value))

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Detected Issues", ln=1)

    if not issues:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, "No major issues detected.", ln=1)
    else:
        render_issue_list(pdf, issues)

    pdf.output(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SEO audit tool that generates a PDF report."
    )
    parser.add_argument("url", help="Website URL to audit (e.g., https://example.com)")
    parser.add_argument(
        "-o",
        "--output",
        default="seo_report.pdf",
        help="Output PDF file path (default: seo_report.pdf)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    url = normalize_url(args.url)

    try:
        response, elapsed = fetch_page(url)
    except requests.RequestException as exc:
        print(f"Failed to fetch URL: {exc}", file=sys.stderr)
        return 1

    summary, issues = analyze_seo(url, response, elapsed)
    create_pdf_report(args.output, url, summary, issues)

    print(f"SEO report saved to {args.output}")
    print(f"Detected {len(issues)} issue(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
