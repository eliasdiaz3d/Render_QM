#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import ast
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional

SKIP_DIRS = {
    ".git", "__pycache__", "venv", ".venv", "node_modules",
    "dist", "build", "site-packages", ".mypy_cache", ".pytest_cache",
    ".idea", ".vscode", ".tox", ".eggs", "egg-info"
}

REQ_FILES = [
    "requirements.txt",
    os.path.join("backend", "requirements.txt")
]

DOCKER_FILES = ["docker-compose.yml", os.path.join("backend", "docker-compose.yml"), "Dockerfile", os.path.join("backend", "Dockerfile")]
ALEMBIC_FILES = ["alembic.ini", os.path.join("backend", "alembic.ini")]
POSSIBLE_ENTRYPOINTS = [
    "main.py", "app/main.py",
    "backend/main.py", "backend/app/main.py", "backend/app/main_working.py",
    "install_render_node.py", os.path.join("backend", "scripts", "setup_master.py"),
    os.path.join("backend", "scripts", "setup_node.py"), os.path.join("backend", "scripts", "migrate_db.py"),
]
FASTAPI_HINTS = [
    re.compile(r"\bfrom\s+fastapi\s+import\b"),
    re.compile(r"\bimport\s+fastapi\b"),
    re.compile(r"\bAPIRouter\b"),
]
BLENDER_HINTS = [
    re.compile(r"\bimport\s+bpy\b"),
    re.compile(r"\bfrom\s+bpy"),
]
ENV_HINTS = [
    re.compile(r"os\.getenv\(\s*[\"']([^\"']+)[\"']"),
    re.compile(r"environ\[\s*[\"']([^\"']+)[\"']\s*\]"),
]
SETTINGS_HINTS = [
    # Pydantic Settings fields like `MY_VAR: str = Field(default=...)`
    re.compile(r"class\s+\w+\(.*BaseSettings.*\):"),
]
SQLALCHEMY_HINTS = [
    re.compile(r"\bimport\s+sqlalchemy\b"),
    re.compile(r"\bfrom\s+sqlalchemy\s+import\b"),
]
UVICORN_HINTS = [
    re.compile(r"\bimport\s+uvicorn\b"),
    re.compile(r"\buvicorn\.run\("),
]
QUEUE_RENDER_HINTS = [
    re.compile(r"\bqueue\b"),
    re.compile(r"\brender\b"),
    re.compile(r"\bblender\b", re.IGNORECASE),
]

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def parse_requirements(text: str) -> List[str]:
    reqs = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # remove hash/pin extras
        line = re.split(r"\s+#", line)[0]
        reqs.append(line)
    return reqs

def list_python_files(root: Path) -> List[Path]:
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # prune skip dirs
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".py"):
                files.append(Path(dirpath) / fn)
    return files

def safe_parse_ast(code: str) -> Optional[ast.AST]:
    try:
        return ast.parse(code)
    except Exception:
        return None

def collect_imports(py_files: List[Path]) -> Tuple[Counter, Dict[str, Set[str]]]:
    """
    Returns:
      - Counter of top-level modules imported.
      - Mapping module -> set(files) where it appears.
    """
    mod_counter = Counter()
    mod_files: Dict[str, Set[str]] = defaultdict(set)
    for f in py_files:
        code = read_text(f)
        tree = safe_parse_ast(code)
        if not tree:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    mod_counter[top] += 1
                    mod_files[top].add(str(f))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top = node.module.split(".")[0]
                    mod_counter[top] += 1
                    mod_files[top].add(str(f))
    return mod_counter, mod_files

def grep_patterns(py_files: List[Path], patterns: List[re.Pattern]) -> Dict[str, List[str]]:
    hits = defaultdict(list)
    for f in py_files:
        text = read_text(f)
        for pat in patterns:
            if pat.search(text):
                hits[pat.pattern].append(str(f))
    return hits

def find_env_vars(py_files: List[Path]) -> Set[str]:
    vars_found = set()
    for f in py_files:
        text = read_text(f)
        for pat in ENV_HINTS:
            for m in pat.finditer(text):
                vars_found.add(m.group(1))
    return vars_found

