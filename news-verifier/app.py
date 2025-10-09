"""
News Verifier API - Versão Completa
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

app = Flask(__name__)
app.config.from_object(Config)


# ============================================================================
# ROTA PRINCIPAL - VERIFICAR NOTÍCIA
# ============================================================================

@app.route('/api/verificar', methods=['POST'])
def verificar_noticia():
    """
    Endpoint principal que recebe uma notícia e retorna análise de veracidade.
    """
    
    try:
        # ====================================================================
        # ETAPA 1: RECEBER E VALIDAR DADOS
        # ====================================================================
        
        dados = request.get_json()
        
        if not dados:
            return jsonify({
                "erro": Config.ERROR_MESSAGES['INVALID_JSON'],
                "codigo": "INVALID_JSON"
            }), 400
        
        if 'tipo' not in dados or 'conteudo' not in dados:
            return jsonify({
                "erro": Config.ERROR_MESSAGES['MISSING_FIELDS'],
                "codigo": "MISSING_FIELDS"
            }), 400
        
        tipo = dados['tipo']
        conteudo = dados['conteudo']
        
        if tipo not in ['url', 'texto']:
            return jsonify({
                "erro": Config.ERROR_MESSAGES['INVALID_TYPE'],
                "codigo": "INVALID_TYPE"
            }), 400
        
        if not conteudo or not conteudo.strip():
            return jsonify({
                "erro": Config.ERROR_MESSAGES['EMPTY_CONTENT'],
                "codigo": "EMPTY_CONTENT"
            }), 400
        
        if len(conteudo.strip()) < Config.MIN_CONTENT_LENGTH:
            return jsonify({
                "erro": Config.ERROR_MESSAGES['CONTENT_TOO_SHORT'],
                "codigo": "CONTENT_TOO_SHORT"
            }), 422
        
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
            titulo_noticia = texto_para_analise[:100] + "..."
        
        
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
        
        # Preparar fontes consultadas com dados reais da busca
        fontes_consultadas = []
        for fonte_nome, fonte_resultados in resultado_busca.items():
            if fonte_nome == 'metadata':
                continue
            
            if fonte_resultados:
                primeiro = fonte_resultados[0]
                fontes_consultadas.append({
                    "nome": fonte_nome,
                    "url": primeiro['url'],
                    "titulo": primeiro['title'],
                    "snippet": primeiro['snippet'][:100] + "..." if primeiro['snippet'] else "N/A",
                    "total_resultados": len(fonte_resultados)
                })
        
        # Montar resposta completa
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
            "fontes_consultadas": fontes_consultadas,
            "metadata": {
                "tipo_entrada": tipo,
                "url_original": url_original,
                "tamanho_conteudo": len(texto_para_analise),
                "versao_sistema": "1.0-with-search",
                "total_fontes_consultadas": len(fontes_consultadas),
                "fontes_disponiveis": len(Config.TRUSTED_SOURCES),
                "processamento_nlp_completo": True,
                "busca_realizada": True,
                "total_resultados_busca": resultado_busca['metadata']['total_resultados'],
                "modo_busca": resultado_busca['metadata']['modo_busca']
            }
        }
        
        return jsonify(resposta), 200
    
    
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "erro": "Erro interno do servidor",
            "detalhes": str(e),
            "codigo": "INTERNAL_ERROR"
        }), 500


# ============================================================================
# ROTA DE SAÚDE
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está online"""
    return jsonify({
        "status": "online",
        "versao": "1.0-with-search",
        "mensagem": "News Verifier API está funcionando!"
    }), 200


# ============================================================================
# ROTA RAIZ
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """Rota raiz - Informações sobre a API"""
    return jsonify({
        "nome": "News Verifier API",
        "versao": "1.0-with-search",
        "descricao": "Sistema de Verificação de Veracidade de Notícias",
        "modulos_ativos": [
            "✅ Extractor (extração de conteúdo)",
            "✅ NLP Processor (análise com IA)",
            "✅ Searcher (busca nas fontes)",
            "⏳ Scraper (próximo)",
            "⏳ Semantic Analyzer (próximo)",
            "⏳ Scorer (próximo)"
        ],
        "endpoints": {
            "POST /api/verificar": "Verificar veracidade de notícia",
            "GET /api/health": "Verificar status da API",
            "GET /": "Informações da API"
        }
    }), 200


# ============================================================================
# INICIALIZAÇÃO DO SERVIDOR
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Iniciando News Verifier API...")
    print("=" * 70)
    print(f"📍 Servidor rodando em: http://127.0.0.1:{Config.PORT}")
    print(f"📍 Versão: 1.0-with-search")
    print(f"📍 Modo de busca: {Config.SEARCH_MODE}")
    print(f"📍 Pressione Ctrl+C para parar o servidor")
    print("=" * 70)
    print()
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )