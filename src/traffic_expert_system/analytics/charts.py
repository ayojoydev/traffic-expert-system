from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


def create_charts(metrics, summaries: list[dict[str, object]], output_dir: str | Path) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    for metric in metrics:
        if not metric.snapshots:
            continue
        times = [row["time"] for row in metric.snapshots]
        queue_columns = [key for key in metric.snapshots[0] if key.startswith("queue_")]
        fig, ax = plt.subplots(figsize=(10, 5))
        for column in queue_columns:
            ax.plot(times, [row[column] for row in metric.snapshots], label=column.removeprefix("queue_"))
        ax.set_title(f"Очереди во времени: {metric.controller}, {metric.scenario}")
        ax.set_xlabel("Время, с")
        ax.set_ylabel("Автомобили в очереди")
        ax.legend()
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(output_path / f"queues_{metric.controller}_{metric.scenario}.png", dpi=140)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    labels = [summary["controller"] for summary in summaries]
    values = [summary["average_wait_seconds"] for summary in summaries]
    bars = ax.bar(labels, values, color=["#6c757d", "#198754"])
    ax.set_title("Среднее время ожидания")
    ax.set_ylabel("Секунды")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value), ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(output_path / "comparison_average_wait.png", dpi=140)
    plt.close(fig)
