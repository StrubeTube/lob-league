"""Compute the full stats layer for the LOB league site -> data/site_data.json.

Owner identity is by user_id (display names change across seasons; latest wins).
Regular season = weeks 1..playoff_week_start-1 per season's league settings.
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SEASONS = ["2024", "2025"]


def load(n):
    with open(os.path.join(DATA, n), encoding="utf-8") as f:
        return json.load(f)


players_db = load("players_nfl.json")
pname = lambda pid: (players_db.get(str(pid)) or {}).get("name") or f"?{pid}"
ppos = lambda pid: (players_db.get(str(pid)) or {}).get("pos") or "?"

# ---------- owner registry ----------
owners = {}          # user_id -> {name, aliases:set, seasons:[]}
season_ctx = {}      # season -> {rmap: roster_id->user_id, users, league, pws}
team_names = {}   # uid -> [{s, tn}]
for s in SEASONS:
    users = load(f"users_{s}.json")
    rosters = load(f"rosters_{s}.json")
    lg = load(f"league_{s}.json")
    umap = {u["user_id"]: u["display_name"] for u in users}
    for u in users:
        tn = (u.get("metadata") or {}).get("team_name") or u["display_name"]
        team_names.setdefault(u["user_id"], []).append({"s": s, "tn": tn})
    rmap = {}
    for r in rosters:
        uid = r["owner_id"] or f"unknown_{s}_{r['roster_id']}"
        rmap[r["roster_id"]] = uid
        o = owners.setdefault(uid, {"aliases": set(), "seasons": []})
        nm = umap.get(uid)
        if nm:
            o["aliases"].add(nm)
            o["name"] = nm  # later seasons overwrite -> latest name
        o.setdefault("name", nm or "Former manager")
        o["seasons"].append(s)
    season_ctx[s] = {"rmap": rmap, "league": lg, "rosters": rosters,
                     "pws": lg["settings"].get("playoff_week_start", 15)}

# ---------- owner merges (same human, different accounts) ----------
def uid_by_alias(alias):
    for uid, o in owners.items():
        if alias in o["aliases"]:
            return uid
    return None

MERGES = []   # no owner merges in LOB
canon_map = {}
for old_alias, new_alias in MERGES:
    old_uid, new_uid = uid_by_alias(old_alias), uid_by_alias(new_alias)
    if old_uid and new_uid and old_uid != new_uid:
        canon_map[old_uid] = new_uid
        owners[new_uid]["aliases"] |= owners[old_uid]["aliases"]
        owners[new_uid]["seasons"] = sorted(set(owners[new_uid]["seasons"] + owners[old_uid]["seasons"]))
        del owners[old_uid]
_sw = None   # no ownerless rosters in LOB
for _uid in [u for u in owners if str(u).startswith("unknown_")]:
    if _sw:
        canon_map[_uid] = _sw
        owners[_sw]["seasons"] = sorted(set(owners[_sw]["seasons"] + owners[_uid]["seasons"]))
        del owners[_uid]

canon = lambda uid: canon_map.get(uid, uid)
for _s in SEASONS:
    season_ctx[_s]["rmap"] = {rid: canon(u) for rid, u in season_ctx[_s]["rmap"].items()}
merged_names = {}
for uid, hist in team_names.items():
    merged_names.setdefault(canon(uid), []).extend(hist)
team_names = {uid: sorted(v, key=lambda x: x["s"]) for uid, v in merged_names.items()}

oname = lambda uid: owners.get(uid, {}).get("name", "Former manager")

# ---------- per-season processing ----------
seasons_out = []
h2h = defaultdict(lambda: [0, 0])          # (uidA,uidB) -> [winsA, lossesA]
career = defaultdict(lambda: defaultdict(float))
game_log = defaultdict(list)               # uid -> chronological reg-season results (W/L)
high_weeks, low_weeks, blowouts, closest, big_loss, cheap_win, blunders = [], [], [], [], [], [], []
player_season_pts = defaultdict(float)     # (season, player_id) -> total pts
roster_week_pts = {}                       # (season, wk, roster_id) -> players_points dict

for s in SEASONS:
    ctx = season_ctx[s]
    rmap, pws = ctx["rmap"], ctx["pws"]
    matchups = load(f"matchups_full_{s}.json")
    weekly_high_uid = {}

    for wk_s, items in matchups.items():
        wk = int(wk_s)
        scores = []
        for m in items:
            if m.get("players_points"):
                roster_week_pts[(s, wk, m["roster_id"])] = m["players_points"]
                for pid, pts in m["players_points"].items():
                    player_season_pts[(s, pid)] += pts or 0
            if m.get("points"):
                bench = sum((m.get("players_points") or {}).values()) - (m["points"] or 0)
                if wk < pws:
                    blunders.append({"s": s, "wk": wk, "uid": rmap[m["roster_id"]],
                                     "bench": round(bench, 1), "pts": m["points"]})
        by_m = defaultdict(list)
        for m in items:
            if m.get("matchup_id") is not None and (m.get("points") or 0) > 0:
                by_m[m["matchup_id"]].append(m)
        if wk >= pws:
            continue  # records/luck/H2H are regular season only
        week_scores = [(m["roster_id"], m["points"]) for pair in by_m.values() for m in pair]
        for rid, pts in week_scores:
            uid = rmap[rid]
            career[uid]["pf"] += pts
            high_weeks.append({"s": s, "wk": wk, "uid": uid, "pts": pts})
            low_weeks.append({"s": s, "wk": wk, "uid": uid, "pts": pts})
            # all-play
            beat = sum(1 for _, p2 in week_scores if p2 < pts)
            career[uid]["ap_w"] += beat
            career[uid]["ap_g"] += len(week_scores) - 1
        if week_scores:
            top_uid = rmap[max(week_scores, key=lambda x: x[1])[0]]
            weekly_high_uid[wk] = top_uid
            career[top_uid]["high_weeks"] += 1
        for pair in by_m.values():
            if len(pair) != 2:
                continue
            a, b = pair
            w, l = (a, b) if a["points"] > b["points"] else (b, a)
            wu, lu = rmap[w["roster_id"]], rmap[l["roster_id"]]
            career[wu]["w"] += 1; career[lu]["l"] += 1
            career[wu]["pa"] += l["points"]; career[lu]["pa"] += w["points"]
            h2h[(wu, lu)][0] += 1; h2h[(lu, wu)][1] += 1
            game_log[wu].append(("W", s, wk)); game_log[lu].append(("L", s, wk))
            margin = round(w["points"] - l["points"], 2)
            rec = {"s": s, "wk": wk, "w_uid": wu, "l_uid": lu,
                   "w_pts": w["points"], "l_pts": l["points"], "margin": margin}
            blowouts.append(rec); closest.append(rec)
            big_loss.append({"s": s, "wk": wk, "uid": lu, "pts": l["points"], "vs": w["points"]})
            cheap_win.append({"s": s, "wk": wk, "uid": wu, "pts": w["points"], "vs": l["points"]})

    # brackets
    wb, lb = load(f"winners_bracket_{s}.json"), load(f"losers_bracket_{s}.json")
    final = next(m for m in wb if m.get("p") == 1)
    third = next((m for m in wb if m.get("p") == 3), None)
    toilet = next((m for m in lb if m.get("p") == 3), None)
    champ, runner = rmap[final["w"]], rmap[final["l"]]
    third_uid = rmap[third["w"]] if third else None
    toilet_uid = rmap[toilet["l"]] if toilet else None
    career[champ]["titles"] += 1; career[runner]["runnerups"] += 1
    if third_uid: career[third_uid]["thirds"] += 1
    if toilet_uid: career[toilet_uid]["toilets"] += 1
    for m in wb:
        for k in ("t1", "t2"):
            if m.get(k) in rmap:
                career[rmap[m[k]]]["po_apps"] = career[rmap[m[k]]].get("po_apps", 0)
    po_teams = {rid for m in wb for rid in (m.get("t1"), m.get("t2")) if rid in rmap}
    for rid in po_teams:
        career[rmap[rid]]["po_apps"] += 1

    standings = []
    for r in sorted(ctx["rosters"], key=lambda x: (-x["settings"]["wins"], -x["settings"].get("fpts", 0))):
        st = r["settings"]
        pf = st.get("fpts", 0) + st.get("fpts_decimal", 0) / 100
        pa = st.get("fpts_against", 0) + st.get("fpts_against_decimal", 0) / 100
        standings.append({"uid": rmap[r["roster_id"]], "name": oname(rmap[r["roster_id"]]),
                          "w": st["wins"], "l": st["losses"], "pf": round(pf, 1), "pa": round(pa, 1)})
    seasons_out.append({"season": s, "champ": oname(champ), "runner": oname(runner),
                        "third": oname(third_uid) if third_uid else None,
                        "toilet": oname(toilet_uid) if toilet_uid else None,
                        "standings": standings,
                        "final_score": f"{final.get('t1_from') and '' or ''}"})

# ---------- streaks ----------
def best_streak(log, kind):
    best = cur = 0
    for res, _, _ in log:
        cur = cur + 1 if res == kind else 0
        best = max(best, cur)
    return best

# ---------- career table ----------
career_out = []
for uid, c in career.items():
    g = c["w"] + c["l"]
    if g == 0 or oname(uid) == "Former manager" or str(uid).startswith("unknown_"):
        continue
    mine = [e for e in high_weeks if e["uid"] == uid]
    bw = max(mine, key=lambda e: e["pts"])
    ww = min(mine, key=lambda e: e["pts"])
    mybl = [e for e in blunders if e["uid"] == uid]
    bl = max(mybl, key=lambda e: e["bench"]) if mybl else None
    avg_bench = round(sum(e["bench"] for e in mybl) / len(mybl), 1) if mybl else 0
    ap_pct = c["ap_w"] / c["ap_g"] if c["ap_g"] else 0
    w_pct = c["w"] / g
    career_out.append({
        "name": oname(uid), "seasons": len(set(owners[uid]["seasons"])),
        "w": int(c["w"]), "l": int(c["l"]), "pct": round(w_pct, 3),
        "pf": round(c["pf"], 1), "pa": round(c["pa"], 1),
        "titles": int(c["titles"]), "runnerups": int(c["runnerups"]),
        "thirds": int(c.get("thirds", 0)), "toilets": int(c["toilets"]),
        "po_apps": int(c["po_apps"]), "high_weeks": int(c["high_weeks"]),
        "luck": round((w_pct - ap_pct) * g, 1),   # wins above all-play expectation
        "ap_pct": round(ap_pct, 3),
        "streak_w": best_streak(game_log[uid], "W"), "streak_l": best_streak(game_log[uid], "L"),
        "aliases": sorted(owners[uid]["aliases"]),
        "active": "2025" in owners[uid]["seasons"],
        "best_week": {"pts": bw["pts"], "s": bw["s"], "wk": bw["wk"]},
        "worst_week": {"pts": ww["pts"], "s": ww["s"], "wk": ww["wk"]},
        "blunder": {"bench": bl["bench"], "s": bl["s"], "wk": bl["wk"]} if bl else None,
        "avg_bench": avg_bench,
        "names": team_names.get(uid, []),
    })
career_out.sort(key=lambda x: (-x["titles"], -x["pct"]))

# ---------- H2H matrix (active owners) ----------
active = [c["name"] for c in career_out if c["active"]]
uid_by_name = {oname(uid): uid for uid in owners}
h2h_out = {a: {b: h2h.get((uid_by_name[a], uid_by_name[b]), [0, 0])[0:1][0:1] and
               {"w": h2h[(uid_by_name[a], uid_by_name[b])][0],
                "l": h2h[(uid_by_name[a], uid_by_name[b])][1]}
               or {"w": 0, "l": 0}
           for b in active if b != a} for a in active}

# ---------- record book ----------
def label(e):
    e = dict(e)
    e["name"] = oname(e.pop("uid"))
    return e

record_book = {
    "high_weeks": [label(e) for e in sorted(high_weeks, key=lambda x: -x["pts"])[:10]],
    "low_weeks": [label(e) for e in sorted(low_weeks, key=lambda x: x["pts"])[:10]],
    "blowouts": [{**e, "w": oname(e["w_uid"]), "l": oname(e["l_uid"])} for e in sorted(blowouts, key=lambda x: -x["margin"])[:10]],
    "closest": [{**e, "w": oname(e["w_uid"]), "l": oname(e["l_uid"])} for e in sorted(closest, key=lambda x: x["margin"])[:10]],
    "big_loss": [label(e) for e in sorted(big_loss, key=lambda x: -x["pts"])[:5]],
    "cheap_win": [label(e) for e in sorted(cheap_win, key=lambda x: x["pts"])[:5]],
    "blunders": [label(e) for e in sorted(blunders, key=lambda x: -x["bench"])[:10]],
}
for lst in ("blowouts", "closest"):
    for e in record_book[lst]:
        e.pop("w_uid"); e.pop("l_uid")

# ---------- drafts: boards + value ----------
drafts_meta = {s: load(f"drafts_{s}.json")[0] for s in SEASONS}
round_pts = defaultdict(list)
draft_rows = defaultdict(list)
for s in SEASONS:
    picks = load(f"draftpicks_{s}_{drafts_meta[s]['draft_id']}.json")
    for p in picks:
        pts = round(player_season_pts.get((s, str(p["player_id"])), 0), 1)
        row = {"s": s, "pick": p["pick_no"], "round": p["round"],
               "player": pname(p["player_id"]), "pos": ppos(p["player_id"]),
               "by": oname(season_ctx[s]["rmap"].get(p.get("roster_id"), "?")),
               "keeper": bool(p.get("is_keeper")), "pts": pts}
        draft_rows[s].append(row)
        round_pts[p["round"]].append(pts)

med = {r: sorted(v)[len(v) // 2] for r, v in round_pts.items()}
all_rows = [r for s in SEASONS for r in draft_rows[s]]
for r in all_rows:
    r["voe"] = round(r["pts"] - med[r["round"]], 1)
steals = sorted([r for r in all_rows if r["round"] >= 6], key=lambda x: -x["voe"])[:12]
busts = sorted([r for r in all_rows if r["round"] <= 2 and not r["keeper"]], key=lambda x: x["voe"])[:12]

# ---------- trade valuation model ----------
# Player value = position-adjusted points over replacement (rest of season,
# realized on the acquiring roster) + a 30% keeper premium on value-over-round
# for cheap-drafted producers. Pick value = historical median VOR of that
# round's picks (6 drafts), discounted 15% per year until it conveys.
REPL_RANK = {"QB": 12, "RB": 28, "WR": 28, "TE": 12, "DEF": 12}
TOT_WEEKS = {s: (16 if s == "2020" else 17) for s in SEASONS}

draft_round_by = {}   # (season, pid) -> round
for s in SEASONS:
    for p in load(f"draftpicks_{s}_{drafts_meta[s]['draft_id']}.json"):
        draft_round_by[(s, str(p["player_id"]))] = p["round"]

repl = {}             # (season, pos) -> replacement season total
for s in SEASONS:
    by_pos = defaultdict(list)
    for (s2, pid), pts in player_season_pts.items():
        if s2 == s:
            by_pos[ppos(pid)].append(pts)
    for pos, lst in by_pos.items():
        lst.sort(reverse=True)
        rank = REPL_RANK.get(pos, 24)
        repl[(s, pos)] = lst[rank - 1] if len(lst) >= rank else (lst[-1] if lst else 0)

round_vor_samples = defaultdict(list)
for (s, pid), rnd in draft_round_by.items():
    pts = player_season_pts.get((s, pid), 0)
    vor = max(0.0, pts - repl.get((s, ppos(pid)), 0))
    round_vor_samples[rnd].append(vor)
# mean (picks are lottery tickets — upside counts), smoothed to be non-increasing
round_vor = {r: sum(v) / len(v) for r, v in round_vor_samples.items()}
for r in range(15, 0, -1):
    round_vor[r] = max(round_vor[r], round_vor.get(r + 1, 0))

# keeper-market layer (S): when a preseason (week-1) pickup gets KEPT that
# season, the buyer banks a draft-day discount = keep slot minus that season's
# national ADP (FFC), converted from draft slots to value points at the
# league's own exchange rate (the pick value curve R1->R16 over its 150 slots)
import re as _re


def _norm_name(name):
    n = _re.sub(r"[^a-z ]", "", (name or "").lower())
    n = _re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return _re.sub(r"\s+", " ", n).strip()


try:
    _adp_hist = load("ffc_adp_hist.json")
except FileNotFoundError:
    _adp_hist = {}
ADP_BY_SEASON = {yr: {_norm_name(p.get("name")): p.get("adp")
                      for p in (d.get("players") or [])}
                 for yr, d in _adp_hist.items()}
KEPT_AT = {}
for s in SEASONS:
    for p in load(f"draftpicks_{s}_{drafts_meta[s]['draft_id']}.json"):
        if p.get("is_keeper"):
            KEPT_AT[(s, str(p["player_id"]), p.get("roster_id"))] = p["round"]
PTS_PER_SLOT = max(0.1, (round_vor.get(1, 0) - round_vor.get(16, 0)) / 150)

# ---------- trades archive with model verdicts (+ activity counts) ----------
trades_out = []
activity = defaultdict(lambda: {"trades_n": 0, "adds_n": 0})
for s in SEASONS:
    ctx = season_ctx[s]
    tx = load(f"transactions_{s}.json")
    tot_w = TOT_WEEKS[s]
    for wk_s, items in tx.items():
        for t in items:
            if t["status"] != "complete":
                continue
            if t["type"] in ("waiver", "free_agent"):
                for pid, rid in (t.get("adds") or {}).items():
                    if rid in ctx["rmap"]:
                        activity[oname(ctx["rmap"][rid])]["adds_n"] += 1
                continue
            if t["type"] != "trade":
                continue
            for rid in t["roster_ids"]:
                if rid in ctx["rmap"]:
                    activity[oname(ctx["rmap"][rid])]["trades_n"] += 1
            wk = int(wk_s)
            adds = t.get("adds") or {}
            remain_frac = max(0, tot_w - wk) / tot_w
            sides = []
            for rid in t["roster_ids"]:
                uid = ctx["rmap"][rid]
                players, picks = [], []
                P = A = K = S = 0.0
                for pid, to_rid in adds.items():
                    if to_rid != rid:
                        continue
                    ros = sum(v.get(pid, 0) or 0
                              for (s2, w2, r2), v in roster_week_pts.items()
                              if s2 == s and r2 == rid and w2 > wk)
                    p_val = max(0.0, ros - repl.get((s, ppos(pid)), 0) * remain_frac)
                    a_val = 0.0
                    rnd = draft_round_by.get((s, str(pid)))
                    season_pts = player_season_pts.get((s, str(pid)), 0)
                    if rnd is not None:
                        a_val = 0.3 * max(0.0, season_pts - med[rnd])
                    pre = season_pts - ros
                    # injury heuristic: produced before the trade then vanished after,
                    # or an early-round pick with almost nothing before a mid-season trade
                    inj = (pre >= 60 and ros <= 15) or \
                          (rnd is not None and rnd <= 6 and wk >= 5 and pre <= 30)
                    if wk == 1:
                        kr = KEPT_AT.get((s, str(pid), rid))
                        adp0 = (ADP_BY_SEASON.get(s) or {}).get(_norm_name(pname(pid)))
                        if kr is not None and adp0:
                            S += ((kr - 0.5) * 10 - adp0) * PTS_PER_SLOT
                    P += p_val
                    A += a_val
                    players.append({"p": pname(pid), "pts": round(ros, 1),
                                    "val": round(p_val + a_val, 1), "inj": bool(inj)})
                for dp in t.get("draft_picks") or []:
                    if dp["owner_id"] != rid:
                        continue
                    years_out = max(0, int(dp["season"]) - int(s))
                    v = round_vor.get(dp["round"], 0) * (0.85 ** years_out)
                    K += v
                    picks.append({"lab": f"{dp['season']} R{dp['round']}", "val": round(v, 1)})
                sides.append({"name": oname(uid), "players": players, "picks": picks,
                              "P": round(P, 1), "A": round(A, 1), "K": round(K, 1),
                              "S": round(S, 1),
                              "total": round(P + A + K + S, 1)})
            if len(sides) == 2 and any(sd["players"] or sd["picks"] for sd in sides):
                diff = sides[0]["total"] - sides[1]["total"]
                loser = None
                if abs(diff) >= 50:
                    loser = sides[0]["name"] if diff < 0 else sides[1]["name"]
                inj_names = [p["p"] for sd in sides for p in sd["players"] if p.get("inj")]
                trades_out.append({"s": s, "wk": wk,
                                   "type": "picks" if any(sd["picks"] for sd in sides) else "players",
                                   "sides": sides, "diff": round(abs(diff), 1), "loser": loser,
                                   "inj": inj_names})
trades_out.sort(key=lambda x: (x["s"], x["wk"]))

# fleece tallies + draft resume onto career rows
fleece = defaultdict(lambda: {"fleeced": 0, "fleeces": 0})
for t in trades_out:
    if t["loser"]:
        fleece[t["loser"]]["fleeced"] += 1
        other = next(sd["name"] for sd in t["sides"] if sd["name"] != t["loser"])
        fleece[other]["fleeces"] += 1
for c in career_out:
    c["fleeced"] = fleece[c["name"]]["fleeced"]
    c["fleeces"] = fleece[c["name"]]["fleeces"]
    c["trades_n"] = activity[c["name"]]["trades_n"]
    c["adds_n"] = activity[c["name"]]["adds_n"]
    rows_by = [r for r in all_rows if r["by"] == c["name"]]
    late = [r for r in rows_by if r["round"] >= 6]
    early = [r for r in rows_by if r["round"] <= 4 and not r["keeper"]]
    c["steal"] = max(late, key=lambda r: r["voe"]) if late else None
    c["bust"] = min(early, key=lambda r: r["voe"]) if early else None

site = {
    "generated": "2026-08-14",
    "seasons": seasons_out, "career": career_out, "h2h": h2h_out,
    "records": record_book,
    "drafts": {"boards": draft_rows, "steals": steals, "busts": busts, "round_median": med},
    "trades": trades_out,
    "pick_values": {r: round(v, 1) for r, v in sorted(round_vor.items())},
}
with open(os.path.join(DATA, "site_data.json"), "w", encoding="utf-8") as f:
    json.dump(site, f, ensure_ascii=False)

print("seasons:", [(x["season"], x["champ"], "toilet:", x["toilet"]) for x in seasons_out])
print("\ncareer:")
for c in career_out:
    print(f"  {c['name']:<16} {c['w']}-{c['l']} ({c['pct']:.3f}) PF {c['pf']:>7} titles {c['titles']} toilets {c['toilets']} luck {c['luck']:+.1f} hi-wks {c['high_weeks']}")
print("\ntop steals:", [(r["player"], r["s"], f"R{r['round']}", r["voe"]) for r in steals[:5]])
print("top busts:", [(r["player"], r["s"], f"R{r['round']}", r["voe"]) for r in busts[:5]])
print("trades:", len(trades_out), "| size:", os.path.getsize(os.path.join(DATA, "site_data.json")) // 1024, "KB")
print("pick values:", {r: round(v) for r, v in sorted(round_vor.items())})
diffs = sorted(t["diff"] for t in trades_out)
print("diff percentiles: p25", diffs[len(diffs)//4], "p50", diffs[len(diffs)//2],
      "p75", diffs[3*len(diffs)//4], "max", diffs[-1])
heists = sorted(trades_out, key=lambda t: -t["diff"])[:5]
for h in heists:
    print(f"  HEIST {h['s']} wk{h['wk']} ({h['type']}): loser {h['loser']} by {h['diff']} | "
          + " vs ".join(f"{sd['name']} {sd['total']}" for sd in h["sides"]))
