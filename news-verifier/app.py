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
from modules.nlp_processor import processar_texto
from modules.searcher import buscar_noticias
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
                    "erro": "Não foi possível extrair conteúdo da URL",
                    "detalhes": resultado_extracao['erro'],
                    "codigo": "EXTRACTION_FAILED"
                }), 422
            
            texto_para_analise = resultado_extracao['texto']
            titulo_noticia = resultado_extracao['titulo']
            print(f"✅ Conteúdo extraído: {len(texto_para_analise)} caracteres")
        
        else:  # tipo == 'texto'
            texto_para_analise = conteudo
            titulo_noticia = texto_para_analise[:100] + "..."  # Primeiros 100 chars como "título"
        
        
        # ====================================================================
        # ETAPA 3: PROCESSAR COM NLP (IA!)
        # ====================================================================
        
        print(f"🤖 Processando texto com IA...")
        resultado_nlp = processar_texto(texto_para_analise)
        
        print(f"✅ NLP concluído:")
        print(f"   - {len(resultado_nlp['entidades'])} entidades encontradas")
        print(f"   - {len(resultado_nlp['palavras_chave'])} palavras-chave extraídas")
        print(f"   - Query de busca: {resultado_nlp['query_busca']}")
        
        
        # ====================================================================
        # ETAPA 4: BUSCAR NAS FONTES CONFIÁVEIS
        # ====================================================================
        
        print(f"🔍 Buscando nas fontes confiáveis...")
        resultado_busca = buscar_noticias(resultado_nlp['query_busca'])
        
        print(f"✅ Busca concluída:")
        print(f"   - Total de resultados: {resultado_busca['metadata']['total_resultados']}")
        print(f"   - Fontes com sucesso: {resultado_busca['metadata']['fontes_com_sucesso']}/{resultado_busca['metadata']['total_fontes']}")
        
        
        # ====================================================================
        # ETAPA 5-7: SCRAPING, ANÁLISE E SCORING (SIMULADO POR ENQUANTO)
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
            "justificativa": f"Análise simulada. {Config.JUSTIFICATION_TEMPLATES['medium_veracity']}",
            "titulo_analisado": titulo_noticia,
            "tamanho_texto_analisado": len(texto_para_analise),
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
                "versao_sistema": "1.0-with-search",
                "total_fontes_consultadas": 2,
                "fontes_disponiveis": len(Config.TRUSTED_SOURCES),
                "processamento_nlp_completo": True,
                "busca_realizada": True,
                "total_resultados_busca": resultado_busca['metadata']['total_resultados'],
                "modo_busca": resultado_busca['metadata']['modo_busca']
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