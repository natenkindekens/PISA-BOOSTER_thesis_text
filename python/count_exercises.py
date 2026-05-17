import pandas as pd
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

CSV_FILES = [
    "data/group_Conditie_1.csv",
    "data/group_Conditie_2.csv",
    "data/group_Conditie_3.csv",
    "data/group_Conditie_4.csv",
]

EXCLUDED_NAMES = [
    "Salematou Touré",
    "Oliver Goudsmedt",
    "Daoud El Abdellaoui",
    "Alexander Naessens",
    "Gaston Furniere",
]

USERNAME_COLUMN = "username"

# ============================================================
# LOAD & FILTER
# ============================================================

df = pd.concat([pd.read_csv(f) for f in CSV_FILES], ignore_index=True)

if EXCLUDED_NAMES:
    df = df[~df[USERNAME_COLUMN].isin(EXCLUDED_NAMES)]

# ============================================================
# COUNT EXERCISES PER STUDENT
# ============================================================

counts = (
    df.groupby(USERNAME_COLUMN)
    .size()
    .reset_index(name="exercise_count")
    .sort_values("exercise_count", ascending=False)
)

print(f"Total students: {len(counts)}")
print(f"Total exercises: {counts['exercise_count'].sum()}")
print()
print(counts.to_string(index=False))

# Save to CSV
output_path = Path("exercise_counts.csv")
counts.to_csv(output_path, index=False)
print(f"\nSaved to: {output_path.resolve()}")
