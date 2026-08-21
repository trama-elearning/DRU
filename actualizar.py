#!/usr/bin/env python3
"""Lee el proyecto DRU-FuXion en Wrike, hornea estado.json y regenera index.html.

Necesita la variable de entorno WRIKE_TOKEN (token permanente de Wrike).
Lo corre GitHub Actions todos los días; también sirve a mano:

    WRIKE_TOKEN=xxx python3 actualizar.py
"""
import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

FOLDER = "IEAG4NK5"          # cuenta
PROYECTO = "MQAAAAEN6Cg0"    # carpeta del proyecto DRU-FuXion
API = "https://www.wrike.com/api/v4"

def wrike(path):
    tok = os.environ.get("WRIKE_TOKEN")
    if not tok:
        sys.exit("Falta WRIKE_TOKEN")
    req = urllib.request.Request(API + path, headers={"Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["data"]
    except urllib.error.HTTPError as e:
        sys.exit(f"Wrike {e.code}: {e.read()[:300].decode('utf8','ignore')}")

def main():
    tareas_wrike = wrike(f"/folders/{PROYECTO}/tasks?subTasks=true&fields=[%22subTaskIds%22]&pageSize=200")
    estado_por_titulo = {t["title"]: t.get("status") == "Completed" for t in tareas_wrike}

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import generar
    tareas = {}
    faltantes = []
    for v in generar.construir():
        for et in v["etapas"]:
            k = et["key"]
            if k not in estado_por_titulo:
                faltantes.append(k)
            tareas[k] = {"completada": bool(estado_por_titulo.get(k))}

    ahora = datetime.now(timezone(timedelta(hours=-3)))
    json.dump({"sello": ahora.strftime("%d/%m %H:%M"), "vivo": True, "tareas": tareas},
              open("estado.json", "w", encoding="utf-8"), ensure_ascii=False)

    hechas = sum(1 for t in tareas.values() if t["completada"])
    print(f"Wrike: {len(tareas_wrike)} tareas leídas · {hechas}/{len(tareas)} etapas completadas")
    if faltantes:
        print(f"AVISO: {len(faltantes)} etapas del plan no aparecen en Wrike "
              f"(¿renombradas?): {', '.join(faltantes[:5])}")
    generar.main()

if __name__ == "__main__":
    main()
