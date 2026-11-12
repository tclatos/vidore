# Justfile for vidore benchmark
# Run `just` to see available recipes.

default:
    @just --list

# ── Development ─────────────────────────────────────────────────────────────

# Install / sync dependencies
sync:
    uv sync

# Format code with ruff
fmt:
    uv run ruff format .

# Lint code with ruff
lint:
    uv run ruff check .

# Format + lint
check: fmt lint

# Run tests
test:
    uv run pytest tests/ -v

# ── Skills ───────────────────────────────────────────────────────────────────

skills:
    uv run cli skills list

lint-skills:
    uv run cli skills validate --all

# ── Benchmark harness ────────────────────────────────────────────────────────

# Setup dependencies including harnessing extra
bench-setup:
    uv sync --extra harnessing

# Run benchmark evaluation
bench:
    uv run cli bench run

# Run specific step
bench-fetch:
    uv run cli bench run --step fetch

bench-build:
    uv run cli bench run --step build

bench-run:
    uv run cli bench run --step run

bench-grade:
    uv run cli bench run --step grade

bench-report:
    uv run cli bench report
