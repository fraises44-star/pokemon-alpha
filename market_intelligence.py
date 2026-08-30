from statistics import mean, pstdev


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_momentum_score(
    trend_price,
    avg_7d=None,
    avg_30d=None,
):
    trend_price = safe_float(trend_price)
    avg_7d = safe_float(avg_7d)
    avg_30d = safe_float(avg_30d)

    if trend_price is None:
        return 50

    reference = avg_30d or avg_7d

    if not reference or reference <= 0:
        return 50

    change_pct = (
        trend_price / reference - 1
    ) * 100

    score = 50 + change_pct * 2

    return round(
        clamp(score),
        1
    )


def calculate_value_score(
    trend_price,
    low_price=None,
    avg_7d=None,
    avg_30d=None,
):
    trend_price = safe_float(trend_price)
    low_price = safe_float(low_price)
    avg_7d = safe_float(avg_7d)
    avg_30d = safe_float(avg_30d)

    if not trend_price or trend_price <= 0:
        return 50

    score = 50

    # Reward a genuine discount versus the longer-term reference,
    # but cap the reward so a collapsing card cannot automatically
    # receive 100/100 Value.
    if avg_30d and avg_30d > 0:
        discount_30d = (
            avg_30d / trend_price - 1
        ) * 100

        if discount_30d > 0:
            score += min(
                discount_30d * 0.8,
                25
            )

        elif discount_30d < 0:
            score += max(
                discount_30d * 0.5,
                -15
            )

    # Compare current trend with the more recent 7-day market.
    if avg_7d and avg_7d > 0:
        change_vs_7d = (
            trend_price / avg_7d - 1
        ) * 100

        # A moderate discount can be attractive.
        if -10 <= change_vs_7d < 0:
            score += 8

        # A large recent fall is a falling-knife warning.
        elif change_vs_7d < -10:
            score -= min(
                abs(change_vs_7d) * 0.8,
                30
            )

        # Strong short-term price expansion makes the card less
        # attractive from a value-entry perspective.
        elif change_vs_7d > 15:
            score -= min(
                change_vs_7d * 0.4,
                15
            )

    # Detect whether the recent 7-day market itself is deteriorating
    # versus the 30-day market.
    if (
        avg_7d
        and avg_30d
        and avg_7d > 0
        and avg_30d > 0
    ):
        seven_vs_thirty = (
            avg_7d / avg_30d - 1
        ) * 100

        if seven_vs_thirty < -10:
            score -= min(
                abs(seven_vs_thirty) * 0.6,
                20
            )

        elif seven_vs_thirty > 5:
            score += min(
                seven_vs_thirty * 0.3,
                8
            )

    # A very large gap between low listing price and trend can indicate
    # unstable pricing or weak market depth. Do not reward it as value.
    if (
        low_price
        and low_price > 0
        and low_price < trend_price
    ):
        spread_pct = (
            trend_price - low_price
        ) / trend_price * 100

        if spread_pct > 20:
            score -= min(
                (spread_pct - 20) * 0.25,
                10
            )

    return round(
        clamp(score),
        1
    )

def calculate_liquidity_score(
    trend_price=None,
    avg_price=None,
    avg_1d=None,
    avg_7d=None,
    avg_30d=None,
):
    values = [
        safe_float(trend_price),
        safe_float(avg_price),
        safe_float(avg_1d),
        safe_float(avg_7d),
        safe_float(avg_30d),
    ]

    present = [
        value
        for value in values
        if value is not None
    ]

    score = 25 + len(present) * 12

    if (
        trend_price
        and avg_price
    ):
        trend = safe_float(
            trend_price
        )

        avg = safe_float(
            avg_price
        )

        if (
            trend
            and avg
            and trend > 0
        ):
            spread = abs(
                trend - avg
            ) / trend

            if spread <= 0.10:
                score += 10

            elif spread <= 0.20:
                score += 5

    return round(
        clamp(score),
        1
    )


def calculate_volatility_score(
    price_history,
):
    prices = []

    for item in price_history or []:
        if isinstance(item, dict):
            price = safe_float(
                item.get("trend_price_eur")
                or item.get("trend")
            )
        else:
            price = safe_float(item)

        if price is not None and price > 0:
            prices.append(price)

    observation_count = len(prices)

    # Not enough proprietary history to judge stability yet.
    if observation_count < 3:
        return None

    average_price = mean(prices)

    if average_price <= 0:
        return None

    volatility = (
        pstdev(prices)
        / average_price
        * 100
    )

    score = 100 - volatility * 3

    # Confidence penalty while our own history is still young.
    if observation_count < 7:
        score *= 0.70

    elif observation_count < 14:
        score *= 0.85

    elif observation_count < 30:
        score *= 0.95

    return round(
        clamp(score),
        1
    )


def calculate_graded_premium_score(
    raw_price,
    graded_sales,
):
    raw_price = safe_float(
        raw_price
    )

    if (
        not raw_price
        or raw_price <= 0
        or not graded_sales
    ):
        return None

    prices = []

    for sale in graded_sales:
        price = safe_float(
            sale.get(
                "sold_price_eur"
            )
        )

        if (
            price is not None
            and price > 0
        ):
            prices.append(price)

    if not prices:
        return 50

    graded_average = mean(
        prices
    )

    premium_pct = (
        graded_average
        / raw_price
        - 1
    ) * 100

    score = 40 + premium_pct * 0.25

    return round(
        clamp(score),
        1
    )


