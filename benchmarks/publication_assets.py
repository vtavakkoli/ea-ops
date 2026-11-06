"""Generate manuscript plots and tables from preserved original/revision CSVs.

No means, confidence bands, extrapolated timeout values, or cross-hardware
speedup claims are added to the paper. Complete revision rows are required.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import statistics


def rows(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def median(records, key):
    values = [float(r[key]) for r in records if r.get(key) not in (None, "")]
    if not values:
        raise ValueError(f"No measurements for {key}")
    return statistics.median(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--scenarios", required=True)
    parser.add_argument("--paper", required=True)
    args = parser.parse_args()
    original, revision, paper = Path(args.original), Path(args.revision), Path(args.paper)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    series = sorted((rows(p) for p in original.glob("performance-*.csv")), key=lambda r: int(r[0]["objects"]))
    xs = [int(r[0]["objects"]) for r in series]
    plots = [("validation_scalability", "validation_seconds", "Median validation (s)", False, 1),
             ("impact_scalability", "impact_seconds", "Median undirected impact (ms)", True, 1000),
             ("memory_scalability", "peak_rss_mb", "Maximum process peak RSS (MiB)", False, 1),
             ("publication_scalability", "report_seconds", "Median publication (s), n = 3", True, 1)]
    for name, key, ylabel, log_y, factor in plots:
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        values = [max(float(x[key]) for x in r) if key == "peak_rss_mb" else median(r, key) * factor for r in series]
        ax.plot(xs, values, "o-", color="#205d91", label="Report" if name.startswith("publication") else None)
        if name.startswith("publication"):
            ax.plot(xs, [median(r, "portal_seconds") for r in series], "s-", color="#c46b19", label="Portal")
            ax.legend(loc="upper left", fontsize=8)
        ax.set_xscale("log")
        if log_y:
            ax.set_yscale("log")
        ax.axvline(316.2278, color="#666666", linestyle="--", linewidth=1)
        ax.text(0.02, 1.02, "Intel (100) | AMD (1,000+)", transform=ax.transAxes, fontsize=8)
        ax.set_xlabel("Architecture objects (log scale)")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.2)
        fig.tight_layout()
        fig.savefig(paper / "figures" / f"{name}.pdf")
        fig.savefig(paper / "figures" / f"{name}.png", dpi=180)
        plt.close(fig)
    supplemental = sorted((rows(p) for p in revision.glob("performance-*.csv")), key=lambda r: int(r[0]["objects"]))
    table = [r"\begin{table*}[t]\centering\small", r"\caption{Supplemental local revision experiment: one warmup, three measured repetitions and three report/portal builds per size. Medians, no confidence intervals; RSS is the maximum process high-water mark. Hardware differs from the original study.}\label{tab:revision}",
             r"\begin{tabular}{rrrrrrrr}\toprule", r"Objects & Relationships & Validate (s) & Impact (ms) & Report (s) & Portal (s) & RSS (MiB) & $n$ \\\midrule"]
    summary = []
    for records in supplemental:
        size = int(records[0]["objects"])
        resource = json.loads((revision / f"resource-{size}.json").read_text())
        if len(records) != 3 or resource["status"] != "completed" or any(not r.get("portal_seconds") for r in records):
            raise ValueError(f"Incomplete revision protocol: {size}")
        entry = {"objects": size, "relationships": int(records[0]["relationships"]),
                 "validation_s": median(records, "validation_seconds"), "impact_ms": median(records, "impact_seconds") * 1000,
                 "report_s": median(records, "report_seconds"), "portal_s": median(records, "portal_seconds"),
                 "peak_rss_mb": max(float(r["peak_rss_mb"]) for r in records),
                 "total_benchmark_elapsed_s": resource["elapsed_seconds"]}
        summary.append(entry)
        table.append(f"{size:,} & {entry['relationships']:,} & {entry['validation_s']:.3f} & {entry['impact_ms']:.3f} & {entry['report_s']:.3f} & {entry['portal_s']:.3f} & {entry['peak_rss_mb']:.1f} & 3 " + r"\\")
    table += [r"\bottomrule\end{tabular}\end{table*}"]
    biggest = summary[-1]
    env = json.loads((revision / "environment.json").read_text())
    intro = ("Table~\\ref{tab:revision} reports the separate revision experiment on " + env["cpu"].replace("_", r"\_") +
             f". At {biggest['objects']:,} objects, the validation median was {biggest['validation_s']:.3f}~s, "
             f"report median {biggest['report_s']:.3f}~s, and maximum process RSS {biggest['peak_rss_mb']:.1f}~MiB. "
             f"The supervised benchmark process completed in {biggest['total_benchmark_elapsed_s']:.1f}~s, including the warmup and measured phases, excluding model generation. "
             "The re-attempt demonstrates completion for this model, implementation, and local protocol; it does not reproduce the original 30-repetition hosted protocol or establish a production scale ceiling. No cross-environment speedup factor is calculated.\n\n")
    (paper / "revision_performance.tex").write_text(intro + "\n".join(table) + "\n")
    typed = [r"\begin{table}[t]\centering\footnotesize", r"\caption{Metroville policy comparison. Counts include seeds and possible dangling IDs. All ten validation sets and all legacy/typed/bounded/change-aware policy oracles match exactly.}\label{tab:typed}",
             r"\begin{tabular}{lrrrr}\toprule", r"ID & Undirected & Typed & 2 hops & Change-aware \\\midrule"]
    for r in rows(Path(args.scenarios)):
        if r["overall_pass"] != "true":
            raise ValueError(f"Scenario failed: {r['scenario']}")
        typed.append(" & ".join(r[k] for k in ("scenario", "impact_size", "typed_current_size", "typed_two_hop_size", "review_scope_size")) + r" \\")
    typed += [r"\bottomrule\end{tabular}\end{table}"]
    (paper / "revision_impact.tex").write_text("\n".join(typed) + "\n")
    (revision / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
