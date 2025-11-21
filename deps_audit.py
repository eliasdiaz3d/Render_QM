#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deps_audit.py — auditoría rápida de dependencias para Render_QM
- Lee project_summary.json y requirements.txt (raíz y backend/)
- Señala duplicados, versiones en conflicto, paquetes no usados/posibles faltantes
- Genera requirements.clean.txt sugerido
"""
import re, json, os, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(".").resolve()
REQ_FILES = ["requirements.txt", "backend/requirements.txt"]
SUMMARY_FILE = "project_summary.json"

def parse_req_line(line: str):
    line = line.strip()
    if not line or line.startswith("#"):
        return None, None
    line = re.split(r"\s+#", line)[0]
    # nombre[extra]==ver  | nombre==ver | nombre>=ver | nombre
    m = re.match(r"^([A-Za-z0-9_.\-]+)(?:\[.*?\])?(?:\s*([=<>!~]{1,2}.*))?$", line)
    if not m:
        return None, None
    return m.group(1).lower(), (m.group(2) or "").strip()

def read_requirements():
    items = defaultdict(list)  # name -> list of (file, spec)
    for rf in REQ_FILES:
        p = ROOT / rf
        if p.exists():
            for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                name, spec = parse_req_line(ln)
                if name:
                    items[name].append((rf, spec))
    return items

def load_summary():
    p = ROOT / SUMMARY_FILE
    if not p.exists():
        print(f"ERROR: No encuentro {SUMMARY_FILE}. Ejecuta primero summarize_project.py")
        sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8"))

def main():
    summary = load_summary()
    reqs = read_requirements()
    imports_top = {x["module"].lower(): x["count"] for x in summary.get("imports_top", [])}
    used_modules = set(imports_top.keys())

    report = {"conflicts": [], "duplicates": [], "unused": [], "maybe_missing": [], "clean": []}

    # Conflictos/duplicados
    for name, entries in reqs.items():
        specs = set(sp for _, sp in entries if sp)
        files = sorted(set(f for f, _ in entries))
        if len(entries) > 1:
            report["duplicates"].append({"package": name, "files": files, "specs": sorted(specs)})
        if len(specs) > 1:
            report["conflicts"].append({"package": name, "files": files, "specs": sorted(specs)})

    # No usados: paquete presente en reqs pero sin import (heurístico por top-level module)
    # Mapeo simple: nombre paquete ~ módulo. (No perfecto pero útil: pydantic->pydantic, websockets->websockets)
    for pkg in reqs.keys():
        if pkg not in used_modules:
            report["unused"].append(pkg)

    # Faltantes: importado pero no en reqs (descarta stdlib comunes)
    stdlib_like = {
        "os","sys","re","json","pathlib","subprocess","typing","asyncio","logging","time",
        "uuid","enum","csv","email","socket","traceback","tkinter","dataclasses","sqlite3",
        "glob","platform","io","hashlib","tempfile","collections","urllib","ast"
    }
    for mod in sorted(used_modules):
        if mod in stdlib_like: 
            continue
        if mod not in reqs:
            report["maybe_missing"].append(mod)

    # Sugerencia de archivo limpio (si hay conflictos, escoge la primera spec encontrada)
    clean_lines = []
    for name, entries in sorted(reqs.items()):
        # preferir una sola especificación; si hay duplicadas, toma la más "pinned" (==) si existe
        pinned = [sp for _, sp in entries if sp.startswith("==")]
        spec = pinned[0] if pinned else (entries[0][1] if entries and entries[0][1] else "")
        clean_lines.append(f"{name}{spec}")
    report["clean"] = clean_lines

    # Output
    print("\n=== Duplicados ===")
    for d in report["duplicates"]:
        print(f"- {d['package']} -> {', '.join(d['files'])} (specs: {', '.join(d['specs']) or 'sin versión'})")
    print("\n=== Conflictos de versión ===")
    for c in report["conflicts"]:
        print(f"- {c['package']} -> specs: {', '.join(c['specs'])}")
    print("\n=== No usados (posibles) ===")
    for u in sorted(report["unused"]):
        print(f"- {u}")
    print("\n=== Posibles faltantes (importado pero no en requirements) ===")
    for m in sorted(report["maybe_missing"]):
        print(f"- {m}")

    out = ROOT / "requirements.clean.txt"
    out.write_text("\n".join(report["clean"]) + "\n", encoding="utf-8")
    print(f"\n✅ Generado: {out}")

if __name__ == "__main__":
    main()
