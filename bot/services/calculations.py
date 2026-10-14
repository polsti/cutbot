"""BMR/TDEE/macro math, per the product spec section 3.2 (Mifflin-St Jeor formula)."""

# Composite activity model: instead of one "pick a bucket" question, the
# coefficient is built from four independent factors a person can answer
# separately. Each factor contributes its own piece, so e.g. an office job
# + heavy lifting 5x/week lands differently than a physical job + nothing
# extra, instead of both being forced into the same "moderate" bucket.
#
# Bounds were chosen to land in the same 1.2-1.9 range the classic
# Harris-Benedict/Mifflin activity multipliers use (literature-calibrated),
# just reached via four smaller knobs instead of one coarse one:
#   min: office job, no training, no extra steps        -> 1.20
#   max: physical job, 5+ lifting, 5+ cardio, 15k+ steps -> 1.90

JOB_TYPE_BASE = {
    "office": 1.2,       # mostly sitting (desk job / studying)
    "physical": 1.375,   # on your feet / physical labor
}

FREQUENCY_BUCKETS = ["0", "1-2", "3-4", "5+"]

STRENGTH_ADD = {"0": 0.0, "1-2": 0.05, "3-4": 0.10, "5+": 0.15}
CARDIO_ADD = {"0": 0.0, "1-2": 0.075, "3-4": 0.15, "5+": 0.225}
STEPS_ADD = {"<5000": 0.0, "5000-10000": 0.05, "10000-15000": 0.10, "15000+": 0.15}

# goal -> pace -> fraction of TDEE to adjust by
GOAL_ADJUSTMENTS = {
    "lose": {"slow": -0.10, "medium": -0.15, "fast": -0.20},
    "gain": {"slow": 0.05, "medium": 0.10, "fast": 0.15},
}

MIN_CALORIES = {"m": 1500, "f": 1200}

WATER_ML_PER_KG = 30

# gender -> goal -> (low, high) grams per kg of bodyweight.
# We use the midpoint of each range as the single value shown to the user.
PROTEIN_G_PER_KG_RANGE = {
    "m": {"lose": (1.8, 2.4), "maintain": (1.6, 2.0), "gain": (1.8, 2.2)},
    "f": {"lose": (1.7, 2.3), "maintain": (1.4, 1.9), "gain": (1.5, 2.0)},
}
FAT_G_PER_KG_RANGE = {
    "m": {"lose": (0.8, 1.0), "maintain": (0.8, 1.2), "gain": (1.0, 1.2)},
    "f": {"lose": (0.8, 1.0), "maintain": (0.8, 1.2), "gain": (1.0, 1.2)},
}


def _midpoint(low: float, high: float) -> float:
    return (low + high) / 2


def calculate_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if gender == "m" else base - 161


def calculate_activity_coefficient(job_type: str, strength_freq: str, cardio_freq: str, steps_bucket: str) -> float:
    return (
        JOB_TYPE_BASE[job_type]
        + STRENGTH_ADD[strength_freq]
        + CARDIO_ADD[cardio_freq]
        + STEPS_ADD[steps_bucket]
    )


def calculate_tdee(bmr: float, activity_coefficient: float) -> float:
    return bmr * activity_coefficient


def calculate_target_calories(tdee: float, gender: str, goal: str, pace: str | None) -> int:
    if goal == "maintain":
        calories = tdee
    else:
        calories = tdee * (1 + GOAL_ADJUSTMENTS[goal][pace])

    return max(round(calories), MIN_CALORIES[gender])


def calculate_macros(gender: str, goal: str, weight_kg: float, target_calories: int) -> dict:
    protein_per_kg = _midpoint(*PROTEIN_G_PER_KG_RANGE[gender][goal])
    fat_per_kg = _midpoint(*FAT_G_PER_KG_RANGE[gender][goal])

    protein_g = round(protein_per_kg * weight_kg)
    fat_g = round(fat_per_kg * weight_kg)

    carbs_kcal = target_calories - (protein_g * 4) - (fat_g * 9)
    carbs_g = max(round(carbs_kcal / 4), 0)

    return {"protein_g": protein_g, "fat_g": fat_g, "carbs_g": carbs_g}


def calculate_water_ml(weight_kg: float) -> int:
    return round(weight_kg * WATER_ML_PER_KG)
