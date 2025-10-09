import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 70)
print("🧪 TESTE INTEGRAÇÃO: APP + EXTRACTOR + NLP")
print("=" * 70)
print()

# Teste 1: Texto direto (mais fácil de controlar)
print("Teste 1: Enviar texto diretamente")
print("-" * 70)

texto_teste = """
O presidente Luiz Inácio Lula da Silva anunciou ontem uma importante 
reforma tributária que reduzirá os impostos sobre alimentos básicos 
em todo o Brasil. A medida será implementada pelo Ministério da Fazenda 
a partir de janeiro de 2025 e deve beneficiar milhões de brasileiros.
"""

dados = {
    "tipo": "texto",
    "conteudo": texto_teste
}

response = requests.post(f'{BASE_URL}/api/verificar', json=dados)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    resultado = response.json()
    
    print("\n✅ ANÁLISE COMPLETA:")
    print(f"\nVeracidade: {resultado['veracidade']}%")
    print(f"\nTítulo: {resultado['titulo_analisado'][:80]}...")
    
    print("\n🤖 ANÁLISE NLP (IA):")
    nlp = resultado['analise_nlp']
    
    print("\n  🏷️  Entidades encontradas:")
    for ent in nlp['entidades_encontradas']:
        print(f"    • {ent['texto']} ({ent['tipo']}) - Importância: {ent['importancia']}")
    
    print("\n  🔑 Palavras-chave:")
    print(f"    {', '.join(nlp['palavras_chave'])}")
    
    print("\n  🔍 Query de busca gerada:")
    print(f"    {nlp['query_busca']}")
    
    print("\n  📊 Estatísticas:")
    for chave, valor in nlp['estatisticas'].items():
        print(f"    • {chave}: {valor}")
    
    print("\n✅ A IA está funcionando! Pronta para próximo módulo!")
else:
    print(f"\n❌ Erro: {response.json()}")

print("\n" + "=" * 70)