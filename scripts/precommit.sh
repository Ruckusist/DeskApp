#!/usr/bin/env bash
# Precommit helper: run lightweight checks, then stage all changes, and optionally commit/push.
# Usage:
#   scripts/precommit.sh                # run checks and stage all changes
#   scripts/precommit.sh -m "msg"       # also commit with message
#   scripts/precommit.sh -m "msg" --push  # also push to current branch
set -euo pipefail

# Move to repo root
ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [[ -z "${ROOT_DIR}" ]]; then
  echo "Error: not a git repository (run inside a repo)." >&2
  exit 1
fi
cd "${ROOT_DIR}"

# Parse args
COMMIT_MSG=""
DO_PUSH=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--message)
      COMMIT_MSG="$2"; shift 2;;
    --push)
      DO_PUSH=1; shift;;
    *)
      echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

# Pick Python
if [[ -x .venv/bin/python ]]; then
  PY=.venv/bin/python
else
  PY=$(command -v python3 || command -v python)
fi
if [[ -z "${PY}" ]]; then
  echo "Error: Python not found." >&2
  exit 1
fi

echo "==> Repo: ${ROOT_DIR}"

# Basic sanity: no merge conflicts
if git diff --name-only --diff-filter=U | grep -q .; then
  echo "Error: Merge conflicts present. Resolve before committing." >&2
  git diff --name-only --diff-filter=U
  exit 1
fi

# Python syntax check (fast)
echo "==> Python syntax check (py_compile)"
# Exclude venv, egg-info, __pycache__
mapfile -d '' PYFILES < <(find . -type f -name "*.py" \
  -not -path "*/.venv/*" -not -path "*/__pycache__/*" -not -path "*/build/*" -not -path "*/dist/*" -print0)
if [[ ${#PYFILES[@]} -gt 0 ]]; then
  "${PY}" - <<'PY'
import sys, py_compile
ok=True
for f in sys.stdin.read().split('\0'):
    if not f: continue
    try:
        py_compile.compile(f, doraise=True)
    except Exception as e:
        ok=False
        print(f"Syntax error: {f}: {e}")
sys.exit(0 if ok else 1)
PY
else
  echo "No Python files found."
fi <<<"${PYFILES[*]}"

# Optional linters/formatters if available
run_if_exists() {
  if command -v "$1" >/dev/null 2>&1; then
    echo "==> $*"
    "$@"
  else
    echo "(skip) $1 not found"
  fi
}

run_if_exists ruff check . || true
run_if_exists black --check . || true
run_if_exists isort --check-only . || true
run_if_exists flake8 . || true

# Optional tests if pytest + tests/ exist
if command -v pytest >/dev/null 2>&1 && [[ -d tests ]]; then
  echo "==> pytest"
  pytest -q || true
fi

# Stage all changes
echo "==> git add -A"
git add -A

echo "==> git status --short"
git status --short

# Commit if message provided
if [[ -n "${COMMIT_MSG}" ]]; then
  echo "==> git commit -m \"${COMMIT_MSG}\""
  git commit -m "${COMMIT_MSG}" || true
  if [[ ${DO_PUSH} -eq 1 ]]; then
    CUR_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "==> git push origin ${CUR_BRANCH}"
    git push origin "${CUR_BRANCH}"
  fi
else
  echo "Staged changes. Provide -m \"message\" to commit, and --push to push."
fi
