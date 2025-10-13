"""
News Verifier API - Versão Completa com Análise Semântica

Sistema de Verificação de Veracidade de Notícias

Autor: Projeto Acadêmico
Data: 2025
"""

from flask import Flask, request, jsonify
from config import Config
from modules.extractor import extrair_conteudo
from modules.nlp_processor import processar_texto
from modules.searcher import buscar_noticias
from modules.filters import filtrar_busca, filtrar_scraping
from modules.scraper import scrape_noticias
from modules.semantic_analyzer import analisar_semantica
from modules.scorer import calcular_veracidade
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Criar instância do Flask
app = Flask(__name__)

# Carregar configurações do config.py
app.config.from_object(Config)


@app.route('/api/verificar', methods=['POST'])
def verificar_noticia():
    """
    Endpoint principal que recebe uma notícia e retorna análise de veracidade.
    """
    
    try:
        # ETAPA 1: VALIDAR DADOS
        dados = request.get_json()
        
        if not dados:
            return jsonify({
                "erro": "Nenhum dado JSON foi enviado",
                "codigo": "INVALID_JSON"
            }), 400
        
        if 'tipo' not in dados or 'conteudo' not in dados:
            return jsonify({
                "erro": "Campos obrigatórios: 'tipo' e 'conteudo'",
                "codigo": "MISSING_FIELDS"
            }), 400
        
        tipo = dados['tipo']
        conteudo = dados['conteudo']
        
        if tipo not in ['url', 'texto']:
            return jsonify({
                "erro": "Tipo deve ser 'url' ou 'texto'",
                "codigo": "INVALID_TYPE"
            }), 400
        
        if not conteudo or not conteudo.strip():
            return jsonify({
                "erro": "Conteúdo não pode estar vazio",
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
        
        
        # ETAPA 2: EXTRAIR CONTEÚDO (se for URL)
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
        
        else:
            texto_para_analise = conteudo
            titulo_noticia = texto_para_analise[:100] + "..."
        
        
        # ETAPA 3: PROCESSAR COM NLP (IA!)
        print(f"🤖 Processando texto com IA...")
        resultado_nlp = processar_texto(texto_para_analise)
        
        print(f"✅ NLP concluído:")
        print(f"   - {len(resultado_nlp['entidades'])} entidades encontradas")
        print(f"   - {len(resultado_nlp['palavras_chave'])} palavras-chave extraídas")
        print(f"   - Query de busca: {resultado_nlp['query_busca']}")
        
        
        # ETAPA 4: BUSCAR NAS FONTES CONFIÁVEIS
        print(f"🔍 Buscando nas fontes confiáveis...")
        resultado_busca = buscar_noticias(resultado_nlp['query_busca'])
        
        print(f"✅ Busca concluída:")
        print(f"   - Total de resultados: {resultado_busca['metadata']['total_resultados']}")
        print(f"   - Fontes com sucesso: {resultado_busca['metadata']['fontes_com_sucesso']}/{resultado_busca['metadata']['total_fontes']}")
        
        # APLICAR FILTROS NA BUSCA
        resultado_busca_filtrado = filtrar_busca(resultado_busca)
        
        print(f"✅ Filtros aplicados:")
        print(f"   - Mantidos: {resultado_busca_filtrado['metadata']['total_resultados']}")
        print(f"   - Filtrados: {resultado_busca_filtrado['metadata'].get('total_filtrados', 0)}")
        
        
        # ETAPA 5: EXTRAIR CONTEÚDO DAS URLs ENCONTRADAS
        print(f"📥 Extraindo conteúdo das notícias encontradas...")
        resultado_scraping = scrape_noticias(resultado_busca_filtrado)
        
        print(f"✅ Scraping concluído:")
        print(f"   - Total processado: {resultado_scraping['metadata']['total_scraped']}")
        print(f"   - Sucessos: {resultado_scraping['metadata']['total_sucesso']}")
        print(f"   - Taxa: {resultado_scraping['metadata']['taxa_sucesso']:.1f}%")
        
        # APLICAR FILTROS NO SCRAPING
        resultado_scraping_filtrado = filtrar_scraping(resultado_scraping, texto_para_analise)
        
        print(f"✅ Filtros aplicados:")
        print(f"   - Mantidos: {resultado_scraping_filtrado['metadata']['total_sucesso']}")
        print(f"   - Filtrados: {resultado_scraping_filtrado['metadata'].get('total_filtrados', 0)}")
        
        
        # ETAPA 6: ANÁLISE SEMÂNTICA COM IA
        print(f"🔬 Analisando similaridade semântica com IA...")
        resultado_analise = analisar_semantica(texto_para_analise, resultado_scraping_filtrado)
        
        print(f"✅ Análise semântica concluída:")
        print(f"   - Confirmam forte: {resultado_analise['metadata']['confirmam_forte']}")
        print(f"   - Confirmam parcial: {resultado_analise['metadata']['confirmam_parcial']}")
        print(f"   - Apenas mencionam: {resultado_analise['metadata']['apenas_mencionam']}")
        
        
        # ETAPA 7: CÁLCULO DE VERACIDADE FINAL (SCORER)
        print(f"🎯 Calculando veracidade final...")
        resultado_score = calcular_veracidade(resultado_analise, {
            'tipo_entrada': tipo,
            'tamanho_conteudo': len(texto_para_analise),
            'total_fontes_buscadas': resultado_busca['metadata']['total_resultados']
        })
        
        print(f"✅ Score calculado: {resultado_score['veracidade']}%")
        print(f"   Nível de confiança: {resultado_score['nivel_confianca']}")
        
        # Preparar fontes consultadas
        fontes_consultadas = []
        
        # Primeiro, coletar TODAS as URLs originais do resultado da busca
        # para garantir que temos as URLs completas
        urls_originais_busca = {}
        for fonte_nome, fonte_resultados in resultado_busca_filtrado.items():
            if fonte_nome == 'metadata':
                continue
            for res in fonte_resultados:
                url = res.get('url', '')
                # Usar título como chave para mapear
                titulo_chave = res.get('title', '')[:50]
                urls_originais_busca[titulo_chave] = url
        
        for fonte_nome, fonte_analises in resultado_analise.items():
            if fonte_nome == 'metadata':
                continue
            
            for analise in fonte_analises:
                if analise.get('sucesso'):
                    # Tentar recuperar URL original da busca
                    titulo = analise.get('titulo', '')
                    titulo_chave = titulo[:50]
                    
                    # Usar URL da análise, mas verificar se não está truncada
                    url_analise = analise.get('url', '')
                    
                    # Se URL parece truncada (< 80 chars), tentar recuperar original
                    if len(url_analise) < 80 and titulo_chave in urls_originais_busca:
                        url_final = urls_originais_busca[titulo_chave]
                        print(f"[RECUPERADO] URL completa de {fonte_nome}: {len(url_final)} chars")
                    else:
                        url_final = url_analise
                    
                    fontes_consultadas.append({
                        "nome": fonte_nome,
                        "url": url_final,  # URL GARANTIDAMENTE COMPLETA
                        "titulo": titulo,
                        "similaridade": analise.get('similaridade', 0),
                        "status": analise.get('status', ''),
                        "motivo": analise.get('motivo', '')
                    })
        
        fontes_consultadas.sort(key=lambda x: x['similaridade'], reverse=True)
        
        # Montar resposta final
        meta_analise = resultado_analise['metadata']
        
        resposta = {
            "veracidade": resultado_score['veracidade'],
            "justificativa": resultado_score['justificativa'],
            "nivel_confianca": resultado_score['nivel_confianca'],
            "titulo_analisado": titulo_noticia,
            "tamanho_texto_analisado": len(texto_para_analise),
            "calculo_detalhado": resultado_score['detalhes'],
            "analise_nlp": {
                "entidades_encontradas": resultado_nlp['entidades'][:5],
                "palavras_chave": resultado_nlp['palavras_chave'][:8],
                "query_busca": resultado_nlp['query_busca'],
                "estatisticas": resultado_nlp['estatisticas']
            },
            "analise_semantica": {
                "total_analisados": meta_analise['total_analisados'],
                "confirmam_forte": meta_analise['confirmam_forte'],
                "confirmam_parcial": meta_analise['confirmam_parcial'],
                "apenas_mencionam": meta_analise['apenas_mencionam'],
                "nao_relacionados": meta_analise['nao_relacionados']
            },
            "fontes_consultadas": fontes_consultadas[:10],
            "metadata": {
                "tipo_entrada": tipo,
                "url_original": url_original,
                "tamanho_conteudo": len(texto_para_analise),
                "versao_sistema": "1.0-final",
                "total_fontes_consultadas": len(fontes_consultadas),
                "fontes_disponiveis": len(Config.TRUSTED_SOURCES),
                "processamento_nlp_completo": True,
                "busca_realizada": True,
                "filtros_aplicados": True,
                "scraping_realizado": True,
                "analise_semantica_realizada": True,
                "scoring_completo": True,
                "total_resultados_busca": resultado_busca['metadata']['total_resultados'],
                "total_scraped": resultado_scraping_filtrado['metadata']['total_scraped'],
                "total_analisados": meta_analise['total_analisados'],
                "modo_busca": resultado_busca['metadata']['modo_busca']
            }
        }
        
        return jsonify(resposta), 200
    
    
    except Exception as e:
        return jsonify({
            "erro": "Erro interno do servidor",
            "detalhes": str(e),
            "codigo": "INTERNAL_ERROR"
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está online."""
    return jsonify({
        "status": "online",
        "versao": "1.0-final",
        "mensagem": "News Verifier API está funcionando!",
        "modulos_ativos": [
            "extractor",
            "nlp_processor",
            "searcher",
            "filters",
            "scraper",
            "semantic_analyzer",
            "scorer"
        ]
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Rota raiz - Informações sobre a API"""
    return jsonify({
        "nome": "News Verifier API",
        "versao": "1.0-complete",
        "descricao": "Sistema de Verificação de Veracidade de Notícias com IA",
        "endpoints": {
            "POST /api/verificar": "Verificar veracidade de notícia",
            "GET /api/health": "Verificar status da API",
            "GET /": "Informações da API"
        },
        "fontes_confiaveis": [fonte['nome'] for fonte in Config.TRUSTED_SOURCES],
        "tecnologias": [
            "Flask",
            "spaCy (NLP)",
            "sentence-transformers (IA Semântica)",
            "newspaper3k",
            "BeautifulSoup"
        ]
    }), 200


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Iniciando News Verifier API...")
    print("=" * 70)
    print(f"📍 Servidor rodando em: http://127.0.0.1:{Config.PORT}")
    print(f"📍 Versão: 1.0-final (COMPLETA)")
    print(f"📍 Pressione Ctrl+C para parar o servidor")
    print("=" * 70)
    print()
    print("✅ Módulos carregados:")
    print("   1. ✅ Extractor (URLs)")
    print("   2. ✅ NLP Processor (spaCy)")
    print("   3. ✅ Searcher (Busca Híbrida)")
    print("   4. ✅ Filters (Anti-paywall/404)")
    print("   5. ✅ Scraper (Conteúdo)")
    print("   6. ✅ Semantic Analyzer (IA)")
    print("   7. ✅ Scorer (Veracidade)")
    print("=" * 70)
    print()
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )