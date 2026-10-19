from bot.services.calculations import calculate_norms, weight_progress


def test_first_weigh_in_has_no_changes():
    p = weight_progress([70.0], "lose", 60.0)
    assert p["since_last"] is None and p["since_start"] is None
    assert p["left"] == 10.0 and p["reached"] is False


def test_losing_toward_target():
    p = weight_progress([70.0, 69.5, 69.0], "lose", 60.0)
    assert p["since_last"] == -0.5
    assert p["since_start"] == -1.0
    assert p["left"] == 9.0
    assert p["toward_goal"] is True


def test_gaining_while_cutting_is_not_progress():
    p = weight_progress([70.0, 70.4], "lose", 60.0)
    assert p["toward_goal"] is False


def test_target_reached_lose_and_gain():
    assert weight_progress([61.0, 59.8], "lose", 60.0)["reached"] is True
    assert weight_progress([74.0, 75.2], "gain", 75.0)["reached"] is True


def test_maintain_has_no_target():
    p = weight_progress([70.0, 70.3], "maintain", None)
    assert p["left"] is None and p["reached"] is None and p["since_last"] == 0.3


def test_norms_shape():
    n = calculate_norms("f", 25, 165, 60, 1.4, "lose", "medium")
    assert set(n) == {"target_calories", "protein_g", "fat_g", "carbs_g", "water_ml"}
    assert n["target_calories"] >= 1200
