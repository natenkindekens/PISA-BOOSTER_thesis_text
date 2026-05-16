"""
Generate engagement SQL queries for RekenRangers thesis evaluation.

Usage:
    # Single CSV
    python generate_engagement_queries.py group_Conditie_3.csv

    # Multiple CSVs (one SQL file with per-condition + combined queries)
    python generate_engagement_queries.py group_Conditie_1.csv group_Conditie_2.csv group_Conditie_3.csv group_Conditie_4.csv

    # Glob also works on most shells
    python generate_engagement_queries.py group_Conditie_*.csv

The CSV is expected to have a 'username' column as the first column.
A label is derived from the filename (e.g. 'group_Conditie_3.csv' -> 'Conditie_3').
"""

import csv
import re
import sys
from pathlib import Path


def extract_usernames(csv_path: Path) -> set[str]:
    """Read the first column (username) from a CSV file."""
    usernames: set[str] = set()
    # utf-8-sig handles the BOM that sometimes appears in exported CSVs
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "username" not in reader.fieldnames:
            raise ValueError(
                f"{csv_path.name}: expected a 'username' column, got "
                f"{reader.fieldnames!r}"
            )
        for row in reader:
            name = (row.get("username") or "").strip()
            if name:
                usernames.add(name)
    return usernames


def label_from_filename(csv_path: Path) -> str:
    """Derive a condition label from the filename, e.g. 'group_Conditie_3.csv' -> 'Conditie_3'."""
    stem = csv_path.stem
    # Strip a leading "group_" if present, keep the rest
    stem = re.sub(r"^group_", "", stem, flags=re.IGNORECASE)
    return stem or csv_path.stem


def sql_escape(s: str) -> str:
    return s.replace("'", "''")


def names_in_clause(names: set[str], indent: str = "        ") -> str:
    """Format a set of names as a SQL IN-list, one per line, sorted alphabetically."""
    return ",\n".join(f"{indent}'{sql_escape(n)}'" for n in sorted(names))


