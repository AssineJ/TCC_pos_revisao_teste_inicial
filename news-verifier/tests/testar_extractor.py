from modules.extractor import extrair_conteudo
import json

print("=" * 70)
print("🧪 TESTE DO EXTRACTOR COM URL REAL")
print("=" * 70)
print()

# URL real do G1 (substitua por uma notícia atual se quiser)
url = "https://www.bbc.com/news/articles/czjvzxn0ekko"

print(f"Extraindo conteúdo de: {url}")
print()

resultado = extrair_conteudo(url)

if resultado['sucesso']:
    print("✅ EXTRAÇÃO BEM-SUCEDIDA!")
    print(f"\nMétodo: {resultado['metodo_extracao']}")
    print(f"\nTítulo:\n{resultado['titulo']}")
    print(f"\nTexto (primeiros 300 caracteres):\n{resultado['texto'][:300]}...")
    print(f"\nData: {resultado['data_publicacao']}")
    print(f"Autor: {resultado['autor']}")
    print(f"\nTamanho do texto: {len(resultado['texto'])} caracteres")
else:
    print("❌ EXTRAÇÃO FALHOU!")
    print(f"Erro: {resultado['erro']}")