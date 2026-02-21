"""Lightweight unit scenarios for zone selection/filter behavior."""

def select_active(scores, countertrend_flags, enabled, mode):
    best = None
    best_score = 10**9
    for i, score in enumerate(scores):
        blocked = enabled and mode == "IGNORE" and countertrend_flags[i]
        if blocked:
            continue
        if enabled and mode == "PENALIZE" and countertrend_flags[i]:
            score += 0.6
        if score < best_score:
            best_score = score
            best = i
    return best


def test_sideways_market_prefers_nearest():
    assert select_active([0.4, 0.8, 1.2], [False, False, False], False, "IGNORE") == 0


def test_fast_trend_countertrend_ignored():
    assert select_active([0.2, 0.35], [True, False], True, "IGNORE") == 1


def test_trap_penalized_not_ignored():
    assert select_active([0.2, 0.5], [True, False], True, "PENALIZE") == 1
