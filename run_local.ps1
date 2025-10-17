# Helper to run app locally with .env values (PowerShell)
if (Test-Path .env) {
    Write-Host "Loading .env"
    Get-Content .env | ForEach-Object {
        if ($_ -match "^\s*([^#=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Write-Host "Setting env var: $name"
            Set-Item -Path Env:\$name -Value $value
        }
    }
} else {
    Write-Host ".env not found. Copy .env.example -> .env and edit it."
}

python -m pip install -r requirements.txt
python init_db.py
python main.py
