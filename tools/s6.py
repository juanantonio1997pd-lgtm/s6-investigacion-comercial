#!/usr/bin/env python3
"""S6 — herramienta mínima de product research. Solo biblioteca estándar.

Claude hace la búsqueda (WebSearch/navegación) y registra aquí cada hallazgo;
este script valida, calcula márgenes, ordena y genera informes/exportaciones.
Datos en data/ (JSON/JSONL). Independiente de DROP-IA.
"""
import argparse, csv, json, os, sys, urllib.request, urllib.error
from datetime import date
from pathlib import Path

ROOT = Path(os.environ.get("S6_ROOT", Path(__file__).resolve().parent.parent))
DATA, REPORTS, EXPORTS = ROOT / "data", ROOT / "reports", ROOT / "exports"
KINDS = ("VERIFICADO", "ESTIMACION", "HIPOTESIS")
SOURCE_TYPES = ("primario", "secundario")  # primario = dato directo (anuncio, tienda, listing, norma)
CONF = ("alta", "media", "baja")
STANCES = ("recomendado", "alternativo", "descartado", "desconocido")

# Tipos de IVA/impuesto de referencia (revisar antes de decidir; no es asesoría fiscal).
VAT = {"ES": .21, "DE": .19, "FR": .20, "IT": .22, "PT": .23, "PL": .23, "RO": .21,
       "BG": .20, "HR": .25, "GR": .24, "NL": .21, "UK": .20, "US": 0.0}
NON_EU = {"UK", "US"}

PROBES = ["facebook.com/ads/library", "trends.google.com", "ads.tiktok.com/business/creativecenter",
          "www.trendtrack.io", "www.aliexpress.com", "www.amazon.de", "www.cjdropshipping.com",
          "www.reddit.com", "www.idealo.de", "es.wikipedia.org"]


def _load(name, default):
    p = DATA / name
    return json.loads(p.read_text()) if p.exists() else default


def _save(name, obj):
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _evidence():
    p = DATA / "evidence.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def _need(cond, msg):
    if not cond:
        raise SystemExit(f"ERROR: {msg}")


# ---------- núcleo ----------
def add_product(pid, name, category, ptype, need, price_lo=None, price_hi=None):
    prods = _load("products.json", {})
    today = date.today().isoformat()
    p = prods.setdefault(pid, {"created": today, "status": "candidato", "markets": {}, "risks": []})
    p.update(name=name, category=category, type=ptype, need=need, updated=today)
    if price_lo is not None:
        p["price_observed_eur"] = [price_lo, price_hi if price_hi is not None else price_lo]
    _save("products.json", prods)
    return p


def add_evidence(product, claim, kind, source_type, confidence, source_url="", source_name="",
                 source_date="", country="", metric=""):
    prods = _load("products.json", {})
    _need(product in prods, f"producto desconocido: {product}")
    _need(kind in KINDS, f"kind debe ser uno de {KINDS}")
    _need(source_type in SOURCE_TYPES, f"source_type debe ser uno de {SOURCE_TYPES}")
    _need(confidence in CONF, f"confidence debe ser uno de {CONF}")
    if kind != "HIPOTESIS":
        _need(source_url and source_date, "VERIFICADO/ESTIMACION exigen --source-url y --source-date")
    if kind == "VERIFICADO":
        _need(source_type == "primario", "VERIFICADO exige fuente primaria (dato directo); un blog es ESTIMACION o HIPOTESIS")
    ev = dict(id=len(_evidence()) + 1, product=product, country=country.upper(), claim=claim, kind=kind,
              source_type=source_type, confidence=confidence, source_url=source_url,
              source_name=source_name, source_date=source_date, metric=metric,
              retrieved=date.today().isoformat())
    DATA.mkdir(parents=True, exist_ok=True)
    with open(DATA / "evidence.jsonl", "a") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    return ev


def set_market(product, country, stance, reason, confidence):
    prods = _load("products.json", {})
    _need(product in prods, f"producto desconocido: {product}")
    _need(stance in STANCES and confidence in CONF, "stance/confidence inválidos")
    prods[product]["markets"][country.upper()] = dict(stance=stance, reason=reason, confidence=confidence,
                                                      updated=date.today().isoformat())
    _save("products.json", prods)


def set_costs(product, cost, ship, basis, country=None, **extra):
    """Costes unitarios (EUR). basis: 'confirmado' o 'estimado' (dejar claro de dónde salen)."""
    prods = _load("products.json", {})
    _need(product in prods, f"producto desconocido: {product}")
    _need(basis in ("confirmado", "estimado"), "basis: confirmado|estimado")
    prods[product]["costs"] = dict(cost_eur=cost, ship_eur=ship, basis=basis, **extra)
    _save("products.json", prods)


