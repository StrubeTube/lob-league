"""Refresh current-league (2026) data from Sleeper: league, users, rosters
(incl. official keepers), drafts, traded picks — and draft picks once the
draft has run. Always overwrites; run build_site.py afterwards.

History files (2020-2025) are frozen and never touched.
"""
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
LEAGUE_2025 = "1256797823983177729"


def get(path):
    with urllib.request.urlopen(f"https://api.sleeper.app/v1{path}") as r:
        return json.loads(r.read().decode())


def save(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f)
    print(f"saved {name}")


# find the 2026 league (use the saved id if we have it, else scan the commish's leagues)
try:
    lid = json.load(open(os.path.join(DATA, "league_2026.json"), encoding="utf-8"))["league_id"]
except (FileNotFoundError, KeyError):
    users25 = json.load(open(os.path.join(DATA, "users_2025.json"), encoding="utf-8"))
    uid = next(u["user_id"] for u in users25 if u["display_name"] == "Strubes")
    lg = next((l for l in (get(f"/user/{uid}/leagues/nfl/2026") or [])
               if l.get("previous_league_id") == LEAGUE_2025), None)
    if lg is None:
        raise SystemExit("2026 league not found on Sleeper yet")
    lid = lg["league_id"]

save("league_2026.json", get(f"/league/{lid}"))
save("users_2026.json", get(f"/league/{lid}/users"))
save("rosters_2026.json", get(f"/league/{lid}/rosters"))
drafts = get(f"/league/{lid}/drafts")
save("drafts_2026.json", drafts)
save("tradedpicks_2026.json", get(f"/league/{lid}/traded_picks"))

# every 2026 transaction (trades live here; offseason deals sit in week 1)
tx = {}
for wk in range(1, 19):
    tx[str(wk)] = get(f"/league/{lid}/transactions/{wk}") or []
save("transactions_2026.json", tx)

# FantasyFootballCalculator ADP: current year daily (keeper-market reads on
# this year's trades), past years once (static history). Never let an FFC
# outage break the Sleeper refresh.
def _ffc(year):
    req = urllib.request.Request(
        f"https://fantasyfootballcalculator.com/api/v1/adp/half-ppr?teams=10&year={year}",
        headers={"User-Agent": "league-site/1.0 (personal fantasy league site)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

try:
    save("ffc_adp_2026.json", _ffc(2026))
except Exception as e:
    print(f"FFC current ADP unavailable ({e}) — keeping the cached file")
if not os.path.exists(os.path.join(DATA, "ffc_adp_hist.json")):
    try:
        save("ffc_adp_hist.json", {str(y): _ffc(y) for y in range(2025, 2026)})
    except Exception as e:
        print(f"FFC ADP history unavailable ({e})")

# once the draft has actually run, pull its picks (carries is_keeper flags)
for d in drafts or []:
    if d.get("status") == "complete":
        save(f"draftpicks_2026_{d['draft_id']}.json", get(f"/draft/{d['draft_id']}/picks"))

ks = sum(1 for r in json.load(open(os.path.join(DATA, "rosters_2026.json"), encoding="utf-8"))
         if r.get("keepers"))
print(f"done — league {lid}, {ks}/10 teams have official keepers set")
