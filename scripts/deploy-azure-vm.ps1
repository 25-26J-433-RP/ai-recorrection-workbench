# ===========================================================
# Akura AI - Azure VM Deployment Script (PowerShell)
# Run this from your LOCAL machine after installing Azure CLI
# ===========================================================

param(
    [string]$ResourceGroup = "akura-ai-rg",
    [string]$Location = "southeastasia",
    [string]$VMName = "akura-ai-vm",
    [string]$VMSize = "Standard_B2ms",  # 2 vCPU, 8GB RAM (~$60/mo, covered by student credits)
    [string]$AdminUsername = "azureuser"
)

Write-Host "=== Akura AI - Azure VM Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Login to Azure
Write-Host "[1/5] Logging into Azure..." -ForegroundColor Yellow
az login
Write-Host ""

# Step 2: Create Resource Group
Write-Host "[2/5] Creating Resource Group: $ResourceGroup in $Location..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location
Write-Host ""

# Step 3: Create the VM
Write-Host "[3/5] Creating VM: $VMName ($VMSize)..." -ForegroundColor Yellow
Write-Host "       This will take 2-5 minutes..." -ForegroundColor Gray
$vmResult = az vm create `
    --resource-group $ResourceGroup `
    --name $VMName `
    --image Ubuntu2404 `
    --size $VMSize `
    --admin-username $AdminUsername `
    --generate-ssh-keys `
    --public-ip-sku Standard `
    --os-disk-size-gb 64 `
    --output json | ConvertFrom-Json

$publicIp = $vmResult.publicIpAddress
Write-Host "VM created! Public IP: $publicIp" -ForegroundColor Green
Write-Host ""

# Step 4: Open required ports
Write-Host "[4/5] Opening ports (SSH:22, API:8000)..." -ForegroundColor Yellow
az vm open-port --resource-group $ResourceGroup --name $VMName --port 22 --priority 1001
az vm open-port --resource-group $ResourceGroup --name $VMName --port 8000 --priority 1002
Write-Host ""

# Step 5: Show connection info
Write-Host "[5/5] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "=========================================="  -ForegroundColor Cyan
Write-Host " VM Public IP: $publicIp" -ForegroundColor White
Write-Host " SSH Command:  ssh ${AdminUsername}@${publicIp}" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. SSH into the VM:" -ForegroundColor White
Write-Host "   ssh ${AdminUsername}@${publicIp}" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Copy and run the setup script on the VM:" -ForegroundColor White
Write-Host "   scp scripts/setup-azure-vm.sh ${AdminUsername}@${publicIp}:~/" -ForegroundColor Gray
Write-Host "   ssh ${AdminUsername}@${publicIp} 'bash ~/setup-azure-vm.sh'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. After setup, your API will be at:" -ForegroundColor White
Write-Host "   http://${publicIp}:8000" -ForegroundColor Gray
Write-Host "   http://${publicIp}:8000/docs" -ForegroundColor Gray
Write-Host ""

# Save the IP for later use
$publicIp | Out-File -FilePath ".azure-vm-ip.txt" -Encoding utf8
Write-Host "VM IP saved to .azure-vm-ip.txt" -ForegroundColor Gray
