#!/usr/bin/env python3
"""Maintenance tool for this repository of Spec Kit extensions, presets, workflows and steps.

Run with ``uv run scripts/repo.py <command>``:

    new {extension,preset,workflow,step} <id>
                                         scaffold a new item from templates/
    validate [ITEM_DIR ...]              validate items with Spec Kit's own validators
    catalog [--check]                    regenerate (or verify) every catalog.json
    package <id or kind/id> [-o DIR]     build an extension's or preset's release zip
    release [--dry-run]                  tag + publish a GitHub release for every
                                         catalog version that has no tag yet
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = tomllib.loads((ROOT / "repo.toml").read_text(encoding="utf-8"))["repo"]
GITHUB = CONFIG["github"]

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# Files that ship in the repo for humans but are not part of a step package.
STEP_DOC_FILES = {"README.md", "CHANGELOG.md"}
IGNORED_PARTS = {"__pycache__", ".DS_Store"}

KINDS = {
    # kind: (directory, manifest file, catalog collection key)
    "extension": ("extensions", "extension.yml", "extensions"),
    "preset": ("presets", "preset.yml", "presets"),
    "workflow": ("workflows", "workflow.yml", "workflows"),
    "step": ("steps", "step.yml", "steps"),
}


class RepoError(Exception):
    pass


# ---------------------------------------------------------------------------
# Item discovery
# ---------------------------------------------------------------------------


@dataclass
class Item:
    kind: str
    id: str
    path: Path
    manifest: dict[str, Any]

    @property
    def meta(self) -> dict[str, Any]:
        """The id/name/version/... block of the manifest."""
        block = self.manifest.get(self.kind)
        return block if isinstance(block, dict) else {}

    @property
    def version(self) -> str:
        return str(self.meta.get("version", ""))

    @property
    def tag(self) -> str:
        return f"{self.kind}-{self.id}-v{self.version}"

    @property
    def rel(self) -> str:
        return self.path.relative_to(ROOT).as_posix()


def load_item(path: Path) -> Item:
    path = path.resolve()
    for kind, (dirname, manifest_name, _) in KINDS.items():
        if path.parent == ROOT / dirname:
            manifest_path = path / manifest_name
            if not manifest_path.is_file():
                raise RepoError(f"{path.relative_to(ROOT)}: missing {manifest_name}")
            data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise RepoError(f"{manifest_path.relative_to(ROOT)}: must be a YAML mapping")
            return Item(kind, path.name, path, data)
    raise RepoError(f"{path}: not an item directory (expected extensions/<id>, presets/<id>, workflows/<id> or steps/<id>)")


def discover(kind: str | None = None) -> list[Item]:
    items = []
    for k, (dirname, _, _) in KINDS.items():
        if kind and k != kind:
            continue
        base = ROOT / dirname
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir() and child.name not in IGNORED_PARTS and not child.name.startswith("."):
                items.append(load_item(child))
    return items


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=check)


def in_git() -> bool:
    return git("rev-parse", "--is-inside-work-tree", check=False).returncode == 0


def tag_exists(tag: str) -> bool:
    return git("rev-parse", "-q", "--verify", f"refs/tags/{tag}", check=False).returncode == 0


def item_files(item: Item) -> list[Path]:
    """Files that make up an item: tracked + untracked-but-not-ignored, sorted.

    Using git's view keeps local catalog builds identical to CI builds.
    """
    if in_git():
        out = git("ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", item.rel).stdout
        files = [ROOT / p for p in out.split("\0") if p]
        files = [f for f in files if f.is_file()]  # drop deleted-but-staged
    else:
        files = [p for p in item.path.rglob("*") if p.is_file()]
    files = [f for f in files if not (set(f.relative_to(item.path).parts) & IGNORED_PARTS)]
    return sorted(files, key=lambda p: p.relative_to(item.path).as_posix())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Spec Kit imports (lazy: only `validate` needs them)
# ---------------------------------------------------------------------------


def speckit():
    try:
        import specify_cli  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise RepoError("specify-cli is not importable; run via `uv run scripts/repo.py ...`") from exc
    from specify_cli.extensions import ExtensionManifest, ValidationError
    from specify_cli.presets import PresetManifest, PresetValidationError
    from specify_cli.workflows import STEP_REGISTRY, load_custom_steps
    from specify_cli.workflows.base import StepBase
    from specify_cli.workflows.engine import WorkflowDefinition, validate_workflow
    from specify_cli.workflows.step.installer import StepInstallError, validate_step_package

    return locals()


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


def _common_checks(item: Item) -> list[str]:
    errors = []
    if not ID_RE.match(item.id):
        errors.append(f"directory name {item.id!r} must be lowercase kebab-case")
    meta = item.meta
    declared = meta.get("type_key" if item.kind == "step" else "id")
    if declared != item.id:
        errors.append(f"manifest id {declared!r} must match directory name {item.id!r}")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", item.version):
        errors.append(f"version {item.version!r} must be semver (X.Y.Z)")
    if not (item.path / "README.md").is_file():
        errors.append("missing README.md")
    if in_git() and item.version and tag_exists(item.tag):
        diff = git("diff", "--quiet", item.tag, "--", item.rel, check=False)
        untracked = git("ls-files", "--others", "--exclude-standard", "--", item.rel).stdout.strip()
        if diff.returncode != 0 or untracked:
            errors.append(f"content changed since release {item.tag}; bump the version")
    return errors


def validate_extension(item: Item, sk: dict[str, Any]) -> list[str]:
    errors = _common_checks(item)
    try:
        manifest = sk["ExtensionManifest"](item.path / "extension.yml")
    except sk["ValidationError"] as exc:
        return errors + [str(exc)]
    for section in ("commands", "templates", "scripts"):
        for entry in getattr(manifest, section):
            rel = entry.get("file") if isinstance(entry, dict) else None
            if rel and not (item.path / rel).is_file():
                errors.append(f"provides.{section}: file not found: {rel}")
    for entry in manifest.config:
        rel = entry.get("template") if isinstance(entry, dict) else None
        if rel and not (item.path / rel).is_file():
            errors.append(f"provides.config: template not found: {rel}")
    return errors


# Placeholder a `wrap` contribution must contain, by contribution type.
WRAP_PLACEHOLDERS = {"template": "{CORE_TEMPLATE}", "command": "{CORE_TEMPLATE}", "script": "$CORE_SCRIPT"}


def validate_preset(item: Item, sk: dict[str, Any]) -> list[str]:
    errors = _common_checks(item)
    try:
        sk["PresetManifest"](item.path / "preset.yml")
    except sk["PresetValidationError"] as exc:
        return errors + [str(exc)]
    for entry in (item.manifest.get("provides") or {}).get("templates") or []:
        rel, kind = entry.get("file"), entry.get("type")
        strategy = str(entry.get("strategy", "replace")).lower()
        f = item.path / rel if rel else None
        if not f or not f.is_file():
            errors.append(f"provides.templates: file not found: {rel}")
            continue
        if strategy == "wrap" and WRAP_PLACEHOLDERS.get(kind, "") not in f.read_text(encoding="utf-8"):
            errors.append(f"{rel}: strategy 'wrap' needs the {WRAP_PLACEHOLDERS.get(kind)} placeholder")
        if kind == "script" and strategy in ("prepend", "append"):
            errors.append(f"{rel}: scripts support only 'replace' and 'wrap'")
    return errors


def _import_step_class(item: Item, sk: dict[str, Any]) -> tuple[type | None, str | None]:
    name = f"_repo_check_step_{item.id.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(
        name, item.path / "__init__.py", submodule_search_locations=[str(item.path)]
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - report any import failure
        return None, f"__init__.py failed to import: {type(exc).__name__}: {exc}"
    finally:
        for key in [k for k in sys.modules if k == name or k.startswith(name + ".")]:
            sys.modules.pop(key, None)
    for attr in vars(module).values():
        if (
            isinstance(attr, type)
            and issubclass(attr, sk["StepBase"])
            and attr is not sk["StepBase"]
            and getattr(attr, "type_key", "") == item.id
        ):
            return attr, None
    return None, f"__init__.py defines no StepBase subclass with type_key = {item.id!r}"


def validate_step(item: Item, sk: dict[str, Any]) -> list[str]:
    errors = _common_checks(item)
    try:
        sk["validate_step_package"](item.path, item.id)
    except sk["StepInstallError"] as exc:
        return errors + [str(exc)]
    if item.id in sk["STEP_REGISTRY"] and item.id not in _custom_loaded:
        errors.append(f"type_key {item.id!r} collides with a built-in step type")
    cls, err = _import_step_class(item, sk)
    if err:
        errors.append(err)
    return errors


_custom_loaded: set[str] = set()


def load_repo_steps(sk: dict[str, Any], steps: list[Item]) -> Path:
    """Install this repo's steps into a scratch project so workflows can use them."""
    tmp = Path(tempfile.mkdtemp(prefix="speckit-repo-"))
    target = tmp / ".specify" / "workflows" / "steps"
    target.mkdir(parents=True)
    for step in steps:
        shutil.copytree(step.path, target / step.id, ignore=shutil.ignore_patterns(*IGNORED_PARTS))
    _custom_loaded.update(sk["load_custom_steps"](tmp))
    return tmp


