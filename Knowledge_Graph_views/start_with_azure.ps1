# Start server.py with Azure OpenAI enabled
$env:USE_AZURE_OPENAI = "true"
Write-Host "Starting server.py with Azure OpenAI..." -ForegroundColor Green
Write-Host "Model: $env:KG_AGENT_MODEL" -ForegroundColor Cyan
python server.py
