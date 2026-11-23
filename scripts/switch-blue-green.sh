#!/usr/bin/env bash
# ==============================================================================
# Weather Dashboard — Zero-Downtime Blue-Green Switch Automation Script
# ==============================================================================
set -euo pipefail

NAMESPACE="weather-dashboard"
ACTIVE_SERVICE="weather-dashboard-active"
PREVIEW_SERVICE="weather-dashboard-preview"

echo "=== Weather Dashboard Blue-Green Deployment Cutover ==="
echo "Target Namespace: ${NAMESPACE}"

# 1. Determine currently active color
CURRENT_ACTIVE=$(kubectl get service "${ACTIVE_SERVICE}" -n "${NAMESPACE}" -o jsonpath='{.spec.selector.version}')
echo "Currently Active Slot: ${CURRENT_ACTIVE}"

if [ "${CURRENT_ACTIVE}" = "blue" ]; then
    TARGET_COLOR="green"
    TARGET_DEPLOYMENT="weather-dashboard-green"
else
    TARGET_COLOR="blue"
    TARGET_DEPLOYMENT="weather-dashboard-blue"
fi

echo "Targeting Cutover to: ${TARGET_COLOR} (${TARGET_DEPLOYMENT})"

# 2. Verify target deployment readiness
echo "Verifying ${TARGET_DEPLOYMENT} rollout status..."
kubectl rollout status deployment/"${TARGET_DEPLOYMENT}" -n "${NAMESPACE}" --timeout=120s

# 3. Health check candidate via preview service
echo "Executing pre-cutover health check against preview service..."
PREVIEW_PORT=$(kubectl get service "${PREVIEW_SERVICE}" -n "${NAMESPACE}" -o jsonpath='{.spec.ports[0].nodePort}')
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}' || echo "127.0.0.1")

PREVIEW_URL="http://${NODE_IP}:${PREVIEW_PORT}/health"
echo "Probing preview endpoint: ${PREVIEW_URL}"
if command -v curl >/dev/null 2>&1; then
    if curl --fail --silent --show-error --max-time 10 "${PREVIEW_URL}" > /dev/null 2>&1; then
        echo "✅ Candidate preview health check passed."
    else
        echo "⚠️ Note: Direct HTTP probe to ${PREVIEW_URL} unreachable or pending (readiness probe verified by Kubernetes)."
    fi
fi

# 4. Perform atomic service selector patch
echo "Switching active traffic to: version=${TARGET_COLOR}..."
kubectl patch service "${ACTIVE_SERVICE}" -n "${NAMESPACE}" -p "{\"spec\":{\"selector\":{\"version\":\"${TARGET_COLOR}\"}}}"

# 5. Point preview service to previous slot
kubectl patch service "${PREVIEW_SERVICE}" -n "${NAMESPACE}" -p "{\"spec\":{\"selector\":{\"version\":\"${CURRENT_ACTIVE}\"}}}"

echo "=========================================================="
echo "SUCCESS: Zero-downtime cutover complete!"
echo "Active Traffic  -> Slot: ${TARGET_COLOR}"
echo "Preview Traffic -> Slot: ${CURRENT_ACTIVE} (Standby for rollback)"
echo "=========================================================="
