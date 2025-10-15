import os
import re

print("=" * 70)
print("🔍 BUSCANDO TRUNCAMENTOS NO CÓDIGO")
print("=" * 70)
print()

# Padrões que podem truncar strings
patterns = [
    r'\[:70\]',
    r'\[:80\]',
    r'\[:60\]',
    r'\.\.\.\"',
    r'url\[:',
]

arquivos_verificar = [
    'app.py',
    'modules/extractor.py',
    'modules/scraper.py',
    'modules/semantic_analyzer.py',
    'modules/scorer.py',
    'modules/filters.py',
]

encontrou_problema = False

for arquivo in arquivos_verificar:
    if not os.path.exists(arquivo):
        continue
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    for i, linha in enumerate(linhas, 1):
        for pattern in patterns:
            if re.search(pattern, linha) and 'print' not in linha.lower():
                print(f"⚠️  {arquivo}:{i}")
                print(f"   {linha.strip()}")
                print()
                encontrou_problema = True

if not encontrou_problema:
    print("✅ Nenhum truncamento óbvio encontrado no código!")
    print()
    print("💡 O problema pode estar em:")
    print("   1. Biblioteca externa (newspaper3k, BeautifulSoup)")
    print("   2. Flask limitando tamanho de resposta")
    print("   3. Alguma transformação JSON")
else:
    print("=" * 70)
    print("❌ ENCONTRADOS POSSÍVEIS TRUNCAMENTOS!")
    print("   Revise os arquivos acima")