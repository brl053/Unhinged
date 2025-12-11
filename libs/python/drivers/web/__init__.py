"""Web search and fetch driver.

@llm-type library.drivers.web
@llm-does search the web and fetch page content
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus

import requests
from lxml import html as lxml_html
from lxml.html import HtmlElement


@dataclass
class SearchResult:
    """A single search result."""

    title: str
    url: str
    snippet: str
    body: str = ""  # Populated if fetch_content=True


def search(
    query: str,
    max_results: int = 10,
    fetch_content: bool = True,
    max_content_chars: int = 4000,
) -> list[SearchResult]:
    """Search the web and optionally fetch page content.

    Uses Brave Search (no API key required).

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 10)
        fetch_content: Whether to fetch and extract page content (default: True)
        max_content_chars: Max characters to extract per page (default: 4000)

    Returns:
        List of SearchResult objects
    """
    results: list[SearchResult] = []

    try:
        url = f"https://search.brave.com/search?q={quote_plus(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        doc = lxml_html.fromstring(resp.text)

        # Extract result divs
        result_divs = doc.xpath('//div[@data-type="web"]')

        seen_urls: set[str] = set()
        for div in result_divs[: max_results * 2]:  # Get extra to filter dupes
            # Find link and title
            link_elem = div.xpath(".//a[@href]")
            if not link_elem:
                continue

            href = link_elem[0].get("href", "")
            if not href.startswith("http") or "brave.com" in href:
                continue
            if href in seen_urls:
                continue
            seen_urls.add(href)

            title_elem = div.xpath('.//div[contains(@class, "title")]//text()')
            title = " ".join(t.strip() for t in title_elem if t.strip())

            snippet_elem = div.xpath('.//div[contains(@class, "snippet")]//text()')
            snippet = " ".join(s.strip() for s in snippet_elem if s.strip())

            results.append(
                SearchResult(
                    title=title or href,
                    url=href,
                    snippet=snippet,
                )
            )

            if len(results) >= max_results:
                break

    except Exception:
        pass  # Return empty results on error

    if fetch_content:
        for result in results:
            result.body = _fetch_page_content(result.url, max_content_chars)

    return results


def _fetch_page_content(url: str, max_chars: int = 4000) -> str:
    """Fetch and extract text content from a URL.

    Uses simple heuristics to extract main content.
    """
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"},
        )
        response.raise_for_status()
        return _extract_text_from_html(response.text, max_chars)
    except Exception:
        return ""


def _extract_text_from_html(html_text: str, max_chars: int) -> str:
    """Extract text content from HTML."""
    from lxml.etree import ParserError

    try:
        doc = lxml_html.fromstring(html_text)
    except ParserError:
        return ""

    # Remove script and style elements
    for elem in doc.xpath("//script | //style | //nav | //footer | //header"):
        parent = elem.getparent()
        if parent is not None:
            parent.remove(elem)

    # Get text from body or main content areas
    text = _get_main_content_text(doc)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def _get_main_content_text(doc: HtmlElement) -> str:
    """Extract text from main content areas of a parsed HTML document."""
    for elem in doc.xpath("//article | //main | //div[@class='content'] | //body"):
        text: str = elem.text_content() or ""
        if text:
            return text.strip()
    content: str = doc.text_content() or ""
    return content


def search_as_text(
    query: str,
    max_results: int = 5,
    max_content_chars: int = 3000,
) -> str:
    """Search and return results as formatted text for LLM consumption.

    Args:
        query: Search query
        max_results: Number of results (default: 5)
        max_content_chars: Max chars per page (default: 3000)

    Returns:
        Formatted string with all search results
    """
    results = search(query, max_results=max_results, max_content_chars=max_content_chars)

    parts: list[str] = []
    for i, r in enumerate(results, 1):
        parts.append(f"[{i}] {r.title}")
        parts.append(f"    URL: {r.url}")
        if r.body:
            parts.append(f"    Content: {r.body[:max_content_chars]}")
        elif r.snippet:
            parts.append(f"    Snippet: {r.snippet}")
        parts.append("")

    return "\n".join(parts)
