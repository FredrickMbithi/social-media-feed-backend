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
