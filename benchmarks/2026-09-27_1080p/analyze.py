"""Analyze explicit QPC intervals; retain long frames and verify output resolution."""
import csv
import json
import math
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parent

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

results = []
intervals = read_csv(ROOT / "intervals.csv")
for build in sorted({row["Build"] for row in intervals}):
    for interval in (row for row in intervals if row["Build"] == build):
        log_name = "old-unit-present.csv" if build == "old" and interval["Section"] == "Units" else f"{build}-present.csv"
        frames = read_csv(ROOT / log_name)
        start, end = int(interval["StartQpc"]), int(interval["EndQpc"])
        selected = []
        previous_qpc = None
        for frame in frames:
            try:
                qpc = int(frame["qpc"])
                dt = float(frame["delta_ms"])
            except (ValueError, TypeError):
                continue  # incomplete trailing row of a still-running capture
            if previous_qpc is not None and previous_qpc >= start and qpc <= end:
                if dt <= 0:
                    raise ValueError("Nonpositive duration inside measurement interval")
                selected.append(frame)
            previous_qpc = qpc
        if not selected:
            raise ValueError(f"No frames for {interval}")
        resolutions = sorted({(int(f["width"]), int(f["height"])) for f in selected})
        chains = sorted({f["swapchain"] for f in selected})
        if resolutions != [(1920, 1080)] or len(chains) != 1:
            raise ValueError(f"Invalid resolution/swapchains: {resolutions}, {chains}")
        durations = sorted(float(f["delta_ms"]) for f in selected)
        slow = durations[-max(1, math.ceil(len(durations) * 0.01)):]
        results.append({
            "Build": build, "Section": interval["Section"], "Repeat": int(interval["Repeat"]),
            "Frames": len(durations), "CapturedSeconds": round(sum(durations) / 1000, 3),
            "AvgFPS": round(1000 / mean(durations), 2),
            "OnePercentLowFPS": round(1000 / mean(slow), 2),
            "P99FrameMs": round(durations[math.ceil(len(durations) * 0.99) - 1], 3),
            "MaxFrameMs": round(max(durations), 3),
            "FramesOver1000ms": sum(dt >= 1000 for dt in durations),
            "Resolution": "1920x1080", "Swapchains": len(chains),
            "PresentAPIs": ",".join(sorted({f["present_api"] for f in selected})),
            "SyncIntervals": ",".join(sorted({f["sync_interval"] for f in selected})),
        })

with (ROOT / "results.csv").open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)
summary = []
for build, section in sorted({(r["Build"], r["Section"]) for r in results}):
    rows = [r for r in results if r["Build"] == build and r["Section"] == section]
    summary.append({"Build": build, "Section": section, "Runs": len(rows),
                    "MedianAvgFPS": median(r["AvgFPS"] for r in rows),
                    "MinAvgFPS": min(r["AvgFPS"] for r in rows),
                    "MaxAvgFPS": max(r["AvgFPS"] for r in rows),
                    "MedianOnePercentLowFPS": median(r["OnePercentLowFPS"] for r in rows)})
(ROOT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
