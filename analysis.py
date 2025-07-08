import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Player usernames
PLAYERS = {
    "David Navara": "FormerProdigy",
    "Magnus Carlsen": "MagnusCarlsen",
    "Hikaru Nakamura": "Hikaru",
    "Daniel Naroditsky": "DanielNaroditsky",
    "Alireza Firouzja": "Firouzja2003",
    "Fabiano Caruana": "FabianoCaruana",
    "Aleksander Grischuk": "Grischuk",
    "Matthias Bluebaum": "Msb2",
    "Christopher Yoo": "ChristopherYoo"
}

folder = "time_pressure_analysis"
dfs = []

for name, username in PLAYERS.items():
    filepath = os.path.join(folder, f"{username}_time_pressure_2024.csv")
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df["player"] = name
        # Drop rows with missing score data (e.g., mate cases)
        df = df.dropna(subset=["best_score", "played_score"])
        # Compute cp_loss
        df["cp_loss"] = df["best_score"] - df["played_score"]
        dfs.append(df)
    else:
        print(f"⚠️ Missing file: {filepath}")

if not dfs:
    raise ValueError("❌ No valid player data found.")

# Combine all data
df_all = pd.concat(dfs, ignore_index=True)

# Compute normalization metrics
df_all["rel_loss"] = df_all["cp_loss"] / (df_all["best_score"].abs() + 1)
df_all["log_norm_loss"] = df_all["cp_loss"] / np.log(df_all["best_score"].abs() + 2)
df_all["is_critical"] = df_all["best_score"].abs() < 100
df_all["is_under_5s"] = df_all["clock"] < 5.0

# Summary per player
summary = df_all.groupby("player").agg(
    avg_cp_loss=("cp_loss", "mean"),
    avg_rel_loss=("rel_loss", "mean"),
    avg_log_norm_loss=("log_norm_loss", "mean"),
    total_moves=("cp_loss", "count"),
    moves_under_5s=("is_under_5s", "sum"),
    critical_moves=("is_critical", "sum")
).sort_values("avg_cp_loss")

# Plot: Average CP loss
plt.figure(figsize=(10, 6))
sns.barplot(data=summary.reset_index(), x="player", y="avg_cp_loss")
plt.title("Average Centipawn Loss (<10s) per Player")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("avg_cp_loss_per_player.png")

# Plot: Average Relative CP Loss
plt.figure(figsize=(10, 6))
sns.barplot(data=summary.reset_index(), x="player", y="avg_rel_loss")
plt.title("Average Relative CP Loss (<10s) per Player")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("avg_rel_cp_loss_per_player.png")

# Plot: Average Log-Normalized CP Loss
plt.figure(figsize=(10, 6))
sns.barplot(data=summary.reset_index(), x="player", y="avg_log_norm_loss")
plt.title("Average Log-Normalized CP Loss (<10s) per Player")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("avg_log_norm_cp_loss_per_player.png")

# Filter only moves under 5 seconds
df_under_5 = df_all[df_all["is_under_5s"]]

# Aggregate stats under 5 seconds
summary_under_5 = df_under_5.groupby("player").agg(
    avg_cp_loss=("cp_loss", "mean"),
    avg_rel_loss=("rel_loss", "mean"),
    avg_log_norm_loss=("log_norm_loss", "mean"),
    total_moves=("cp_loss", "count")
).sort_values("avg_cp_loss")

# Plot: Average cp_loss under 5s
plt.figure(figsize=(10, 6))
sns.barplot(data=summary_under_5.reset_index(), x="player", y="avg_cp_loss")
plt.title("Average CP Loss (<5s) per Player")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("avg_cp_loss_under_5s.png")

# Plot: Relative loss under 5s
plt.figure(figsize=(10, 6))
sns.barplot(data=summary_under_5.reset_index(), x="player", y="avg_rel_loss")
plt.title("Average Relative CP Loss (<5s) per Player")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("avg_rel_cp_loss_under_5s.png")

# Plot: Log-normalized loss under 5s
plt.figure(figsize=(10, 6))
sns.barplot(data=summary_under_5.reset_index(), x="player", y="avg_log_norm_loss")
plt.title("Average Log-Normalized CP Loss (<5s) per Player")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("avg_log_norm_cp_loss_under_5s.png")

# Filter only critical moves (|best_score| < 100)
df_critical = df_all[df_all["is_critical"]]

# Aggregate stats for critical moves
summary_critical = df_critical.groupby("player").agg(
    avg_cp_loss=("cp_loss", "mean"),
    avg_rel_loss=("rel_loss", "mean"),
    avg_log_norm_loss=("log_norm_loss", "mean"),
    total_moves=("cp_loss", "count")
).sort_values("avg_cp_loss")

# Plot: Average cp_loss on critical moves
plt.figure(figsize=(10, 6))
sns.barplot(data=summary_critical.reset_index(), x="player", y="avg_cp_loss")
plt.title("Average CP Loss (Critical Moves) per Player")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("avg_cp_loss_critical_moves.png")

# Plot: Relative loss on critical moves
plt.figure(figsize=(10, 6))
sns.barplot(data=summary_critical.reset_index(), x="player", y="avg_rel_loss")
plt.title("Average Relative CP Loss (Critical Moves) per Player")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("avg_rel_cp_loss_critical_moves.png")

# Plot: Log-normalized loss on critical moves
plt.figure(figsize=(10, 6))
sns.barplot(data=summary_critical.reset_index(), x="player", y="avg_log_norm_loss")
plt.title("Average Log-Normalized CP Loss (Critical Moves) per Player")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("avg_log_norm_cp_loss_critical_moves.png")



# Save summary
summary.reset_index(inplace=True)
summary.to_csv("player_time_pressure_summary.csv", index=False)

print("✅ Analysis complete")
