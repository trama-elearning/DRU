#!/usr/bin/env python3
"""Genera index.html del panel FuXion.

Uso:
    python3 generar.py                 -> usa estado.json si existe; si no, plan puro
    python3 generar.py estado.json     -> hornea los estados reales de Wrike

estado.json: {"sello":"20/08 16:30","tareas":{"<titulo exacto de la tarea>":{"completada":bool,"estado":"..."}}}
"""
import json, sys, os
from datetime import date, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))

def addbd(d, n):
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5: n -= 1
    return d

ETAPAS = [("Guion",2,"DI",0),("Validación cliente guion",2,"CL",0),("Propuesta Gráfica",1,"DG",0),
          ("Realización audiovisual",3,"ED",0),("Interacción",1,"DI",0),
          ("QA y correcciones internas",2,"QA",0),("Validación cliente Audiovisual",2,"CL",0),
          ("Correcciones cliente",2,"ED",1),("LMS",1,"QA",1)]
ABBR = ["Guion","Val. guion","Gráfica","Realización","Interac.","QA int.","Val. video","Correcc.","LMS"]
NOMBRE_ROL = {"DI":"Diseño instruccional","DG":"Diseño gráfico","EdA":"Editor A",
              "EdB":"Editor B","QA":"QA / LMS","CL":"Validación FuXion"}
VIDEOS = [("Onboarding","Onboarding",4532099296)] + [
    (f"V{i}", f"Paso {i}", pl) for i, pl in enumerate(
        [4532105630,4532115561,4532136420,4532136489,4532136550,
         4532136588,4532136639,4532136684,4532136697,4532136709], 1)]
INICIO = date(2026,8,24); TAKT = 3

def construir():
    out = []
    for i,(code,label,link) in enumerate(VIDEOS):
        cur = addbd(INICIO, TAKT*i); et = []
        for j,(n,dur,rol,buf) in enumerate(ETAPAS):
            cur = addbd(cur, buf); fin = addbd(cur, dur-1)
            r = ("EdA" if i%2==0 else "EdB") if rol=="ED" else rol
            et.append({"n":j+1,"nombre":n,"abbr":ABBR[j],"ini":cur.isoformat(),
                       "fin":fin.isoformat(),"rol":r,
                       "key":("" if code=="Onboarding" else code+". ")+n})
            cur = addbd(fin, 1)
        out.append({"code":code,"label":label,"link":link,
                    "editor":"Editor A" if i%2==0 else "Editor B",
                    "ini":et[0]["ini"],"fin":et[-1]["fin"],"etapas":et})
    return out

def main():
    estado = {"sello": None, "tareas": {}, "vivo": False}
    ruta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "estado.json")
    if os.path.exists(ruta):
        estado = json.load(open(ruta, encoding="utf-8"))
    datos = {"videos": construir(), "roles": NOMBRE_ROL,
             "sello": estado.get("sello"), "tareas": estado.get("tareas", {}),
             "vivo": bool(estado.get("vivo", estado.get("tareas"))),
             "proyecto": {"link": 4528285748, "takt": TAKT,
                          "inicio": INICIO.isoformat(), "fin": "2026-10-28"}}
    plantilla = open(os.path.join(AQUI, "plantilla.html"), encoding="utf-8").read()
    html = plantilla.replace("__DATOS__", json.dumps(datos, ensure_ascii=False, separators=(",",":")))
    open(os.path.join(AQUI, "index.html"), "w", encoding="utf-8").write(html)
    print(f"index.html generado · {len(datos['videos'])} videos · "
          f"{'con estados de Wrike' if datos['vivo'] else 'solo cronograma'}")

if __name__ == "__main__":
    main()
