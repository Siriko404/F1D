# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 6.x     | :white_check_mark: |
| < 6.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in this project, please report it responsibly.

### How to Report

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Email security concerns to the project maintainer (see repository owner)
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Triage**: Within 5 business days
- **Resolution**: Depends on severity (critical: 7 days, high: 14 days, medium: 30 days)

## Security Best Practices

This project handles sensitive financial data. Please ensure:

1. **Never commit credentials** - Use environment variables or `.env` files (already in `.gitignore`)
2. **Keep dependencies updated** - Dependabot is configured for automated updates
3. **Review code changes** - All PRs require review before merging
4. **Report suspicious activity** - If you notice unusual behavior, report it immediately

## Data Security

- **Input Data**: This project processes proprietary financial data. Ensure you have proper authorization.
- **Output Data**: Generated outputs should be stored securely and not shared publicly.
- **Logs**: Log files may contain sensitive information. Do not commit logs to version control.

## Dependency Security

We use the following tools to maintain dependency security:

- **Dependabot**: Automated dependency updates (weekly)
- **pip-audit**: Vulnerability scanning for Python packages
- **Bandit**: Static analysis security testing (SAST)

To run security checks locally:

```bash
# Check for known vulnerabilities in dependencies
pip-audit

# Run Bandit SAST
bandit -r src/f1d/
```

## Security Features

This project implements:

- [x] Input validation for file paths
- [x] Output schema validation (Pandera)
- [x] Type checking (mypy)
- [x] Linting with security rules (ruff + bandit)
- [x] Dependency scanning (Dependabot)
- [x] Secrets excluded from version control (.gitignore)
