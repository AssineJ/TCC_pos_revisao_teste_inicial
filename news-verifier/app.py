"""
News Verifier API - Versão 1.5 (Com NLP e Extractor)
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
from modules.nlp_processor import processar_texto
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
        "titulo_analisado": "...",
        "analise_nlp": {...},
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
                "erro": Config.ERROR_MESSAGES['INVALID_JSON'],
                "codigo": "INVALID_JSON"
            }), 400
        
        # Validação: verificar se campos obrigatórios existem
        if 'tipo' not in dados or 'conteudo' not in dados:
            return jsonify({
                "erro": Config.ERROR_MESSAGES['MISSING_FIELDS'],
                "codigo": "MISSING_FIELDS"
            }), 400
        
        # Extrair dados
        tipo = dados['tipo']
        conteudo = dados['conteudo']
        
        # Validação: tipo deve ser 'url' ou 'texto'
        if tipo not in ['url', 'texto']:
            return jsonify({
                "erro": Config.ERROR_MESSAGES['INVALID_TYPE'],
                "codigo": "INVALID_TYPE"
            }), 400
        
        # Validação: conteúdo não pode estar vazio
        if not conteudo or not conteudo.strip():
            return jsonify({
                "erro": Config.ERROR_MESSAGES['EMPTY_CONTENT'],
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
        # ETAPA 2: EXTRAIR CONTEÚDO (se for URL)
        # ====================================================================
        
        texto_para_analise = ""
        titulo_noticia = ""
        url_original = conteudo if tipo == 'url' else None
        
        if tipo == 'url':
            # Usar o extractor para pegar conteúdo da URL
            print(f"📥 Extraindo conteúdo de: {conteudo}")
            resultado_extracao = extrair_conteudo(conteudo)
            
            if not resultado_extracao['sucesso']:
                return jsonify({
                    "erro": Config.ERROR_MESSAGES['NO_CONTENT_EXTRACTED'],
                    "detalhes": resultado_extracao['erro'],
                    "codigo": "EXTRACTION_FAILED"
                }), 422
            
            texto_para_analise = resultado_extracao['texto']
            titulo_noticia = resultado_extracao['titulo']
            print(f"✅ Conteúdo extraído: {len(texto_para_analise)} caracteres")
        
        else:  # tipo == 'texto'
            texto_para_analise = conteudo
            titulo_noticia = texto_para_analise[:100] + "..."
        
        
        # ====================================================================
        # ETAPA 3: PROCESSAR COM NLP (IA!)
        # ====================================================================
        
        try:
            print(f"🤖 Processando texto com IA...")
            print(f"   Tamanho do texto: {len(texto_para_analise)} caracteres")
            
            resultado_nlp = processar_texto(texto_para_analise)
            
            print(f"✅ NLP concluído:")
            print(f"   - {len(resultado_nlp['entidades'])} entidades encontradas")
            print(f"   - {len(resultado_nlp['palavras_chave'])} palavras-chave extraídas")
            print(f"   - Query de busca: {resultado_nlp['query_busca']}")
            
        except Exception as e:
            print(f"❌ ERRO no processamento NLP: {str(e)}")
            return jsonify({
                "erro": "Erro no processamento NLP",
                "detalhes": str(e),
                "codigo": "NLP_ERROR"
            }), 500
        
        
        # ====================================================================
        # ETAPA 4-7: BUSCA E ANÁLISE (SIMULADO POR ENQUANTO)
        # ====================================================================
        
        # Aqui futuramente chamaremos os módulos:
        # - searcher.py (buscar nas fontes)
        # - semantic_analyzer.py (análise semântica)
        # - scorer.py (calcular veracidade)
        
        # Por enquanto, retornamos dados simulados com informações REAIS do NLP
        resposta = {
            "veracidade": 65,
            "justificativa": f"Análise simulada. {Config.JUSTIFICATION_TEMPLATES['medium_veracity']}",
            "titulo_analisado": titulo_noticia,
            "tamanho_texto_analisado": len(texto_para_analise),
            "analise_nlp": {
                "entidades_encontradas": resultado_nlp['entidades'][:5],
                "palavras_chave": resultado_nlp['palavras_chave'][:8],
                "query_busca": resultado_nlp['query_busca'],
                "estatisticas": resultado_nlp['estatisticas']
            },
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
                "url_original": url_original,
                "tamanho_conteudo": len(texto_para_analise),
                "versao_sistema": "1.5-with-nlp",
                "total_fontes_analisadas": 2,
                "fontes_disponiveis": len(Config.TRUSTED_SOURCES),
                "processamento_nlp_completo": True
            }
        }
        
        # Retornar JSON com código 200 (sucesso)
        return jsonify(resposta), 200
    
    
    except Exception as e:
        # ====================================================================
        # TRATAMENTO DE ERROS INESPERADOS
        # ====================================================================
        
        print(f"❌ ERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "erro": Config.ERROR_MESSAGES['INTERNAL_ERROR'],
            "detalhes": str(e),
            "codigo": "INTERNAL_ERROR"
        }), 500


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
        "versao": "1.5"
    }
    """
    return jsonify({
        "status": "online",
        "versao": "1.5-with-nlp",
        "mensagem": "News Verifier API está funcionando!",
        "modulos_ativos": ["extractor", "nlp_processor"]
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
        "versao": "1.5-with-nlp",
        "descricao": "Sistema de Verificação de Veracidade de Notícias com IA",
        "modulos": {
            "extractor": "Extração de conteúdo de URLs",
            "nlp_processor": "Processamento com IA (spaCy)",
            "searcher": "Em desenvolvimento",
            "semantic_analyzer": "Em desenvolvimento",
            "scorer": "Em desenvolvimento"
        },
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
    """
    
    print("=" * 70)
    print("🚀 Iniciando News Verifier API...")
    print("=" * 70)
    print(f"📍 Servidor rodando em: http://127.0.0.1:{Config.PORT}")
    print(f"📍 Versão: 1.5-with-nlp")
    print(f"📍 Módulos ativos: extractor.py, nlp_processor.py")
    print(f"📍 Pressione Ctrl+C para parar o servidor")
    print("=" * 70)
    print()
    
    # Iniciar servidor Flask
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )