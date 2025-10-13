from modules.nlp_processor import processar_texto
from modules.searcher import buscar_noticias
from modules.scraper import scrape_noticias
from modules.semantic_analyzer import analisar_semantica

print("=" * 70)
print("🧪 TESTE INTEGRAÇÃO COMPLETA COM IA SEMÂNTICA")
print("=" * 70)
print()

texto_original = """
O presidente Luiz Inácio Lula da Silva anunciou nesta semana uma 
importante reforma tributária que vai reduzir impostos sobre alimentos 
básicos em todo o Brasil. A medida será implementada pelo Ministério 
da Fazenda e deve beneficiar milhões de famílias brasileiras.
"""

print("📝 Texto original:")
print(texto_original.strip())
print()

# ETAPA 1: NLP
print("ETAPA 1: Processamento NLP...")
resultado_nlp = processar_texto(texto_original)
print(f"✅ Query gerada: {resultado_nlp['query_busca']}")
print()

# ETAPA 2: Busca
print("ETAPA 2: Buscando nas fontes...")
resultado_busca = buscar_noticias(resultado_nlp['query_busca'])
print(f"✅ Encontrados: {resultado_busca['metadata']['total_resultados']} resultados")
print()

# ETAPA 3: Scraping
print("ETAPA 3: Extraindo conteúdo...")
conteudos = scrape_noticias(resultado_busca)
print(f"✅ Extraídos: {conteudos['metadata']['total_sucesso']} conteúdos")
print()

# ETAPA 4: Análise Semântica (NOVO!)
print("ETAPA 4: Análise semântica com IA...")
analise = analisar_semantica(texto_original, conteudos)
print()

# Mostrar resultados
print("=" * 70)
print("📊 RESULTADOS DA ANÁLISE SEMÂNTICA:")
print("=" * 70)
print()

meta = analise['metadata']
print(f"Total analisado: {meta['total_analisados']}")
print(f"Confirmam forte: {meta['confirmam_forte']}")
print(f"Confirmam parcial: {meta['confirmam_parcial']}")
print(f"Apenas mencionam: {meta['apenas_mencionam']}")
print(f"Não relacionados: {meta['nao_relacionados']}")
print()

# Mostrar top 3 mais similares
print("🏆 TOP 3 MAIS SIMILARES:")
print()

todas_analises = []
for fonte_nome, fonte_analises in analise.items():
    if fonte_nome != 'metadata':
        for a in fonte_analises:
            if a.get('sucesso'):
                todas_analises.append({
                    'fonte': fonte_nome,
                    **a
                })

# Ordenar por similaridade
todas_analises.sort(key=lambda x: x.get('similaridade', 0), reverse=True)

for i, a in enumerate(todas_analises[:3], 1):
    print(f"{i}. {a['fonte']} - Similaridade: {a['similaridade']:.4f}")
    print(f"   Status: {a['status']}")
    print(f"   Título: {a['titulo'][:60]}...")
    print(f"   URL: {a['url']}")
    print()

print("=" * 70)
print("🎉 SISTEMA QUASE COMPLETO!")
print("=" * 70)