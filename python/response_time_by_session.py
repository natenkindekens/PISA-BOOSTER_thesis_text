import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams.update({
    "font.size": 13,
    "axes.titlesize": 15,
    "axes.labelsize": 13,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 11,
})

# ============================================================
# CONFIGURATION
# ============================================================

EXCLUDED_NAMES = [
    "Salematou Touré",
    "Oliver Goudsmedt",
    "Daoud El Abdellaoui",
    "Alexander Naessens",
    "Gaston Furniere",
]

SESSIONS_PER_DAY = 3
NUM_DAYS = 4
EXERCISES_PER_SESSION = 18
TOTAL_SESSIONS = SESSIONS_PER_DAY * NUM_DAYS      # 12
EXPECTED_EXERCISES = TOTAL_SESSIONS * EXERCISES_PER_SESSION  # 216

OUTPUT_DIR = Path("response_time_analysis_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DAY_COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]

RT_COL = "response_time_exercies"  # typo is in the source data

# ============================================================
# HELPERS
# ============================================================

def load_and_clean(csv_files):
    df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
    if EXCLUDED_NAMES:
        df = df[~df["username"].isin(EXCLUDED_NAMES)]
    df["exercise_timestamp"] = pd.to_datetime(df["exercise_timestamp"])
    df[RT_COL] = pd.to_numeric(df[RT_COL], errors="coerce")
    df = df.sort_values(["username", "exercise_timestamp"])
    return df


def assign_session_numbers(user_df):
    session_order = (
        user_df.groupby("set_id")["exercise_timestamp"]
        .min()
        .sort_values()
    )
    session_map = {sid: i + 1 for i, sid in enumerate(session_order.index)}
    user_df = user_df.copy()
    user_df["session_num"] = user_df["set_id"].map(session_map)
    return user_df


def print_incomplete(df, label):
    exercise_counts = df.groupby("username").size()
    incomplete = exercise_counts[exercise_counts != EXPECTED_EXERCISES]
    if not incomplete.empty:
        print(f"[{label}] Participants with unexpected exercise count (expected {EXPECTED_EXERCISES}):")
        for name, count in sorted(incomplete.items(), key=lambda x: x[1]):
            print(f"  {name}: {count} exercises ({count // EXERCISES_PER_SESSION} sessions)")
        print()


def make_figure(csv_files, title, out_filename):
    df = load_and_clean(csv_files)
    print_incomplete(df, title)

    df = df.groupby("username", group_keys=False).apply(assign_session_numbers)
    df = df[df["session_num"] <= TOTAL_SESSIONS]
    df["day_num"] = ((df["session_num"] - 1) // SESSIONS_PER_DAY) + 1

    session_idx = np.arange(1, TOTAL_SESSIONS + 1)
    session_avg = df.groupby("session_num")[RT_COL].mean().reindex(session_idx)
    day_avg = df.groupby("day_num")[RT_COL].mean()

    fig, ax = plt.subplots(figsize=(14, 6))

    bar_colors = [DAY_COLORS[(s - 1) // SESSIONS_PER_DAY] for s in session_idx]
    bars = ax.bar(session_idx, session_avg.values, color=bar_colors, edgecolor="white", zorder=2)

    for bar, val in zip(bars, session_avg.values):
        if not np.isnan(val):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + 0.05,
                f"{val:.1f}s",
                ha="center", va="bottom", fontsize=11, color="#333333",
            )

    for day in range(1, NUM_DAYS + 1):
        first_s = (day - 1) * SESSIONS_PER_DAY + 1
        last_s = day * SESSIONS_PER_DAY
        avg = day_avg.get(day, np.nan)
        if not np.isnan(avg):
            ax.hlines(
                avg,
                first_s - 0.45, last_s + 0.45,
                colors=DAY_COLORS[day - 1],
                linewidth=2.5,
                linestyles="--",
                zorder=3,
                label=f"Day {day} avg: {avg:.1f}s",
            )

    for day in range(1, NUM_DAYS):
        ax.axvline(day * SESSIONS_PER_DAY + 0.5, color="gray", linewidth=1, linestyle=":", zorder=1)

    ax.set_xticks(session_idx)
    ax.set_xticklabels([f"S{i}" for i in session_idx])
    ax.set_xlabel("Session")
    ax.set_ylabel("Average Response Time (s)")
    ax.set_title(title, pad=28)

    y_max = session_avg.max()
    ax.set_ylim(0, y_max * 1.15)

    for day in range(1, NUM_DAYS + 1):
        mid_x = ((day - 1) * SESSIONS_PER_DAY + (SESSIONS_PER_DAY + 1) / 2 - 0.5) / (TOTAL_SESSIONS - 1)
        ax.text(
            mid_x, 1.04,
            f"Day {day}",
            ha="center", va="bottom",
            fontsize=13, fontweight="bold",
            color=DAY_COLORS[day - 1],
            transform=ax.transAxes,
        )

    ax.grid(axis="y", alpha=0.35, zorder=0)
    ax.legend(loc="upper right", fontsize=11)

    plt.tight_layout()
    out_path = OUTPUT_DIR / out_filename
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Plot saved to: {out_path.resolve()}")


# ============================================================
# GENERATE FIGURES
# ============================================================

make_figure(
    csv_files=["data/group_Conditie_1.csv", "data/group_Conditie_2.csv"],
    title="Average Response Time per Session and per Day — No Adaptivity (Conditions 1 & 2)",
    out_filename="response_time_by_session_no_adaptivity.png",
)

make_figure(
    csv_files=["data/group_Conditie_3.csv", "data/group_Conditie_4.csv"],
    title="Average Response Time per Session and per Day — Adaptivity (Conditions 3 & 4)",
    out_filename="response_time_by_session_adaptivity.png",
)
