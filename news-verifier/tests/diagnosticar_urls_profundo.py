from modules.searcher import buscar_noticias
from modules.nlp_processor import processar_texto
import json

print("=" * 70)
print("🔍 DIAGNÓSTICO PROFUNDO DE URLs")
print("=" * 70)
print()

texto = "Bolsonaro sanciona lei que cria o 'Dia do Orgulho Heterossexual' em 2024"

print("ETAPA 1: Processamento NLP")
resultado_nlp = processar_texto(texto)
query = resultado_nlp['query_busca']
print(f"Query: {query}")
print()

print("ETAPA 2: Busca")
print("-" * 70)
resultado_busca = buscar_noticias(query)

# Verificar cada fonte
for fonte_nome, resultados in resultado_busca.items():
    if fonte_nome == 'metadata':
        continue
    
    if resultados:
        print(f"\n{fonte_nome}:")
        for i, r in enumerate(resultados[:2], 1):
            url = r.get('url', '')
            print(f"\n  Resultado {i}:")
            print(f"    Tamanho: {len(url)} caracteres")
            print(f"    URL completa: {url}")
            print(f"    Tem '...'? {'SIM ❌' if '...' in url else 'NÃO ✅'}")
            print(f"    Termina corretamente? {'SIM ✅' if url.endswith(('.html', '.ghtml', '.shtml', '/')) else 'NÃO ❌'}")

print()
print("=" * 70)
print("ANÁLISE:")

# Contar URLs problemáticas
total_urls = 0
urls_ok = 0
urls_truncadas = 0

for fonte_nome, resultados in resultado_busca.items():
    if fonte_nome == 'metadata':
        continue
    for r in resultados:
        url = r.get('url', '')
        total_urls += 1
        if '...' in url or not url.endswith(('.html', '.ghtml', '.shtml', '/')):
            urls_truncadas += 1
        else:
            urls_ok += 1

print(f"Total URLs: {total_urls}")
print(f"URLs OK: {urls_ok}")
print(f"URLs truncadas: {urls_truncadas}")

if urls_truncadas > 0:
    print("\n❌ URLs ESTÃO SENDO TRUNCADAS NO SEARCHER!")
else:
    print("\n✅ URLs do searcher estão OK!")
    print("   O problema pode ser no scraper ou app.py")