"""Quote two-asset weighted geometric pools across trade sizes with fee-adjusted input and invariant diagnostics."""

from .common import (
    number,
    integer,
    identity,
    records,
    chronology,
    allocate,
    result,
    validate_document,
)
from decimal import Decimal


def _analyze(d):
    x = float(number(d["balance_in"], minimum="0.000000000000000001"))
    y = float(number(d["balance_out"], minimum="0.000000000000000001"))
    w = float(number(d["weight_in"], maximum=1))
    fee = float(number(d["fee"], maximum=1))
    if w == 0 or w == 1 or fee == 1:
        raise ValueError("strictly interior weight and fee below one required")
    rows = []
    for a in d["amounts"]:
        amount = float(number(a, minimum="0.000000000000000001"))
        effective = amount * (1 - fee)
        output = y * (1 - (x / (x + effective)) ** (w / (1 - w)))
        spot = (y / (1 - w)) / (x / w)
        price = output / amount
        rows.append(
            {
                "amount_in": amount,
                "output": output,
                "price_impact": 1 - price / spot,
                "initial_invariant": x**w * y ** (1 - w),
                "post_invariant": (x + amount) ** w * (y - output) ** (1 - w),
            }
        )
    return result({"quotes": rows, "spot_price": (y / (1 - w)) / (x / w)})


def analyze(document):
    validate_document(document)
    try:
        return result(_analyze(document))
    except (KeyError, TypeError, ArithmeticError, RecursionError) as error:
        raise ValueError("invalid domain input: " + str(error)) from error
