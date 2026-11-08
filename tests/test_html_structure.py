"""A single mismatched closing tag once collapsed the whole dashboard layout. Catch that class of bug in CI."""
from html.parser import HTMLParser
from pathlib import Path

CONTAINERS = {"div", "button", "section", "aside", "header", "main", "nav", "form", "details", "ol", "ul", "table", "select", "label"}


class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag in CONTAINERS:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag not in CONTAINERS:
            return
        if not self.stack or self.stack[-1][0] != tag:
            opened = self.stack[-1] if self.stack else None
            self.errors.append(f"line {self.getpos()[0]}: </{tag}> closes {opened}")
            if self.stack and any(t == tag for t, _ in self.stack):
                while self.stack and self.stack.pop()[0] != tag:
                    pass
        else:
            self.stack.pop()


def test_index_html_tags_are_balanced():
    p = Balance()
    p.feed(Path(__file__).resolve().parent.parent.joinpath("app", "static", "index.html").read_text(encoding="utf-8"))
    assert not p.errors, p.errors[:5]
    assert not p.stack, f"unclosed tags: {p.stack[:5]}"