def find_fastapi_routes(py_files: List[Path]) -> Dict[str, List[str]]:
    """
    Heurística: encuentra APIRouter y rutas via .get/ .post / .put / .delete.
    """
    routes = defaultdict(list)
    route_regex = re.compile(r'@(?:router|app)\.(get|post|put|patch|delete)\(\s*[\"\\\']([^\"\\\']+)')
    for f in py_files:
        text = read_text(f)
        for m in route_regex.finditer(text):
            method, path = m.group(1).upper(), m.group(2)
            routes[str(f)].append(f"{method} {path}")
    return routes

def detect_files(root: Path, candidates: List[str]) -> List[str]:
    found = []
    for c in candidates:
        p = root / c
        if p.exists():
            found.append(c)
    return found

def short_rel(root: Path, p: Path) -> str:
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)

def summarize_structure(root: Path) -> Dict[str, List[str]]:
    """
    Lista carpetas de primer nivel y algunos submódulos comunes.
    """
    def list_dir(d: Path):
        return sorted([x.name for x in d.iterdir() if x.is_dir()])

    summary = {}
    if root.exists():
        top_dirs = [x for x in root.iterdir() if x.is_dir()]
        summary["top_level_dirs"] = sorted([x.name for x in top_dirs])
        # detectar subcarpetas clave
        for key in ["app", "backend", "blender_addon", "frontend", "scripts", "deploy", "docs", "config"]:
            d = root / key
            if d.exists() and d.is_dir():
                summary[key] = list_dir(d)
    return summary

def read_project_name(root: Path) -> str:
    # intenta README o setup.py
    readme = None
    for name in ("README.md", "readme.md", "README", "README.rst"):
        p = root / name
        if p.exists():
            readme = read_text(p)
            break
    if readme:
        m = re.search(r"#+\s+(.+)", readme)
        if m:
            return m.group(1).strip()
    setup = root / "setup.py"
    if setup.exists():
        text = read_text(setup)
        m = re.search(r"name\s*=\s*[\"']([^\"']+)[\"']", text)
        if m:
            return m.group(1).strip()
    return root.name

