"""Fetch LOB League data from the Sleeper API into ./data/."""
import json
import os
import urllib.request

BASE = "https://api.sleeper.app/v1"
START_LEAGUE = "1389331963885670400"  # LOB 2026 season (walks back to 2024)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT, exist_ok=True)


def get(path):
    url = f"{BASE}{path}"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read().decode())


def save(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f)
    print(f"saved {name}")


# 1. Walk the league chain back through all seasons
chain = []
lid = START_LEAGUE
while lid and lid != "0":
    lg = get(f"/league/{lid}")
    chain.append({"league_id": lid, "season": lg["season"], "name": lg["name"]})
    save(f"league_{lg['season']}.json", lg)
    lid = lg.get("previous_league_id")
save("chain.json", chain)
print("seasons:", [c["season"] for c in chain])

# 2. Full detail for 2025 (retro-analysis target) + draft results for all seasons
for c in chain:
    season, lid = c["season"], c["league_id"]
    drafts = get(f"/league/{lid}/drafts")
    save(f"drafts_{season}.json", drafts)
    for d in drafts:
        picks = get(f"/draft/{d['draft_id']}/picks")
        save(f"draftpicks_{season}_{d['draft_id']}.json", picks)
    if season in ("2025", "2024"):
        save(f"users_{season}.json", get(f"/league/{lid}/users"))
        save(f"rosters_{season}.json", get(f"/league/{lid}/rosters"))
        save(f"tradedpicks_{season}.json", get(f"/league/{lid}/traded_picks"))
        tx = {}
        for wk in range(1, 18):
            tx[wk] = get(f"/league/{lid}/transactions/{wk}")
        save(f"transactions_{season}.json", tx)

# 3. Player DB (large; skip if already cached)
pdb_path = os.path.join(OUT, "players_nfl.json")
if not os.path.exists(pdb_path):
    print("downloading player DB...")
    players = get("/players/nfl")
    slim = {
        pid: {
            "name": p.get("full_name") or f"{p.get('first_name','')} {p.get('last_name','')}".strip(),
            "pos": p.get("position"),
            "team": p.get("team"),
        }
        for pid, p in players.items()
    }
    save("players_nfl.json", slim)
print("done")
