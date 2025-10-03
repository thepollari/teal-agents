# Security Scanning Guide

## Overview
This guide documents the security scanning process for the Teal Agents repository.

## Tools
- **pip-audit**: Primary security scanning tool for Python dependencies
- **Installation**: `pip install pip-audit`

## Scanning Individual Components

### Basic Scan
```bash
cd <component-directory>
uv pip freeze > /tmp/requirements.txt
pip-audit --requirement /tmp/requirements.txt
```

### Scan All Components
Use the provided script:
```bash
bash scripts/scan_security.sh
```

## Interpreting Results

### Understanding Severity Levels
- **CRITICAL** (9.0-10.0): Immediate action required
- **HIGH** (7.0-8.9): Action required within days
- **MEDIUM** (4.0-6.9): Action required within weeks
- **LOW** (0.1-3.9): Monitor and fix when convenient

### False Positives
pip-audit may report false positives when:
1. Scanning pyproject.toml directly (use `uv pip freeze` output instead)
2. Scanning with incorrect Python environment
3. Reporting transitive dependencies that don't apply to your usage

Always verify findings by checking actual installed packages:
```bash
uv pip list | grep -i <package-name>
```

## Common Issues

### pip-audit Warning: "will run pip against system Python"
**Cause:** uv virtual environments don't include pip by default  
**Solution:** Export requirements with `uv pip freeze` and scan the exported file  
**Not a Problem:** The warning is expected and doesn't affect scan accuracy when using exported requirements

### System pip Vulnerability
**Issue:** pip-audit may report vulnerabilities in system pip  
**Reality:** pip is not a project dependency in uv-managed projects  
**Action:** Monitor for pip updates but don't treat as project vulnerability

## Maintenance Schedule
- **Monthly:** Run comprehensive security scan
- **Before Release:** Run security scan as part of release checklist
- **After Major Dependency Updates:** Run security scan to verify safety

## Remediation Process
When vulnerabilities are found:

1. **Assess Severity:** Determine impact and urgency
2. **Research Fix:** Check if patched versions are available
3. **Update Dependencies:** Use `uv add <package>@<safe-version>`
4. **Test Changes:** Run full test suite
5. **Update Lock Files:** Ensure `uv.lock` reflects updates
6. **Re-scan:** Verify vulnerability is resolved
7. **Document:** Update SECURITY_ASSESSMENT.md

## Integration with CI/CD
Consider adding security scans to GitHub Actions workflow:
```yaml
- name: Security Scan
  run: |
    pip install pip-audit
    bash scripts/scan_security.sh
```
