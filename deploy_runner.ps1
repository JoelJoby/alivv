$ErrorActionPreference = "Stop"

$Key = "C:\JOEL\alivv-key-fresh.pem"
$Ip = "16.170.218.5"
$User = "ubuntu"
$LocalScript = "setup_remote.sh"
$RemoteScript = "/home/ubuntu/setup_remote.sh"

Write-Host "1. Uploading setup script to $Ip..."
scp -i "$Key" -o StrictHostKeyChecking=no $LocalScript "${User}@${Ip}:${RemoteScript}"

Write-Host "2. Making script executable..."
ssh -i "$Key" -o StrictHostKeyChecking=no "${User}@${Ip}" "chmod +x $RemoteScript"

Write-Host "3. Executing deployment script remotely..."
ssh -i "$Key" -o StrictHostKeyChecking=no "${User}@${Ip}" "$RemoteScript"

Write-Host "Done!"
