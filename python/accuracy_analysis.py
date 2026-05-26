import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import norm

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

# Add all adaptive condition CSV files here
ADAPTIVE_FILES = [
    "data/group_Conditie_3.csv",
    "data/group_Conditie_4.csv"
]

# Add all non-adaptive condition CSV files here
NON_ADAPTIVE_FILES = [
    "data/group_Conditie_1.csv",
    "data/group_Conditie_2.csv"
]

# Column names in your CSV
USERNAME_COLUMN = "username"
CORRECT_COLUMN = "is_correct"

# Optional: names to exclude
EXCLUDED_NAMES = [
    "Salematou Touré",
    "Oliver Goudsmedt",
    "Daoud El Abdellaoui",
    "Alexander Naessens",
    "Gaston Furniere"
]

# Output directory
OUTPUT_DIR = Path("accuracy_analysis_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================


def load_condition(files, label):
    """
    Load and combine multiple CSV files into one dataframe.
    """

    all_data = []

    for file in files:
        df = pd.read_csv(file)
        df["condition_type"] = label
        df["source_file"] = file
        all_data.append(df)

    if not all_data:
        raise ValueError(f"No files provided for {label}")

    combined = pd.concat(all_data, ignore_index=True)

    return combined



def compute_student_accuracy(df):
    """
    Compute per-student accuracy rates.
    """

    # Remove excluded names
    if EXCLUDED_NAMES:
        df = df[~df[USERNAME_COLUMN].isin(EXCLUDED_NAMES)]

    # Convert correctness column to numeric if needed
    df[CORRECT_COLUMN] = df[CORRECT_COLUMN].astype(int)

    student_accuracy = (
        df.groupby(USERNAME_COLUMN)[CORRECT_COLUMN]
        .mean()
        .reset_index()
    )

    student_accuracy.rename(columns={
        CORRECT_COLUMN: "accuracy"
    }, inplace=True)

    return student_accuracy



def summarize_accuracy(student_df, label):
    """
    Print summary statistics.
    """

    accuracies = student_df["accuracy"]

    mean_acc = accuracies.mean()
    std_acc = accuracies.std()
    median_acc = accuracies.median()

    print("=" * 60)
    print(f"{label.upper()} CONDITION")
    print("=" * 60)
    print(f"Number of students: {len(student_df)}")
    print(f"Mean accuracy: {mean_acc:.4f} ({mean_acc * 100:.2f}%)")
    print(f"Median accuracy: {median_acc:.4f} ({median_acc * 100:.2f}%)")
    print(f"Standard deviation: {std_acc:.4f}")
    print(f"Distance from target (75%): {abs(mean_acc - 0.75):.4f}")
    print()

    return {
        "condition": label,
        "mean": mean_acc,
        "median": median_acc,
        "std": std_acc,
        "distance_to_target": abs(mean_acc - 0.75)
    }


# ============================================================
# LOAD DATA
# ============================================================

adaptive_df = load_condition(ADAPTIVE_FILES, "Adaptive")
non_adaptive_df = load_condition(NON_ADAPTIVE_FILES, "Non-Adaptive")

# ============================================================
# COMPUTE PER-STUDENT ACCURACY
# ============================================================

adaptive_students = compute_student_accuracy(adaptive_df)
non_adaptive_students = compute_student_accuracy(non_adaptive_df)

# ============================================================
# SUMMARY STATISTICS
# ============================================================

adaptive_stats = summarize_accuracy(adaptive_students, "Adaptive")
non_adaptive_stats = summarize_accuracy(non_adaptive_students, "Non-Adaptive")

# Save summary table
summary_df = pd.DataFrame([
    adaptive_stats,
    non_adaptive_stats
])

summary_df.to_csv(OUTPUT_DIR / "summary_statistics.csv", index=False)

# ============================================================
# PLOT 1: HISTOGRAM COMPARISON
# ============================================================

plt.figure(figsize=(12, 6))

bins = np.linspace(0, 1, 20)

plt.hist(
    adaptive_students["accuracy"],
    bins=bins,
    alpha=0.6,
    label="Adaptive"
)

plt.hist(
    non_adaptive_students["accuracy"],
    bins=bins,
    alpha=0.6,
    label="Non-Adaptive"
)

# Target line at 75%
plt.axvline(0.75, linestyle="--", label="Target Accuracy (75%)")

plt.xlabel("Per-Student Accuracy")
plt.ylabel("Number of Students")
plt.title("Distribution of Student Accuracy Rates")
plt.legend()
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "accuracy_distribution_histogram.png")
plt.close()

