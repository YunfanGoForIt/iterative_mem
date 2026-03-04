from __future__ import annotations

import math


def stdp_delta(
    activation_i: float,
    activation_j: float,
    dt_seconds: float,
    alpha: float = 0.25,
    tau: float = 180.0,
    beta: float = 0.15,
    interference_penalty: float = 0.0,
) -> float:
    base = alpha * activation_i * activation_j * math.exp(-abs(dt_seconds) / tau)
    return base - (beta * interference_penalty)


def clip_weight(weight: float, w_min: float = -1.0, w_max: float = 1.0) -> float:
    return max(w_min, min(w_max, weight))
