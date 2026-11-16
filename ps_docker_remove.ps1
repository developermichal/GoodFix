<#
.SYNOPSIS
    Interactive Docker Cleanup Utility for PowerShell.

.DESCRIPTION
    Prompts the user to clean all Docker components system-wide, or selectively
    removes containers, images, volumes, networks, and build cache step-by-step.
#>

[CmdletBinding()]
param()

function Check-Docker {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Error: docker command not found. Please ensure Docker is installed and in your PATH."
        exit 1
    }
}

function Ask-Ynx {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PromptMessage
    )

    while ($true) {
        $rawInput = Read-Host "$PromptMessage [y/n/x]"
        if ($null -eq $rawInput) {
            return "x"
        }

        $inputVal = $rawInput.Trim().ToLower()
        switch ($inputVal) {
            "y" { return "y" }
            "n" { return "n" }
            "x" { return "x" }
            default {
                Write-Host "Invalid input. Please enter 'y', 'n', or 'x'." -ForegroundColor Yellow
            }
        }
    }
}

function Remove-DockerContainers {
    Write-Host "Removing all Docker containers..." -ForegroundColor Cyan
    try {
        $containers = (& docker ps -aq 2>$null) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
        if ($containers) {
            & docker rm -f $containers
            Write-Host "All Docker containers have been removed." -ForegroundColor Green
        } else {
            Write-Host "No Docker containers found to remove." -ForegroundColor Gray
        }
    } catch {
        Write-Warning "Failed while removing containers: $_"
    }
}

function Remove-DockerImages {
    Write-Host "Removing all Docker images..." -ForegroundColor Cyan
    try {
        $images = (& docker images -aq 2>$null) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
        if ($images) {
            & docker rmi -f $images
            Write-Host "All Docker images have been removed." -ForegroundColor Green
        } else {
            Write-Host "No Docker images found to remove." -ForegroundColor Gray
        }
    } catch {
        Write-Warning "Failed while removing images: $_"
    }
}

function Remove-DockerVolumes {
    Write-Host "Removing all Docker volumes..." -ForegroundColor Cyan
    try {
        $volumes = (& docker volume ls -q 2>$null) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
        if ($volumes) {
            & docker volume rm -f $volumes 2>$null
            if ($LASTEXITCODE -ne 0) {
                & docker volume prune -f 2>$null
            }
            Write-Host "All Docker volumes have been removed." -ForegroundColor Green
        } else {
            Write-Host "No Docker volumes found to remove." -ForegroundColor Gray
        }
    } catch {
        Write-Warning "Failed while removing volumes: $_"
    }
}

function Remove-DockerNetworks {
    Write-Host "Removing all custom Docker networks..." -ForegroundColor Cyan
    try {
        & docker network prune -f 2>$null
        Write-Host "Custom Docker networks have been removed." -ForegroundColor Green
    } catch {
        Write-Warning "Failed while removing networks: $_"
    }
}

function Remove-DockerBuildCache {
    Write-Host "Removing Docker build cache..." -ForegroundColor Cyan
    try {
        & docker builder prune -a -f 2>$null
        if ($LASTEXITCODE -ne 0) {
            & docker buildx prune -a -f 2>$null
        }
        Write-Host "Docker build cache has been removed." -ForegroundColor Green
    } catch {
        Write-Warning "Failed while removing build cache: $_"
    }
}

function Remove-AllDocker {
    Write-Host "Removing all Docker components from the system..." -ForegroundColor Magenta
    Remove-DockerContainers
    Remove-DockerImages
    Remove-DockerVolumes
    Remove-DockerNetworks
    Remove-DockerBuildCache
    Write-Host "Running system prune to ensure the system is completely clean..." -ForegroundColor Cyan
    & docker system prune -a --volumes -f 2>$null
    Write-Host "All Docker components removed. System is clean." -ForegroundColor Green
}

function Main {
    Check-Docker

    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "         Docker Cleanup Utility           " -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan

    $choice = Ask-Ynx -PromptMessage "Do you want to delete ALL Docker components system-wide?"
    if ($choice -eq "y") {
        Remove-AllDocker
        exit 0
    } elseif ($choice -eq "x") {
        Write-Host "Exiting script. No changes made." -ForegroundColor Yellow
        exit 0
    }

    Write-Host ""
    Write-Host "Proceeding with component-by-component cleanup..." -ForegroundColor Cyan

    # 1. Containers
    $choice = Ask-Ynx -PromptMessage "1. Do you want to remove all Docker containers (running or stopped)?"
    if ($choice -eq "y") {
        Remove-DockerContainers
    } elseif ($choice -eq "x") {
        Write-Host "Exiting script." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "Skipping Docker containers." -ForegroundColor Gray
    }

    # 2. Images
    Write-Host ""
    $choice = Ask-Ynx -PromptMessage "2. Do you want to remove all Docker images?"
    if ($choice -eq "y") {
        Remove-DockerImages
    } elseif ($choice -eq "x") {
        Write-Host "Exiting script." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "Skipping Docker images." -ForegroundColor Gray
    }

    # 3. Volumes
    Write-Host ""
    $choice = Ask-Ynx -PromptMessage "3. Do you want to remove all Docker volumes?"
    if ($choice -eq "y") {
        Remove-DockerVolumes
    } elseif ($choice -eq "x") {
        Write-Host "Exiting script." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "Skipping Docker volumes." -ForegroundColor Gray
    }

    # 4. Networks
    Write-Host ""
    $choice = Ask-Ynx -PromptMessage "4. Do you want to remove all custom Docker networks?"
    if ($choice -eq "y") {
        Remove-DockerNetworks
    } elseif ($choice -eq "x") {
        Write-Host "Exiting script." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "Skipping Docker networks." -ForegroundColor Gray
    }

    # 5. Build Cache
    Write-Host ""
    $choice = Ask-Ynx -PromptMessage "5. Do you want to remove Docker build cache?"
    if ($choice -eq "y") {
        Remove-DockerBuildCache
    } elseif ($choice -eq "x") {
        Write-Host "Exiting script." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "Skipping Docker build cache." -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "Cleanup process finished." -ForegroundColor Green
}

Main
