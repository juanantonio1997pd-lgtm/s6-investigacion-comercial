# S6 — Product research provisional para DROP-IA

Repo independiente (no toca DROP-IA). Se usa hablando con Claude Code (ver `CLAUDE.md`):
"busca nuevos productos", "analiza X", "compara países para X", "mejores candidatos", "actualiza X", "informe".

CLI (stdlib, Python 3): `python3 tools/s6.py -h`. Tests: `python3 -m unittest discover -s tests`.
Datos en `data/`, informes en `reports/`, exportables para M4 en `exports/` (CSV/JSON).
Limitación actual: acceso de red restringido; ver `data/source_access.json`.
