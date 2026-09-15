#!/usr/bin/env python3
"""Rewrite dependency versions in CrownOS manifests to match crown-versions.toml.

    sync-versions.py --all <parent-dir> [--dry-run]

Only the version field is touched. Features, default-features, optional and
every other key are left exactly as they are, and formatting elsewhere in the
file is untouched -- this edits lines, it does not round-trip the TOML.

Entries in [exceptions] are skipped. Run check-versions.py afterwards.
"""
import argparse, pathlib, re, sys, tomllib

HERE = pathlib.Path(__file__).resolve().parent.parent
SPEC = tomllib.load((HERE / "crown-versions.toml").open("rb"))
PINNED = {**SPEC["crownos"], **SPEC["dependencies"]}
EXCEPTIONS = SPEC.get("exceptions", {})

TABLE_RE = re.compile(r'^\[(dependencies|dev-dependencies|workspace\.dependencies)\]\s*$')
ANY_TABLE_RE = re.compile(r'^\[')


def repo_name(repo: pathlib.Path) -> str:
    if repo.name == "main" and repo.parent.name.endswith(".git"):
        return repo.parent.name[:-4]
    return repo.name[:-4] if repo.name.endswith(".git") else repo.name


def sync(manifest: pathlib.Path, name: str, dry: bool):
    lines = manifest.read_text().splitlines(keepends=True)
    out, in_deps, changes = [], False, []
    for line in lines:
        if TABLE_RE.match(line):
            in_deps = True; out.append(line); continue
        if ANY_TABLE_RE.match(line) and not TABLE_RE.match(line):
            in_deps = False; out.append(line); continue
        if not in_deps or not line.strip() or line.lstrip().startswith("#"):
            out.append(line); continue

        m = re.match(r'^(\s*)([A-Za-z0-9_-]+)\s*=\s*(.*)$', line.rstrip("\n"))
        if not m:
            out.append(line); continue
        indent, dep, rhs = m.groups()
        want = PINNED.get(dep)
        if want is None or f"{name}.{dep}" in EXCEPTIONS:
            out.append(line); continue

        if rhs.startswith('"'):                       # dep = "1.0"
            got = rhs.strip().strip('"')
            if got != want:
                changes.append((dep, got, want))
                line = f'{indent}{dep} = "{want}"\n'
        elif rhs.startswith("{"):                     # dep = { version = "1.0", ... }
            vm = re.search(r'version\s*=\s*"([^"]+)"', rhs)
            if vm and vm.group(1) != want:
                changes.append((dep, vm.group(1), want))
                new_rhs = rhs[:vm.start(1)] + want + rhs[vm.end(1):]
                line = f'{indent}{dep} = {new_rhs}\n'
        out.append(line)

    if changes and not dry:
        manifest.write_text("".join(out))
    return changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", metavar="DIR", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    parent = pathlib.Path(a.all)
    repos = [p for p in sorted(parent.iterdir()) if (p / "Cargo.toml").exists()]
    repos += [p / "main" for p in sorted(parent.glob("*.git"))
              if (p / "main" / "Cargo.toml").exists()]

    total = 0
    for repo in repos:
        name = repo_name(repo)
        for manifest in [repo / "Cargo.toml", *sorted(repo.glob("*/Cargo.toml"))]:
            if not manifest.exists():
                continue
            for dep, got, want in sync(manifest, name, a.dry_run):
                print(f"  {name}: {dep} {got} -> {want}")
                total += 1
    print(("would change " if a.dry_run else "changed ") + f"{total} declarations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
