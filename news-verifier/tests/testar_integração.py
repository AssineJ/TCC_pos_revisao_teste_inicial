import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 70)
print("🧪 TESTE DE INTEGRAÇÃO: APP + EXTRACTOR + NLP")
print("=" * 70)
print()

# URL da notícia real do G1
url_noticia = "https://ge.globo.com/futebol/times/sao-paulo/noticia/2025/10/07/sao-paulo-envia-oficio-e-pede-publicacao-de-audios-do-var-do-classico-cbf-vai-consultar-fifa.ghtml"

print(f"📰 Notícia: {url_noticia}")
print()
print("Teste: Enviar URL de notícia do G1")
print("-" * 70)

dados = {
    "tipo": "url",
    "conteudo": url_noticia
}

try:
    response = requests.post(f'{BASE_URL}/api/verificar', json=dados)
    print(f"Status HTTP: {response.status_code}")
    print()
    
    if response.status_code == 200:
        resultado = response.json()
        
        print("✅ ANÁLISE COMPLETA BEM-SUCEDIDA!")
        print("=" * 70)
        
        # Informações gerais
        print(f"\n📊 VERACIDADE: {resultado['veracidade']}%")
        print(f"\n📝 TÍTULO ANALISADO:")
        print(f"   {resultado['titulo_analisado'][:100]}...")
        
        print(f"\n📏 TAMANHO DO TEXTO: {resultado['tamanho_texto_analisado']} caracteres")
        
        # Análise NLP
        print("\n🤖 ANÁLISE DE IA (NLP):")
        print("-" * 70)
        
        nlp = resultado['analise_nlp']
        
        print("\n  🏷️  ENTIDADES ENCONTRADAS:")
        if nlp['entidades_encontradas']:
            for ent in nlp['entidades_encontradas']:
                print(f"    • {ent['texto']} ({ent['tipo']}) - Importância: {ent['importancia']}")
        else:
            print("    Nenhuma entidade encontrada")
        
        print("\n  🔑 PALAVRAS-CHAVE:")
        if nlp['palavras_chave']:
            print(f"    {', '.join(nlp['palavras_chave'])}")
        else:
            print("    Nenhuma palavra-chave encontrada")
        
        print("\n  🔍 QUERY DE BUSCA GERADA:")
        print(f"    {nlp['query_busca']}")
        
        print("\n  📊 ESTATÍSTICAS:")
        for chave, valor in nlp['estatisticas'].items():
            print(f"    • {chave}: {valor}")
        
        # Justificativa
        print("\n💬 JUSTIFICATIVA:")
        print(f"   {resultado['justificativa']}")
        
        # Fontes consultadas
        print("\n📰 FONTES CONSULTADAS (simuladas):")
        for fonte in resultado['fontes_consultadas']:
            print(f"   • {fonte['nome']}: {fonte['status']} (similaridade: {fonte['similaridade']})")
        
        # Metadata
        print("\n🔧 METADATA:")
        for chave, valor in resultado['metadata'].items():
            print(f"   • {chave}: {valor}")
        
        print("\n" + "=" * 70)
        print("✅ TODOS OS MÓDULOS FUNCIONANDO!")
        print("   - Extractor: OK")
        print("   - NLP Processor: OK")
        print("   - Próximo: searcher.py (busca nas fontes)")
        print("=" * 70)
        
    else:
        print("❌ ERRO NA REQUISIÇÃO")
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

except requests.exceptions.ConnectionError:
    print("❌ ERRO: Não foi possível conectar ao servidor!")
    print("   Certifique-se de que o servidor está rodando:")
    print("   python app.py")

except Exception as e:
    print(f"❌ ERRO INESPERADO: {e}")
    import traceback
    traceback.print_exc()