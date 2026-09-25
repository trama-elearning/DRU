#!/usr/bin/env python3
"""Genera index.html del panel FuXion.

Uso:
    python3 generar.py                 -> usa estado.json si existe; si no, plan puro
    python3 generar.py estado.json     -> hornea los estados reales de Wrike

estado.json: {"sello":"20/08 16:30","tareas":{"<titulo exacto de la tarea>":{"completada":bool,"estado":"..."}}}

Replanificación 25/09/2026: desde V3 la propuesta gráfica pasa de 1 a 4 días y la
realización audiovisual de 3 a 5 días (dos videos en paralelo, un editor cada uno).
Eso obliga a un takt de 4 días. Onboarding, V1 y V2 conservan el plan original.
"""
import json, sys, os
from datetime import date, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))

def addbd(d, n):
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5: n -= 1
    return d

# (nombre, duracion_dias, rol, holgura_previa_dias)
ETAPAS_ORIG = [("Guion",2,"DI",0),("Validación cliente guion",2,"CL",0),("Propuesta Gráfica",1,"DG",0),
               ("Realización audiovisual",3,"ED",0),("Interacción",1,"DI",0),
               ("QA y correcciones internas",2,"QA",0),("Validación cliente Audiovisual",2,"CL",0),
               ("Correcciones cliente",2,"ED",1),("LMS",1,"QA",1)]

ETAPAS_NUEVO = [("Guion",2,"DI",0),("Validación cliente guion",2,"CL",0),("Propuesta Gráfica",4,"DG",0),
                ("Realización audiovisual",5,"ED",0),("Interacción",1,"DI",1),
                ("QA y correcciones internas",2,"QA",1),("Validación cliente Audiovisual",2,"CL",0),
                ("Correcciones cliente",2,"ED",1),("LMS",1,"QA",0)]

ABBR = ["Guion","Val. guion","Gráfica","Realización","Interac.","QA int.","Val. video","Correcc.","LMS"]
NOMBRE_ROL = {"DI":"Diseño instruccional","DG":"Diseño gráfico","EdA":"Editor A",
              "EdB":"Editor B","QA":"QA / LMS","CL":"Validación FuXion"}
VIDEOS = [("Onboarding","Onboarding",4532099296)] + [
    (f"V{i}", f"Paso {i}", pl) for i, pl in enumerate(
        [4532105630,4532115561,4532136420,4532136489,4532136550,
         4532136588,4532136639,4532136684,4532136697,4532136709], 1)]

INICIO      = date(2026,8,24); TAKT      = 3   # Onboarding, V1, V2 (indices 0-2)
INICIO_NUEVO= date(2026,9,24); TAKT_NUEVO= 4   # V3..V10 (indices 3-10)
CORTE = 3                                       # primer indice con el plan nuevo
FIN_PROYECTO = "2026-12-04"

def construir(fechas=None):
    """fechas: {titulo exacto: [inicio, fin]} tomado de Wrike. Manda sobre el plan calculado."""
    fechas = fechas or {}
    out = []
    for i,(code,label,link) in enumerate(VIDEOS):
        if i < CORTE:
            etapas, cur = ETAPAS_ORIG, addbd(INICIO, TAKT*i)
        else:
            etapas, cur = ETAPAS_NUEVO, addbd(INICIO_NUEVO, TAKT_NUEVO*(i-CORTE))
        et = []
        for j,(n,dur,rol,buf) in enumerate(etapas):
            cur = addbd(cur, buf); fin = addbd(cur, dur-1)
            r = ("EdA" if i%2==0 else "EdB") if rol=="ED" else rol
            key = ("" if code=="Onboarding" else code+". ")+n
            ini_s, fin_s = cur.isoformat(), fin.isoformat()
            real = fechas.get(key)
            if real and real[0] and real[1]: ini_s, fin_s = real[0], real[1]
            et.append({"n":j+1,"nombre":n,"abbr":ABBR[j],"ini":ini_s,
                       "fin":fin_s,"rol":r,"key":key})
            cur = addbd(fin, 1)
        rango = [e["ini"] for e in et] + [e["fin"] for e in et]
        out.append({"code":code,"label":label,"link":link,
                    "editor":"Editor A" if i%2==0 else "Editor B",
                    "ini":min(rango),"fin":max(rango),"etapas":et})
    return out

def main():
    estado = {"sello": None, "tareas": {}, "vivo": False}
    ruta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "estado.json")
    if os.path.exists(ruta):
        estado = json.load(open(ruta, encoding="utf-8"))
    videos = construir(estado.get("fechas"))
    fin_real = max(v["fin"] for v in videos)
    datos = {"videos": videos, "roles": NOMBRE_ROL,
             "sello": estado.get("sello"), "tareas": estado.get("tareas", {}),
             "vivo": bool(estado.get("vivo", estado.get("tareas"))),
             "proyecto": {"link": 4528285748, "takt": TAKT_NUEVO,
                          "inicio": INICIO.isoformat(), "fin": fin_real}}
    plantilla = open(os.path.join(AQUI, "plantilla.html"), encoding="utf-8").read()
    html = plantilla.replace("__DATOS__", json.dumps(datos, ensure_ascii=False, separators=(",",":")))
    open(os.path.join(AQUI, "index.html"), "w", encoding="utf-8").write(html)
    print(f"index.html generado · {len(datos['videos'])} videos · "
          f"{'con estados de Wrike' if datos['vivo'] else 'solo cronograma'}")

if __name__ == "__main__":
    main()
