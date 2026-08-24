"""Assemble the league site: site_templates/*.html + site_data.json -> docs/."""
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
TPL = os.path.join(HERE, "site_templates")
OUT = os.path.join(HERE, "docs")
os.makedirs(OUT, exist_ok=True)


def load(n):
    with open(os.path.join(DATA, n), encoding="utf-8") as f:
        return json.load(f)


site = load("site_data.json")
fonts = json.load(open(os.path.join(HERE, "poppins_b64.json"), encoding="utf-8"))
users25 = load("users_2025.json")
commish_uid = next(u["user_id"] for u in users25 if u["display_name"] == "Strubes")

# ---------------- shared CSS ----------------
CSS = """
@font-face{font-family:'Poppins';font-style:normal;font-weight:400;font-display:swap;src:url(data:font/woff2;base64,F400) format('woff2');}
@font-face{font-family:'Poppins';font-style:normal;font-weight:600;font-display:swap;src:url(data:font/woff2;base64,F600) format('woff2');}
@font-face{font-family:'Poppins';font-style:normal;font-weight:800;font-display:swap;src:url(data:font/woff2;base64,F800) format('woff2');}
/* LOB burger palette: dark maroon base, orange accent (the --mint variable name
   is kept from the shared codebase — its VALUE is the LOB brand orange) */
:root{--bg:#251010;--surface:#2C1414;--card:#331818;--card2:#2C1313;--line:#4A2424;--line2:#5C2D2D;
--ink:#F8EFEA;--ink2:#D6B7A9;--ink3:#A58274;--mint:#FF9A3C;--mint-ink:#2A1404;--mark:#E07B1F;
--coral:#FF5147;--coral-soft:rgba(255,81,71,.16);--gold:#E8B54A;--navy:#131C4D;--navy-line:#FF9A3C;}
@media (prefers-color-scheme: light){:root{--bg:#FBF2EA;--surface:#FDF8F2;--card:#FFFFFF;--card2:#F8EFE6;
--line:#EAD6C6;--line2:#DCC2AD;--ink:#361410;--ink2:#6E4A3C;--ink3:#9C7A6B;--mint:#C25A0E;--mint-ink:#FFFFFF;
--mark:#C25A0E;--coral:#CC3D2F;--coral-soft:rgba(204,61,47,.10);--gold:#8C6A10;--navy:#1A2560;--navy-line:#C25A0E;}}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:'Poppins',system-ui,sans-serif;line-height:1.55;margin:0}
.wrap{max-width:1360px;margin:0 auto;padding:28px 20px 80px}
h1,h2,h3{text-wrap:balance;margin:0}p{margin:0}a{color:var(--mint)}
.eyebrow{font-size:12px;font-weight:600;letter-spacing:.13em;text-transform:uppercase;color:var(--mint)}
.hero{margin:18px 0 6px}
h1{font-size:clamp(30px,5.5vw,46px);font-weight:800;line-height:1.08;margin:8px 0 12px}
.lede{color:var(--ink2);font-size:15.5px;max-width:64ch}
section{margin-top:52px}
.sec-head{display:flex;flex-direction:column;gap:6px;margin-bottom:16px}
h2{font-size:22px;font-weight:800}
.sec-note{color:var(--ink2);font-size:14px;max-width:65ch}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.scroll{overflow-x:auto}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 16px 13px}
.tile .num{font-size:30px;font-weight:800;line-height:1.1;font-variant-numeric:tabular-nums}
.tile .num.bad{color:var(--coral)}.tile .num.good{color:var(--mint)}
.tile .lbl{font-size:12.5px;color:var(--ink2);margin-top:6px;line-height:1.45}
.chip{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:2px 10px;font-size:11.5px;font-weight:600;white-space:nowrap}
.chip.gold{color:var(--gold);border:1px solid var(--gold)}
.chip.fire{color:var(--coral);border:1px solid var(--coral)}
.chip.flag{background:var(--coral);color:#fff;letter-spacing:.04em}
.chip.even{color:var(--ink3);border:1px solid var(--line2)}
.chip.wk{background:var(--navy);color:#EDF7F2;border:1px solid var(--navy-line);letter-spacing:.06em}
.chip.mini{color:var(--mint);border:1px solid var(--mint);padding:0 7px}
.tbl{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}
.tbl th{font-size:10.5px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink3);font-weight:600;text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--line2)}
.tbl td{padding:6px 10px 6px 0;border-bottom:1px solid var(--line)}
.tbl tr:last-child td{border-bottom:none}
.mut{color:var(--ink3)}.small{font-size:11px}
.good{color:var(--mint)}.bad{color:var(--coral)}
.departed td{opacity:.55}
.duo-cards{display:grid;gap:12px}
@media(min-width:640px){.duo-cards{grid-template-columns:1fr 1fr}}
.bigcard{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;text-decoration:none;color:var(--ink);transition:border-color .12s}
.bigcard:hover{border-color:var(--mint)}
.bigcard h3{font-size:18px;font-weight:800;margin:6px 0 8px}
.bigcard p{color:var(--ink2);font-size:13.5px}
.hof,.shame{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.banner{background:linear-gradient(180deg,var(--card),var(--card2));border:1px solid var(--gold);border-radius:12px 12px 4px 4px;padding:16px 14px;text-align:center}
.banner .byear{font-size:12px;font-weight:600;letter-spacing:.12em;color:var(--gold)}
.banner .bname{font-weight:800;font-size:15px;margin-top:6px}
.banner .bsub{font-size:11px;color:var(--ink3);margin-top:4px}
.shamecard{background:var(--card2);border:1px dashed var(--coral);border-radius:12px;padding:14px;text-align:center}
.shamecard .byear{font-size:12px;font-weight:600;letter-spacing:.12em;color:var(--coral)}
.shamecard .bname{font-weight:800;font-size:14px;margin-top:5px}
.matrix th.rot{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;padding:4px 2px;font-size:10px}
.matrix td{text-align:center;padding:5px 6px}
.matrix td.winrec{color:var(--mint);font-weight:600}
.matrix td.loserec{color:var(--coral)}
.matrix td.self{color:var(--ink3)}
.matrix th{padding-right:8px}
.seasonbox{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin-bottom:10px}
.seasonbox summary{cursor:pointer;font-size:14px}
.seasonbox summary b{font-weight:800}
.seasonbox .tbl{margin-top:10px}
.reclist{margin:0;padding-left:22px;font-size:13.5px;display:grid;gap:7px;font-variant-numeric:tabular-nums}
.reclist b{font-weight:800}
.recgrid{display:grid;gap:0}
@media(min-width:760px){.recgrid{grid-template-columns:1fr 1fr;gap:0 16px}}
.luckrow{display:grid;grid-template-columns:130px 1fr 52px;align-items:center;gap:10px;min-height:30px}
.lname{font-size:12.5px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lucktrack{position:relative;height:14px;background:var(--card2);border:1px solid var(--line);border-radius:7px}
.luckbar{position:absolute;top:2px;bottom:2px}
.luckbar.pos{background:var(--mark);border-radius:0 5px 5px 0}
.luckbar.neg{background:var(--coral);border-radius:5px 0 0 5px}
.luckmid{position:absolute;left:50%;top:-2px;bottom:-2px;width:1px;background:var(--line2)}
.lval{font-size:12px;font-weight:600;text-align:right;font-variant-numeric:tabular-nums}
.filterrow{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}
.tpill{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:6px 14px;font-size:13px;font-weight:600;color:var(--ink2);cursor:pointer;font-family:inherit}
.tpill.active{background:var(--mint);color:var(--mint-ink);border-color:var(--mint)}
.trades{display:grid;gap:12px}
.trade{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:13px 16px 15px}
.trade-head{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:10px}
.trade-sides{display:grid;gap:10px}
@media(min-width:640px){.trade-sides{grid-template-columns:1fr 1fr}}
.side{background:var(--card2);border:1px solid var(--line);border-radius:10px;padding:11px 13px}
.side.losing{border-color:var(--coral)}
.side-head{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;margin-bottom:7px}
.side-team{font-weight:600;font-size:13.5px}
.side-cap{font-size:12px;color:var(--ink2);font-variant-numeric:tabular-nums}
.gets{display:flex;flex-wrap:wrap;gap:6px}
.pchip{display:inline-flex;align-items:baseline;gap:6px;background:var(--surface);border:1px solid var(--line2);border-radius:8px;padding:3px 9px;font-size:12px;font-weight:600}
.pchip .s{font-weight:400;color:var(--ink2);font-size:11px;font-variant-numeric:tabular-nums}
.pchip.pick{border-style:dashed;font-weight:400;color:var(--ink2)}
.pchip.none{border:none;background:transparent;color:var(--ink3);font-weight:400}
nav.ggg{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
nav.ggg .in{max-width:1360px;margin:0 auto;display:flex;align-items:center;gap:4px;padding:10px 20px;flex-wrap:wrap}
nav.ggg .logo{width:34px;height:34px;background:var(--mint);color:var(--mint-ink);border-radius:8px;display:grid;place-items:center;font-weight:800;font-size:13px;margin-right:10px}
nav.ggg a{color:var(--ink2);text-decoration:none;font-size:13px;font-weight:600;padding:6px 11px;border-radius:8px}
nav.ggg a:hover{color:var(--ink)}
nav.ggg a.on{background:var(--card);color:var(--mint)}
footer.ggg{border-top:1px solid var(--line);margin-top:60px}
footer.ggg .in{max-width:1360px;margin:0 auto;padding:18px 20px;font-size:12px;color:var(--ink3)}
.teambar{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.chiprow{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.timeline{display:grid;grid-template-columns:repeat(auto-fit,minmax(64px,1fr));gap:8px}
.tcell{background:var(--card2);border:1px solid var(--line);border-radius:10px;text-align:center;padding:8px 4px}
.tcell.gold{border-color:var(--gold)}.tcell.fire{border-color:var(--coral)}
.tyear{font-size:10.5px;color:var(--ink3);font-weight:600;letter-spacing:.08em}
.tplace{font-weight:800;font-size:15px;margin-top:3px}
.cardh{font-size:12px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--ink2);margin-bottom:10px}
.bignum{font-size:32px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1.05}
.bignum small{font-size:15px;font-weight:600;color:var(--ink3)}
.bignum.over{color:var(--coral)}
.subnum{font-size:12.5px;color:var(--ink2);margin-top:4px}
.meter{height:12px;border-radius:6px;background:var(--card2);border:1px solid var(--line);margin-top:12px;position:relative;overflow:hidden}
.meter .fillbar{position:absolute;inset:0 auto 0 0;background:var(--mark);border-radius:6px 0 0 6px;transition:width .18s}
.meter .fillbar.over{background:var(--coral)}
.rostercard{margin-top:12px}
.roster{display:grid;gap:6px}
.prow{display:grid;grid-template-columns:auto auto 1fr auto auto auto;gap:10px;align-items:center;background:var(--card2);border:1px solid var(--line);border-radius:10px;padding:8px 13px;cursor:pointer}
.pshot{width:30px;height:30px;border-radius:50%;object-fit:cover;background:var(--surface);border:1px solid var(--line2);flex:none}
.prow.on{border-color:var(--mint)}
.prow.inel{cursor:default;opacity:.55}
.prow:focus-visible{outline:2px solid var(--mint);outline-offset:2px}
.tick{width:17px;height:17px;border-radius:5px;border:2px solid var(--line2);display:grid;place-items:center;font-size:11px;color:var(--mint-ink);flex:none}
.prow.on .tick{background:var(--mint);border-color:var(--mint)}
.pname{font-weight:600;font-size:13px;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pname .meta{font-weight:400;color:var(--ink3);font-size:11px;margin-left:6px}
.rnd{font-size:11px;color:var(--ink3);font-variant-numeric:tabular-nums}
.cost{font-weight:800;font-size:13.5px;text-align:right;min-width:34px;font-variant-numeric:tabular-nums}
.next{font-size:11px;color:var(--ink3);text-align:right;min-width:48px;white-space:nowrap;font-variant-numeric:tabular-nums}
.grudges{display:grid;grid-template-columns:repeat(auto-fill,minmax(108px,1fr));gap:8px}
.gcell{background:var(--card2);border:1px solid var(--line);border-radius:10px;text-align:center;padding:9px 6px}
.gname{font-size:11px;font-weight:600;color:var(--ink2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.grec{font-weight:800;font-size:15px;margin-top:2px;font-variant-numeric:tabular-nums}
.grec.winrec{color:var(--mint)}.grec.loserec{color:var(--coral)}
.wrap.wide{max-width:1400px}
.dashhero{display:flex;flex-direction:column;gap:14px}
.idband{display:flex;gap:16px;align-items:stretch;margin-top:26px;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px 20px;flex-wrap:wrap}
.archbadge{flex:none;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;background:var(--card2);border:1px solid var(--line2);border-radius:14px;padding:14px 22px}
.archemoji{font-size:34px;line-height:1}
.archname{font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--mint);white-space:nowrap}
.idmid{flex:1;min-width:260px;display:flex;flex-direction:column;gap:12px;justify-content:center}
.idmid .chiprow{margin-bottom:0}
.dash{display:grid;grid-template-columns:repeat(12,1fr);gap:14px;margin-top:14px}
.dcard{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 18px;display:flex;flex-direction:column;gap:10px;min-width:0}
.dcard.c3{grid-column:span 3}.dcard.c4{grid-column:span 4}.dcard.c5{grid-column:span 5}
.dcard.c6{grid-column:span 6}.dcard.c7{grid-column:span 7}.dcard.c12{grid-column:span 12}
@media(max-width:1100px){.dcard.c3,.dcard.c4{grid-column:span 6}.dcard.c5,.dcard.c6,.dcard.c7{grid-column:span 12}}
@media(max-width:680px){.dcard{grid-column:span 12 !important}.wrap{padding-left:12px;padding-right:12px}}
.dcard-head{display:flex;align-items:center;justify-content:space-between;gap:8px}
.dcard-head .cardh{margin-bottom:0}
.chip.soon{background:transparent;color:var(--gold);border:1px dashed var(--gold);letter-spacing:.08em;font-size:10px}
.cardnote{font-size:11.5px;color:var(--ink3);line-height:1.5;margin-top:auto}
.kmeters{display:grid;gap:12px}
.mlabel{font-size:12px;font-weight:600;color:var(--ink2);margin-bottom:5px}
.kmeters .meter{margin-top:0}
.tallroster{max-height:none}
.skel{height:13px;border-radius:7px;background:var(--card2);border:1px solid var(--line)}
@media(prefers-reduced-motion:no-preference){
.skel{background:linear-gradient(90deg,var(--card2) 25%,var(--line) 50%,var(--card2) 75%);background-size:200% 100%;animation:shimmer 1.8s infinite}
@keyframes shimmer{to{background-position:-200% 0}}}
.gauge{width:120px;height:120px;border-radius:50%;margin:6px auto;display:grid;place-items:center;background:conic-gradient(var(--line2) 0deg,var(--card2) 0deg);border:1px solid var(--line);position:relative}
.gauge::before{content:'';position:absolute;inset:12px;border-radius:50%;background:var(--card)}
.gaugev{position:relative;font-weight:800;font-size:22px;color:var(--ink3);font-variant-numeric:tabular-nums}
.vsrow{display:flex;align-items:center;gap:14px;justify-content:space-between}
.vsteam{font-weight:800;font-size:16px}
.vsmark{font-size:11px;font-weight:800;color:var(--ink3);letter-spacing:.14em}
.vitals,.vrow{display:flex;flex-direction:column;gap:0}
.vrow{flex-direction:row;justify-content:space-between;gap:10px;padding:6px 0;border-bottom:1px solid var(--line);font-size:12.5px;font-variant-numeric:tabular-nums}
.vrow:last-of-type{border-bottom:none}
.vrow .tn{text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:70%}
.vrow.wire{font-size:12.5px;line-height:1.5}
.nemduo{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.nemcard{border-radius:12px;padding:12px 14px;background:var(--card2);border:1px solid var(--line)}
.nemcard.good2{border-color:var(--mark)}.nemcard.bad2{border-color:var(--coral)}
.nemname{font-weight:800;font-size:15px;margin-top:2px}
.nemrec{font-weight:800;font-size:19px;font-variant-numeric:tabular-nums}
.pickchips{display:flex;flex-wrap:wrap;gap:6px}
.pk{background:var(--card2);border:1px solid var(--line2);border-radius:8px;padding:3px 10px;font-size:12px;font-weight:600;font-variant-numeric:tabular-nums}
.pk .frm{font-weight:400;color:var(--ink3);font-size:11px}
.cardnote2{font-size:11.5px;color:var(--ink3);line-height:1.5}
.cbrow{display:grid;grid-template-columns:minmax(120px,150px) 1fr 92px;align-items:center;gap:10px;min-height:38px}
.cbname{display:flex;align-items:center;gap:6px;min-width:0}
.cbteam{font-size:12.5px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cbname.good .cbteam{color:var(--mint)}
.cbtrack{position:relative;height:18px;background:var(--card2);border:1px solid var(--line);border-radius:9px;overflow:hidden}
.cbseg{position:absolute;top:2px;bottom:2px;transition:width .18s,left .18s}
.cbseg.k{background:var(--mark);border-radius:7px 0 0 7px}
.cbseg.d{background:var(--mark);opacity:.4}
.cbseg.f{background:var(--mark);opacity:.15}
.cbcap{position:absolute;top:-2px;bottom:-2px;width:0;border-left:2px dashed var(--coral)}
.cbval{display:flex;flex-direction:column;align-items:flex-end;line-height:1.25;font-variant-numeric:tabular-nums}
.cbval b{font-weight:800;font-size:13.5px}
.cbval b.bad{color:var(--coral)}
.chk{display:flex;gap:12px;align-items:flex-start;padding:8px 0;border-bottom:1px solid var(--line)}
.chk:last-of-type{border-bottom:none}
.chkbox{flex:none;width:20px;height:20px;border-radius:6px;border:2px solid var(--line2);display:grid;place-items:center;font-size:12px;color:var(--mint-ink);margin-top:1px}
.chk.done .chkbox{background:var(--mint);border-color:var(--mint)}
.chk.done .chktxt{text-decoration:line-through;color:var(--ink2)}
.chktxt{font-size:13.5px;font-weight:600}
.idname{font-size:19px;font-weight:800;line-height:1.25;text-align:center;max-width:260px;text-wrap:balance}
.filterrow.tight{margin-bottom:4px;gap:6px}
.tpill.sm{padding:4px 11px;font-size:11.5px}
.mcrow{display:flex;gap:18px;align-items:center}
.mcl{flex:1;display:flex;flex-direction:column;gap:10px;min-width:0}
.mcrow .gauge{flex:none;margin:0}
details.histbox{grid-column:1 / -1;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px 18px;margin-top:6px}
details.histbox summary{cursor:pointer;font-size:13px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--ink2)}
details.histbox summary:hover{color:var(--mint)}
details.histbox .dash{margin-top:14px}
.ctl{padding:10px 0;border-bottom:1px solid var(--line)}
.ctl:last-of-type{border-bottom:none}
.ctlrow{display:grid;grid-template-columns:110px 1fr 84px;align-items:center;gap:10px}
.ctlname{font-size:12.5px;font-weight:600;color:var(--ink2)}
.ctlval{font-size:12.5px;font-weight:800;text-align:right;font-variant-numeric:tabular-nums}
input[type=range]{width:100%;accent-color:var(--mint);background:transparent}
input[type=range]:disabled{opacity:.35}
.salary-mini{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}
.tmini{display:flex;flex-direction:column;align-items:center;background:var(--card2);border:1px solid var(--line);border-radius:6px;padding:3px 6px;min-width:34px}
.tmini b{font-size:11.5px;font-weight:800;font-variant-numeric:tabular-nums}
.tmini i{font-style:normal;font-size:9px;color:var(--ink3);letter-spacing:.04em}
.ctlnote{font-size:11px;color:var(--ink3);line-height:1.5;margin-top:6px}
.labbanner{margin-top:14px;background:var(--card);border:1px dashed var(--gold);border-radius:10px;padding:9px 14px;font-size:12.5px;color:var(--ink2);line-height:1.5}
.labbanner a{color:var(--gold);font-weight:600}
.tbl td{white-space:nowrap}
.tbl td.wrapok{white-space:normal}
.tbl th.sortable{cursor:pointer;user-select:none;white-space:nowrap}
.tbl th.sortable:hover{color:var(--mint)}
.valbreak{margin-top:8px;font-size:11px;color:var(--ink3);font-variant-numeric:tabular-nums}
.tbl-details{margin-top:12px;font-size:12.5px}
.tbl-details summary{cursor:pointer}
.chip.ok{color:var(--mint);border:1px solid var(--mint);letter-spacing:.04em}
.chip.inj{color:var(--gold);border:1px dashed var(--gold);letter-spacing:.04em}
.cbfloor{position:absolute;top:0;bottom:0;width:0;border-left:2px dashed var(--gold);opacity:.8}
.cbrange{position:absolute;top:6px;height:4px;background:var(--gold);opacity:.6;border-radius:2px;pointer-events:none}
.cbtick{position:absolute;top:1px;bottom:1px;width:3px;background:var(--mint);border-radius:2px}
.cbtick.bad{background:var(--coral)}
.navgrp{display:flex;flex-direction:column;gap:0;margin-right:14px}
.navgrp .navcap{font-size:8.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--ink3);padding:2px 11px 0;white-space:nowrap;user-select:none;opacity:.85}
.navgrp .navlinks{display:flex;gap:2px}
.navgrp.newg .navcap{color:var(--mint)}
.navgrp.histg{border-left:1px solid var(--line);padding-left:10px}
.navgrp.histg a{color:var(--ink3)}
.navgrp.histg a:hover{color:var(--ink)}
nav.ggg a.pitchtab{margin-left:auto;background:var(--gold);color:#1B1403;border-radius:999px;padding:5px 13px;font-weight:800}
nav.ggg a.pitchtab:hover{color:#000}
nav.ggg a.pitchtab.on{outline:2px solid var(--gold);outline-offset:2px}
@media(max-width:680px){nav.ggg a.pitchtab{margin-left:0}}
nav.ggg a.labtab{margin-left:0;border:none;color:var(--ink3);font-size:12px;border-radius:8px;padding:6px 10px}
nav.ggg a.labtab:hover{color:var(--ink2)}
nav.ggg a.labtab.on{background:var(--card);color:var(--ink)}
.lockwrap{max-width:380px;margin:80px auto;text-align:center}
.lockwrap .lockemoji{font-size:44px}
.lockcode{display:flex;gap:10px;justify-content:center;margin-top:18px}
.lockcode input{width:200px;text-align:center;font-family:inherit;font-size:26px;font-weight:800;letter-spacing:.35em;
background:var(--card);border:1px solid var(--line2);border-radius:12px;color:var(--ink);padding:10px 6px}
.lockcode input:focus{outline:2px solid var(--mint);border-color:var(--mint)}
.lockbtn{background:var(--mint);color:var(--mint-ink);border:none;border-radius:12px;padding:10px 20px;
font-family:inherit;font-weight:800;font-size:15px;cursor:pointer}
.lockerr{color:var(--coral);font-size:13px;font-weight:600;margin-top:12px;min-height:18px}
.enterbtn{display:inline-block;background:linear-gradient(135deg,var(--gold),#EFC85F 55%,var(--gold));background-size:200% 200%;
color:#1B1403;border-radius:18px;padding:20px 46px;font-weight:800;font-size:21px;text-decoration:none;
animation:goldpulse 2.4s ease-out infinite,goldsheen 5s ease infinite;transition:transform .12s}
.enterbtn:hover{transform:translateY(-3px) scale(1.03)}
@keyframes goldpulse{0%{box-shadow:0 0 0 0 rgba(217,169,60,.55)}70%{box-shadow:0 0 0 20px rgba(217,169,60,0)}100%{box-shadow:0 0 0 0 rgba(217,169,60,0)}}
@keyframes goldsheen{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
@media(prefers-reduced-motion:reduce){.enterbtn{animation:none}}
.cbarrow{position:absolute;top:50%;transform:translate(-50%,-50%);font-size:11px;font-weight:800;
white-space:nowrap;z-index:3;pointer-events:none;text-shadow:0 1px 3px rgba(0,0,0,.6)}
.cbarrow.good2{color:#fff}
.cbarrow.bad2{color:#fff}
.probgrid{display:grid;gap:12px}
@media(min-width:760px){.probgrid{grid-template-columns:1fr 1fr 1fr}}
.probcard{background:var(--card);border:1px solid var(--coral);border-radius:14px;padding:16px 18px}
.probcard .pemoji{font-size:26px}
.probcard h3{font-size:15px;font-weight:800;margin:8px 0 6px}
.probcard p{font-size:13px;color:var(--ink2)}
.optcard{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px}
.optcard.a{border-color:var(--mint)}
.optcard.b{border-color:var(--gold)}
.optcard .opttag{font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
.optcard.a .opttag{color:var(--mint)}
.optcard.b .opttag{color:var(--gold)}
.optcard h3{font-size:18px;font-weight:800;margin:6px 0 8px}
.optcard p{font-size:13.5px;color:var(--ink2)}
.optcard ul{margin:10px 0 0;padding-left:20px;font-size:13px;color:var(--ink2);display:grid;gap:5px}
.bigsteps{counter-reset:s;list-style:none;margin:0;padding:0;display:grid;gap:10px}
.bigsteps li{counter-increment:s;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px 14px 56px;position:relative;font-size:14px}
.bigsteps li::before{content:counter(s);position:absolute;left:16px;top:13px;width:26px;height:26px;border-radius:50%;
background:var(--mint);color:var(--mint-ink);font-weight:800;display:grid;place-items:center;font-size:14px}
.tradebox{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
.tradep{background:var(--card2);border:1px solid var(--line);border-radius:999px;padding:4px 12px;font-size:12px;font-weight:600;color:var(--ink2);cursor:pointer;font-family:inherit;transition:border-color .1s}
.tradep b{color:var(--ink);font-weight:700}
.tradep .pp{color:var(--ink3)}
.tradep:hover{border-color:var(--mint)}
.tradep.out{border-color:var(--coral);background:var(--coral-soft)}
.tradep.out b{color:var(--coral)}
.dcard.c12{grid-column:span 12}
.anatwrap{position:relative;margin-top:30px;padding-top:2px}
.anatbar{position:relative;height:78px;background:var(--card2);border:1px solid var(--line);border-radius:12px;display:flex;overflow:hidden}
.anatseg{position:relative;height:100%;border-right:1.5px solid var(--bg);display:flex;align-items:center;justify-content:center;overflow:hidden;min-width:0}
.anatseg.k{background:var(--mark)}
.anatseg.d{background:var(--mark);opacity:.38}
.anatseg.fr{box-shadow:inset 0 0 0 2px var(--gold)}
.anatseg span{writing-mode:vertical-rl;transform:rotate(180deg);font-size:10.5px;font-weight:600;color:#fff;white-space:nowrap;max-height:72px;overflow:hidden}
.anatline{position:absolute;top:-8px;bottom:-8px;width:0;border-left:2px dashed var(--coral);z-index:2}
.anatline.floor{border-color:var(--gold)}
.anattag{position:absolute;top:-26px;transform:translateX(-50%);font-size:10.5px;font-weight:700;letter-spacing:.05em;color:var(--coral);white-space:nowrap;z-index:2}
.anattag.floor{color:var(--gold)}
.anattip{position:absolute;top:88px;transform:translateX(-50%);background:var(--card);border:1px solid var(--mint);
border-radius:8px;padding:5px 11px;font-size:12.5px;font-weight:600;white-space:nowrap;z-index:5;
box-shadow:0 6px 18px rgba(0,0,0,.35);pointer-events:none}
.anatseg:hover{filter:brightness(1.25)}
.anatlegend{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}
.anattotal{margin-top:12px;font-size:13.5px;font-weight:600}
/* expandable cap-board rows + per-team breakdown panel */
.cbrow.clickable{cursor:pointer}
.cbrow.clickable:hover .cbteam{color:var(--mint)}
.cbrow.clickable:focus-visible{outline:2px solid var(--mint);outline-offset:2px;border-radius:8px}
.caret{color:var(--ink3);font-size:10px;flex:none;width:11px}
.cbdetail{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px 13px;margin:4px 0 10px}
.cbdetail .mlabel{margin-top:14px}
.klist{display:flex;flex-direction:column;gap:7px;margin-top:2px}
.kchip{display:flex;align-items:center;gap:9px;font-size:13.5px;flex-wrap:wrap}
.kchip .meta{color:var(--ink3);font-size:12px}
.kchip .meta.bad{color:var(--coral)}
.gobtn{display:block;text-align:center;margin-top:12px;padding:12px 16px;border-radius:12px;background:var(--mint);color:var(--mint-ink);font-weight:700;font-size:14px;text-decoration:none}
.gobtn:hover{filter:brightness(1.07)}
/* the trade circle (Trade Archive) */
.flowwrap{position:relative}
.tradeweb{width:100%;height:auto;display:block}
.flowedge{opacity:.78;cursor:pointer}
.flowedge:hover{opacity:1}
.flowedge.faded{opacity:.08}
.flownode circle{fill:var(--mint);stroke:var(--bg);stroke-width:2;cursor:pointer}
.flownode .ncount{fill:var(--mint-ink);font-weight:800;font-size:13px;pointer-events:none}
.flownode text{fill:var(--ink2);font-size:13px;font-weight:600;cursor:pointer}
.flownode.off circle{fill:var(--line2);opacity:.6}
.flownode.off text{opacity:.45}
.mkline{font-size:11.5px;color:var(--ink2);border-top:1px dashed var(--line);margin-top:9px;padding-top:8px;line-height:1.9}
.mkline .chip{margin-left:6px}
.mkline .comps{display:block;color:var(--ink3);font-size:10.5px;line-height:1.5;margin-top:2px}
.cdrows{display:grid;gap:9px;margin-top:6px}
.cdrow{display:flex;align-items:center;justify-content:space-between;gap:10px;border-bottom:1px solid var(--line);padding-bottom:8px}
.cdrow:last-child{border-bottom:none;padding-bottom:0}
.cdlab{font-size:12.5px;font-weight:700}
.cdnum{font-size:26px;font-weight:800;line-height:1;font-variant-numeric:tabular-nums}
.cdnum small{font-size:13px;font-weight:600;color:var(--ink3);margin-left:1px}
.cdnum.good{color:var(--mint)}
.rtrade{background:var(--card2);border:1px solid var(--line);border-radius:10px;padding:9px 12px;margin-top:8px;font-size:12px}
.rtrade.rblocked{border-color:var(--coral)}
.rtrade .trade-head{margin-bottom:6px}
.rline{display:flex;justify-content:space-between;gap:12px;padding:2px 0;flex-wrap:wrap;font-variant-numeric:tabular-nums}
.ctl.modded{border:1px dashed var(--gold);border-radius:10px;padding:10px 12px;margin:8px 0;background:color-mix(in srgb,var(--gold) 14%,transparent)}
.ctl.modded::before{content:'🆕 NET NEW vs the old league rules';display:block;font-size:10px;font-weight:800;letter-spacing:.1em;color:var(--gold);margin-bottom:6px}
/* ---------- mobile (single breakpoint, all pages) ---------- */
@media(max-width:680px){
html{-webkit-text-size-adjust:100%}
.wrap{padding:18px 12px 56px}
section{margin-top:36px}
h1{font-size:clamp(24px,7.6vw,32px)}
.lede{font-size:14px}
h2{font-size:19px}
.card,.dcard{padding:13px 13px}
.card:has(> .tbl){overflow-x:auto}
/* nav collapses to one horizontally-scrollable row; captions hide */
nav.ggg .in{flex-wrap:nowrap;overflow-x:auto;gap:2px;padding:8px 12px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
nav.ggg .in::-webkit-scrollbar{display:none}
nav.ggg .logo{width:28px;height:28px;font-size:11px;margin-right:6px;flex:none}
.navgrp{margin-right:6px;flex:none}
.navgrp .navcap{display:none}
.navgrp.histg{padding-left:6px}
nav.ggg a{font-size:12.5px;padding:6px 9px;white-space:nowrap}
nav.ggg a.pitchtab,nav.ggg a.labtab{flex:none}
.idband{padding:13px;gap:10px}
.archbadge{width:100%;padding:10px 12px}
.idname{font-size:16px;max-width:none}
.teambar .tpill{padding:5px 11px;font-size:12px}
/* keeper rows: the next-year column goes; everything tightens */
.prow{grid-template-columns:auto auto 1fr auto auto;gap:8px;padding:7px 10px}
.prow .next{display:none}
.pshot{width:26px;height:26px}
.pname{font-size:12.5px}
/* salary bar rows (cap board / Trade Tester / proposal demo):
   name and value share the top line, the track gets the full width below */
.cbrow{grid-template-columns:minmax(0,1fr) auto;row-gap:5px;column-gap:8px;min-height:0;padding:2px 0}
.cbtrack{grid-column:1 / -1;grid-row:2;height:20px}
.cbval{max-width:60%}
.cbval .small{font-size:10.5px}
.luckrow{grid-template-columns:92px 1fr 46px}
.mcrow{flex-direction:column;align-items:center}
.enterbtn{display:block;text-align:center;padding:17px 20px;font-size:18px}
.anatbar{height:64px}
.anatseg span{max-height:58px}
.anattip{top:74px}
.cbdetail{padding:11px 12px 10px}
.kchip{font-size:12.5px}
.gobtn{font-size:13px;padding:11px 12px}
.flowwrap{overflow-x:auto}
.tradeweb{min-width:560px}
.lockwrap{margin:48px auto}
.ctlrow{grid-template-columns:90px 1fr 64px}
footer.ggg .in{padding:14px 12px}
}
"""
CSS = CSS.replace("F400", fonts["400"]).replace("F600", fonts["600"]).replace("F800", fonts["800"])
with open(os.path.join(OUT, "ggg.css"), "w", encoding="utf-8") as f:
    f.write(CSS)