def economics(price_gross, cost, ship, country, return_rate=0.08, pay_pct=0.029, pay_fixed=0.30,
              return_loss=0.5, target_margin=0.15):
    """Contribución por pedido antes de publicidad. Todo en EUR; price_gross incluye IVA.
    Devoluciones: se pierde el ingreso neto y la fracción `return_loss` de coste+envío."""
    vat = VAT.get(country.upper())
    _need(vat is not None, f"sin tipo de IVA de referencia para {country}")
    net = price_gross / (1 + vat)
    fee = price_gross * pay_pct + pay_fixed
    ret = return_rate * (net + return_loss * (cost + ship))
    contrib = net - cost - ship - fee - ret
    return dict(country=country.upper(), price_gross=round(price_gross, 2), vat=vat, net=round(net, 2),
                fee=round(fee, 2), returns=round(ret, 2), contribution_pre_ads=round(contrib, 2),
                breakeven_cpa=round(contrib, 2),
                max_cpa_for_target=round(contrib - target_margin * net, 2),
                roas_breakeven=round(price_gross / contrib, 2) if contrib > 0 else None)


def combos():
    """Una fila por producto-país con estado de evidencia. Sin puntuación opaca: orden explícito."""
    prods, evs, rows = _load("products.json", {}), _evidence(), []
    for pid, p in prods.items():
        if p.get("status") == "descartado":
            continue
        for cc, m in p["markets"].items():
            e = [x for x in evs if x["product"] == pid and x["country"] in (cc, "")]
            n = {k: sum(1 for x in e if x["kind"] == k) for k in KINDS}
            row = dict(product=pid, name=p["name"], country=cc, stance=m["stance"], confidence=m["confidence"],
                       verificado=n["VERIFICADO"], estimacion=n["ESTIMACION"], hipotesis=n["HIPOTESIS"],
                       costs_basis=p.get("costs", {}).get("basis", "sin datos"), breakeven_cpa=None, reason=m["reason"])
            c, lo = p.get("costs"), p.get("price_observed_eur")
            if c and lo:
                price = sum(lo) / 2
                row["breakeven_cpa"] = economics(price, c["cost_eur"], c["ship_eur"], cc)["breakeven_cpa"]
            rows.append(row)
    so = {s: i for i, s in enumerate(STANCES)}
    co = {c: i for i, c in enumerate(CONF)}
    rows.sort(key=lambda r: (so[r["stance"]], co[r["confidence"]], -r["verificado"], -r["estimacion"],
                             -(r["breakeven_cpa"] if r["breakeven_cpa"] is not None else -999)))
    return rows


def check_access(timeout=8):
    res = {}
    for host in PROBES:
        try:
            urllib.request.urlopen(f"https://{host}", timeout=timeout)
            res[host] = "ok"
        except urllib.error.HTTPError as e:
            res[host] = "ok" if e.code < 400 else f"http {e.code}"
        except Exception as e:  # proxy 403 aparece como URLError/OSError
            res[host] = f"bloqueado ({str(e)[:60]})"
    out = {"checked": date.today().isoformat(), "hosts": res}
    _save("source_access.json", out)
    return out


def export():
    EXPORTS.mkdir(exist_ok=True)
    prods, evs, cb = _load("products.json", {}), _evidence(), combos()
    (EXPORTS / "products.json").write_text(json.dumps(prods, ensure_ascii=False, indent=2) + "\n")
    for name, rows in (("evidence.csv", evs), ("combos.csv", cb)):
        with open(EXPORTS / name, "w", newline="") as f:
            if rows:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader(); w.writerows(rows)
    return EXPORTS


