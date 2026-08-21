# Panel DRU · FuXion

Tablero de producción del proyecto **DRU-FuXion** en Wrike: 11 videos × 9 etapas.
Se publica con GitHub Pages y se actualiza solo.

## Cómo se actualiza

`.github/workflows/panel.yml` corre de lunes a viernes a las 9:00 (America/Cordoba):
lee Wrike, reescribe `estado.json`, regenera `index.html` y commitea si algo cambió.
También se puede disparar a mano desde la pestaña **Actions → Actualizar panel → Run workflow**.

Requiere un secret **`WRIKE_TOKEN`** (Settings → Secrets and variables → Actions):
un token permanente de Wrike con permiso de lectura sobre el proyecto.

A mano, desde una terminal:

```bash
WRIKE_TOKEN=xxx python3 actualizar.py
```

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | El panel. Autocontenido. **Generado — no editar a mano.** |
| `plantilla.html` | La plantilla real. Acá se tocan estilos y secciones. |
| `generar.py` | Cronograma + `estado.json` → `index.html`. |
| `actualizar.py` | Lee Wrike y llama a `generar.py`. Lo corre el workflow. |
| `estado.json` | Última lectura de Wrike. |
| `robots.txt`, `.nojekyll` | El repo es público pero no se indexa. |

## Si cambia el cronograma

Las fechas del plan viven en `generar.py` (`ETAPAS`, `INICIO`, `TAKT`). El workflow lee
**estados**, no fechas: si se replanifica en Wrike hay que reflejarlo ahí y volver a generar,
o el panel compara contra un plan viejo. Si una etapa se renombra en Wrike, `actualizar.py`
lo avisa en el log del workflow.
