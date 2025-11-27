#!/usr/bin/env bash
# Simple security audit script: safety, bandit, django check
set -euo pipefail

echo "Installing security tools..."
pip install --quiet safety bandit

echo "Running safety..."
safety check || true

echo "Running bandit..."
bandit -r posts/ users/ socialfeed/ -ll || true

echo "Running Django deploy checks..."
pip install -r requirements.txt --quiet
python manage.py check --deploy --settings=socialfeed.settings || true

echo "Security audit complete."
#!/usr/bin/env bash
set -euo pipefail

# Simple security audit script: runs safety, bandit, and Django deploy checks.
# Usage: `bash scripts/security_audit.sh`

echo "==> Updating/installing audit tools (within current Python env)"
python -m pip install --upgrade pip >/dev/null
python -m pip install --upgrade safety bandit >/dev/null

echo "==> Running safety (vulnerability database)"
if command -v safety >/dev/null 2>&1; then
  safety check || true
else
  echo "safety not available"
fi

echo "==> Running bandit (static analysis)"
if command -v bandit >/dev/null 2>&1; then
  bandit -r . || true
else
  echo "bandit not available"
fi

echo "==> Running Django deploy checks"
python manage.py check --deploy || true

echo "Security audit completed"
#!/bin/bash

echo "========================================="
echo "   Security Audit - Social Feed API"
echo "========================================="

echo -e "\n[1/4] Checking for vulnerable dependencies..."
safety check --json || echo "⚠️  Vulnerabilities found or safety not installed"

echo -e "\n[2/4] Running static code analysis (Bandit)..."
bandit -r posts/ users/ socialfeed/ -ll -f screen || echo "⚠️  Issues found or bandit not installed"

echo -e "\n[3/4] Checking for hardcoded secrets..."
echo "Scanning for passwords..."
grep -rn "password.*=.*['\"]" --include="*.py" posts/ users/ socialfeed/ || echo "✅ No hardcoded passwords found"
echo "Scanning for API keys..."
grep -rn "api_key.*=.*['\"]" --include="*.py" posts/ users/ socialfeed/ || echo "✅ No hardcoded API keys found"

echo -e "\n[4/4] Django deployment security check..."
python manage.py check --deploy

echo -e "\n========================================="
echo "   Security Audit Complete"
echo "========================================="
