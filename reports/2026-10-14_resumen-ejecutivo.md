# S6 — Resumen ejecutivo, primera pasada (14/10/2026)

## Conclusión honesta
**Ningún producto está validado ni listo para prueba comercial.** Esta sesión no puede abrir Meta Ads Library, Google Trends, TikTok Creative Center, TrendTrack, AliExpress, Amazon, CJ ni ningún marketplace (403 de la política de red; ver `data/source_access.json`). Solo funciona la búsqueda web, que devuelve blogs de proveedores y herramientas sin datos de ventas. Por eso no hay ni un solo hecho `VERIFICADO` en la base de datos: 0 de 14 evidencias.

## Qué sí se ha establecido (estimaciones, confianza baja/media)
- Black Friday es el 27/11/2026 y Cyber Monday el 30/11. El CPM sube 40–80 % en noviembre (fuente: guía de Copyfy, sin verificar).
- Reglamento GPSR de seguridad de productos: se necesita operador responsable en la UE y sus datos en la ficha. Los productos eléctricos o con batería añaden CE y normativa de pilas.
- Polonia: pagos con BLIK en fuerte crecimiento (+23 % en valor online, Q1 2026, nota de prensa de BLIK).
- Alemania aparece como gran importador de mantas eléctricas (informe de pago de IndexBox, sin datos 2026).

## Candidatos (7 registrados, 1 descartado) — todos pendientes de validar
| Producto | Estado | Motivo principal |
|---|---|---|
| Puzzle 3D de madera | candidato | Regalo, bajo riesgo regulatorio, muy demostrable en vídeo; sin datos de demanda |
| Manta eléctrica | candidato | Estacional invierno; riesgo de seguridad (CE/LVD) alto y competencia local polaca sin medir |
| Calentador de manos recargable | candidato débil | Solo mención no confirmada; batería de litio |
| Mini proyector | candidato débil | Categoría muy anunciada |
| Power bank magnético / 3 en 1 | candidato débil | Baterías, saturación probable |
| Corrector de postura | candidato débil | Fuente antigua; riesgo en afirmaciones de salud |
| Rodillo quitapelos | **descartado** | Precio <25 € y margen absoluto insuficiente |

Países: no hay ninguna combinación producto-país `recomendada`. Las únicas posturas `alternativo` son manta eléctrica–DE y puzzle 3D–ES, ambas con confianza baja.

## Economía ilustrativa (supuestos, NO datos)
Con un PVP de 39,90 € con IVA, coste de producto de 12 € y envío de 5 €, el CPA de equilibrio sale en 10,7–11,7 € según el país (ROAS de equilibrio ≈3,4–3,7). Con CPM más caros en Q4, ese margen es estrecho. Los costes reales de proveedor están **sin confirmar**.

## Plazos
Hoy 14/10; lanzamiento 1/11 (18 días). Solo es viable stock en la UE (BigBuy/CJ UE, 3–7 días según guías, sin verificar). Hive Polonia avisa de que puede no aceptar entradas de stock en Black Friday/Navidad. Los envíos desde China no llegan a tiempo.

## Qué falta para tener una recomendación real
1. Desbloquear Meta Ads Library, Google Trends, TikTok Creative Center, AliExpress/CJ/BigBuy y Amazon/Idealo (lista en `data/source_access.json`).
2. Por producto y país: anuncios activos y su antigüedad, tendencia 90 días, precios de la competencia y cotización de proveedor con stock UE.
3. Confirmar certificación CE y el operador responsable para cualquier producto eléctrico.