# ---------------------------------------------------------------------------
# SQL block builder
# ---------------------------------------------------------------------------
def build_block(label: str, names: set[str]) -> str:
    """Build the five engagement queries for one condition."""
    in_list = names_in_clause(names)
    header = (
        f"-- ============================================================\n"
        f"-- CONDITION: {label}    (n = {len(names)})\n"
        f"-- ============================================================\n"
    )

    return f"""{header}
-- ------------------------------------------------------------
-- [{label}] 1) UNUSED COINS / SPENDING RATIO (puzzle engagement)
-- ------------------------------------------------------------
SELECT
    '{label}'                                             AS condition_label,
    s.username,
    COALESCE(sp.points, 0)                                AS unused_coins,
    COALESCE(SUM(p.piece_cost), 0)                        AS spent_coins,
    COALESCE(sp.points, 0) + COALESCE(SUM(p.piece_cost), 0) AS total_earned,
    ROUND(
        COALESCE(SUM(p.piece_cost), 0)
        / NULLIF(COALESCE(sp.points,0) + COALESCE(SUM(p.piece_cost),0), 0) * 100,
        1
    ) AS pct_spent,
    COUNT(spp.id)                                         AS pieces_unlocked
FROM students s
LEFT JOIN student_points sp         ON sp.student_id = s.id
LEFT JOIN student_puzzle_pieces spp ON spp.student_id = s.id
LEFT JOIN puzzles p                 ON p.id = spp.puzzle_id
WHERE s.username IN (
{in_list}
)
GROUP BY s.id, s.username, sp.points
ORDER BY pct_spent ASC;


-- ------------------------------------------------------------
-- [{label}] 2) PUZZLES COMPLETED PER STUDENT
-- ------------------------------------------------------------
SELECT
    '{label}'                                             AS condition_label,
    s.username,
    SUM(CASE WHEN owned_pieces = p.rows_count * p.cols_count THEN 1 ELSE 0 END) AS puzzles_completed,
    SUM(CASE WHEN owned_pieces > 0 AND owned_pieces < p.rows_count * p.cols_count THEN 1 ELSE 0 END) AS puzzles_started,
    COUNT(DISTINCT p.id) AS puzzles_touched
FROM students s
JOIN (
    SELECT student_id, puzzle_id, COUNT(*) AS owned_pieces
    FROM student_puzzle_pieces
    GROUP BY student_id, puzzle_id
) spp ON spp.student_id = s.id
JOIN puzzles p ON p.id = spp.puzzle_id
WHERE s.username IN (
{in_list}
)
GROUP BY s.id, s.username
ORDER BY puzzles_completed DESC;


-- ------------------------------------------------------------
-- [{label}] 3) OVERALL ACTIVITY / VOLUME PER STUDENT
-- ------------------------------------------------------------
SELECT
    '{label}'                                  AS condition_label,
    s.username,
    COUNT(e.id)                                AS total_exercises,
    ROUND(AVG(e.is_correct) * 100, 1)          AS accuracy_pct,
    ROUND(AVG(e.response_time), 2)             AS avg_response_time_s,
    COUNT(DISTINCT e.set_id)                   AS sets_played,
    MIN(e.timestamp)                           AS first_seen,
    MAX(e.timestamp)                           AS last_seen,
    TIMESTAMPDIFF(MINUTE, MIN(e.timestamp), MAX(e.timestamp)) AS active_span_minutes
FROM students s
LEFT JOIN exercises e ON e.student_id = s.id
WHERE s.username IN (
{in_list}
)
GROUP BY s.id, s.username
ORDER BY total_exercises DESC;


-- ------------------------------------------------------------
-- [{label}] 4) METACOGNITION ENGAGEMENT
-- ------------------------------------------------------------
SELECT
    '{label}'                                             AS condition_label,
    s.username,
    COUNT(CASE WHEN e.meta_self_score IS NOT NULL AND e.meta_self_score > 0 THEN 1 END) AS confidence_answers,
    ROUND(AVG(e.meta_self_score), 2)                      AS avg_confidence,
    ROUND(STDDEV(e.meta_self_score), 2)                   AS sd_confidence,
    ROUND(AVG(e.time_self_score), 2)                      AS avg_time_self_score_s
FROM students s
LEFT JOIN exercises e ON e.student_id = s.id
WHERE s.username IN (
{in_list}
)
GROUP BY s.id, s.username
ORDER BY confidence_answers DESC;


-- ------------------------------------------------------------
-- [{label}] 5) GROUP-LEVEL HEADLINE NUMBERS
-- ------------------------------------------------------------
SELECT
    '{label}'                                             AS condition_label,
    COUNT(*)                                              AS n_students,
    ROUND(AVG(unused_coins), 1)                           AS mean_unused_coins,
    ROUND(AVG(spent_coins), 1)                            AS mean_spent_coins,
    ROUND(AVG(pct_spent), 1)                              AS mean_pct_spent,
    SUM(CASE WHEN spent_coins = 0 THEN 1 ELSE 0 END)      AS students_who_spent_nothing,
    SUM(CASE WHEN pct_spent >= 50 THEN 1 ELSE 0 END)      AS students_spent_half_or_more
FROM (
    SELECT
        s.id,
        COALESCE(sp.points, 0)                                AS unused_coins,
        COALESCE(SUM(p.piece_cost), 0)                        AS spent_coins,
        ROUND(
            COALESCE(SUM(p.piece_cost), 0)
            / NULLIF(COALESCE(sp.points,0) + COALESCE(SUM(p.piece_cost),0), 0) * 100,
            1
        ) AS pct_spent
    FROM students s
    LEFT JOIN student_points sp         ON sp.student_id = s.id
    LEFT JOIN student_puzzle_pieces spp ON spp.student_id = s.id
    LEFT JOIN puzzles p                 ON p.id = spp.puzzle_id
    WHERE s.username IN (
{in_list}
    )
    GROUP BY s.id, sp.points
) t;
"""


