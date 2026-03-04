from openclaw_memory.core.plasticity import clip_weight, stdp_delta


def test_stdp_positive_without_penalty() -> None:
    delta = stdp_delta(activation_i=1.0, activation_j=0.8, dt_seconds=10)
    assert delta > 0


def test_stdp_penalty_can_reduce_update() -> None:
    delta = stdp_delta(activation_i=0.3, activation_j=0.3, dt_seconds=10, interference_penalty=1.0)
    assert delta < 0


def test_clip_weight_bounds() -> None:
    assert clip_weight(2.0) == 1.0
    assert clip_weight(-2.0) == -1.0
