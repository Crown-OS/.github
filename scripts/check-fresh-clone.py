#!/usr/bin/env python3
"""Fail if a repository does not resolve its dependencies from a clean checkout.

Usage:
    check-fresh-clone.py <repo-dir> [<repo-dir> ...]
    check-fresh-clone.py --all <parent-dir>

This is the "works on my machine" detector, and it exists because that is
exactly what happened. Every CrownOS crate declares `crownshell = "0.3"` or
`crownos-config = "0.2"`. Neither version is on crates.io. Everything still
built for the maintainer, because a `.cargo/config.toml` sitting above the
checkouts patched both to local paths -- so `cargo build` succeeded on one
machine and failed at `cargo metadata` on every other one. Nothing noticed,
because nothing ever built outside that directory.

The check copies each repo's manifests into a temporary directory OUTSIDE the
tree, where no parent `.cargo/config.toml` can reach it, and asks cargo to
resolve. That is the same thing a stranger's `git clone` does.

`--allow` names repos that are known not to resolve yet and must not fail the
run; they are reported as expected failures. Passing a repo not in `--allow`
that resolves anyway is also reported, so the allowlist cannot rot.
"""
import argparse, os, pathlib, shutil, subprocess, sys, tempfile

RED, YEL, GRN, DIM, R = "\033[31m", "\033[33m", "\033[32m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    RED = YEL = GRN = DIM = R = ""

SKIP = {"target", ".git", "node_modules", ".direnv", "out", "work"}


def repo_name(repo: pathlib.Path) -> str:
    if repo.name == "main" and repo.parent.name.endswith(".git"):
        return repo.parent.name[:-4]
    return repo.name[:-4] if repo.name.endswith(".git") else repo.name


def copy_manifest_tree(src: pathlib.Path, dst: pathlib.Path):
    """Copy just enough for `cargo metadata`: every manifest, the lockfile, and
    a stub for each target cargo will look for. Copying `src/` wholesale would
    drag gigabytes for no benefit -- resolution never reads the code."""
    shutil.copytree(
        src, dst,
        ignore=shutil.ignore_patterns(*SKIP),
        ignore_dangling_symlinks=True,
        dirs_exist_ok=True,
    )
    # A workspace member with no src/ makes cargo fail for a reason that has
    # nothing to do with what we are testing.
    for manifest in dst.rglob("Cargo.toml"):
        pkg_dir = manifest.parent
        srcdir = pkg_dir / "src"
        if not srcdir.exists():
            continue
        if not any(srcdir.glob("*.rs")):
            (srcdir / "lib.rs").write_text("")


def resolves(repo: pathlib.Path) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="crownos-fresh-") as tmp:
        dst = pathlib.Path(tmp) / repo_name(repo)
        try:
            copy_manifest_tree(repo, dst)
        except Exception as e:                       # noqa: BLE001
            return False, f"could not stage a copy: {e}"
        env = dict(os.environ)
        # Anything the caller's shell set up is exactly what we are testing
        # against, so drop it.
        env.pop("CARGO_TARGET_DIR", None)
        env["CARGO_NET_OFFLINE"] = "false"
        try:
            p = subprocess.run(
                ["cargo", "metadata", "--format-version", "1"],
                cwd=dst, env=env, capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired:
            return False, "cargo metadata timed out after 600s"
        if p.returncode == 0:
            return True, ""
        errs = [l for l in p.stderr.splitlines() if l.startswith(("error", "  candidate", "caused by"))]
        return False, " | ".join(errs[:3]) or p.stderr.strip().splitlines()[-1]


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--all", metavar="PARENT")
    ap.add_argument("--allow", default="", metavar="NAMES",
                    help="space- or comma-separated repos expected to fail")
    ap.add_argument("repos", nargs="*")
    ap.add_argument("-h", "--help", action="store_true")
    a = ap.parse_args(argv)
    if a.help or (not a.all and not a.repos):
        print(__doc__)
        return 2

    if a.all:
        parent = pathlib.Path(a.all)
        repos = [p for p in sorted(parent.iterdir()) if (p / "Cargo.toml").exists()]
        repos += [p / "main" for p in sorted(parent.glob("*.git"))
                  if (p / "main" / "Cargo.toml").exists()]
    else:
        repos = [pathlib.Path(x) for x in a.repos]

    allow = set(a.allow.replace(",", " ").split())
    failures, surprises = [], []

    for repo in repos:
        name = repo_name(repo)
        ok, why = resolves(repo)
        if ok and name in allow:
            surprises.append(name)
            print(f"{YEL}!{R}  {name}: resolves now -- remove it from --allow")
        elif ok:
            print(f"{GRN}ok{R} {name}")
        elif name in allow:
            print(f"{DIM}   {name}: expected failure -- {why}{R}")
        else:
            failures.append((name, why))
            print(f"{RED}x{R}  {name}: {why}")

    print()
    if failures:
        print(f"{RED}{len(failures)} repo(s) cannot be built by anyone but you.{R}")
        print("A dependency they declare does not exist where a stranger would look.")
        print("Publish it, or record the repo in --allow with a reason.")
        return 1
    if surprises:
        print(f"{YEL}--allow is stale: {' '.join(surprises)} resolve now.{R}")
        return 1
    print(f"{GRN}ok{R} every repo resolves from a clean checkout")
    return 0


if __name__ == "__main__":
    sys.exit(main())
