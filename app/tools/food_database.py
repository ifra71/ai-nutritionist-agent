import httpx

from app.db.database import settings

BASE_URL = "https://api.nal.usda.gov/fdc/v1"

NUTRIENTS = {
    1008: ("calories", "kcal"),
    1003: ("protein", "g"),
    1005: ("carbs", "g"),
    1004: ("fat", "g"),
    1079: ("fiber", "g"),
    2000: ("sugar", "g"),
    1093: ("sodium", "mg"),
    1087: ("calcium", "mg"),
    1089: ("iron", "mg"),
    1092: ("potassium", "mg"),
    1098: ("copper", "mg"),
    1101: ("manganese", "mg"),
    1090: ("magnesium", "mg"),
    1095: ("zinc", "mg"),
    1162: ("vitamin_c", "mg"),
    1106: ("vitamin_a", "µg"),
    1114: ("vitamin_d", "µg"),
    1109: ("vitamin_e", "mg"),
    1185: ("vitamin_k", "µg"),
    1165: ("vitamin_b1", "mg"),
    1166: ("vitamin_b2", "mg"),
    1167: ("vitamin_b3", "mg"),
    1170: ("vitamin_b6", "mg"),
    1175: ("vitamin_b9", "µg"),
    1178: ("vitamin_b12", "µg")
}


async def search_food_nutrition(food_name: str):
    params = {
        "api_key": settings.USDA_API_KEY
    }

    payload = {
        "query": food_name,
        "pageSize": 5
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{BASE_URL}/foods/search",
            params=params,
            json=payload
        )

        response.raise_for_status()
        data = response.json()

        foods = []

        for food in data.get("foods", []):
            food_id = food.get("fdcId")

            detail_response = await client.get(
                f"{BASE_URL}/food/{food_id}",
                params=params
            )

            detail_response.raise_for_status()
            details = detail_response.json()

            nutrients = {}

            for item in details.get("foodNutrients", []):
                nutrient = item.get("nutrient", {})
                nutrient_id = nutrient.get("id")

                if nutrient_id in NUTRIENTS:
                    name, unit = NUTRIENTS[nutrient_id]
                    amount = item.get("amount")

                    if amount is not None:
                        nutrients[name] = {
                            "amount": amount,
                            "unit": unit
                        }

            food_result = {
                "food_id": food_id,
                "food_name": food.get("description"),
                "nutrients_per_100g": nutrients
            }

            for name in ("calories", "protein", "carbs", "fat"):
                value = nutrients.get(name)
                food_result[f"{name}_per_100g"] = (
                    value["amount"] if value else None
                )

            foods.append(food_result)

    return foods
