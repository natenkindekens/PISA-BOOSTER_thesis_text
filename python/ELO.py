import pandas as pd
import matplotlib.pyplot as plt
import random
from pathlib import Path

plt.rcParams.update({
    "font.size": 16,
    "axes.titlesize": 20,
    "axes.labelsize": 17,
    "xtick.labelsize": 15,
    "ytick.labelsize": 15,
    "legend.fontsize": 14,
})

# ============================================================
# CONFIGURATION
# ============================================================

# Paths to your CSV files (add as many as you want)
CSV_FILES = [
    "data/group_Conditie_3.csv",
    "data/group_Conditie_4.csv"
    # "data/group_Conditie_2.csv",
]

# Names to exclude from the analysis
EXCLUDED_NAMES = [
    "Salematou Touré",
    "Oliver Goudsmedt",
    "Daoud El Abdellaoui",
    "Alexander Naessens",
    "Gaston Furniere"
]

# Output folders
OUTPUT_DIR = Path("elo_analysis_output")
TRAJECTORY_DIR = OUTPUT_DIR / "trajectories"
FINAL_ELO_DIR = OUTPUT_DIR / "final_elo"

# ============================================================
# LOAD DATA
# ============================================================

# Read and combine all CSV files
df = pd.concat([pd.read_csv(f) for f in CSV_FILES], ignore_index=True)

# ============================================================
# CLEANING & PREPARATION
# ============================================================

# Remove excluded names
if EXCLUDED_NAMES:
    df = df[~df["username"].isin(EXCLUDED_NAMES)]

# Convert timestamp to datetime if available
if "exercise_timestamp" in df.columns:
    df["exercise_timestamp"] = pd.to_datetime(df["exercise_timestamp"])
    df = df.sort_values(["username", "exercise_timestamp"])

# Create output folders
TRAJECTORY_DIR.mkdir(parents=True, exist_ok=True)
FINAL_ELO_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CALCULATE FINAL ELO
# ============================================================

# Final elo = current_elo + delta_elo of the last exercise
final_elos = []

for username, user_df in df.groupby("username"):
    user_df = user_df.reset_index(drop=True)

    last_row = user_df.iloc[-1]

    final_elo = last_row["current_elo"] + last_row["delta_elo"]

    final_elos.append({
        "username": username,
        "final_elo": final_elo
    })

final_elo_df = pd.DataFrame(final_elos)
final_elo_df = final_elo_df.sort_values("final_elo", ascending=False)

# Save final elo table
final_elo_df.to_csv(OUTPUT_DIR / "final_elo_scores.csv", index=False)

# ============================================================
# PLOT 1: FINAL ELO OVERVIEW
# ============================================================

plt.figure(figsize=(12, 6))
plt.bar(final_elo_df["username"], final_elo_df["final_elo"])
plt.xticks(rotation=90)
plt.xlabel("Participant")
plt.ylabel("Final ELO")
plt.title("Final ELO per Participant")
plt.tight_layout()

plt.savefig(FINAL_ELO_DIR / "final_elo_overview.png")
plt.close()

# ============================================================
# PLOT 2: INDIVIDUAL TRAJECTORIES
# ============================================================
"""
for username, user_df in df.groupby("username"):
    user_df = user_df.reset_index(drop=True)

    # ELO after each exercise
    elo_progression = user_df["current_elo"] + user_df["delta_elo"]

    plt.figure(figsize=(10, 5))
    plt.plot(range(1, len(elo_progression) + 1), elo_progression, marker="o")

    plt.xlabel("Exercise Number")
    plt.ylabel("ELO")
    plt.title(f"ELO Trajectory - {username}")
    plt.grid(True)
    plt.tight_layout()

    # Safe filename
    safe_name = username.replace("/", "_").replace("\\", "_")

    plt.savefig(TRAJECTORY_DIR / f"{safe_name}_trajectory.png")
    plt.close()
"""
# ============================================================
# OPTIONAL: SAMPLE TRAJECTORIES IN ONE PLOT
# ============================================================

STARTING_ELO = 450

all_usernames = list(df["username"].unique())
sample_size = min(20, len(all_usernames))
sampled_users = random.sample(all_usernames, sample_size)


plt.figure(figsize=(14, 7))

for username in sampled_users:
    user_df = df[df["username"] == username].reset_index(drop=True)
    elo_progression = [STARTING_ELO] + list(user_df["current_elo"] + user_df["delta_elo"])

    plt.plot(
        range(len(elo_progression)),
        elo_progression,
        label=username,
        marker="o",
        markersize=3
    )

plt.xlabel("Exercise Number")
plt.ylabel("ELO")
plt.title(f"ELO Trajectories – {sample_size} Random Participants")
#plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.grid(True)
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "sample_trajectories_all.png")
plt.close()

# ============================================================
# OPTIONAL: SAMPLE TRAJECTORIES IN ONE PLOT
# ============================================================

STARTING_ELO = 450

all_usernames = list(df["username"].unique())
sample_size = min(5, len(all_usernames))
sampled_users = random.sample(all_usernames, sample_size)
sampled_users = ["Ilias Ayadi", "Juna Stoffels", "Isaac Meziani", "Nikola Pietryk", "Yasmin El Wahabi Benkib"]

plt.figure(figsize=(14, 7))

for username in sampled_users:
    user_df = df[df["username"] == username].reset_index(drop=True)
    elo_progression = [STARTING_ELO] + list(user_df["current_elo"] + user_df["delta_elo"])

    plt.plot(
        range(len(elo_progression)),
        elo_progression,
        label=username,
        marker="o",
        markersize=3
    )

plt.xlabel("Exercise Number")
plt.ylabel("ELO")
plt.title(f"ELO Trajectories – {sample_size} Random Participants")
#plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.grid(True)
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "sample_trajectories.png")
plt.close()

# ============================================================
# PLOT 3: ELO SCORE DISTRIBUTION (HISTOGRAM)
# ============================================================

plt.figure(figsize=(10, 5))
plt.hist(final_elo_df["final_elo"], bins=20, edgecolor="black", range=(0, 1000))
plt.xlim(0, 1000)
plt.xlabel("ELO Score")
plt.ylabel("Number of Students")
plt.title("Distribution of Final ELO Scores")
plt.grid(axis="y")
plt.tight_layout()

plt.savefig(FINAL_ELO_DIR / "elo_distribution_histogram.png")
plt.close()

# ============================================================
# PLOT 4: ELO DISTRIBUTION IN 5 BLOCKS (0-200, 200-400, …)
# ============================================================

bins = [0, 200, 400, 600, 800, 1000]
labels = ["0–200", "200–400", "400–600", "600–800", "800–1000"]
counts = [
    ((final_elo_df["final_elo"] >= lo) & (final_elo_df["final_elo"] < hi)).sum()
    for lo, hi in zip(bins, bins[1:])
]

plt.figure(figsize=(8, 5))
plt.bar(labels, counts, edgecolor="black")
plt.xlabel("ELO Range")
plt.ylabel("Number of Students")
plt.title("Final ELO Distribution by Range")
plt.grid(axis="y")
plt.tight_layout()

plt.savefig(FINAL_ELO_DIR / "elo_distribution_blocks.png")
plt.close()

# ============================================================
# DONE
# ============================================================

print("Analysis completed successfully!")
print(f"Results saved in: {OUTPUT_DIR.resolve()}")
