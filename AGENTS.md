# AGENTS.md

## Cursor Cloud specific instructions

This is a Python/Streamlit web application (WCS Analysis Platform) for GPS sports performance data analysis. It has no external service dependencies (no database, no Docker, no Redis).

### Running the application

```bash
python3 -m streamlit run src/app.py --server.port 8501 --server.headless true
```

The app is accessible at `http://localhost:8501`.

### Lint

```bash
python3 -m black --check src/ tests/
python3 -m flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503
```

Note: The existing codebase has pre-existing lint failures (formatting and style). Use `python3 -m` prefix for all tools since pip scripts directory is not on PATH.

### Tests

```bash
python3 -m pytest tests/ -v
```

Note: 13 of 20 tests fail due to pre-existing issues in the test suite (API mismatches between tests and source). 7 tests pass.

### Key caveats

- **No sample data files are committed** to the repository. To test the app manually, create a sample CSV. The `quick_start.py` script references `data/sample_data/` but does not generate data.
- **Supported GPS file formats**: StatSport, Catapult, Generic GPS. StatSport files require columns: `Player Id`, `Player Display Name`, `Time`, `  Speed m/s` (note leading spaces), `Elapsed Time (s)`.
- **pip scripts not on PATH**: Always use `python3 -m <tool>` (e.g. `python3 -m pytest`, `python3 -m black`, `python3 -m flake8`) rather than bare command names.