import hashlib
css_v = hashlib.md5(CSS.encode()).hexdigest()[:8]

# ---------------- favicon: the orange LOB square from the nav ----------------
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#FF9A3C"/>
<text x="32" y="43" text-anchor="middle" font-family="Arial,Helvetica,sans-serif"
 font-size="26" font-weight="900" fill="#2A1404" letter-spacing="-1.5">LOB</text>
</svg>"""
with open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(FAVICON_SVG)

try:
    from PIL import Image, ImageDraw, ImageFont
    for size, fname in ((32, "favicon-32.png"), (180, "apple-touch-icon.png")):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        r = round(size * 14 / 64)
        d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=(255, 154, 60, 255))
        try:
            fnt = ImageFont.truetype("arialbd.ttf", round(size * 0.40))
        except OSError:
            fnt = ImageFont.load_default()
        bb = d.textbbox((0, 0), "LOB", font=fnt)
        d.text(((size - (bb[2] - bb[0])) / 2 - bb[0], (size - (bb[3] - bb[1])) / 2 - bb[1]),
               "LOB", font=fnt, fill=(42, 20, 4, 255))
        img.save(os.path.join(OUT, fname))
    print("favicons written (svg + png)")
except ImportError:
    print("favicons written (svg only — Pillow not installed)")

VIEWPORT = '<meta name="viewport" content="width=device-width,initial-scale=1">'
ICONS = ('<link rel="icon" type="image/svg+xml" href="favicon.svg">'
         '<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">'
         '<link rel="apple-touch-icon" href="apple-touch-icon.png">')

NAV_NEW = [("index.html", "Home"), ("analyzer.html", "Trade Tester")]
NAV_HIST = [("history.html", "History"), ("records.html", "Records"),
            ("drafts.html", "Drafts"), ("trades.html", "Trades")]


def nav(active):
    def links(pairs):
        return "".join(f'<a href="{h}" class="{"on" if h == active else ""}">{t}</a>'
                       for h, t in pairs)
    new_g = ('<div class="navgrp newg"><span class="navcap">New · your team</span>'
             '<div class="navlinks">' + links(NAV_NEW) + '</div></div>')
    hist_g = ('<div class="navgrp histg"><span class="navcap">League history</span>'
              '<div class="navlinks">' + links(NAV_HIST) + '</div></div>')
    pitch = f'<a href="pitch.html" class="pitchtab{" on" if active == "pitch.html" else ""}">🗳️ The Proposal</a>'
    lab = f'<a href="lab.html" class="labtab{" on" if active == "lab.html" else ""}">⚙️ Commish tools</a>'
    return f'<nav class="ggg"><div class="in"><span class="logo">LOB</span>{new_g}{hist_g}{pitch}{lab}</div></nav>'


FOOT = ('<footer class="ggg"><div class="in">LOB League — League of Burger · data from the Sleeper API · '
        f'stats computed {site["generated"]} · regular-season records unless noted · '
        'grudges update automatically</div></footer>')

# front-door gate: first visit on any page redirects to the pitch. The pitch
# page sets the flag on load, so one read-through unlocks the whole site.
GATE = """<script>try{if(!localStorage.getItem('lob-pitch-v2'))location.replace('pitch.html');}catch(e){}</script>"""

# ---------------- keeper-planner team data (same order/sort as cap-planner) ----------------
# maxKeep 5: everyone may select up to 5 keeps — with 3 or fewer no budget
# applies (Plan A); a 4th/5th keep requires the whole class to fit budget5
# (Plan B preview). The Home page shows both worlds on one screen.
# budget5 $50: a fresh R1 keep is $30 and a star re-kept past R1 is $36+, so
# 4-5 keeps means star + bargains or a mid-round fistful — not star + mids.
# Keep rounds: fresh 2025 draftees keep at their drafted round for one year;
# players who were already keepers in 2025 (kp=1) escalate one round now.
CFG = {"cap": 230, "floor": 160, "budget": 0, "maxKeep": 5, "budget5": 50, "waiver": 0,
       "franchise": False, "kcap": "on",
       "table": {1: 30, 2: 26, 3: 22, 4: 19, 5: 16, 6: 14, 7: 12, 8: 10,
                 9: 8, 10: 7, 11: 6, 12: 5, 13: 4, 14: 3, 15: 2, 16: 2}}
STEEP_TABLE = {1: 34, 2: 28, 3: 23, 4: 19, 5: 16, 6: 13, 7: 11, 8: 9,
               9: 7, 10: 5, 11: 4, 12: 3, 13: 2, 14: 2, 15: 1, 16: 1}


def escalate(round_2025, steps):
    r = round_2025 - steps
    return CFG["table"][r] if r >= 1 else CFG["table"][1] + 6 * (1 - r)


def planner_teams():
    players_db = load("players_nfl.json")
    users = {u["user_id"]: u for u in load("users_2025.json")}
    rosters = load("rosters_2025.json")
    d25_id = load("drafts_2025.json")[0]["draft_id"]
    draft25 = load(f"draftpicks_2025_{d25_id}.json")
    draft_round = {str(p["player_id"]): p["round"] for p in draft25}
    # players who were already keepers in 2025: their keep round escalates NOW
    # (one earlier than the round they were kept at); fresh 2025 draftees keep
    # at their drafted round for one year before the climb starts
    kept25 = {str(p["player_id"]) for p in draft25 if p.get("is_keeper")}
    name_of = {r["roster_id"]: (users.get(r["owner_id"]) or {}).get("display_name", "Former manager")
               for r in rosters}

    def picks_for(season):
        owner = {(rnd, rid): rid for rnd in range(1, 17) for rid in name_of}
        pick_files = ["tradedpicks_2024.json", "tradedpicks_2025.json"]
        if os.path.exists(os.path.join(DATA, "tradedpicks_2026.json")):
            pick_files.append("tradedpicks_2026.json")   # new trades in the renewed league
        for fname in pick_files:
            for tp in load(fname):
                if tp["season"] == season and (tp["round"], tp["roster_id"]) in owner:
                    owner[(tp["round"], tp["roster_id"])] = tp["owner_id"]
        po = {rid: [] for rid in name_of}
        for (rnd, orig), cur in owner.items():
            e = {"r": rnd}
            if orig != cur:
                e["from"] = name_of[orig]
            po[cur].append(e)
        for rid in po:
            po[rid].sort(key=lambda p: (p["r"], "from" in p))
        return po

    picks_of = picks_for("2026")
    picks_27 = picks_for("2027")
    # official keepers from the renewed 2026 league (rosters carry a `keepers` field)
    official = {}
    try:
        for r in load("rosters_2026.json"):
            official[r["roster_id"]] = {str(p) for p in (r.get("keepers") or [])}
    except FileNotFoundError:
        pass
    teams = []
    for r in sorted(rosters, key=lambda x: x["roster_id"]):
        plist = []
        for pid in (r.get("players") or []):
            pdb = players_db.get(str(pid), {})
            rnd = draft_round.get(str(pid))
            e = {"pid": str(pid), "n": pdb.get("name") or f"?{pid}",
                 "pos": pdb.get("pos") or "?", "t": pdb.get("team") or ""}
            if rnd is not None:
                kp = 1 if str(pid) in kept25 else 0
                e.update({"el": True, "r": rnd, "kp": kp,
                          "k26": escalate(rnd, kp), "k27": escalate(rnd, kp + 1)})
            else:
                e["el"] = False
            plist.append(e)
        plist.sort(key=lambda p: (not p["el"], p.get("k26", 999), p["n"]))
        ok = official.get(r["roster_id"], set())
        teams.append({"name": name_of[r["roster_id"]], "rid": r["roster_id"],
                      "picks": picks_of[r["roster_id"]],
                      "p27": picks_27[r["roster_id"]], "players": plist,
                      "ok": [i for i, e in enumerate(plist) if e["pid"] in ok]})
    return teams


def _norm_name(name):
    import re
    n = re.sub(r"[^a-z ]", "", (name or "").lower())
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return re.sub(r"\s+", " ", n).strip()


_SLOT = lambda rd: (rd - 0.5) * 10
_PSLOT = lambda rd, out: max(0.0, (16.5 - min(16, rd)) * 10) * (0.85 ** out)
MARKET_SEASONS = ["2025"]


# Commissioner-confirmed 2026 keeps that aren't locked in Sleeper yet
# (Alex, 2026-08-24): pid -> roster_id. The keeper market and the trade-card
# reads count these as kept; each entry is redundant (and removable) once the
# manager locks the keeper officially.
KEEP_FIXES = {}


def keeper_market():
    """The league's own keeper price history: every preseason (week-1) trade
    where the acquired player was KEPT that season — keep round, FFC ADP at
    the time, surplus (cost slot − ADP), and pick-slots paid — plus the fitted
    going rate (paid = a + b·surplus) that this year's deals are graded on."""
    try:
        hist_adp = load("ffc_adp_hist.json")
    except FileNotFoundError:
        hist_adp = {}
    players_db = load("players_nfl.json")
    events = []
    for s in MARKET_SEASONS:
        adp_map = {_norm_name(p.get("name")): p.get("adp")
                   for p in (hist_adp.get(s) or {}).get("players") or []}
        try:
            dmeta = load(f"drafts_{s}.json")[0]
            picks = load(f"draftpicks_{s}_{dmeta['draft_id']}.json")
            tx = load(f"transactions_{s}.json")
            users = {u["user_id"]: u["display_name"] for u in load(f"users_{s}.json")}
            rosters = load(f"rosters_{s}.json")
        except FileNotFoundError:
            continue
        rmap = {r["roster_id"]: users.get(r["owner_id"], "?") for r in rosters}
        kept = {(str(p["player_id"]), p.get("roster_id")): p["round"]
                for p in picks if p.get("is_keeper")}
        for wk_s, items in tx.items():
            if int(wk_s) != 1:
                continue
            for t in items or []:
                if t.get("type") != "trade" or t.get("status") != "complete":
                    continue
                rids = t.get("roster_ids") or []
                if len(rids) != 2:
                    continue
                adds = t.get("adds") or {}
                dps = t.get("draft_picks") or []
                for i, rid in enumerate(rids):
                    other = rids[1 - i]
                    paid = [(dp["round"], max(0, int(dp["season"]) - int(s)))
                            for dp in dps if dp["owner_id"] == other]
                    got = [(dp["round"], max(0, int(dp["season"]) - int(s)))
                           for dp in dps if dp["owner_id"] == rid]
                    ks = []
                    for pid, to in adds.items():
                        if to != rid:
                            continue
                        kr = kept.get((str(pid), rid))
                        if kr is None:
                            continue
                        nm = (players_db.get(str(pid)) or {}).get("name") or str(pid)
                        a = adp_map.get(_norm_name(nm))
                        ks.append({"n": nm, "kr": kr, "adp": round(a) if a else None,
                                   "surp": round(_SLOT(kr) - a) if a else None})
                    if not ks:
                        continue
                    surp = (sum(k["surp"] for k in ks)
                            if all(k["surp"] is not None for k in ks) else None)
                    events.append({"s": s, "team": rmap.get(rid, "?"), "ks": ks,
                                   "paid": sorted(r for r, _ in paid),
                                   "got": sorted(r for r, _ in got),
                                   "pslots": round(sum(_PSLOT(r, o) for r, o in paid)
                                                   - sum(_PSLOT(r, o) for r, o in got)),
                                   "surp": surp})
    # 2026, pre-draft: provisional events — "kept" = among the acquirer's
    # OFFICIAL Sleeper keepers (locks at the draft); excluded from the fit so
    # this year's deals are graded against history, never against themselves
    if "2026" not in MARKET_SEASONS:
        try:
            tx26 = load("transactions_2026.json")
            users26 = {u["user_id"]: u["display_name"] for u in load("users_2026.json")}
            rosters26 = load("rosters_2026.json")
            d25_id = load("drafts_2025.json")[0]["draft_id"]
            draft25 = load(f"draftpicks_2025_{d25_id}.json")
            adp26 = {_norm_name(p.get("name")): p.get("adp")
                     for p in (load("ffc_adp_2026.json").get("players") or [])}
        except FileNotFoundError:
            tx26 = None
        if tx26:
            rmap26 = {r["roster_id"]: users26.get(r["owner_id"], "?") for r in rosters26}
            ok26 = {r["roster_id"]: {str(p) for p in (r.get("keepers") or [])} for r in rosters26}
            dr26 = {str(p["player_id"]): p["round"] for p in draft25}
            kp26 = {str(p["player_id"]) for p in draft25 if p.get("is_keeper")}
            for items in tx26.values():
                for t in items or []:
                    if t.get("type") != "trade" or t.get("status") != "complete":
                        continue
                    rids = t.get("roster_ids") or []
                    if len(rids) != 2:
                        continue
                    for i, rid in enumerate(rids):
                        other = rids[1 - i]
                        paid = [(dp["round"], max(0, int(dp["season"]) - 2026))
                                for dp in t.get("draft_picks") or [] if dp["owner_id"] == other]
                        got = [(dp["round"], max(0, int(dp["season"]) - 2026))
                               for dp in t.get("draft_picks") or [] if dp["owner_id"] == rid]
                        ks = []
                        for pid, to in (t.get("adds") or {}).items():
                            pid = str(pid)
                            if to != rid or dr26.get(pid) is None or not (
                                    pid in ok26.get(rid, set()) or KEEP_FIXES.get(pid) == rid):
                                continue
                            kr = max(1, dr26[pid] - (1 if pid in kp26 else 0))
                            nm = (players_db.get(pid) or {}).get("name") or pid
                            a = adp26.get(_norm_name(nm))
                            ks.append({"n": nm, "kr": kr, "adp": round(a) if a else None,
                                       "surp": round(_SLOT(kr) - a) if a else None})
                        if not ks:
                            continue
                        surp = (sum(k["surp"] for k in ks)
                                if all(k["surp"] is not None for k in ks) else None)
                        events.append({"s": "2026", "team": rmap26.get(rid, "?"), "ks": ks,
                                       "paid": sorted(r for r, _ in paid),
                                       "got": sorted(r for r, _ in got),
                                       "pslots": round(sum(_PSLOT(r, o) for r, o in paid)
                                                       - sum(_PSLOT(r, o) for r, o in got)),
                                       "surp": surp, "prov": True})
    pts = [(e["surp"], e["pslots"]) for e in events
           if e["surp"] is not None and e["pslots"] > 0 and not e.get("prov")]
    fit = None
    if len(pts) >= 8:
        n = len(pts)
        sx = sum(x for x, _ in pts); sy = sum(y for _, y in pts)
        sxx = sum(x * x for x, _ in pts); sxy = sum(x * y for x, y in pts)
        den = n * sxx - sx * sx
        b = (n * sxy - sx * sy) / den if den else 0
        if b > 0:
            fit = {"a": round((sy - b * sx) / n, 1), "b": round(b, 2),
                   "n": n, "young": False}
    if fit is None and pts:
        ys = sorted(y for _, y in pts)
        fit = {"a": float(ys[len(ys) // 2]), "b": 0, "n": len(pts), "young": True}
    if fit:
        for e in events:
            if e["surp"] is not None and e["pslots"] > 0:
                e["fair"] = round(fit["a"] + fit["b"] * e["surp"])
                e["delta"] = e["pslots"] - e["fair"]
    events.sort(key=lambda e: -int(e["s"]))
    return {"events": events, "fit": fit}


MARKET = keeper_market()


def trades_2026():
    """This year's completed Sleeper trades, priced in cap dollars, with a
    live keeper-market read (surplus vs picks paid vs the fitted going rate)."""
    import datetime
    try:
        tx = load("transactions_2026.json")
        users = {u["user_id"]: u["display_name"] for u in load("users_2026.json")}
        rosters = load("rosters_2026.json")
        name_of = {r["roster_id"]: users.get(r["owner_id"], "?") for r in rosters}
    except FileNotFoundError:
        return []
    ok_of = {r["roster_id"]: {str(p) for p in (r.get("keepers") or [])} for r in rosters}
    players_db = load("players_nfl.json")
    d25_id = load("drafts_2025.json")[0]["draft_id"]
    draft25 = load(f"draftpicks_2025_{d25_id}.json")
    dround = {str(p["player_id"]): p["round"] for p in draft25}
    kept25 = {str(p["player_id"]) for p in draft25 if p.get("is_keeper")}
    try:
        adp26 = {_norm_name(p.get("name")): p.get("adp")
                 for p in (load("ffc_adp_2026.json").get("players") or [])}
    except FileNotFoundError:
        adp26 = {}
    fit = (MARKET or {}).get("fit")
    deals = []
    for items in tx.values():
        for t in items or []:
            if (t.get("type") == "trade" and t.get("status") == "complete"
                    and len(t.get("roster_ids") or []) == 2):
                deals.append(t)
    deals.sort(key=lambda t: t["status_updated"], reverse=True)
    out = []
    for t in deals:
        rids = t["roster_ids"]
        sides = {rid: {"name": name_of.get(rid, "?"), "players": [], "picks": [], "sal": 0}
                 for rid in rids}
        for pid, rid in (t.get("adds") or {}).items():
            pid = str(pid)
            pdb = players_db.get(pid) or {}
            rnd = dround.get(pid)
            sal = escalate(rnd, 1 if pid in kept25 else 0) if rnd else 0
            sides[rid]["players"].append(
                {"n": pdb.get("name") or f"?{pid}", "pos": pdb.get("pos") or "?", "sal": sal})
            sides[rid]["sal"] += sal
        for dp in t.get("draft_picks") or []:
            rid = dp["owner_id"]
            if rid not in sides:
                continue
            cur = dp["season"] == "2026"
            val = CFG["table"][dp["round"]] if cur else 0
            via = f" via {name_of.get(dp['roster_id'], '?')}" if dp["roster_id"] not in rids else ""
            sides[rid]["picks"].append(
                {"lab": f"{dp['season']} R{dp['round']}{via}", "val": val, "cur": cur})
            sides[rid]["sal"] += val
        # the keeper-market read: each side that landed keeper-eligible players
        mks = []
        for i, rid in enumerate(rids):
            other = rids[1 - i]
            paid = [(dp["round"], max(0, int(dp["season"]) - 2026))
                    for dp in t.get("draft_picks") or [] if dp["owner_id"] == other]
            got = [(dp["round"], max(0, int(dp["season"]) - 2026))
                   for dp in t.get("draft_picks") or [] if dp["owner_id"] == rid]
            ks = []
            for pid, to in (t.get("adds") or {}).items():
                pid = str(pid)
                if to != rid or dround.get(pid) is None:
                    continue
                kr = max(1, dround[pid] - (1 if pid in kept25 else 0))
                nm = (players_db.get(pid) or {}).get("name") or pid
                a = adp26.get(_norm_name(nm))
                ks.append({"n": nm, "kr": kr, "adp": round(a) if a else None,
                           "surp": round(_SLOT(kr) - a) if a else None,
                           "kept": pid in ok_of.get(rid, set()) or KEEP_FIXES.get(pid) == rid,
                           "kset": bool(ok_of.get(rid))})
            if not ks:
                continue
            surp = (sum(k["surp"] for k in ks)
                    if all(k["surp"] is not None for k in ks) else None)
            mk = {"team": name_of.get(rid, "?"), "ks": ks,
                  "paid": sorted(r for r, _ in paid),
                  "got": sorted(r for r, _ in got),
                  "pslots": round(sum(_PSLOT(r, o) for r, o in paid)
                                  - sum(_PSLOT(r, o) for r, o in got)), "surp": surp}
            if fit and surp is not None and mk["pslots"] > 0:
                mk["fair"] = round(fit["a"] + fit["b"] * surp)
                mk["delta"] = mk["pslots"] - mk["fair"]
            mks.append(mk)
        entry = {"date": None, "sides": [sides[r] for r in rids]}
        d = __import__("datetime").datetime.fromtimestamp(t["status_updated"] / 1000)
        entry["date"] = f"{d.strftime('%b')} {d.day}"
        if mks:
            entry["mk"] = mks
        out.append(entry)
    return out


# League-confirmed corrections to the fire-sale heuristic, keyed
# (season, week, a moved player) -> corrected tag. None yet for LOB.
FIRE_FIXES = {}


def build_replay():
    """Compact per-season replay logs so the Lab can re-run history client-side."""
    from collections import defaultdict
    players_db = load("players_nfl.json")
    out = []
    for s in ["2025", "2024"]:
        users = {u["user_id"]: u["display_name"] for u in load(f"users_{s}.json")}
        rosters = load(f"rosters_{s}.json")
        rmap = {r["roster_id"]: users.get(r["owner_id"], "Former manager") for r in rosters}
        dmeta = load(f"drafts_{s}.json")[0]
        cutoff = dmeta.get("last_picked") or dmeta.get("start_time") or 0
        picks = load(f"draftpicks_{s}_{dmeta['draft_id']}.json")
        draft = [{"pid": str(p["player_id"]), "r": p["round"], "rid": p["roster_id"],
                  "k": 1 if p.get("is_keeper") else 0}
                 for p in picks if p.get("roster_id") is not None]
        dround = {d["pid"]: d["r"] for d in draft}

        matchups = load(f"matchups_full_{s}.json")
        pws = load(f"league_{s}.json")["settings"].get("playoff_week_start", 15)
        results = []  # (week, winner_rid, loser_rid)
        for wk_s, items in matchups.items():
            wk = int(wk_s)
            if wk >= pws:
                continue
            by_m = defaultdict(list)
            for m in items:
                if m.get("matchup_id") is not None and (m.get("points") or 0) > 0:
                    by_m[m["matchup_id"]].append(m)
            for pair in by_m.values():
                if len(pair) != 2:
                    continue
                a, b = pair
                w_, l_ = (a, b) if a["points"] > b["points"] else (b, a)
                results.append((wk, w_["roster_id"], l_["roster_id"]))

        def losing_record(rid, week):
            w = sum(1 for wk, wr, _ in results if wk < week and wr == rid)
            l = sum(1 for wk, _, lr in results if wk < week and lr == rid)
            return l > w

        allt = []
        for wk_s, items in load(f"transactions_{s}.json").items():
            for t in items:
                if t["status"] == "complete":
                    allt.append((int(wk_s), t))
        allt.sort(key=lambda x: x[1]["status_updated"])

        evs, names = [], {}
        for wk, t in allt:
            adds = t.get("adds") or {}
            drops = t.get("drops") or {}
            if t["type"] == "trade":
                if t["status_updated"] < cutoff:
                    continue
                mv = []
                for pid, rid in adds.items():
                    pid = str(pid)
                    mv.append([pid, drops.get(pid), rid])
                    names[pid] = (players_db.get(pid) or {}).get("name") or "?"
                pk = {}
                for dp in t.get("draft_picks") or []:
                    pk.setdefault(str(dp["owner_id"]), []).append(
                        f"{dp['season']} R{dp['round']}")
                for labs in pk.values():
                    labs.sort()
                fire = 0
                rids = t.get("roster_ids") or []
                if len(rids) == 2:
                    for rid in rids:
                        if not losing_record(rid, wk):
                            continue
                        sent = [dround.get(p, 16) for p, frm, _ in mv if frm == rid]
                        got = [dround.get(p, 16) for p, _, to in mv if to == rid]
                        if sent and min(sent) <= 7 and (not got or min(got) >= 8):
                            fire = 1
                moved = {names[p] for p, _, _ in mv}
                for (fs, fw, fname), tag in FIRE_FIXES.items():
                    if fs == s and fw == wk and fname in moved:
                        fire = tag
                ev = {"w": wk, "t": 1, "mv": mv, "f": fire}
                if pk:
                    ev["pk"] = pk
                evs.append(ev)
            elif t["type"] in ("waiver", "free_agent"):
                mv = ([[str(p), None, rid] for p, rid in adds.items()]
                      + [[str(p), rid, None] for p, rid in drops.items()])
                evs.append({"w": wk, "t": 0, "mv": mv})
        out.append({"s": s, "teams": [{"rid": rid, "name": nm} for rid, nm in sorted(rmap.items())],
                    "draft": draft, "events": evs, "names": names})
    return out


try:
    lg26 = load("league_2026.json")
except FileNotFoundError:
    lg26 = {}

career = site["career"]
finishes = {}
for sn in site["seasons"]:
    for i, t in enumerate(sn["standings"]):
        finishes.setdefault(t["name"], []).append(
            {"s": sn["season"], "place": i + 1,
             "champ": t["name"] == sn["champ"], "toilet": t["name"] == sn["toilet"]})
replay = build_replay()
# fire-sale-shaped trades flagged by the heuristic across LOB history (for the pitch receipts)
fires = sum(1 for sn in replay for ev in sn["events"] if ev.get("t") == 1 and ev.get("f"))
slices = {
    "index.html": {"cfg": CFG, "teams": planner_teams(), "career": career,
                   "h2h": site["h2h"], "finishes": finishes, "steep": STEEP_TABLE,
                   "commishUserId": commish_uid, "leagueId2025": "1256797823983177729",
                   "leagueId2026": lg26.get("league_id"), "leagueName2026": lg26.get("name")},
    "history.html": {"seasons": site["seasons"], "career": career, "h2h": site["h2h"]},
    "records.html": {"records": site["records"], "career": career},
    "drafts.html": {"drafts": site["drafts"]},
    "trades.html": {"trades": site["trades"], "pickValues": site["pick_values"],
                    "trades26": trades_2026(), "market": MARKET},
    "lab.html": {"teams": planner_teams(), "adopted": CFG["table"],
                 "leagueId2026": lg26.get("league_id"),
                 "repo": "https://github.com/StrubeTube/lob-league",
                 # Same proposed rule set as the GGG site (the base): flattened
                 # table, keepers count against team salary, keepers slot on the
                 # board at their keep round, $230 cap / $160 floor band.
                 "defaults": {"cap": 230, "floor": 160, "budget5": 50},
                 "replay": replay},
    "pitch.html": {"cfg": {"cap": CFG["cap"], "floor": CFG["floor"], "table": CFG["table"],
                           "budget5": CFG["budget5"]},
                   "fires": fires, "nseasons": len(replay)},
    "analyzer.html": {"teams": planner_teams(), "steep": STEEP_TABLE,
                      "cfg": {"cap": CFG["cap"], "floor": CFG["floor"], "table": CFG["table"]}},
}

for page, data in slices.items():
    with open(os.path.join(TPL, page), encoding="utf-8") as f:
        html = f.read()
    # shared templates say GGG; this is the LOB build (localStorage keys get the
    # lob- prefix so the two sites don't collide on the shared github.io origin)
    html = html.replace("GGG", "LOB").replace("'ggg-", "'lob-")
    html = html.replace("__NAV__", nav(page)).replace("__FOOT__", FOOT)
    gate = GATE if page != "pitch.html" else ""
    html = html.replace('<link rel="stylesheet" href="ggg.css">',
                        gate + VIEWPORT + ICONS + '<link rel="stylesheet" href="ggg.css">', 1)
    html = html.replace('href="ggg.css"', f'href="ggg.css?v={css_v}"')
    html = html.replace("/*__DATA__*/{}", json.dumps(data, ensure_ascii=False))
    with open(os.path.join(OUT, page), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"built {page} ({os.path.getsize(os.path.join(OUT, page))//1024} KB)")

# cap tools (planner/report) removed from the site for now — sources kept in repo
# root via build_planner.py / build_report.py for when The Case gets redone.
for stale in ("cap-planner.html", "cap-report.html"):
    p = os.path.join(OUT, stale)
    if os.path.exists(p):
        os.remove(p)
        print(f"removed {stale}")

open(os.path.join(OUT, ".nojekyll"), "w").close()
print("site assembled ->", OUT)