def build_cross_condition_block(conditions: dict[str, set[str]]) -> str:
    """Compare all conditions side by side using a CASE on username."""
    # Build a CASE expression that tags each username with its condition.
    when_clauses = []
    all_names: set[str] = set()
    for label, names in conditions.items():
        all_names |= names
        names_list = ", ".join(f"'{sql_escape(n)}'" for n in sorted(names))
        when_clauses.append(f"        WHEN s.username IN ({names_list}) THEN '{label}'")
    case_expr = "    CASE\n" + "\n".join(when_clauses) + "\n    END AS condition_label"

    big_in = names_in_clause(all_names)

    return f"""-- ============================================================
-- CROSS-CONDITION COMPARISON
-- All {len(all_names)} students across {len(conditions)} condition(s),
-- tagged with their condition_label for grouping/filtering.
-- ============================================================

-- ------------------------------------------------------------
-- Per-student unused coins, with condition label
-- ------------------------------------------------------------
SELECT
{case_expr},
    s.username,
    COALESCE(sp.points, 0)                                AS unused_coins,
    COALESCE(SUM(p.piece_cost), 0)                        AS spent_coins,
    COALESCE(sp.points, 0) + COALESCE(SUM(p.piece_cost), 0) AS total_earned,
    ROUND(
        COALESCE(SUM(p.piece_cost), 0)
        / NULLIF(COALESCE(sp.points,0) + COALESCE(SUM(p.piece_cost),0), 0) * 100,
        1
    ) AS pct_spent
FROM students s
LEFT JOIN student_points sp         ON sp.student_id = s.id
LEFT JOIN student_puzzle_pieces spp ON spp.student_id = s.id
LEFT JOIN puzzles p                 ON p.id = spp.puzzle_id
WHERE s.username IN (
{big_in}
)
GROUP BY s.id, s.username, sp.points
ORDER BY condition_label, pct_spent ASC;


-- ------------------------------------------------------------
-- Condition-level means (one row per condition)
-- ------------------------------------------------------------
SELECT
    condition_label,
    COUNT(*)                                         AS n_students,
    ROUND(AVG(unused_coins), 1)                      AS mean_unused_coins,
    ROUND(AVG(spent_coins), 1)                       AS mean_spent_coins,
    ROUND(AVG(pct_spent), 1)                         AS mean_pct_spent,
    SUM(CASE WHEN spent_coins = 0 THEN 1 ELSE 0 END) AS students_who_spent_nothing
FROM (
    SELECT
{case_expr},
        COALESCE(sp.points, 0)                                AS unused_coins,
        COALESCE(SUM(p.piece_cost), 0)                        AS spent_coins,
        ROUND(
            COALESCE(SUM(p.piece_cost), 0)
            / NULLIF(COALESCE(sp.points,0) + COALESCE(SUM(p.piece_cost),0), 0) * 100,
            1
        ) AS pct_spent
    FROM students s
    LEFT JOIN student_points sp         ON sp.student_id = s.id
    LEFT JOIN student_puzzle_pieces spp ON spp.student_id = s.id
    LEFT JOIN puzzles p                 ON p.id = spp.puzzle_id
    WHERE s.username IN (
{big_in}
    )
    GROUP BY s.id, sp.points
) t
GROUP BY condition_label
ORDER BY condition_label;
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1

    csv_paths = [Path(p) for p in argv[1:]]
    missing = [p for p in csv_paths if not p.is_file()]
    if missing:
        for p in missing:
            print(f"ERROR: file not found: {p}", file=sys.stderr)
        return 2

    conditions: dict[str, set[str]] = {}
    for path in csv_paths:
        label = label_from_filename(path)
        names = extract_usernames(path)
        if label in conditions:
            # Avoid silently overwriting if two files map to the same label
            label = f"{label}_{path.stem}"
        conditions[label] = names
        print(f"  {label:30s} -> {len(names):3d} students  ({path.name})")

    # Build the output
    parts: list[str] = []
    parts.append(
        "-- ============================================================\n"
        "-- Engagement metrics for RekenRangers\n"
        f"-- Generated from {len(csv_paths)} CSV file(s):\n"
        + "".join(f"--   - {p.name}\n" for p in csv_paths)
        + "-- ============================================================\n"
    )

    for label, names in conditions.items():
        parts.append(build_block(label, names))

    if len(conditions) >= 2:
        parts.append(build_cross_condition_block(conditions))

    out_path = Path("engagement_queries.sql")
    out_path.write_text("\n".join(parts), encoding="utf-8")
    total = sum(len(n) for n in conditions.values())
    print(f"\nWrote {out_path.resolve()}  ({total} student rows across "
          f"{len(conditions)} condition(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
