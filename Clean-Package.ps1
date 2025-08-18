# Cleanup only the package installed via "pip install ." and build artifacts, keep .venv

# 1. Get package name from setup.py
$setup = Get-Content .\setup.py -Raw
if ($setup -match "name\s*=\s*['\''](.+?)['\'']") {
    $PackageName = $matches[1]
    Write-Host "Package name detected: $PackageName"
} else {
    Write-Host "Could not determine package name from setup.py"
    exit
}

# 2. Uninstall the package
Write-Host "Uninstalling package: $PackageName"
pip uninstall -y $PackageName

# 3. Remove build artifacts
Write-Host "Removing build/, dist/, *.egg-info..."
Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue

Write-Host "Cleanup complete! .venv is intact."