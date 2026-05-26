import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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

EXCEL_FILE = "data/Masterfile_TrainingDays.xlsx"
TRAINING_DAY = 2
SESSIONS = [1, 2, 3, 4]
SESSION_LABELS = {
    "Testloop1_Training": 1,
    "Testloop2_Training": 2,
    "Testloop3_Training": 3,
    "Testloop4_Training": 4,
}
SESSION_COLOR = "#4C72B0"

OUTPUT_DIR = Path("correctness_analysis_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOAD DATA
# ============================================================

df_raw = pd.read_excel(EXCEL_FILE, sheet_name="Data_TrainingDays")

df = df_raw[
    (df_raw["TrainingDay"] == TRAINING_DAY) &
    (df_raw["TaskLoop"].isin(SESSION_LABELS))
].copy()

df["session_num"] = df["TaskLoop"].map(SESSION_LABELS)
df["TrainingArithmetic_RTcorrect"] = pd.to_numeric(
    df["TrainingArithmetic_RTcorrect"], errors="coerce"
)
df["TrainingArithmetic_RT"] = pd.to_numeric(
    df["TrainingArithmetic_RT"], errors="coerce"
)
df["TrainingArithmetic_Acc"] = pd.to_numeric(
    df["TrainingArithmetic_Acc"], errors="coerce"
)

# ============================================================
# HELPERS
# ============================================================

def add_value_labels(ax, bars, values, fmt="{:.1%}"):
    for bar, val in zip(bars, values):
        if not np.isnan(val):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + ax.get_ylim()[1] * 0.005,
                fmt.format(val),
                ha="center", va="bottom", fontsize=14, color="#333333",
            )


def add_overall_line(ax, overall, color, label):
    ax.axhline(
        overall, color=color, linewidth=1, linestyle="--",
        zorder=3, label=label,
    )


# ============================================================
# FIGURE 1 — Accuracy per Session
# ============================================================

session_acc = df.groupby("session_num")["TrainingArithmetic_Acc"].mean().reindex(SESSIONS)
overall_acc = df["TrainingArithmetic_Acc"].mean()

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(SESSIONS, session_acc.values, color=SESSION_COLOR, edgecolor="white", zorder=2)
add_value_labels(ax, bars, session_acc.values)
add_overall_line(ax, overall_acc, SESSION_COLOR, f"Overall avg: {overall_acc:.1%}")

ax.set_xticks(SESSIONS)
ax.set_xticklabels([f"Session {i}" for i in SESSIONS])
ax.set_xlabel("Session")
ax.set_ylabel("Average Accuracy")
ax.set_title(f"Average Accuracy per Session — Training Day {TRAINING_DAY}", pad=14)
ax.set_ylim(0, 1.1)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
ax.grid(axis="y", alpha=0.35, zorder=0)
ax.legend(loc="lower right", fontsize=14)
plt.tight_layout()
out = OUTPUT_DIR / f"accuracy_by_session_day{TRAINING_DAY}.png"
plt.savefig(out, dpi=150)
plt.close()
print(f"Saved: {out.resolve()}")

# ============================================================
# FIGURE 2 — Response Time (all trials) per Session
# ============================================================

session_rt = df.groupby("session_num")["TrainingArithmetic_RT"].mean().reindex(SESSIONS)
overall_rt = df["TrainingArithmetic_RT"].mean()

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(SESSIONS, session_rt.values / 1000, color=SESSION_COLOR, edgecolor="white", zorder=2)

for bar, val in zip(bars, session_rt.values):
    if not np.isnan(val):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val / 1000 + overall_rt / 1000 * 0.005,
            f"{val/1000:.2f}s",
            ha="center", va="bottom", fontsize=14, color="#333333",
        )

ax.axhline(overall_rt / 1000, color=SESSION_COLOR, linewidth=1, linestyle="--",
           zorder=3, label=f"Overall avg: {overall_rt/1000:.2f}s")

ax.set_xticks(SESSIONS)
ax.set_xticklabels([f"Session {i}" for i in SESSIONS])
ax.set_xlabel("Session")
ax.set_ylabel("Average Response Time (s)")
ax.set_title(f"Average Response Time per Session — Training Day {TRAINING_DAY}", pad=14)
ax.grid(axis="y", alpha=0.35, zorder=0)
ax.legend(loc="lower right", fontsize=14)
plt.tight_layout()
out = OUTPUT_DIR / f"rt_by_session_day{TRAINING_DAY}.png"
plt.savefig(out, dpi=150)
plt.close()
print(f"Saved: {out.resolve()}")

# ============================================================
# FIGURE 3 — Response Time (correct trials only) per Session
# ============================================================

session_rtc = df.groupby("session_num")["TrainingArithmetic_RTcorrect"].mean().reindex(SESSIONS)
overall_rtc = df["TrainingArithmetic_RTcorrect"].mean()

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(SESSIONS, session_rtc.values / 1000, color=SESSION_COLOR, edgecolor="white", zorder=2)

for bar, val in zip(bars, session_rtc.values):
    if not np.isnan(val):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val / 1000 + overall_rtc / 1000 * 0.005,
            f"{val/1000:.2f}s",
            ha="center", va="bottom", fontsize=14, color="#333333",
        )

ax.axhline(overall_rtc / 1000, color=SESSION_COLOR, linewidth=1, linestyle="--",
           zorder=3, label=f"Overall avg: {overall_rtc/1000:.2f}s")

ax.set_xticks(SESSIONS)
ax.set_xticklabels([f"Session {i}" for i in SESSIONS])
ax.set_xlabel("Session")
ax.set_ylabel("Average Response Time — Correct Trials (s)")
ax.set_title(f"Average Response Time (Correct Only) per Session — Training Day {TRAINING_DAY}", pad=14)
ax.grid(axis="y", alpha=0.35, zorder=0)
ax.legend(loc="lower right", fontsize=14)
plt.tight_layout()
out = OUTPUT_DIR / f"rt_correct_by_session_day{TRAINING_DAY}.png"
plt.savefig(out, dpi=150)
plt.close()
print(f"Saved: {out.resolve()}")

print("\nDone. All 3 figures saved to:", OUTPUT_DIR.resolve())
