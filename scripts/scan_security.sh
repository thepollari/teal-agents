#!/bin/bash

set -e

echo "=== Teal Agents Security Scan ==="
echo "Date: $(date)"
echo ""

components=(
  "shared/ska_utils"
  "src/sk-agents"
  "src/orchestrators/assistant-orchestrator/orchestrator"
  "src/orchestrators/assistant-orchestrator/services"
  "src/orchestrators/collab-orchestrator/orchestrator"
  "src/orchestrators/workflow-orchestrator/orchestrator"
)

mkdir -p /tmp/security_scans

for component in "${components[@]}"; do
  echo "=== Scanning $component ==="
  cd "$component"
  
  tmp_file="/tmp/security_scans/requirements_${component//\//_}.txt"
  uv pip freeze > "$tmp_file"
  
  pip-audit --requirement "$tmp_file" || echo "Scan completed with findings"
  
  echo ""
  cd - > /dev/null
done

echo "=== Security Scan Complete ==="
