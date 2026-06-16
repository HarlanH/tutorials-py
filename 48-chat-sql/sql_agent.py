"""SQLAgent: translates a natural language question into SQL and runs it.

The caller passes the full database schema as part of the task string so the
agent can write correct SQL in one shot. The only primitive is run_query.
"""

from __future__ import annotations

import re
import sqlite3

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import decomposition, primitive

MAX_ROWS = 10
COL_WIDTH = 50


class SQLAgent(PlanExecute):

    def __init__(self, db_path: str, llm) -> None:
        super().__init__(llm=llm)
        self._conn = sqlite3.connect(db_path)

    def full_schema(self) -> str:
        """Return a compact schema string for every table."""
        tables = self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        lines = []
        for (table,) in tables:
            cols = self._conn.execute(f"PRAGMA table_info({table})").fetchall()
            fks = self._conn.execute(f"PRAGMA foreign_key_list({table})").fetchall()
            fk_map = {fk[3]: f"{fk[2]}.{fk[4]}" for fk in fks}
            col_parts = [
                f"{col[1]} -> {fk_map[col[1]]}" if col[1] in fk_map else col[1]
                for col in cols
            ]
            lines.append(f"{table}({', '.join(col_parts)})")
        return "\n".join(lines)

    @decomposition(
        intent="Who are the top 5 artists by total sales?",
        expanded_intent=(
            "Join artists → albums → tracks → invoice_items to sum revenue. "
            "Always GROUP BY a.Name (not ArtistId) to avoid ambiguous column errors. "
            "Always JOIN customers using e.EmployeeId = c.SupportRepId, not SupportRepId = SupportRepId."
        ),
    )
    def _example(self):
        return self.run_query(
            "SELECT a.Name, SUM(ii.UnitPrice * ii.Quantity) AS TotalSales "
            "FROM artists a "
            "JOIN albums al ON a.ArtistId = al.ArtistId "
            "JOIN tracks t ON al.AlbumId = t.AlbumId "
            "JOIN invoice_items ii ON t.TrackId = ii.TrackId "
            "GROUP BY a.Name "
            "ORDER BY TotalSales DESC "
            "LIMIT 5"
        )

    @primitive(read_only=True)
    def run_query(self, sql: str) -> str:
        """Execute a SQL SELECT query and return the results as a formatted table."""
        # Remove stray bare numbers on their own line (e.g. "LIMIT 5\n6")
        sql = re.sub(r'\n\d+\s*$', '', sql.strip())
        try:
            cursor = self._conn.execute(sql)
        except sqlite3.Error as e:
            return f"SQL error: {e}"
        rows = cursor.fetchmany(MAX_ROWS)
        if not rows:
            return "(no results)"
        headers = [d[0] for d in cursor.description]
        widths = [
            min(COL_WIDTH, max(len(h), max(len(str(r[i])) for r in rows)))
            for i, h in enumerate(headers)
        ]
        sep = "  "
        fmt = sep.join(f"{{:<{w}}}" for w in widths)
        lines = [
            fmt.format(*[h[:w] for h, w in zip(headers, widths)]),
            sep.join("-" * w for w in widths),
        ]
        for row in rows:
            lines.append(fmt.format(*[str(v)[:w] for v, w in zip(row, widths)]))
        return "\n".join(lines)