def validate_workflow(item: Item, sk: dict[str, Any]) -> list[str]:
    errors = _common_checks(item)
    # Catalog installs fetch workflow.yml by raw URL; sibling files never arrive.
    allowed = {"workflow.yml"} | STEP_DOC_FILES
    extra = [f.relative_to(item.path).as_posix() for f in item_files(item)]
    extra = [f for f in extra if f not in allowed]
    if extra:
        errors.append(
            "only workflow.yml, README.md and CHANGELOG.md are allowed (catalog installs "
            f"don't fetch other files): {', '.join(extra)}"
        )
    try:
        definition = sk["WorkflowDefinition"].from_yaml(item.path / "workflow.yml")
    except Exception as exc:  # noqa: BLE001
        return errors + [f"workflow.yml: {exc}"]
    return errors + sk["validate_workflow"](definition)


VALIDATORS = {
    "extension": validate_extension,
    "preset": validate_preset,
    "workflow": validate_workflow,
    "step": validate_step,
}
# Kinds released as a zip attached to the GitHub release.
ZIPPED_KINDS = {"extension", "preset"}


def cmd_validate(args: argparse.Namespace) -> int:
    sk = speckit()
    items = [load_item(Path(p)) for p in args.paths] if args.paths else discover()
    # Steps are validated (and loaded) first so workflows may use them.
    items.sort(key=lambda i: ["step", "extension", "preset", "workflow"].index(i.kind))
    scratch = load_repo_steps(sk, discover("step"))
    failed = 0
    try:
        for item in items:
            errors = VALIDATORS[item.kind](item, sk)
            if errors:
                failed += 1
                print(f"FAIL {item.rel}")
                for e in errors:
                    print(f"     - {e}")
            else:
                print(f"ok   {item.rel} ({item.version})")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    if not items:
        print("nothing to validate")
    return 1 if failed else 0


