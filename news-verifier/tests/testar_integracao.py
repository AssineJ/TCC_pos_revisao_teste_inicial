import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 70)
print("🧪 TESTE DE INTEGRAÇÃO COMPLETO: APP + EXTRACTOR + NLP")
print("=" * 70)
print()

# ============================================================================
# Teste 1: TEXTO DIRETO
# ============================================================================

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

try:
    response = requests.post(f'{BASE_URL}/api/verificar', json=dados)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        resultado = response.json()
        
        print("\n✅ ANÁLISE COMPLETA:")
        print(f"\nVeracidade: {resultado['veracidade']}%")
        print(f"\nTítulo: {resultado['titulo_analisado'][:80]}...")
        
        # Verificar se tem análise NLP
        if 'analise_nlp' in resultado:
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
        else:
            print("\n⚠️  Análise NLP não encontrada na resposta")
            print("Resposta recebida:")
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        
        print("\n✅ Teste 1 concluído com sucesso!")
    else:
        print(f"\n❌ Erro {response.status_code}: {response.json()}")

except Exception as e:
    print(f"\n❌ ERRO INESPERADO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print()

# ============================================================================
# Teste 2: URL REAL (OPCIONAL)
# ============================================================================

#print("Teste 2: Enviar URL de notícia (opcional)")
#print("-" * 70)
#print("⚠️  Para testar com URL, cole uma URL real de notícia abaixo")
#print("https://g1.globo.com/rj/rio-de-janeiro/noticia/2025/10/08/secretaria-de-seguranca-publica-do-rj-alerta-para-golpe-com-uso-de-voz.ghtml")
#print()

# Descomente e cole uma URL real para testar:
url_noticia = "https://g1.globo.com/ac/acre/noticia/2025/10/08/vereadores-trocam-socos-e-empurroes-durante-sessao-em-camara-no-acre-video.ghtml"
dados_url = {
    "tipo": "url",
    "conteudo": url_noticia
}
response_url = requests.post(f'{BASE_URL}/api/verificar', json=dados_url)
print(json.dumps(response_url.json(), indent=2, ensure_ascii=False))

#print("Para testar URL, descomente as linhas acima e cole uma URL real")
#print()
#print("=" * 70)