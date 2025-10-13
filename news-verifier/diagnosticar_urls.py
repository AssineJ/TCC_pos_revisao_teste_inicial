from modules.searcher import buscar_noticias
from modules.scraper import scrape_noticias
from modules.nlp_processor import processar_texto

print("=" * 70)
print("🔍 DIAGNÓSTICO DE URLs TRUNCADAS")
print("=" * 70)
print()

# Usar a notícia problemática
texto_teste = """
O Supremo Tribunal Federal teve apenas três mulheres ministras em sua 
história e movimentos sociais começam a cobrar do presidente Lula pela 
sucessão de Barroso. A discussão sobre diversidade de gênero no STF 
ganhou força com a aproximação da aposentadoria do ministro.
"""

print("ETAPA 1: Processamento NLP")
print("-" * 70)
resultado_nlp = processar_texto(texto_teste)
print(f"Query: {resultado_nlp['query_busca']}")
print()

print("ETAPA 2: Busca nas fontes")
print("-" * 70)
resultado_busca = buscar_noticias(resultado_nlp['query_busca'])

# Verificar URLs da busca
for fonte_nome, resultados in resultado_busca.items():
    if fonte_nome == 'metadata':
        continue
    
    if resultados:
        print(f"\n{fonte_nome}:")
        for i, r in enumerate(resultados[:2], 1):
            url = r.get('url', '')
            print(f"  {i}. Tamanho URL: {len(url)} caracteres")
            print(f"     URL: {url}")
            print(f"     Completa? {'✅' if url.startswith('http') and len(url) > 50 else '❌'}")

print()
print("=" * 70)
print("ETAPA 3: Scraping")
print("-" * 70)

# Fazer scraping de apenas 1 URL de cada fonte para testar
resultado_busca_reduzido = {}
for fonte_nome, resultados in resultado_busca.items():
    if fonte_nome == 'metadata':
        resultado_busca_reduzido['metadata'] = resultados
    else:
        # Pegar apenas primeira URL
        resultado_busca_reduzido[fonte_nome] = resultados[:1] if resultados else []

resultado_scraping = scrape_noticias(resultado_busca_reduzido)

# Verificar URLs após scraping
for fonte_nome, conteudos in resultado_scraping.items():
    if fonte_nome == 'metadata':
        continue
    
    if conteudos:
        print(f"\n{fonte_nome}:")
        for i, c in enumerate(conteudos, 1):
            url = c.get('url', '')
            print(f"  {i}. Tamanho URL: {len(url)} caracteres")
            print(f"     URL: {url}")
            print(f"     Completa? {'✅' if len(url) > 50 else '❌'}")
            print(f"     Sucesso scraping? {'✅' if c.get('sucesso') else '❌'}")

print()
print("=" * 70)
print("🎯 ANÁLISE")
print("=" * 70)
print()

# Verificar se alguma URL está truncada
urls_truncadas = []
for fonte_nome, conteudos in resultado_scraping.items():
    if fonte_nome == 'metadata':
        continue
    for c in conteudos:
        url = c.get('url', '')
        if url and len(url) < 50:
            urls_truncadas.append((fonte_nome, url))

if urls_truncadas:
    print("❌ URLs TRUNCADAS ENCONTRADAS:")
    for fonte, url in urls_truncadas:
        print(f"   • {fonte}: {url}")
else:
    print("✅ NENHUMA URL TRUNCADA!")

print()
print("=" * 70)