# ---------------------------------------------------------------------------
# package
# ---------------------------------------------------------------------------


def build_zip(item: Item) -> bytes:
    """Byte-for-byte reproducible zip: sorted entries, fixed timestamps, stored."""
    import io

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        for f in item_files(item):
            info = zipfile.ZipInfo(f"{item.id}/{f.relative_to(item.path).as_posix()}", (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            mode = 0o755 if os.access(f, os.X_OK) else 0o644
            info.external_attr = (0o100000 | mode) << 16
            info.compress_type = zipfile.ZIP_STORED
            zf.writestr(info, f.read_bytes())
    return buf.getvalue()


def zip_name(item: Item) -> str:
    return f"{item.id}-{item.version}.zip"


def cmd_package(args: argparse.Namespace) -> int:
    if "/" in args.id:
        item = load_item(ROOT / args.id)
        if item.kind not in ZIPPED_KINDS:
            raise RepoError(f"{item.rel}: only extensions and presets are packaged")
    else:
        matches = [ROOT / KINDS[k][0] / args.id for k in sorted(ZIPPED_KINDS)]
        matches = [m for m in matches if m.is_dir()]
        if len(matches) != 1:
            hint = " (pass extensions/<id> or presets/<id>)" if matches else ""
            raise RepoError(f"expected one extension or preset named {args.id!r}, found {len(matches)}{hint}")
        item = load_item(matches[0])
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    data = build_zip(item)
    (out / zip_name(item)).write_bytes(data)
    print(f"{out / zip_name(item)}  sha256={sha256(data)}")
    return 0


# ---------------------------------------------------------------------------
# catalog
# ---------------------------------------------------------------------------


def _blob(tag: str, rel: str) -> str:
    return f"https://github.com/{GITHUB}/blob/{tag}/{rel}"


def _raw(tag: str, rel: str) -> str:
    return f"https://raw.githubusercontent.com/{GITHUB}/{tag}/{rel}"


def _docs(item: Item) -> dict[str, str]:
    out = {"repository": f"https://github.com/{GITHUB}"}
    out["documentation"] = _blob(item.tag, f"{item.rel}/README.md")
    if (item.path / "CHANGELOG.md").is_file():
        out["changelog"] = _blob(item.tag, f"{item.rel}/CHANGELOG.md")
    return out


def extension_entry(item: Item) -> dict[str, Any]:
    meta, m = item.meta, item.manifest
    provides = m.get("provides") or {}
    entry: dict[str, Any] = {
        "id": item.id,
        "name": meta.get("name", item.id),
        "description": meta.get("description", ""),
        "author": meta.get("author", CONFIG["author"]),
        "version": item.version,
        "download_url": f"https://github.com/{GITHUB}/releases/download/{item.tag}/{zip_name(item)}",
        "sha256": sha256(build_zip(item)),
        **_docs(item),
        "homepage": _blob(item.tag, item.rel),
        "license": meta.get("license", CONFIG["license"]),
    }
    for key in ("category", "effect"):
        if meta.get(key):
            entry[key] = meta[key]
    entry["requires"] = m.get("requires") or {}
    entry["provides"] = {
        k: len(v) for k, v in provides.items() if isinstance(v, list) and v
    }
    if m.get("hooks"):
        entry["provides"]["hooks"] = len(m["hooks"])
    entry["tags"] = list(m.get("tags") or [])
    return entry


def preset_entry(item: Item) -> dict[str, Any]:
    meta, m = item.meta, item.manifest
    contributions = (m.get("provides") or {}).get("templates") or []
    counts = {"templates": 0, "commands": 0, "scripts": 0}
    for c in contributions:
        key = {"template": "templates", "command": "commands", "script": "scripts"}.get(c.get("type"))
        if key:
            counts[key] += 1
    return {
        "id": item.id,
        "name": meta.get("name", item.id),
        "description": meta.get("description", ""),
        "author": meta.get("author", CONFIG["author"]),
        "version": item.version,
        "download_url": f"https://github.com/{GITHUB}/releases/download/{item.tag}/{zip_name(item)}",
        "sha256": sha256(build_zip(item)),
        **_docs(item),
        "homepage": _blob(item.tag, item.rel),
        "license": meta.get("license", CONFIG["license"]),
        "requires": m.get("requires") or {},
        "provides": counts,
        "tags": list(m.get("tags") or []),
    }


def workflow_entry(item: Item) -> dict[str, Any]:
    meta, m = item.meta, item.manifest
    wf_file = item.path / "workflow.yml"
    entry: dict[str, Any] = {
        "id": item.id,
        "name": meta.get("name", item.id),
        "description": meta.get("description", ""),
        "author": meta.get("author", CONFIG["author"]),
        "version": item.version,
        "url": _raw(item.tag, f"{item.rel}/workflow.yml"),
        "sha256": sha256(wf_file.read_bytes()),
        **_docs(item),
        "license": meta.get("license", CONFIG["license"]),
        "requires": m.get("requires") or {},
        "tags": list(meta.get("tags") or m.get("tags") or []),
    }
    return entry


def step_entry(item: Item) -> dict[str, Any]:
    meta = item.meta
    files = [f for f in item_files(item) if f.relative_to(item.path).as_posix() not in STEP_DOC_FILES]
    rels = {f.relative_to(item.path).as_posix(): f for f in files}
    extra = {r: _raw(item.tag, f"{item.rel}/{r}") for r in rels if r not in ("step.yml", "__init__.py")}
    entry: dict[str, Any] = {
        "id": item.id,
        "name": meta.get("name", item.id),
        "description": meta.get("description", ""),
        "author": meta.get("author", CONFIG["author"]),
        "version": item.version,
        "step_yml_url": _raw(item.tag, f"{item.rel}/step.yml"),
        "init_url": _raw(item.tag, f"{item.rel}/__init__.py"),
    }
    if extra:
        entry["extra_files"] = extra
    entry["sha256"] = {r: sha256(f.read_bytes()) for r, f in rels.items()}
    entry.update(_docs(item))
    entry["license"] = meta.get("license", CONFIG["license"])
    entry["tags"] = list(meta.get("tags") or [])
    return entry


ENTRY_BUILDERS = {
    "extension": extension_entry,
    "preset": preset_entry,
    "workflow": workflow_entry,
    "step": step_entry,
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_catalog(kind: str) -> tuple[Path, dict[str, Any]]:
    dirname, _, key = KINDS[kind]
    path = ROOT / dirname / "catalog.json"
    old = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    old_entries: dict[str, Any] = old.get(key) or {}
    now = _now()
    entries: dict[str, Any] = {}
    for item in discover(kind):
        entry = ENTRY_BUILDERS[kind](item)
        prev = old_entries.get(item.id)
        if prev:
            stripped = {k: v for k, v in prev.items() if k not in ("created_at", "updated_at")}
            unchanged = stripped == entry
            entry["created_at"] = prev.get("created_at", now)
            entry["updated_at"] = prev.get("updated_at", now) if unchanged else now
        else:
            entry["created_at"] = entry["updated_at"] = now
        entries[item.id] = entry
    catalog = {
        "schema_version": "1.0",
        "updated_at": old.get("updated_at", now) if entries == old_entries else now,
        "catalog_url": _raw("main", f"{dirname}/catalog.json"),
        key: entries,
    }
    return path, catalog


def dump(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def cmd_catalog(args: argparse.Namespace) -> int:
    stale = []
    for kind in KINDS:
        path, catalog = build_catalog(kind)
        text = dump(catalog)
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if text == current:
            continue
        if args.check:
            stale.append(path.relative_to(ROOT).as_posix())
        else:
            path.write_text(text, encoding="utf-8")
            print(f"updated {path.relative_to(ROOT)}")
    if stale:
        print("catalog out of date: " + ", ".join(stale))
        print("run `uv run scripts/repo.py catalog` and commit the result")
        return 1
    if args.check:
        print("catalogs up to date")
    return 0


# ---------------------------------------------------------------------------
# release
# ---------------------------------------------------------------------------


def is_prerelease(version: str) -> bool:
    """0.x versions and versions with a pre-release suffix (1.0.0-rc.1) aren't stable yet."""
    return version.startswith("0.") or "-" in version.split("+", 1)[0]


def draft_release_ids() -> dict[str, list[str]]:
    """Draft releases by tag name (drafts are listed only to users who can push)."""
    out = subprocess.run(
        ["gh", "api", "--paginate", "repos/{owner}/{repo}/releases",
         "--jq", '.[] | select(.draft) | "\\(.tag_name) \\(.id)"'],
        cwd=ROOT, text=True, capture_output=True, check=True,
    ).stdout
    drafts: dict[str, list[str]] = {}
    for line in out.splitlines():
        tag, _, release_id = line.rpartition(" ")
        drafts.setdefault(tag, []).append(release_id)
    return drafts


def cmd_release(args: argparse.Namespace) -> int:
    if not in_git():
        raise RepoError("release must run inside the git repository")
    head = git("rev-parse", "HEAD").stdout.strip()
    pending = [i for i in discover() if not tag_exists(i.tag)]
    if not pending:
        print("nothing to release")
        return 0
    drafts = draft_release_ids()
    with tempfile.TemporaryDirectory() as tmp:
        for item in pending:
            # A failed asset upload or publish leaves a draft without a tag; drop it so the
            # retry starts clean instead of piling up drafts.
            for draft_id in drafts.get(item.tag, []):
                delete = ["gh", "api", "-X", "DELETE", f"repos/{{owner}}/{{repo}}/releases/{draft_id}"]
                print(("would run: " if args.dry_run else "") + " ".join(delete))
                if not args.dry_run:
                    subprocess.run(delete, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
            title =f"{item.meta.get('name', item.id)} {item.version} ({item.kind})"
            notes = f"{item.kind.capitalize()} `{item.id}` version {item.version}.\n\nSee {item.rel}/CHANGELOG.md."
            cmd = ["gh", "release", "create", item.tag, "--target", head, "--title", title, "--notes", notes]
            if is_prerelease(item.version):
                cmd.append("--prerelease")
            if item.kind in ZIPPED_KINDS:
                asset = Path(tmp) / zip_name(item)
                asset.write_bytes(build_zip(item))
                cmd.append(str(asset))
            print(("would run: " if args.dry_run else "") + " ".join(cmd))
            if not args.dry_run:
                subprocess.run(cmd, cwd=ROOT, check=True)
    return 0


# ---------------------------------------------------------------------------
# new
# ---------------------------------------------------------------------------


def cmd_new(args: argparse.Namespace) -> int:
    if not ID_RE.match(args.id):
        raise RepoError(f"id {args.id!r} must be lowercase kebab-case")
    dirname = KINDS[args.kind][0]
    dest = ROOT / dirname / args.id
    if dest.exists():
        raise RepoError(f"{dest.relative_to(ROOT)} already exists")
    name = args.name or args.id.replace("-", " ").title()
    subs = {
        "__ID__": args.id,
        "__NAME__": name,
        "__DESCRIPTION__": args.description or f"TODO: describe {name}",
        "__AUTHOR__": CONFIG["author"],
        "__GITHUB__": GITHUB,
        "__LICENSE__": CONFIG["license"],
        "__SPECKIT_VERSION__": CONFIG["speckit_version"],
        "__CLASS__": "".join(p.capitalize() for p in args.id.split("-")),
    }

    def render(text: str) -> str:
        for k, v in subs.items():
            text = text.replace(k, v)
        return text

    src = ROOT / "templates" / args.kind
    for f in sorted(src.rglob("*")):
        if not f.is_file() or set(f.relative_to(src).parts) & IGNORED_PARTS:
            continue
        out = dest / render(f.relative_to(src).as_posix())
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(f.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"created {out.relative_to(ROOT)}")
    return 0


# ---------------------------------------------------------------------------


def main(argv: Iterable[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="repo.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("new", help="scaffold a new item")
    s.add_argument("kind", choices=list(KINDS))
    s.add_argument("id")
    s.add_argument("--name")
    s.add_argument("--description")
    s.set_defaults(func=cmd_new)

    s = sub.add_parser("validate", help="validate items")
    s.add_argument("paths", nargs="*", help="item directories (default: all)")
    s.set_defaults(func=cmd_validate)

    s = sub.add_parser("catalog", help="regenerate catalog.json files")
    s.add_argument("--check", action="store_true", help="fail if catalogs are stale instead of writing")
    s.set_defaults(func=cmd_catalog)

    s = sub.add_parser("package", help="build an extension or preset release zip")
    s.add_argument("id")
    s.add_argument("-o", "--output", default=str(ROOT / "dist"))
    s.set_defaults(func=cmd_package)

    s = sub.add_parser("release", help="publish GitHub releases for untagged versions")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=cmd_release)

    args = p.parse_args(list(argv) if argv is not None else None)
    try:
        return args.func(args)
    except RepoError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