def collect_entrypoints(root: Path) -> List[str]:
    found = []
    for rel in POSSIBLE_ENTRYPOINTS:
        if (root / rel).exists():
            found.append(rel)
    # además, cualquier .py en scripts/ y backend/scripts/
    for extra_dir in ["scripts", os.path.join("backend", "scripts")]:
        p = root / extra_dir
        if p.exists():
            for py in sorted(p.rglob("*.py")):
                found.append(short_rel(root, py))
    return sorted(set(found))

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Resumen estático de un proyecto Python (librerías, dependencias, endpoints, etc.)")
    parser.add_argument("path", nargs="?", default=".", help="Ruta al proyecto (default: .)")
    parser.add_argument("--max-imports", type=int, default=50, help="Máximo de módulos importados a mostrar")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    py_files = list_python_files(root)

    # Estructura
    structure = summarize_structure(root)
    project_name = read_project_name(root)

    # Requisitos
    requirements: List[str] = []
    for rf in REQ_FILES:
        p = root / rf
        if p.exists():
            requirements += parse_requirements(read_text(p))
    requirements = sorted(set(requirements))

    # Imports reales
    mod_counter, mod_files = collect_imports(py_files)
    most_common_imports = mod_counter.most_common(args.max_imports)

    # Heurísticas por stack
    has_docker = detect_files(root, DOCKER_FILES)
    has_alembic = detect_files(root, ALEMBIC_FILES)
    entrypoints = collect_entrypoints(root)

    # Detecciones por regex
    fastapi_hits = grep_patterns(py_files, FASTAPI_HINTS)
    blender_hits = grep_patterns(py_files, BLENDER_HINTS)
    sqlalchemy_hits = grep_patterns(py_files, SQLALCHEMY_HINTS)
    uvicorn_hits = grep_patterns(py_files, UVICORN_HINTS)
    queue_render_hits = grep_patterns(py_files, QUEUE_RENDER_HINTS)
    env_vars = sorted(find_env_vars(py_files))
    routes = find_fastapi_routes(py_files)

    # Archivos .env / DB
    env_files = [short_rel(root, p) for p in root.rglob(".env")]
    sqlite_dbs = [short_rel(root, p) for p in root.rglob("*.db")]

    # Resultado consolidado
    summary = {
        "project_name": project_name,
        "root": str(root),
        "python_files_count": len(py_files),
        "structure": structure,
        "requirements": requirements,
        "imports_top": [{"module": m, "count": c} for m, c in most_common_imports],
        "docker": has_docker,
        "alembic": has_alembic,
        "entrypoints": entrypoints,
        "fastapi_detected": bool(fastapi_hits),
        "sqlalchemy_detected": bool(sqlalchemy_hits),
        "pydantic_detected": any(m for m in most_common_imports if m[0] in {"pydantic", "pydantic_settings"}),
        "uvicorn_detected": bool(uvicorn_hits),
        "blender_bpy_detected": bool(blender_hits),
        "render_queue_hints": any(v for v in queue_render_hits.values()),
        "env_files": env_files,
        "env_vars_referenced": env_vars,
        "sqlite_databases": sqlite_dbs,
        "fastapi_routes": routes,  # archivo -> ["GET /x", ...]
        "module_occurrences": {k: sorted(v) for k, v in mod_files.items()},
    }

    # Imprime resumen humano + guarda JSON/Markdown
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    out_json = root / "project_summary.json"
    out_md = root / "project_summary.md"

    with out_json.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Markdown corto y útil
    md = []
    md.append(f"# Resumen del proyecto: {project_name}")
    md.append("")
    md.append(f"- Ruta: `{root}`")
    md.append(f"- Archivos .py: **{len(py_files)}**")
    md.append("")
    if structure.get("top_level_dirs"):
        md.append("## Estructura (primer nivel)")
        md.append(", ".join(f"`{d}`" for d in structure["top_level_dirs"]))
        md.append("")
    if requirements:
        md.append("## Dependencias (requirements)")
        for r in requirements:
            md.append(f"- {r}")
        md.append("")
    if most_common_imports:
        md.append("## Imports más comunes")
        for m, c in most_common_imports[:25]:
            md.append(f"- {m}: {c}")
        md.append("")
    md.append("## Stack detectado")
    md.append(f"- FastAPI: {'sí' if summary['fastapi_detected'] else 'no'}")
    md.append(f"- SQLAlchemy: {'sí' if summary['sqlalchemy_detected'] else 'no'}")
    md.append(f"- Pydantic: {'sí' if summary['pydantic_detected'] else 'no'}")
    md.append(f"- Uvicorn: {'sí' if summary['uvicorn_detected'] else 'no'}")
    md.append(f"- Blender (bpy): {'sí' if summary['blender_bpy_detected'] else 'no'}")
    if has_docker:
        md.append(f"- Docker: sí ({', '.join(has_docker)})")
    if has_alembic:
        md.append(f"- Alembic: sí ({', '.join(has_alembic)})")
    md.append("")
    if entrypoints:
        md.append("## Posibles entrypoints / scripts")
        for e in entrypoints:
            md.append(f"- `{e}`")
        md.append("")
    if env_files or env_vars:
        md.append("## Variables de entorno")
        if env_files:
            md.append(f"- Archivos .env: {', '.join(env_files)}")
        if env_vars:
            md.append("- Nombres referenciados:")
            for v in env_vars:
                md.append(f"  - `{v}`")
        md.append("")
    if routes:
        md.append("## Endpoints detectados (heurístico)")
        total = 0
        for fpath, rts in routes.items():
            if not rts: 
                continue
            md.append(f"- **{fpath}**")
            for r in rts:
                md.append(f"  - {r}")
                total += 1
        if total == 0:
            md.append("_No se encontraron decoradores típicos de rutas._")
        md.append("")
    if sqlite_dbs:
        md.append("## Bases de datos SQLite encontradas")
        for db in sqlite_dbs:
            md.append(f"- `{db}`")
        md.append("")

    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"\n✅ Guardados:\n- {out_json}\n- {out_md}")

if __name__ == "__main__":
    main()
