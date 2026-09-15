#!/usr/bin/env python3
"""Fail if a repo's Cargo.toml disagrees with crown-versions.toml.

Usage:
    check-versions.py <repo-dir> [<repo-dir> ...]
    check-versions.py --all <parent-dir>     # every CrownOS repo below it
    check-versions.py --lint-spec            # audit crown-versions.toml itself

Only dependencies named in crown-versions.toml are checked. A repo may declare
anything else it likes. Entries in [exceptions], keyed "<repo>.<dep>", are
allowed to differ and are reported as known exceptions rather than failures.

This exists because the same dependency was declared four different ways across
the tree (anyhow as "1", "1.0.100", "1.0.102" and "1.0.104"), and because
crowndictator carried a hand-written comment saying its Wayland pins were
"matched to crownshell" -- alignment that nothing enforced.
"""
import sys, pathlib, tomllib

RED, YEL, GRN, DIM, R = "\033[31m", "\033[33m", "\033[32m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    RED = YEL = GRN = DIM = R = ""

HERE = pathlib.Path(__file__).resolve().parent.parent
SPEC = tomllib.load((HERE / "crown-versions.toml").open("rb"))
PINNED = {**SPEC["crownos"], **SPEC["dependencies"]}
EXCEPTIONS = SPEC.get("exceptions", {})


def dep_version(value):
    """A dependency value is either a version string or a table."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("version")
    return None


def crate_name(dep, value):
    """The crate actually depended on, which is not always the key.

    crownpositor declares `config = { package = "crownpositor-config", ... }`.
    Keying on `config` meant the pin for crownpositor-config could never match
    anything, so it silently checked nothing.
    """
    if isinstance(value, dict) and "package" in value:
        return value["package"]
    return dep


def same_requirement(a, b):
    """`0.1` and `0.1.0` are the same cargo requirement; `1` and `1.0.104`
    are not. Compare with trailing zeros trimmed and nothing else relaxed."""
    def norm(v):
        v = v.lstrip("^=~ ")
        parts = v.split(".")
        if not all(p.isdigit() for p in parts):
            return v
        while len(parts) > 1 and parts[-1] == "0":
            parts.pop()
        return ".".join(parts)
    return norm(a) == norm(b)


def iter_manifests(repo: pathlib.Path):
    root = repo / "Cargo.toml"
    if root.exists():
        yield root
    for sub in sorted(repo.glob("*/Cargo.toml")):
        yield sub


def repo_name(repo: pathlib.Path) -> str:
    """Handle both a flat checkout (crownbar/) and a linked worktree
    (crownbar.git/main/), which is what the maintainer's machine uses."""
    if repo.name == "main" and repo.parent.name.endswith(".git"):
        return repo.parent.name[:-4]
    return repo.name[:-4] if repo.name.endswith(".git") else repo.name


def check(repo: pathlib.Path, seen=None):
    """`seen` accumulates {crate: {repos declaring it}} for the unpinned-drift
    audit, which is the thing crown-versions.toml exists to prevent and was not
    itself checking."""
    seen = {} if seen is None else seen
    name = repo_name(repo)
    problems, notes = [], []
    for manifest in iter_manifests(repo):
        try:
            data = tomllib.load(manifest.open("rb"))
        except Exception as e:                      # noqa: BLE001
            problems.append(f"{manifest}: unparseable: {e}")
            continue
        tables = [("dependencies", data.get("dependencies", {})),
                  ("dev-dependencies", data.get("dev-dependencies", {})),
                  ("workspace.dependencies",
                   data.get("workspace", {}).get("dependencies", {}))]
        for table, deps in tables:
            for dep, value in deps.items():
                dep = crate_name(dep, value)
                want = PINNED.get(dep)
                if want is None:
                    seen.setdefault(dep, set()).add(name)
                    continue
                got = dep_version(value)
                if got is None:            # `{ workspace = true }` inherits
                    continue
                key = f"{name}.{dep}"
                if key in EXCEPTIONS:
                    if not same_requirement(got, EXCEPTIONS[key]):
                        problems.append(
                            f"{name}: {dep} = {got!r} but the recorded exception "
                            f"is {EXCEPTIONS[key]!r} ({manifest.name}/{table})")
                    else:
                        notes.append(f"{name}: {dep} = {got!r} (known exception)")
                elif not same_requirement(got, want):
                    problems.append(
                        f"{name}: {dep} = {got!r}, crown-versions.toml says "
                        f"{want!r} ({manifest.name}/{table})")

        # MSRV must match the pinned toolchain.
        pkg = data.get("package", {})
        rv = pkg.get("rust-version")
        if isinstance(rv, dict):      # { workspace = true } -- inherited
            rv = None
        if rv and rv != SPEC["meta"]["msrv"]:
            problems.append(f"{name}: rust-version = {rv!r}, expected "
                            f"{SPEC['meta']['msrv']!r}")
    return problems, notes


