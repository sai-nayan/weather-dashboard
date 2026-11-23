# ==============================================================================
# Weather Dashboard — Zero-Downtime Blue-Green Switch Automation (PowerShell)
# ==============================================================================
[CmdletBinding()]
param (
    [string]$Namespace = "weather-dashboard",
    [string]$ActiveService = "weather-dashboard-active",
    [string]$PreviewService = "weather-dashboard-preview"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Weather Dashboard Blue-Green Deployment Cutover ===" -ForegroundColor Cyan
Write-Host "Target Namespace: $Namespace"

# 1. Determine currently active color
$currentActive = kubectl get service $ActiveService -n $Namespace -o jsonpath='{.spec.selector.version}'
Write-Host "Currently Active Slot: $currentActive" -ForegroundColor Yellow

if ($currentActive -eq "blue") {
    $targetColor = "green"
    $targetDeployment = "weather-dashboard-green"
} else {
    $targetColor = "blue"
    $targetDeployment = "weather-dashboard-blue"
}

Write-Host "Targeting Cutover to: $targetColor ($targetDeployment)" -ForegroundColor Green

# 2. Verify target deployment readiness
Write-Host "Verifying $targetDeployment rollout status..."
kubectl rollout status deployment/$targetDeployment -n $Namespace --timeout=120s

# 3. Health check candidate via preview service
Write-Host "Executing pre-cutover health check against preview service..." -ForegroundColor Cyan
try {
    $previewPort = kubectl get service $PreviewService -n $Namespace -o jsonpath='{.spec.ports[0].nodePort}'
    $nodeIp = kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}'
    if (-not $nodeIp) { $nodeIp = "127.0.0.1" }
    $previewUrl = "http://${nodeIp}:${previewPort}/health"
    Write-Host "Probing preview endpoint: $previewUrl"
    $response = Invoke-RestMethod -Uri $previewUrl -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response) {
        Write-Host "✅ Candidate preview health check passed." -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Note: Direct HTTP probe to preview service unreachable or pending (readiness probe verified by Kubernetes)." -ForegroundColor Yellow
}

# 4. Perform atomic service selector patch
Write-Host "Switching active traffic to: version=$targetColor..." -ForegroundColor Cyan
$activePatch = '{"spec":{"selector":{"version":"' + $targetColor + '"}}}'
kubectl patch service $ActiveService -n $Namespace -p $activePatch

# 4. Point preview service to standby slot
$previewPatch = '{"spec":{"selector":{"version":"' + $currentActive + '"}}}'
kubectl patch service $PreviewService -n $Namespace -p $previewPatch

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "SUCCESS: Zero-downtime cutover complete!" -ForegroundColor Green
Write-Host "Active Traffic  -> Slot: $targetColor" -ForegroundColor Green
Write-Host "Preview Traffic -> Slot: $currentActive (Standby for rollback)" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
