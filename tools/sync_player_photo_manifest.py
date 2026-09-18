"""Offline manifest sync. Not imported by app.py."""
import csv, sys
from pathlib import Path
new_csv, manifest_csv = map(Path, sys.argv[1:3])
with manifest_csv.open(encoding="utf-8-sig", newline="") as f:
    old_rows=list(csv.DictReader(f))
old={str(r["player_id"]):r for r in old_rows}
with new_csv.open(encoding="utf-8-sig", newline="") as f:
    new_rows=list(csv.DictReader(f))
out=[]; new_ids=[]
for r in new_rows:
    pid=str(r["Id"]).strip()
    if pid in old:
        x=old[pid]
        x["nome"]=r.get("Nome",x["nome"]); x["squadra"]=r.get("Squadra",x["squadra"])
        x["ruolo_classico"]=r.get("R",x["ruolo_classico"]); x["ruolo_mantra"]=r.get("RM",x["ruolo_mantra"])
    else:
        x={"player_id":pid,"nome":r.get("Nome",""),"squadra":r.get("Squadra",""),"ruolo_classico":r.get("R",""),"ruolo_mantra":r.get("RM",""),"file":f"{pid}.jpg","fonte":"","licenza":"","autore":"","stato":"DA_REPERIRE"}
        new_ids.append(pid)
    out.append(x)
fields=["player_id","nome","squadra","ruolo_classico","ruolo_mantra","file","fonte","licenza","autore","stato"]
with manifest_csv.open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
print(f"Giocatori: {len(out)} | nuovi ID: {len(new_ids)}")
if new_ids: print("Nuovi:",", ".join(new_ids))
