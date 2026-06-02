"""Per-trial scoring, per-scenario aggregation, and A/B comparison."""

from __future__ import annotations

import statistics
from collections import defaultdict

from .contracts import TrialRecord

W_L2 = 0.4
W_L3 = 0.6


def score_trial(l1: dict, l2: dict, l3: dict) -> tuple[bool, float]:
    """Per SPEC: 0 if any L1 gate fails, else the weighted mean of L2 and L3.

    Both l2 and l3 values are in 0..1. (Judge 1-5 scores are normalized to 0..1 in judges.py before
    they enter l3; acceptance_pass is already 0/1.) Missing layers drop out and the present-layer
    weights renormalize.
    """
    l1_pass = all(bool(v) for v in l1.values()) if l1 else True
    if not l1_pass:
        return False, 0.0

    parts: list[tuple[float, float]] = []  # (weight, value-in-0..1)
    if l2:
        parts.append((W_L2, _mean(l2.values())))
    if l3:
        parts.append((W_L3, _mean(l3.values())))
    if not parts:
        return True, 1.0
    wsum = sum(w for w, _ in parts)
    return True, sum(w * v for w, v in parts) / wsum


def _mean(vals) -> float:
    vals = list(vals)
    return sum(vals) / len(vals) if vals else 0.0


def aggregate(records: list[TrialRecord]) -> dict:
    """Group by scenario; report gate pass-rate, score mean/stdev, per-dim L2/L3, cost means."""
    by_scn: dict[str, list[TrialRecord]] = defaultdict(list)
    for r in records:
        by_scn[r.scenario].append(r)

    out = {}
    for scn, recs in sorted(by_scn.items()):
        scores = [r.score for r in recs]
        out[scn] = {
            "trials": len(recs),
            "gate_pass_rate": round(sum(1 for r in recs if r.l1_pass) / len(recs), 3),
            "score_mean": round(_mean(scores), 4),
            "score_stdev": round(statistics.pstdev(scores), 4) if len(scores) > 1 else 0.0,
            "l2_mean": _dim_means([r.l2 for r in recs]),
            "l3_mean": _dim_means([r.l3 for r in recs]),
            "cost_mean": _cost_means([r.cost for r in recs]),
        }
    return out


def _dim_means(dicts: list[dict]) -> dict:
    keys = {k for d in dicts for k in d}
    return {k: round(_mean([d[k] for d in dicts if k in d]), 3) for k in sorted(keys)}


def _cost_means(costs: list[dict]) -> dict:
    keys = {k for c in costs for k in c}
    return {k: round(_mean([c[k] for c in costs if k in c]), 1) for k in sorted(keys)}


def ab_compare(records_a: list[TrialRecord], records_b: list[TrialRecord]) -> dict:
    """Per-scenario deltas (B - A) with regression flags (a gate that passed in A and fails in B)."""
    agg_a, agg_b = aggregate(records_a), aggregate(records_b)
    out = {}
    for scn in sorted(set(agg_a) | set(agg_b)):
        a, b = agg_a.get(scn), agg_b.get(scn)
        if not a or not b:
            out[scn] = {"note": "present in only one version"}
            continue
        out[scn] = {
            "score_delta": round(b["score_mean"] - a["score_mean"], 4),
            "gate_pass_rate_delta": round(b["gate_pass_rate"] - a["gate_pass_rate"], 3),
            "regression": b["gate_pass_rate"] < a["gate_pass_rate"],
            "score_a": a["score_mean"],
            "score_b": b["score_mean"],
        }
    return out
