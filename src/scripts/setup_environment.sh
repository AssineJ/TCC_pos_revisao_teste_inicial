@echo off
echo [INFO] Configurando ambiente News Verifier no Windows...

:: Criar ambiente virtual
python -m venv venv
echo [INFO] Ambiente virtual criado

:: Ativar ambiente virtual
call venv\Scripts\activate.bat
echo [INFO] Ambiente virtual ativado

:: Instalar dependências
pip install -r requirements\base.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha na instalação das dependências base
    exit /b 1
)

pip install -r requirements\dev.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha na instalação das dependências de desenvolvimento
    exit /b 1
)

:: Download do modelo spaCy em português
python -m spacy download pt_core_news_sm
echo [INFO] Modelo spaCy baixado

:: Configurar pre-commit
pre-commit install
echo [INFO] Pre-commit configurado

echo [SUCESSO] Ambiente configurado com sucesso!
echo [INSTRUÇÃO] Para ativar o ambiente: venv\Scripts\activate.bat