# ============================================================
# PLOT 2: NORMAL DISTRIBUTION FIT
# ============================================================

plt.figure(figsize=(12, 6))

# Adaptive fit
adaptive_mu, adaptive_sigma = norm.fit(adaptive_students["accuracy"])
adaptive_x = np.linspace(0, 1, 500)
adaptive_y = norm.pdf(adaptive_x, adaptive_mu, adaptive_sigma)

plt.plot(
    adaptive_x,
    adaptive_y,
    label=f"Adaptive Fit (μ={adaptive_mu:.2f}, σ={adaptive_sigma:.2f})"
)

# Non-adaptive fit
non_mu, non_sigma = norm.fit(non_adaptive_students["accuracy"])
non_x = np.linspace(0, 1, 500)
non_y = norm.pdf(non_x, non_mu, non_sigma)

plt.plot(
    non_x,
    non_y,
    label=f"Non-Adaptive Fit (μ={non_mu:.2f}, σ={non_sigma:.2f})"
)

# Target line
plt.axvline(0.75, linestyle="--", label="Target Accuracy (75%)")

plt.xlabel("Per-Student Accuracy")
plt.ylabel("Probability Density")
plt.title("Normal Distribution Fit of Accuracy Rates")
plt.legend()
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "normal_distribution_fit.png")
plt.close()

# ============================================================
# PLOT 3: BOX PLOT
# ============================================================

plt.figure(figsize=(8, 6))

plt.boxplot([
    adaptive_students["accuracy"],
    non_adaptive_students["accuracy"]
], labels=["Adaptive", "Non-Adaptive"])

plt.axhline(0.75, linestyle="--", label="Target Accuracy (75%)")

plt.ylabel("Per-Student Accuracy")
plt.title("Accuracy Spread Comparison")
plt.legend()
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "accuracy_boxplot.png")
plt.close()

# ============================================================
# PLOT 4: INDIVIDUAL STUDENT ACCURACY
# ============================================================

adaptive_students_sorted = adaptive_students.sort_values("accuracy")
non_adaptive_students_sorted = non_adaptive_students.sort_values("accuracy")

plt.figure(figsize=(14, 6))

plt.scatter(
    range(len(adaptive_students_sorted)),
    adaptive_students_sorted["accuracy"],
    label="Adaptive"
)

plt.scatter(
    range(len(non_adaptive_students_sorted)),
    non_adaptive_students_sorted["accuracy"],
    label="Non-Adaptive"
)

plt.axhline(0.75, linestyle="--", label="Target Accuracy (75%)")

plt.xlabel("Students (sorted by accuracy)")
plt.ylabel("Per-Student Accuracy")
plt.title("Per-Student Accuracy Rates")
plt.legend()
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "student_accuracy_scatter.png")
plt.close()

# ============================================================
# SAVE RAW STUDENT ACCURACIES
# ============================================================

adaptive_students["condition"] = "Adaptive"
non_adaptive_students["condition"] = "Non-Adaptive"

combined_students = pd.concat([
    adaptive_students,
    non_adaptive_students
], ignore_index=True)

combined_students.to_csv(
    OUTPUT_DIR / "student_accuracy_rates.csv",
    index=False
)

# ============================================================
# RESPONSE TIME ANALYSIS
# ============================================================

