"""
News Verifier API - Versão 1 (Minimal)
Sistema de Verificação de Veracidade de Notícias

Autor: Projeto Acadêmico
Data: 2025
"""

# ============================================================================
# IMPORTAÇÕES
# ============================================================================

from flask import Flask, request, jsonify
from config import Config
from modules.extractor import extrair_conteudo
import sys

# ============================================================================
# CONFIGURAÇÃO DA APLICAÇÃO FLASK
# ============================================================================

# Criar instância do Flask
app = Flask(__name__)

# Carregar configurações do config.py
app.config.from_object(Config)


# ============================================================================
# ROTA PRINCIPAL - VERIFICAR NOTÍCIA
# ============================================================================

@app.route('/api/verificar', methods=['POST'])
def verificar_noticia():
    """
    Endpoint principal que recebe uma notícia e retorna análise de veracidade.
    
    Método: POST
    Content-Type: application/json
    
    Body esperado:
    {
        "tipo": "url" ou "texto",
        "conteudo": "https://..." ou "texto da notícia..."
    }
    
    Retorna:
    {
        "veracidade": 75,
        "justificativa": "...",
        "fontes_consultadas": [...],
        "metadata": {...}
    }
    """
    
    try:
        # ====================================================================
        # ETAPA 1: RECEBER E VALIDAR DADOS
        # ====================================================================
        
        # Pegar dados JSON do body da requisição
        dados = request.get_json()
        
        # Validação básica: verificar se JSON foi enviado
        if not dados:
            return jsonify({
                "erro": "Nenhum dado JSON foi enviado",
                "codigo": "INVALID_JSON"
            }), 400  # 400 = Bad Request
        
        # Validação: verificar se campos obrigatórios existem
        if 'tipo' not in dados or 'conteudo' not in dados:
            return jsonify({
                "erro": "Campos obrigatórios: 'tipo' e 'conteudo'",
                "codigo": "MISSING_FIELDS"
            }), 400
        
        # Extrair dados
        tipo = dados['tipo']
        conteudo = dados['conteudo']
        
        # Validação: tipo deve ser 'url' ou 'texto'
        if tipo not in ['url', 'texto']:
            return jsonify({
                "erro": "Tipo deve ser 'url' ou 'texto'",
                "codigo": "INVALID_TYPE"
            }), 400
        
        # Validação: conteúdo não pode estar vazio
        if not conteudo or not conteudo.strip():
            return jsonify({
                "erro": "Conteúdo não pode estar vazio",
                "codigo": "EMPTY_CONTENT"
            }), 400
        
        # Validação: conteúdo muito curto
        if len(conteudo.strip()) < Config.MIN_CONTENT_LENGTH:
            return jsonify({
                "erro": Config.ERROR_MESSAGES['CONTENT_TOO_SHORT'],
                "codigo": "CONTENT_TOO_SHORT"
            }), 422
        
        # Validação: conteúdo muito longo
        if len(conteudo.strip()) > Config.MAX_CONTENT_LENGTH:
            return jsonify({
                "erro": Config.ERROR_MESSAGES['CONTENT_TOO_LONG'],
                "codigo": "CONTENT_TOO_LONG"
            }), 422
        
        
        # ====================================================================
        # ETAPA 2-7: PROCESSAMENTO (SIMULADO POR ENQUANTO)
        # ====================================================================
        
        # Aqui futuramente chamaremos os módulos:
        # - extractor.py (extrair conteúdo de URL)
        # - nlp_processor.py (processar com IA)
        # - searcher.py (buscar nas fontes)
        # - semantic_analyzer.py (análise semântica)
        # - scorer.py (calcular veracidade)
        
        # Por enquanto, retornamos dados simulados (dummy)
        resposta = {
            "veracidade": 65,
            "justificativa": f"Análise simulada para '{tipo}'. {Config.JUSTIFICATION_TEMPLATES['medium_veracity']}",
            "fontes_consultadas": [
                {
                    "nome": Config.TRUSTED_SOURCES[0]["nome"],
                    "url": f"{Config.TRUSTED_SOURCES[0]['url_base']}/exemplo",
                    "titulo": "Exemplo de notícia relacionada",
                    "similaridade": 0.72,
                    "status": "confirma"
                },
                {
                    "nome": Config.TRUSTED_SOURCES[1]["nome"],
                    "url": f"{Config.TRUSTED_SOURCES[1]['url_base']}/exemplo",
                    "titulo": "Outra notícia relacionada",
                    "similaridade": 0.58,
                    "status": "parcial"
                }
            ],
            "metadata": {
                "tipo_entrada": tipo,
                "tamanho_conteudo": len(conteudo),
                "versao_sistema": "1.0-minimal",
                "total_fontes_analisadas": 2,
                "fontes_disponiveis": len(Config.TRUSTED_SOURCES)
            }
        }
        
        # Retornar JSON com código 200 (sucesso)
        return jsonify(resposta), 200
    
    
    except Exception as e:
        # ====================================================================
        # TRATAMENTO DE ERROS INESPERADOS
        # ====================================================================
        
        # Capturar qualquer erro não tratado
        return jsonify({
            "erro": "Erro interno do servidor",
            "detalhes": str(e),
            "codigo": "INTERNAL_ERROR"
        }), 500  # 500 = Internal Server Error


# ============================================================================
# ROTA DE SAÚDE - VERIFICAR SE API ESTÁ FUNCIONANDO
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint simples para verificar se a API está online.
    
    Método: GET
    
    Retorna:
    {
        "status": "online",
        "versao": "1.0"
    }
    """
    return jsonify({
        "status": "online",
        "versao": "1.0-minimal",
        "mensagem": "News Verifier API está funcionando!"
    }), 200


# ============================================================================
# ROTA RAIZ - INFORMAÇÕES DA API
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """
    Rota raiz - Informações sobre a API
    """
    return jsonify({
        "nome": "News Verifier API",
        "versao": "1.0-minimal",
        "descricao": "Sistema de Verificação de Veracidade de Notícias",
        "endpoints": {
            "POST /api/verificar": "Verificar veracidade de notícia",
            "GET /api/health": "Verificar status da API",
            "GET /": "Informações da API"
        },
        "documentacao": "Envie POST para /api/verificar com JSON: {tipo: 'url'|'texto', conteudo: '...'}"
    }), 200


# ============================================================================
# INICIALIZAÇÃO DO SERVIDOR
# ============================================================================

if __name__ == '__main__':
    """
    Bloco de inicialização - só executa quando rodamos 'python app.py'
    Não executa quando importamos o app em outro arquivo
    """
    
    print("=" * 70)
    print("🚀 Iniciando News Verifier API...")
    print("=" * 70)
    print(f"📍 Servidor rodando em: http://127.0.0.1:5000")
    print(f"📍 Versão: 1.0-minimal")
    print(f"📍 Pressione Ctrl+C para parar o servidor")
    print("=" * 70)
    print()
    
    # Iniciar servidor Flask
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )