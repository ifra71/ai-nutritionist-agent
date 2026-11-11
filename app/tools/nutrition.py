def calculate_nutrition(
    quantity_grams: float,
    calories_per_100g: float,
    protein_per_100g: float,
    carbs_per_100g: float,
    fat_per_100g: float,
    additional_nutrients_per_100g: dict | None = None
):
    multiplier = quantity_grams / 100

    result = {
        "quantity_grams": quantity_grams,
        "calories": round(calories_per_100g * multiplier, 2),
        "protein": round(protein_per_100g * multiplier, 2),
        "carbs": round(carbs_per_100g * multiplier, 2),
        "fat": round(fat_per_100g * multiplier, 2)
    }

    if additional_nutrients_per_100g:
        result["additional_nutrients"] = {}

        for nutrient, value in additional_nutrients_per_100g.items():
            if value is None:
                continue

            if isinstance(value, dict):
                amount = value.get("amount")
                unit = value.get("unit")
            else:
                amount = value
                unit = None

            if amount is None:
                continue

            calculated_amount = round(
                float(amount) * multiplier, 2
            )

            result["additional_nutrients"][nutrient] = {
                "amount": calculated_amount,
                "unit": unit
            }

    return result
