#!/usr/bin/env python3
"""Fail if a workflow's apt list disagrees with crownos-setup/deps.toml.

    check-ci-packages.py <path-to-crownos-setup>

The base set in rust.yml/release.yml/publish.yml, and each repo's `packages:`
input, are all generated from deps.toml. This is what stops them drifting back.

They had drifted before this existed: the base set installed
`libfontconfig-1-dev`, which exists on neither Debian nor Ubuntu, and
crownpositor's list omitted `xwayland` despite smithay's xwayland feature.
"""
import pathlib, re, sys, tomllib

HERE = pathlib.Path(__file__).resolve().parent.parent


def expected(setup: pathlib.Path):
    d = tomllib.load((setup / "deps.toml").open("rb"))
    base, seen = [], set()
    for g in ("toolchain", "base"):
        for p in d["groups"][g]["debian"]:
            if p not in seen:
                seen.add(p); base.append(p)
    extra = {}
    for comp, gs in d["components"].items():
        more = []
        for g in gs:
            if g in ("toolchain", "base"):
                continue
            more += [p for p in d["groups"][g]["debian"] if p not in seen]
        if more:
            extra[comp] = sorted(set(more))
    return set(base), extra


def apt_list(text: str):
    m = re.search(r'apt-get install -y --no-install-recommends\s*\\\n((?:\s+.*\\\n)*\s+.*)', text)
    if not m:
        return None
    body = m.group(1)
    body = re.sub(r'\$\{\{[^}]*\}\}', ' ', body)
    return {tok for tok in re.split(r'[\s\\]+', body) if tok and not tok.startswith('#')}


def main(argv):
    if not argv:
        print(__doc__); return 2
    setup = pathlib.Path(argv[0])
    base, extra = expected(setup)
    problems = []

    for wf in ("rust.yml", "release.yml", "publish.yml"):
        p = HERE / ".github" / "workflows" / wf
        if not p.exists():
            continue
        got = apt_list(p.read_text())
        if got is None:
            problems.append(f"{wf}: could not find the apt install block")
            continue
        if got != base:
            for m in sorted(base - got):
                problems.append(f"{wf}: missing {m}")
            for m in sorted(got - base):
                problems.append(f"{wf}: unexpected {m} (not in deps.toml)")

    print("\n".join(f"  x {p}" for p in problems) if problems
          else f"ok base apt set matches deps.toml ({len(base)} packages)")
    if not problems:
        print("  expected per-repo `packages:` inputs:")
        for comp, pkgs in sorted(extra.items()):
            print(f"    {comp}: {' '.join(pkgs)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
