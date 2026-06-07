"""A small book catalog agent, used to show how decomposition coverage works.

Four primitives: find a book, look up its author, look up its page count, and
format a response sentence from a template. Two decompositions are few-shot
examples of how a user expects two different question shapes to be answered.
"""

from __future__ import annotations

from difflib import get_close_matches

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive

CATALOG: dict[str, dict[str, str | int]] = {
    "Foundation":   {"author": "Isaac Asimov",       "pages": 244},
    "Neuromancer":  {"author": "William Gibson",      "pages": 271},
    "Dune":         {"author": "Frank Herbert",       "pages": 412},
    "1984":         {"author": "George Orwell",       "pages": 328},
    "Hyperion":     {"author": "Dan Simmons",         "pages": 482},
}


class BookCatalog(PlanExecute):

    @primitive(read_only=True)
    def find(self, query: str) -> str:
        """Find a book by title and return its canonical title."""
        hits = get_close_matches(query, CATALOG.keys(), n=1, cutoff=0.4)
        if not hits:
            raise ValueError(f"No book found for: {query}")
        return hits[0]

    @primitive(read_only=True)
    def author(self, title: str) -> str:
        """Return the author of a book given its canonical title."""
        return str(CATALOG[title]["author"])

    @primitive(read_only=True)
    def pages(self, title: str) -> int:
        """Return the page count of a book given its canonical title."""
        return int(CATALOG[title]["pages"])

    @primitive(read_only=True)
    def format(self, template: str, title: str = "", author: str = "", pages: int = 0) -> str:
        """Compose a response sentence by filling title, author, and pages into a template."""
        return template.format(title=title, author=author, pages=pages)

    @decomposition(intent="tell me about Foundation")
    def _example_about(self) -> str:
        title = self.find("Foundation")
        auth = self.author(title)
        pg = self.pages(title)
        return self.format("{title} by {author} has {pages} pages", title=title, author=auth, pages=pg)

    @decomposition(intent="how many pages is Neuromancer?")
    def _example_pages(self) -> str:
        title = self.find("Neuromancer")
        pg = self.pages(title)
        return self.format("{title} has {pages} pages", title=title, pages=pg)
