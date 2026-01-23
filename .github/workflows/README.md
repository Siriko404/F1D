# CI/CD Configuration

## Workflows

### test.yml

Runs automated tests on every push and pull request.

**Trigger conditions:**
- Push to `main` or `master` branch
- Pull request to `main` or `master` branch

**Steps:**
1. Checkout code
2. Set up Python 3.13
3. Cache pip dependencies
4. Install dependencies (requirements.txt)
5. Run tests with pytest and coverage
6. Upload coverage to Codecov (optional)
7. Upload coverage report as artifact
8. Upload test results as artifact

**Artifacts:**
- `coverage-report`: HTML coverage report (retained for 30 days)
- `test-results`: Test cache and results (retained for 30 days)

## Running Tests Locally

Before pushing, run tests locally:

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=2_Scripts --cov-report=html --cov-report=term

# Run only unit tests (faster)
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v -m integration

# Run tests excluding integration (faster)
pytest -m "not integration"
```

## Coverage Reporting

Coverage targets:
- Shared modules: 80%+
- Main pipeline scripts: 50%+

Coverage is generated in two formats:
- HTML: `htmlcov/index.html` (view in browser)
- Terminal: Printed to console
- XML: `coverage.xml` (for Codecov)

## Enabling GitHub Actions

The workflow is created but GitHub Actions may not be enabled yet. To enable:

1. Go to repository on GitHub
2. Navigate to Settings > Actions > General
3. Under "Actions permissions", select:
   - "Allow all actions and reusable workflows" OR
   - "Allow [your organization] and select non-[your organization] actions and reusable workflows"
4. Click "Save"

Once enabled, workflow will automatically run on push and pull requests.

If you prefer not to enable GitHub Actions yet, see CI-CD-PLACEHOLDER.md for deferred setup options.

## Troubleshooting

**Tests fail in CI but pass locally:**
- Check Python version (CI uses 3.13)
- Check dependencies (CI installs from requirements.txt)
- Check environment variables (CI may have different env)

**Coverage not uploading to Codecov:**
- Ensure Codecov token is set in GitHub Secrets
- Check codecov-action logs for errors

**Workflow not triggering:**
- Check workflow YAML syntax (yamllint)
- Check trigger conditions (branch names)
- Check GitHub Actions permissions (Settings > Actions > General)