def lint_spec():
    """Audit crown-versions.toml without needing the tree.

    `check()` skips any dependency that is not in PINNED, so an [exceptions]
    entry for an unpinned dependency can never fire. Seven of the nine entries
    were dead that way -- they read like decisions and enforced nothing.
    """
    problems = []
    for key in EXCEPTIONS:
        if "." not in key:
            problems.append(f"exception {key!r} is not of the form "
                            f'"<repo>.<dep>"')
            continue
        _, dep = key.split(".", 1)
        if dep not in PINNED:
            problems.append(
                f"exception {key!r} can never fire: {dep!r} is not pinned in "
                f"[crownos] or [dependencies], so check() skips it entirely")
    if problems:
        print(f"{RED}crown-versions.toml has {len(problems)} dead or malformed "
              f"entries:{R}")
        for x in problems:
            print(f"  {RED}x{R} {x}")
        print("\nAn exception is only meaningful for a dependency that is "
              "otherwise pinned.\nEither pin the base version, or delete the "
              "exception.")
        return 1
    print(f"{GRN}ok{R} crown-versions.toml: {len(PINNED)} pins, "
          f"{len(EXCEPTIONS)} live exceptions")
    return 0


def report_unpinned(seen, repos):
    """Dependencies two or more repos declare but crown-versions.toml does not
    pin -- exactly the drift this file was written to stop, which it was not
    looking for."""
    wide = {d: r for d, r in seen.items() if len(r) >= 2}
    if not wide:
        return
    print(f"\n{YEL}unpinned and declared by 2+ repos ({len(wide)}):{R}")
    for dep, repos_ in sorted(wide.items()):
        print(f"  {YEL}?{R} {dep} -- {', '.join(sorted(repos_))}")
    print(f"{DIM}  Advisory. Add to [dependencies] to enforce, or ignore.{R}")


def main(argv):
    if not argv:
        print(__doc__); return 2
    if argv[0] == "--lint-spec":
        return lint_spec()
    if argv[0] == "--all":
        parent = pathlib.Path(argv[1])
        repos = [p for p in sorted(parent.iterdir())
                 if (p / "Cargo.toml").exists()]
        repos += [p / "main" for p in sorted(parent.glob("*.git"))
                  if (p / "main" / "Cargo.toml").exists()]
    else:
        repos = [pathlib.Path(a) for a in argv]

    total, all_notes, seen = [], [], {}
    for repo in repos:
        problems, notes = check(repo, seen)
        total += problems
        all_notes += notes

    for n in all_notes:
        print(f"{DIM}  note  {n}{R}")
    if total:
        print(f"\n{RED}version drift ({len(total)}):{R}")
        for p in total:
            print(f"  {RED}x{R} {p}")
        print(f"\nEither align the repo, or record a deliberate difference in "
              f"crown-versions.toml [exceptions].")
        return 1
    print(f"{GRN}ok{R} {len(repos)} repos agree with crown-versions.toml")
    report_unpinned(seen, repos)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
