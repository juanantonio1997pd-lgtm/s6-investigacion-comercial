# S6 — Product research provisional (DROP-IA)

Repo independiente. **Nunca** tocar el repo DROP-IA ni interferir con S1–S5. Provisional hasta que exista M4.
Sin gasto, suscripciones ni APIs de pago sin autorización expresa. No eludir bloqueos de acceso.

## Cómo se usa (lenguaje natural)
El usuario pide, tú ejecutas con WebSearch + `python3 tools/s6.py ...` y respondes en español, corto.

| Petición | Qué haces |
|---|---|
| "Busca nuevos productos" | Lee `s6.py rank`/`data/products.json` para no repetir. Busca (varias WebSearch en paralelo), registra con `add-product` + `evidence`. Descarta con `discard` y motivo. |
| "Analiza el producto X" | Demanda, competidores, anuncios, precios, proveedor, riesgos UE → `evidence`, `costs`, `economics`. |
| "Compara países para X" | Producto primero, mercado después. Un `market` por país con postura, motivo y confianza. No limitarse a ES/DE/FR/IT/UK/US. |
| "Mejores candidatos" | `s6.py rank` y resume. |
| "Actualiza X" | Revisa evidencias con fecha antigua, añade nuevas (no borres las viejas). |
| "Informe" | `s6.py report [--product id]` y `s6.py export`; resume en chat y enlaza el .md. |

Al empezar cualquier investigación: `python3 tools/s6.py status` (comprueba qué fuentes están accesibles) y dilo si hay bloqueos.
Al terminar: commit + push a la rama de la sesión (nunca PR sin pedirlo).

## Reglas de evidencia (obligatorias)
- `VERIFICADO`: dato directo de fuente **primaria** vista por ti (anuncio activo en Meta Ads Library, página de tienda/listing, norma oficial, Google Trends). El script lo exige.
- `ESTIMACION`: cifra de fuente secundaria (blog, herramienta de terceros) o cálculo propio con supuestos. Con URL y fecha.
- `HIPOTESIS`: idea sin dato. Sin fuente.
- Un blog que dice "producto ganador" **no** es demanda verificada. Alcance ≠ ventas; facturación estimada ≠ beneficio; poca competencia ≠ demanda.
- Cada hallazgo: fuente, fecha de la fuente, confianza (alta/media/baja). Nada inventado cuando una herramienta bloquea: se anota la limitación.
- Costes: `basis` = `confirmado` (cotización/listing visto) o `estimado`. Precios de proveedor sin acceso → pendiente, no inventar.
- Publicidad: usar anuncios solo como referencia; creatividades originales.

## Restricciones comerciales fijas
- Fecha objetivo de prueba: 1/11/2026. Un producto solo es "listo para noviembre" si hay stock/proveedor con entrega UE viable antes de Navidad.
- Venta desde España: UE con OSS (IVA de destino); UK/US son extra-UE (aduanas, IVA/sales tax) → mayor fricción.
- UE: marcado CE, GPSR (seguridad general de productos, responsable en la UE), 14 días de desistimiento, etiquetado y RAEE/baterías según producto.

## Estructura
- `tools/s6.py` CLI (stdlib), `tests/` (`python3 -m unittest discover -s tests`)
- `data/products.json`, `data/evidence.jsonl` (solo se añade), `data/source_access.json`
- `reports/` informes Markdown, `exports/` CSV/JSON para M4.
