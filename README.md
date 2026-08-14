# LOB League site

League website for the **LOB League — League of Burger** (10-team, 0.5 PPR Sleeper
keeper league, est. 2024), carrying the 2026 **Cap Keeper** rules proposal.
Direct port of the [GGG league site](https://github.com/StrubeTube/ggg-league)
with LOB data and the burger color scheme.

Live at **https://strubetube.github.io/lob-league/** (GitHub Pages from `main:/docs`).

## Pages

- **pitch.html** — The Proposal (front door: every first visit lands here)
- **index.html** — per-team franchise HQ: keeper corner, cap board, cap anatomy
- **analyzer.html** — Trade Tester (cap-band verdicts)
- **history / records / drafts / trades** — 2024–2025 league history, roasted
- **lab.html** — Commish tools (code-locked)

## Pipeline

```
python fetch_league.py    # league chain, drafts, rosters (2024-2026)
python fetch_history.py   # matchups, transactions, brackets, traded picks
python refresh_2026.py    # current-season refresh (rosters, official keepers)
python compute_site.py    # stats layer -> data/site_data.json
python build_site.py      # assemble site -> docs/
```

`.github/workflows/refresh.yml` runs the refresh + rebuild daily and commits as
`lob-refresh-bot` — **pull before local work**.

Proposed rules (same base as GGG): salary = draft round (flattened table,
$30 R1 → $2 R16), $230 cap / $160 floor checked on trades only in the worsening
direction, keepers count against team salary and slot on the board at their keep
round (drafted round; one earlier per prior keep year), $0 waivers. Open vote:
3 keepers no budget vs up to 5 under a $50 keeper budget.