def calculate_population_score(
    population_history,
):
    if not population_history:
         return None

    rows = []

    for item in population_history:
        population = safe_float(
            item.get(
                "population"
            )
        )

        if population is not None:
            rows.append(
                {
                    "grader": item.get(
                        "grader"
                    ),
                    "grade": item.get(
                        "grade"
                    ),
                    "population": population,
                    "recorded_at": item.get(
                        "recorded_at"
                    ),
                }
            )

    if not rows:
        return 50

    latest_population = sum(
        row["population"]
        for row in rows
    )

    if latest_population <= 100:
        score = 90

    elif latest_population <= 500:
        score = 80

    elif latest_population <= 2000:
        score = 68

    elif latest_population <= 5000:
        score = 58

    elif latest_population <= 15000:
        score = 48

    else:
        score = 38

    return round(
        clamp(score),
        1
    )


def calculate_reprint_risk_score(
    set_name=None,
    rarity=None,
):
    set_name = (
        set_name or ""
    ).lower()

    rarity = (
        rarity or ""
    ).lower()

    score = 60

    if "promo" in set_name:
        score -= 8

    if "special illustration" in rarity:
        score += 15

    elif "illustration rare" in rarity:
        score += 10

    elif "hyper rare" in rarity:
        score += 8

    elif "ultra rare" in rarity:
        score += 5

    return round(
        clamp(score),
        1
    )


def calculate_opportunity_score(
    momentum_score,
    value_score,
    liquidity_score,
    volatility_score,
    graded_premium_score,
    population_score,
    reprint_risk_score,
):
    components = {
        "momentum": safe_float(momentum_score),
        "value": safe_float(value_score),
        "liquidity": safe_float(liquidity_score),
        "volatility": safe_float(volatility_score),
        "graded_premium": safe_float(graded_premium_score),
        "population": safe_float(population_score),
        "reprint_risk": safe_float(reprint_risk_score),
    }

    weights = {
        "momentum": 0.20,
        "value": 0.20,
        "liquidity": 0.15,
        "volatility": 0.10,
        "graded_premium": 0.15,
        "population": 0.10,
        "reprint_risk": 0.10,
    }

    available = {
        key: value
        for key, value in components.items()
        if value is not None
    }

    if not available:
        return None

    available_weight = sum(
        weights[key]
        for key in available
    )

    if available_weight <= 0:
        return None

    score = sum(
        available[key] * weights[key]
        for key in available
    ) / available_weight

    return round(
        clamp(score),
        1
    )


def build_market_signal(
    card,
    price_history=None,
    graded_sales=None,
    population_history=None,
):
    prices = card.get("prices") or {
        "trend": card.get("trend"),
        "low": card.get("low"),
        "avg": card.get("avg"),
        "avg1": card.get("avg1"),
        "avg7": card.get("avg7"),
        "avg30": card.get("avg30"),
    }

    momentum_score = (
        calculate_momentum_score(
            prices.get("trend"),
            prices.get("avg7"),
            prices.get("avg30"),
        )
    )

    value_score = (
        calculate_value_score(
            prices.get("trend"),
            prices.get("low"),
            prices.get("avg7"),
            prices.get("avg30"),
        )
    )

    liquidity_score = (
        calculate_liquidity_score(
            prices.get("trend"),
            prices.get("avg"),
            prices.get("avg1"),
            prices.get("avg7"),
            prices.get("avg30"),
        )
    )

    volatility_score = (
        calculate_volatility_score(
            price_history
        )
    )

    graded_premium_score = (
        calculate_graded_premium_score(
            prices.get("trend"),
            graded_sales,
        )
    )

    population_score = (
        calculate_population_score(
            population_history
        )
    )

    reprint_risk_score = (
        calculate_reprint_risk_score(
            card.get("set_name"),
            card.get("rarity"),
        )
    )

    opportunity_score = (
        calculate_opportunity_score(
            momentum_score,
            value_score,
            liquidity_score,
            volatility_score,
            graded_premium_score,
            population_score,
            reprint_risk_score,
        )
    )
    confidence_points = 0
    confidence_max = 0

    core_price_fields = [
        prices.get("trend"),
        prices.get("avg7"),
        prices.get("avg30"),
    ]

    for value in core_price_fields:
        confidence_max += 10

        if safe_float(value) is not None:
            confidence_points += 10

    history_count = len(price_history or [])

    confidence_max += 25

    if history_count >= 30:
        confidence_points += 25

    elif history_count >= 14:
        confidence_points += 20

    elif history_count >= 7:
        confidence_points += 15

    elif history_count >= 3:
        confidence_points += 8

    confidence_max += 15

    if volatility_score is not None:
        confidence_points += 15

    confidence_max += 15

    if graded_premium_score is not None:
        confidence_points += 15

    confidence_max += 15

    if population_score is not None:
        confidence_points += 15

    data_confidence = round(
        confidence_points
        / confidence_max
        * 100,
        1
    )
    return {
        "card_id": card.get("id"),
        "momentum_score": momentum_score,
        "value_score": value_score,
        "liquidity_score": liquidity_score,
        "volatility_score": volatility_score,
        "graded_premium_score": graded_premium_score,
        "population_score": population_score,
        "reprint_risk_score": reprint_risk_score,
        "data_confidence": data_confidence,
        "opportunity_score": opportunity_score,
    }