def report(only=None):
    prods, evs, cb = _load("products.json", {}), _evidence(), combos()
    acc = _load("source_access.json", {})
    L = [f"# Informe S6 — {date.today().isoformat()}", ""]
    if acc:
        bl = [h for h, s in acc["hosts"].items() if s != "ok"]
        L += [f"> Fuentes bloqueadas en la última comprobación ({acc['checked']}): {', '.join(bl) or 'ninguna'}. "
              "Lo que dependa de ellas está marcado como no verificado.", ""]
    L += ["## Ranking producto-país", "",
          "Orden: postura → confianza → nº de evidencias verificadas → estimaciones → CPA de equilibrio. "
          "No hay puntuación global.", "",
          "| Producto | País | Postura | Conf. | Verif. | Estim. | Hipót. | Costes | CPA equilibrio € | Motivo |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in cb:
        if only and r["product"] != only:
            continue
        L.append(f"| {r['name']} | {r['country']} | {r['stance']} | {r['confidence']} | {r['verificado']} | "
                 f"{r['estimacion']} | {r['hipotesis']} | {r['costs_basis']} | "
                 f"{'' if r['breakeven_cpa'] is None else r['breakeven_cpa']} | {r['reason']} |")
    for pid, p in prods.items():
        if only and pid != only:
            continue
        L += ["", f"## {p['name']} ({p['status']})", "", f"- Tipo: {p.get('type')} · Categoría: {p.get('category')}",
              f"- Necesidad: {p.get('need')}", f"- Precio observado €: {p.get('price_observed_eur', 'sin datos')}"]
        if p.get("costs"):
            L.append(f"- Costes ({p['costs']['basis']}): {p['costs']}")
        if p.get("discard_reason"):
            L.append(f"- Descartado: {p['discard_reason']}")
        if p.get("risks"):
            L.append("- Riesgos: " + "; ".join(p["risks"]))
        for k in KINDS:
            es = [e for e in evs if e["product"] == pid and e["kind"] == k]
            if es:
                L += ["", f"**{k}**"]
                for e in es:
                    src = f"[{e['source_name'] or e['source_url']}]({e['source_url']})" if e["source_url"] else "sin fuente"
                    L.append(f"- {e['claim']} — {e['country'] or 'global'}, {src}, fecha fuente {e['source_date'] or 'n/d'}, "
                             f"confianza {e['confidence']}, fuente {e['source_type']}")
    REPORTS.mkdir(exist_ok=True)
    path = REPORTS / f"{date.today().isoformat()}_{only or 'general'}.md"
    path.write_text("\n".join(L) + "\n")
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(prog="s6")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("--offline", action="store_true")
    s = sub.add_parser("add-product")
    for a in ("id", "name", "category", "type", "need"): s.add_argument("--" + a, required=True)
    s.add_argument("--price-lo", type=float); s.add_argument("--price-hi", type=float)
    s = sub.add_parser("evidence")
    s.add_argument("--product", required=True); s.add_argument("--claim", required=True)
    s.add_argument("--kind", required=True); s.add_argument("--source-type", default="secundario")
    s.add_argument("--confidence", required=True)
    for a in ("source-url", "source-name", "source-date", "country", "metric"): s.add_argument("--" + a, default="")
    s = sub.add_parser("market")
    for a in ("product", "country", "stance", "reason", "confidence"): s.add_argument("--" + a, required=True)
    s = sub.add_parser("costs")
    s.add_argument("--product", required=True); s.add_argument("--cost", type=float, required=True)
    s.add_argument("--ship", type=float, required=True); s.add_argument("--basis", required=True)
    s.add_argument("--supplier", default="")
    s = sub.add_parser("economics")
    s.add_argument("--price", type=float, required=True); s.add_argument("--cost", type=float, required=True)
    s.add_argument("--ship", type=float, required=True); s.add_argument("--countries", default="ES,DE,FR,IT,PT,PL,RO,BG,HR,GR")
    s.add_argument("--return-rate", type=float, default=0.08)
    s = sub.add_parser("discard"); s.add_argument("--product", required=True); s.add_argument("--reason", required=True)
    sub.add_parser("rank")
    s = sub.add_parser("report"); s.add_argument("--product")
    sub.add_parser("export")
    a = ap.parse_args(argv)

    if a.cmd == "status":
        if a.offline: print(json.dumps(_load("source_access.json", {}), indent=2, ensure_ascii=False))
        else: print(json.dumps(check_access(), indent=2, ensure_ascii=False))
    elif a.cmd == "add-product":
        add_product(a.id, a.name, a.category, a.type, a.need, a.price_lo, a.price_hi); print("ok", a.id)
    elif a.cmd == "evidence":
        print("ok evidencia", add_evidence(a.product, a.claim, a.kind, a.source_type, a.confidence, a.source_url,
                                          a.source_name, a.source_date, a.country, a.metric)["id"])
    elif a.cmd == "market":
        set_market(a.product, a.country, a.stance, a.reason, a.confidence); print("ok")
    elif a.cmd == "costs":
        set_costs(a.product, a.cost, a.ship, a.basis, supplier=a.supplier); print("ok")
    elif a.cmd == "economics":
        for cc in a.countries.split(","):
            print(economics(a.price, a.cost, a.ship, cc, a.return_rate))
    elif a.cmd == "discard":
        prods = _load("products.json", {}); _need(a.product in prods, "producto desconocido")
        prods[a.product].update(status="descartado", discard_reason=a.reason); _save("products.json", prods); print("ok")
    elif a.cmd == "rank":
        for r in combos(): print(r)
    elif a.cmd == "report": print(report(a.product))
    elif a.cmd == "export": print(export())


if __name__ == "__main__":
    main()
