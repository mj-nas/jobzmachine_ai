# Set script to stop on errors
$ErrorActionPreference = "Stop"

# Define variables
$volumeName = "jobzmachine_ai_weaviate_data"
$backupFile = "weaviate_backup.tar.gz"
$backupPath = (Get-Location).Path

# Step 1: Ensure Docker volume exists (Docker Compose should have created it)
Write-Host "Ensuring Docker volume '$volumeName' exists..."
docker volume inspect $volumeName > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Volume does not exist. Starting Docker Compose to create it..."
    docker compose up -d
    Start-Sleep -Seconds 10
}

# Step 2: Restore backup into volume
Write-Host "Restoring backup from '$backupFile' into Docker volume '$volumeName'..."
docker run --rm `
  -v "${volumeName}:/data" `
  -v "${backupPath}:/backup" `
  alpine `
  sh -c "rm -rf /data/* && tar xzvf /backup/${backupFile} -C /data"

Write-Host "`n✅ Restore complete. You can now start your Weaviate container."
Write-Host "To start Weaviate, run: docker compose up -d" -ForegroundColor Green
Write-Host "To check the status of Weaviate, run: docker compose ps" -ForegroundColor Green