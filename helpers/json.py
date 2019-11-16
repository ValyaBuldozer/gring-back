import json


def to_json(obj, lam=lambda o: o.to_json()):
    return json.dumps(
        obj,
        default=lam,
        ensure_ascii=False,
        indent=4
    )
    