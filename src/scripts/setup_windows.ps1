Write-Host "Configurando ambiente News Verifier no Windows..." -ForegroundColor Green

# Criar ambiente virtual
python -m venv venv
Write-Host "Ambiente virtual criado" -ForegroundColor Green

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1
Write-Host "Ambiente virtual ativado" -ForegroundColor Green

# Instalar dependências
pip install -r requirements/base.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Falha na instalação das dependências base" -ForegroundColor Red
    exit 1
}

pip install -r requirements/dev.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Falha na instalação das dependências de desenvolvimento" -ForegroundColor Red
    exit 1
}

# Download do modelo spaCy
python -m spacy download pt_core_news_sm
Write-Host "Modelo spaCy baixado" -ForegroundColor Green

# Configurar pre-commit
pre-commit install
Write-Host "Pre-commit configurado" -ForegroundColor Green

Write-Host "Ambiente configurado com sucesso!" -ForegroundColor Green
Write-Host "Para ativar o ambiente: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow