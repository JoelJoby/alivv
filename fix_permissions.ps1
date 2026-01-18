$Key = "C:\JOEL\alivv-key-fresh.pem"

# Reset permissions
icacls $Key /reset

# Grant full control to the current user
icacls $Key /grant:r "$($env:USERNAME):(R)"

# Remove inheritance
icacls $Key /inheritance:r

Write-Host "Permissions fixed for $Key"