# IMPORTANT:
# Change this column name if your CSV uses a different one.
# Examples:
# - "response_time"
# - "time_taken"
# - "duration"
# - "solving_time"
RESPONSE_TIME_COLUMN = "response_time_exercies"

# Check whether the response time column exists
if RESPONSE_TIME_COLUMN in adaptive_df.columns and RESPONSE_TIME_COLUMN in non_adaptive_df.columns:

    # Remove excluded names again for consistency
    adaptive_rt_df = adaptive_df.copy()
    non_adaptive_rt_df = non_adaptive_df.copy()

    if EXCLUDED_NAMES:
        adaptive_rt_df = adaptive_rt_df[
            ~adaptive_rt_df[USERNAME_COLUMN].isin(EXCLUDED_NAMES)
        ]

        non_adaptive_rt_df = non_adaptive_rt_df[
            ~non_adaptive_rt_df[USERNAME_COLUMN].isin(EXCLUDED_NAMES)
        ]

    # Convert to numeric
    adaptive_rt_df[RESPONSE_TIME_COLUMN] = pd.to_numeric(
        adaptive_rt_df[RESPONSE_TIME_COLUMN],
        errors="coerce"
    )

    non_adaptive_rt_df[RESPONSE_TIME_COLUMN] = pd.to_numeric(
        non_adaptive_rt_df[RESPONSE_TIME_COLUMN],
        errors="coerce"
    )

    # ------------------------------------------------------------
    # PER-STUDENT MEAN RESPONSE TIME
    # ------------------------------------------------------------

    adaptive_rt_students = (
        adaptive_rt_df.groupby(USERNAME_COLUMN)[RESPONSE_TIME_COLUMN]
        .mean()
        .reset_index()
    )

    non_adaptive_rt_students = (
        non_adaptive_rt_df.groupby(USERNAME_COLUMN)[RESPONSE_TIME_COLUMN]
        .mean()
        .reset_index()
    )

    adaptive_rt_students.rename(columns={
        RESPONSE_TIME_COLUMN: "mean_response_time"
    }, inplace=True)

    non_adaptive_rt_students.rename(columns={
        RESPONSE_TIME_COLUMN: "mean_response_time"
    }, inplace=True)

    # ------------------------------------------------------------
    # SUMMARY STATISTICS
    # ------------------------------------------------------------

    adaptive_rt_mean = adaptive_rt_students["mean_response_time"].mean()
    adaptive_rt_std = adaptive_rt_students["mean_response_time"].std()

    non_rt_mean = non_adaptive_rt_students["mean_response_time"].mean()
    non_rt_std = non_adaptive_rt_students["mean_response_time"].std()

    print("=" * 60)
    print("RESPONSE TIME ANALYSIS")
    print("=" * 60)

    print(f"Adaptive mean response time: {adaptive_rt_mean:.2f}")
    print(f"Adaptive std response time: {adaptive_rt_std:.2f}")
    print()
    print(f"Non-adaptive mean response time: {non_rt_mean:.2f}")
    print(f"Non-adaptive std response time: {non_rt_std:.2f}")
    print()

    # Save response time summary
    response_time_summary = pd.DataFrame([
        {
            "condition": "Adaptive",
            "mean_response_time": adaptive_rt_mean,
            "std_response_time": adaptive_rt_std
        },
        {
            "condition": "Non-Adaptive",
            "mean_response_time": non_rt_mean,
            "std_response_time": non_rt_std
        }
    ])

    response_time_summary.to_csv(
        OUTPUT_DIR / "response_time_summary.csv",
        index=False
    )

    # ------------------------------------------------------------
    # PLOT 5: RESPONSE TIME DISTRIBUTION
    # ------------------------------------------------------------

    plt.figure(figsize=(12, 6))

    plt.hist(
        adaptive_rt_students["mean_response_time"],
        bins=20,
        alpha=0.6,
        label="Adaptive"
    )

    plt.hist(
        non_adaptive_rt_students["mean_response_time"],
        bins=20,
        alpha=0.6,
        label="Non-Adaptive"
    )

    plt.xlim(0, 15)
    plt.xlabel("Mean Response Time per Student")
    plt.ylabel("Number of Students")
    plt.title("Response Time Distribution")
    plt.legend()
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "response_time_distribution.png")
    plt.close()

    # ------------------------------------------------------------
    # PLOT 6: RESPONSE TIME BOXPLOT
    # ------------------------------------------------------------

    plt.figure(figsize=(8, 6))

    plt.boxplot([
        adaptive_rt_students["mean_response_time"],
        non_adaptive_rt_students["mean_response_time"]
    ], labels=["Adaptive", "Non-Adaptive"])

    plt.ylabel("Mean Response Time")
    plt.title("Response Time Spread Comparison")
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "response_time_boxplot.png")
    plt.close()

    # ------------------------------------------------------------
    # PLOT 7: NORMAL DISTRIBUTION FIT
    # ------------------------------------------------------------

    plt.figure(figsize=(12, 6))

    # Adaptive fit
    rt_mu_a, rt_sigma_a = norm.fit(
        adaptive_rt_students["mean_response_time"]
    )

    rt_x_a = np.linspace(
        adaptive_rt_students["mean_response_time"].min(),
        adaptive_rt_students["mean_response_time"].max(),
        500
    )

    rt_y_a = norm.pdf(rt_x_a, rt_mu_a, rt_sigma_a)

    plt.plot(
        rt_x_a,
        rt_y_a,
        label=f"Adaptive Fit (μ={rt_mu_a:.2f}, σ={rt_sigma_a:.2f})"
    )

    # Non-adaptive fit
    rt_mu_n, rt_sigma_n = norm.fit(
        non_adaptive_rt_students["mean_response_time"]
    )

    rt_x_n = np.linspace(
        non_adaptive_rt_students["mean_response_time"].min(),
        non_adaptive_rt_students["mean_response_time"].max(),
        500
    )

    rt_y_n = norm.pdf(rt_x_n, rt_mu_n, rt_sigma_n)

    plt.plot(
        rt_x_n,
        rt_y_n,
        label=f"Non-Adaptive Fit (μ={rt_mu_n:.2f}, σ={rt_sigma_n:.2f})"
    )

    plt.xlabel("Mean Response Time per Student")
    plt.ylabel("Probability Density")
    plt.title("Normal Distribution Fit of Response Times")
    plt.legend()
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "response_time_normal_fit.png")
    plt.close()

    # Save raw response times
    adaptive_rt_students["condition"] = "Adaptive"
    non_adaptive_rt_students["condition"] = "Non-Adaptive"

    response_time_students = pd.concat([
        adaptive_rt_students,
        non_adaptive_rt_students
    ], ignore_index=True)

    response_time_students.to_csv(
        OUTPUT_DIR / "student_response_times.csv",
        index=False
    )

