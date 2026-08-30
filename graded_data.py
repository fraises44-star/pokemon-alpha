from datetime import datetime
from supabase_db import get_supabase


SUPPORTED_GRADERS = [
    "PSA",
    "BGS",
    "CGC",
    "TAG",
    "SGC",
    "ACE",
]


def normalize_grader(grader):
    if not grader:
        return None

    grader = grader.upper().strip()

    aliases = {
        "BECKETT": "BGS",
        "BECKETT GRADING": "BGS",
        "BECKETT GRADING SERVICES": "BGS",
        "PSA": "PSA",
        "CGC": "CGC",
        "TAG": "TAG",
        "SGC": "SGC",
        "ACE": "ACE",
    }

    return aliases.get(grader, grader)


def save_graded_sale(
    card_id,
    grader,
    grade,
    sold_price_eur,
    sold_at=None,
    marketplace=None,
    source=None,
    source_reference=None,
):
    supabase = get_supabase()

    if supabase is None:
        raise RuntimeError("Supabase is not connected.")

    grader = normalize_grader(grader)

    if sold_at is None:
        sold_at = datetime.utcnow().isoformat()

    payload = {
        "card_id": card_id,
        "grader": grader,
        "grade": str(grade),
        "sold_price_eur": sold_price_eur,
        "sold_at": sold_at,
        "marketplace": marketplace,
        "source": source,
        "source_reference": source_reference,
    }

    supabase.table("graded_sales").insert(payload).execute()

    return payload


def load_graded_sales(card_id, limit=100):
    supabase = get_supabase()

    if supabase is None:
        return []

    result = (
        supabase
        .table("graded_sales")
        .select("*")
        .eq("card_id", card_id)
        .order("sold_at", desc=True)
        .limit(limit)
        .execute()
    )

    return result.data or []


def latest_sale_by_grade(card_id):
    sales = load_graded_sales(card_id, limit=500)

    latest = {}

    for sale in sales:
        key = (
            sale.get("grader"),
            sale.get("grade"),
        )

        if key not in latest:
            latest[key] = sale

    return list(latest.values())


def average_sales_by_grade(card_id):
    sales = load_graded_sales(card_id, limit=1000)

    grouped = {}

    for sale in sales:
        grader = sale.get("grader")
        grade = sale.get("grade")
        price = sale.get("sold_price_eur")

        if price is None:
            continue

        key = (grader, grade)

        grouped.setdefault(
            key,
            []
        ).append(float(price))

    results = []

    for (grader, grade), prices in grouped.items():

        results.append({
            "grader": grader,
            "grade": grade,
            "sales_count": len(prices),
            "average_price_eur": round(
                sum(prices) / len(prices),
                2
            ),
            "min_price_eur": round(
                min(prices),
                2
            ),
            "max_price_eur": round(
                max(prices),
                2
            ),
        })

    return results


def calculate_graded_premium(
    raw_price_eur,
    graded_price_eur,
):
    if not raw_price_eur:
        return None

    if not graded_price_eur:
        return None

    premium = (
        graded_price_eur
        / raw_price_eur
        - 1
    ) * 100

    return round(premium, 1)
