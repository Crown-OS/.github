# Contributing to CrownOS

Thanks for helping build CrownOS. This guide applies to every repository in the
[Crown-OS](https://github.com/Crown-OS) organization unless a repository ships
its own `CONTRIBUTING.md`.

## Ground rules

- Be kind. Everything here is covered by the [Code of Conduct](CODE_OF_CONDUCT.md).
- Security problems go through [SECURITY.md](SECURITY.md), never a public issue.
- Questions go to [Discussions](https://github.com/orgs/Crown-OS/discussions);
  issues are for bugs and concrete proposals.
- For anything bigger than a small fix, open or comment on an issue first so we
  can agree on the approach before you write code.

## Finding something to work on

- [`good first issue`](https://github.com/search?q=org%3ACrown-OS+label%3A%22good+first+issue%22+state%3Aopen&type=issues)
  — scoped, mentored, with an implementation plan from CodeRabbit on the issue.
- [`help wanted`](https://github.com/search?q=org%3ACrown-OS+label%3A%22help+wanted%22+state%3Aopen&type=issues)
  — larger tasks maintainers would welcome help with.

Comment on the issue to claim it. If you go quiet for two weeks, someone else may
pick it up.

## Setting up

CrownOS repositories depend on each other through sibling paths
(`path = "../crownui"`), so clone them **next to each other**:

```sh
mkdir crownos && cd crownos
gh repo fork Crown-OS/crownbar --clone        # the repo you are changing
git clone https://github.com/Crown-OS/crownui  # each sibling it depends on
```

`cargo build` tells you which sibling is missing. CI builds inside an Arch Linux
container with the package list in
[`prepare-workspace`](.github/actions/prepare-workspace/action.yml); installing
the same packages locally gives you the same environment.

## Making a change

1. Branch from an up-to-date `main`: `git switch -c fix/short-description`.
2. Keep the PR to **one logical change**. Unrelated cleanups go in their own PR.
3. Sign off every commit (see [DCO](#developer-certificate-of-origin)):
   `git commit -s`.
4. Before pushing, run what CI runs:

   ```sh
   cargo fmt --check
   cargo clippy --all-targets
   cargo test --all
   ```

   Your change must not add new clippy warnings. Some repositories still have
   older warnings that are being cleared.

   Optional: run the [CodeRabbit CLI](https://docs.coderabbit.ai/cli) locally
   with `coderabbit review --base main` to catch review comments before the PR.
5. Open a pull request against `main` and fill in the template.

### Pull request titles

PRs are **squash-merged**, so the PR title becomes the commit on `main`. It must
follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```text
<type>(<optional scope>)<optional !>: <description>
```

| type | use for |
|---|---|
| `feat` | a new user-visible capability |
| `fix` | a bug fix |
| `perf` | a change that only makes things faster or lighter |
| `refactor` | restructuring with no behaviour change |
| `docs`, `test`, `build`, `ci`, `chore` | what they say |
| `revert` | reverting an earlier commit |

Write the description in the imperative mood, start it lowercase, leave off
the trailing period and keep the whole title under 72 characters. Add `!` for
breaking changes: `feat(ipc)!: rename the workspace mode request`.

Commits inside your branch can be messy. They are squashed.

### Changes that span repositories

CI resolves sibling repositories from their `main` branch. If your change needs
an unmerged change in another repository:

1. Open the upstream PR first (for example in `crownui`).
2. Open the downstream PR and link it under **Cross-repo changes** in the
   template. Its CI will fail until the upstream PR merges; that is expected.
3. Maintainers merge in dependency order and re-run CI.

## Review

Every pull request gets:

1. **CI**: formatting, build, clippy and tests. Formatting, build and tests must
   pass. Clippy is advisory for now, but new code should not add warnings.
2. **CodeRabbit**: an automated review within a few minutes. Address each
   comment or reply explaining why not. You can talk to it with
   `@coderabbitai` (for example `@coderabbitai explain this suggestion`).
   Resolve the threads you have handled.
3. **A maintainer review**: the merge decision is always a human's.

Low-effort or machine-generated PRs that do not engage with the codebase are
labelled `slop` and closed.

## Code style

Rust code follows these conventions, and CodeRabbit checks them:

- No `unwrap()` or `expect()` outside tests and examples. Propagate errors
  with `?`.
- Library crates define error types with `thiserror`. Binaries use `anyhow`
  with `.context()`.
- Borrow rather than clone. Take `&str` or `impl Into<String>`, not `String`.
  Use `Cow<str>` when ownership is conditional.
- Use enums instead of boolean parameters, named constants instead of magic
  numbers, and early returns instead of deep nesting.
- Use self-explanatory names. If a comment is needed to explain *what* the code
  does, rename or restructure the code instead.
- Keep modules focused. Shared helpers go in `src/util/<name>.rs`.
- Performance and memory footprint matter. Pre-size collections, prefer
  iterators and use GPU paths where available.
- Never block inside async code. Use `spawn_blocking` for CPU-heavy work.
- `cargo fmt` must be clean, and changes must not add clippy warnings.

Repositories may add their own rules in `CLAUDE.md` or `AGENTS.md`. CodeRabbit
reads those too.

## Developer Certificate of Origin

By contributing you certify the [Developer Certificate of Origin 1.1](https://developercertificate.org/):
you wrote the change, or otherwise have the right to submit it under the
repository's license. Show this by adding a `Signed-off-by` line to every commit. Commits made in the
GitHub web UI, including accepted CodeRabbit suggestions, are signed off
automatically:

```sh
git commit -s -m "fix(dock): keep the icon highlight after a drag"
```

Forgot? Sign off all commits on your branch with
`git rebase --signoff main && git push --force-with-lease`.

## License

Unless a repository says otherwise, contributions are dual-licensed under the
[MIT](https://opensource.org/license/mit) and
[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) licenses, at the
user's option, with no additional terms.