else:
    print(
        f"WARNING: Column '{RESPONSE_TIME_COLUMN}' not found in one or more CSV files."
    )
    print("Response time analysis skipped.")

# ============================================================
# EXERCISE DIFFICULTY ANALYSIS
# ============================================================

# IMPORTANT:
# Change this if your difficulty column has another name.
# Example names:
# - "difficulty"
# - "exercise_difficulty"
# - "level"
DIFFICULTY_COLUMN = "exercise_difficulty"

if DIFFICULTY_COLUMN in adaptive_df.columns and DIFFICULTY_COLUMN in non_adaptive_df.columns:

    adaptive_diff_df = adaptive_df.copy()
    non_adaptive_diff_df = non_adaptive_df.copy()

    # Remove excluded names
    if EXCLUDED_NAMES:
        adaptive_diff_df = adaptive_diff_df[
            ~adaptive_diff_df[USERNAME_COLUMN].isin(EXCLUDED_NAMES)
        ]

        non_adaptive_diff_df = non_adaptive_diff_df[
            ~non_adaptive_diff_df[USERNAME_COLUMN].isin(EXCLUDED_NAMES)
        ]

    # Convert to numeric
    adaptive_diff_df[DIFFICULTY_COLUMN] = pd.to_numeric(
        adaptive_diff_df[DIFFICULTY_COLUMN],
        errors="coerce"
    )

    non_adaptive_diff_df[DIFFICULTY_COLUMN] = pd.to_numeric(
        non_adaptive_diff_df[DIFFICULTY_COLUMN],
        errors="coerce"
    )

    # ------------------------------------------------------------
    # PER-STUDENT MEAN DIFFICULTY
    # ------------------------------------------------------------

    adaptive_difficulty_students = (
        adaptive_diff_df.groupby(USERNAME_COLUMN)[DIFFICULTY_COLUMN]
        .mean()
        .reset_index()
    )

    non_adaptive_difficulty_students = (
        non_adaptive_diff_df.groupby(USERNAME_COLUMN)[DIFFICULTY_COLUMN]
        .mean()
        .reset_index()
    )

    adaptive_difficulty_students.rename(columns={
        DIFFICULTY_COLUMN: "mean_difficulty"
    }, inplace=True)

    non_adaptive_difficulty_students.rename(columns={
        DIFFICULTY_COLUMN: "mean_difficulty"
    }, inplace=True)

    # ------------------------------------------------------------
    # SUMMARY STATISTICS
    # ------------------------------------------------------------

    adaptive_diff_mean = adaptive_difficulty_students[
        "mean_difficulty"
    ].mean()

    adaptive_diff_std = adaptive_difficulty_students[
        "mean_difficulty"
    ].std()

    non_diff_mean = non_adaptive_difficulty_students[
        "mean_difficulty"
    ].mean()

    non_diff_std = non_adaptive_difficulty_students[
        "mean_difficulty"
    ].std()

    print("=" * 60)
    print("EXERCISE DIFFICULTY ANALYSIS")
    print("=" * 60)

    print(f"Adaptive mean difficulty: {adaptive_diff_mean:.2f}")
    print(f"Adaptive std difficulty: {adaptive_diff_std:.2f}")
    print()
    print(f"Non-adaptive mean difficulty: {non_diff_mean:.2f}")
    print(f"Non-adaptive std difficulty: {non_diff_std:.2f}")
    print()

    # Save summary
    difficulty_summary = pd.DataFrame([
        {
            "condition": "Adaptive",
            "mean_difficulty": adaptive_diff_mean,
            "std_difficulty": adaptive_diff_std
        },
        {
            "condition": "Non-Adaptive",
            "mean_difficulty": non_diff_mean,
            "std_difficulty": non_diff_std
        }
    ])

    difficulty_summary.to_csv(
        OUTPUT_DIR / "difficulty_summary.csv",
        index=False
    )

    # ------------------------------------------------------------
    # PLOT 8: DIFFICULTY DISTRIBUTION
    # ------------------------------------------------------------

    plt.figure(figsize=(12, 6))

    plt.hist(
        adaptive_difficulty_students["mean_difficulty"],
        bins=15,
        alpha=0.6,
        density=True,
        label="Adaptive"
    )

    plt.hist(
        non_adaptive_difficulty_students["mean_difficulty"],
        bins=15,
        alpha=0.6,
        density=True,
        label="Non-Adaptive"
    )

    plt.xlabel("Mean Exercise Difficulty per Student")
    plt.ylabel("Density")
    plt.title("Distribution of Exercise Difficulty")
    plt.legend()
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "difficulty_distribution.png")
    plt.close()

    # ------------------------------------------------------------
    # PLOT 9: DIFFICULTY BOXPLOT
    # ------------------------------------------------------------

    plt.figure(figsize=(8, 6))

    plt.boxplot([
        adaptive_difficulty_students["mean_difficulty"],
        non_adaptive_difficulty_students["mean_difficulty"]
    ], labels=["Adaptive", "Non-Adaptive"])

    plt.ylabel("Mean Exercise Difficulty")
    plt.title("Difficulty Spread Comparison")
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "difficulty_boxplot.png")
    plt.close()

    # ------------------------------------------------------------
    # PLOT 10: NORMAL DISTRIBUTION FIT
    # ------------------------------------------------------------

    plt.figure(figsize=(12, 6))

    # Adaptive fit
    diff_mu_a, diff_sigma_a = norm.fit(
        adaptive_difficulty_students["mean_difficulty"]
    )

    diff_x_a = np.linspace(
        adaptive_difficulty_students["mean_difficulty"].min(),
        adaptive_difficulty_students["mean_difficulty"].max(),
        500
    )

    diff_y_a = norm.pdf(diff_x_a, diff_mu_a, diff_sigma_a)

    plt.plot(
        diff_x_a,
        diff_y_a,
        label=f"Adaptive Fit (μ={diff_mu_a:.2f}, σ={diff_sigma_a:.2f})"
    )

    # Non-adaptive fit
    diff_mu_n, diff_sigma_n = norm.fit(
        non_adaptive_difficulty_students["mean_difficulty"]
    )

    diff_x_n = np.linspace(
        non_adaptive_difficulty_students["mean_difficulty"].min(),
        non_adaptive_difficulty_students["mean_difficulty"].max(),
        500
    )

    diff_y_n = norm.pdf(diff_x_n, diff_mu_n, diff_sigma_n)

    plt.plot(
        diff_x_n,
        diff_y_n,
        label=f"Non-Adaptive Fit (μ={diff_mu_n:.2f}, σ={diff_sigma_n:.2f})"
    )

    plt.xlabel("Mean Exercise Difficulty per Student")
    plt.ylabel("Probability Density")
    plt.title("Normal Distribution Fit of Exercise Difficulty")
    plt.legend()
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "difficulty_normal_fit.png")
    plt.close()

    # ------------------------------------------------------------
    # PLOT 11: PER-STUDENT DIFFICULTY
    # ------------------------------------------------------------

    adaptive_difficulty_sorted = adaptive_difficulty_students.sort_values(
        "mean_difficulty"
    )

    non_adaptive_difficulty_sorted = non_adaptive_difficulty_students.sort_values(
        "mean_difficulty"
    )

    plt.figure(figsize=(14, 6))

    plt.scatter(
        range(len(adaptive_difficulty_sorted)),
        adaptive_difficulty_sorted["mean_difficulty"],
        label="Adaptive"
    )

    plt.scatter(
        range(len(non_adaptive_difficulty_sorted)),
        non_adaptive_difficulty_sorted["mean_difficulty"],
        label="Non-Adaptive"
    )

    plt.xlabel("Students (sorted by mean difficulty)")
    plt.ylabel("Mean Exercise Difficulty")
    plt.title("Per-Student Mean Exercise Difficulty")
    plt.legend()
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "student_difficulty_scatter.png")
    plt.close()

    # Save raw student difficulties
    adaptive_difficulty_students["condition"] = "Adaptive"
    non_adaptive_difficulty_students["condition"] = "Non-Adaptive"

    all_difficulties = pd.concat([
        adaptive_difficulty_students,
        non_adaptive_difficulty_students
    ], ignore_index=True)

    all_difficulties.to_csv(
        OUTPUT_DIR / "student_mean_difficulties.csv",
        index=False
    )

else:
    print(
        f"WARNING: Column '{DIFFICULTY_COLUMN}' not found in one or more CSV files."
    )
    print("Difficulty analysis skipped.")

# ============================================================
# FINAL OUTPUT
# ============================================================

print("Analysis completed successfully!")
print(f"Results saved to: {OUTPUT_DIR.resolve()}")

print("\nGenerated files:")
print("- summary_statistics.csv")
print("- student_accuracy_rates.csv")
print("- accuracy_distribution_histogram.png")
print("- normal_distribution_fit.png")
print("- accuracy_boxplot.png")
print("- student_accuracy_scatter.png")
