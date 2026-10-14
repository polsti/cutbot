from bot.services.calculations import (
    calculate_bmr,
    calculate_macros,
    calculate_target_calories,
    calculate_tdee,
    calculate_water_ml,
)


def test_bmr_male_vs_female_formula():
    male = calculate_bmr("m", weight_kg=80, height_cm=180, age=25)
    female = calculate_bmr("f", weight_kg=80, height_cm=180, age=25)
    assert male == 10 * 80 + 6.25 * 180 - 5 * 25 + 5
    assert female == 10 * 80 + 6.25 * 180 - 5 * 25 - 161


def test_tdee_applies_activity_coefficient():
    assert calculate_tdee(1000, 1.2) == 1200
    assert calculate_tdee(1000, 1.9) == 1900


def test_lose_weight_reduces_calories():
    tdee = 2000
    target = calculate_target_calories(tdee, "f", "lose", "medium")
    assert target == round(tdee * 0.85)


def test_gain_weight_increases_calories():
    tdee = 2000
    target = calculate_target_calories(tdee, "m", "gain", "fast")
    assert target == round(tdee * 1.15)


def test_calorie_floor_protects_low_tdee_women():
    target = calculate_target_calories(tdee=1000, gender="f", goal="lose", pace="fast")
    assert target == 1200  # floor, not 800


def test_calorie_floor_protects_low_tdee_men():
    target = calculate_target_calories(tdee=1300, gender="m", goal="lose", pace="fast")
    assert target == 1500  # floor, not 1040


def test_macros_roughly_sum_to_target_calories():
    macros = calculate_macros(gender="m", goal="maintain", weight_kg=70, target_calories=2000)
    recomputed = macros["protein_g"] * 4 + macros["fat_g"] * 9 + macros["carbs_g"] * 4
    assert abs(recomputed - 2000) <= 5  # rounding slack


def test_macros_male_cut_uses_midpoint_of_given_range():
    # protein 1.8-2.4 g/kg -> midpoint 2.1; fat 0.8-1.0 g/kg -> midpoint 0.9
    macros = calculate_macros(gender="m", goal="lose", weight_kg=80, target_calories=2200)
    assert macros["protein_g"] == round(2.1 * 80)
    assert macros["fat_g"] == round(0.9 * 80)


def test_macros_female_gain_uses_midpoint_of_given_range():
    # protein 1.5-2.0 g/kg -> midpoint 1.75; fat 1.0-1.2 g/kg -> midpoint 1.1
    macros = calculate_macros(gender="f", goal="gain", weight_kg=60, target_calories=2200)
    assert macros["protein_g"] == round(1.75 * 60)
    assert macros["fat_g"] == round(1.1 * 60)


def test_macros_differ_between_genders_for_same_goal():
    male = calculate_macros(gender="m", goal="maintain", weight_kg=70, target_calories=2200)
    female = calculate_macros(gender="f", goal="maintain", weight_kg=70, target_calories=2200)
    assert male["protein_g"] != female["protein_g"]


def test_water_is_30ml_per_kg():
    assert calculate_water_ml(70) == 2100


def test_activity_coefficient_bounds():
    from bot.services.calculations import calculate_activity_coefficient

    minimum = calculate_activity_coefficient("office", "0", "0", "<5000")
    maximum = calculate_activity_coefficient("physical", "5+", "5+", "15000+")
    assert minimum == 1.2
    assert maximum == 1.9


def test_activity_coefficient_rewards_training_even_with_office_job():
    from bot.services.calculations import calculate_activity_coefficient

    office_sedentary = calculate_activity_coefficient("office", "0", "0", "<5000")
    office_active = calculate_activity_coefficient("office", "5+", "3-4", "10000-15000")
    assert office_active > office_sedentary
