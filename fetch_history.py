"""Pull full league history: matchups (with player points), transactions,
users/rosters, playoff brackets, and traded picks for every season 2020-2025."""
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def get(path):
    with urllib.request.urlopen(f"https://api.sleeper.app/v1{path}") as r:
        return json.loads(r.read().decode())


def save(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f)


chain = json.load(open(os.path.join(DATA, "chain.json"), encoding="utf-8"))

for c in chain:
    season, lid = c["season"], c["league_id"]
    if season >= "2026":
        continue   # pre-draft season - refresh_2026.py owns it

    for ep, fname in (("users", f"users_{season}.json"), ("rosters", f"rosters_{season}.json")):
        path = os.path.join(DATA, fname)
        if not os.path.exists(path):
            save(fname, get(f"/league/{lid}/{ep}"))

    # full-season matchups incl. players_points (slimmed)
    mpath = os.path.join(DATA, f"matchups_full_{season}.json")
    if not os.path.exists(mpath):
        out = {}
        for wk in range(1, 19):
            items = get(f"/league/{lid}/matchups/{wk}") or []
            out[str(wk)] = [{
                "roster_id": m["roster_id"], "matchup_id": m.get("matchup_id"),
                "points": m.get("points"), "starters": m.get("starters"),
                "players_points": m.get("players_points"),
            } for m in items]
        save(f"matchups_full_{season}.json", out)
        print(f"{season}: matchups ok")

    tpath = os.path.join(DATA, f"transactions_{season}.json")
    if not os.path.exists(tpath):
        tx = {}
        for wk in range(1, 19):
            tx[wk] = get(f"/league/{lid}/transactions/{wk}") or []
        save(f"transactions_{season}.json", tx)
        print(f"{season}: transactions ok")

    for ep in ("winners_bracket", "losers_bracket"):
        bpath = os.path.join(DATA, f"{ep}_{season}.json")
        if not os.path.exists(bpath):
            save(f"{ep}_{season}.json", get(f"/league/{lid}/{ep}"))

    ppath = os.path.join(DATA, f"tradedpicks_{season}.json")
    if not os.path.exists(ppath):
        save(f"tradedpicks_{season}.json", get(f"/league/{lid}/traded_picks"))

    print(f"{season}: complete")
print("done")
