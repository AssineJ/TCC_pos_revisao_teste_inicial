import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 70)
print("🧪 TESTE COM URL REAL DE NOTÍCIA")
print("=" * 70)
print()

# PASSO 1: Você precisa escolher uma URL real
# Acesse um dos portais e copie uma URL de notícia recente:
# - https://g1.globo.com/
# - https://www.folha.uol.com.br/
# - https://noticias.uol.com.br/
# - https://istoe.com.br/
# - https://www.estadao.com.br/

# Cole a URL aqui:
url_noticia = input("📰 Cole a URL da notícia para testar: ").strip()

if not url_noticia:
    print("❌ URL não fornecida!")
    exit()

print()
print(f"🔗 URL: {url_noticia}")
print()

# Escolher modo de busca
print("🔧 Escolha o modo de busca:")
print("   1. mock (rápido, dados simulados)")
print("   2. googlesearch (gratuito, pode ser bloqueado)")
print("   3. serpapi (preciso, requer chave)")
print("   4. hybrid (tenta tudo)")
print()

escolha = input("Digite o número (1-4): ").strip()

modos = {
    '1': 'mock',
    '2': 'googlesearch',
    '3': 'serpapi',
    '4': 'hybrid'
}

modo = modos.get(escolha, 'mock')

# Mudar modo temporariamente
from config import Config
modo_original = Config.SEARCH_MODE
Config.SEARCH_MODE = modo

print()
print(f"✅ Modo selecionado: {modo}")
print()
print("⏳ Processando... (pode demorar até 60s)")
print()

dados = {
    "tipo": "url",
    "conteudo": url_noticia
}

try:
    response = requests.post(f'{BASE_URL}/api/verificar', json=dados, timeout=90)
    
    if response.status_code == 200:
        resultado = response.json()
        
        print("=" * 70)
        print("✅ ANÁLISE CONCLUÍDA!")
        print("=" * 70)
        print()
        
        print(f"🎯 VERACIDADE: {resultado['veracidade']}%")
        print()
        
        print(f"📰 TÍTULO:")
        print(f"   {resultado['titulo_analisado']}")
        print()
        
        print(f"📝 JUSTIFICATIVA:")
        print(f"   {resultado['justificativa']}")
        print()
        
        print("🤖 NLP - Principais Termos Extraídos:")
        nlp = resultado['analise_nlp']
        print(f"   Entidades: {', '.join([e['texto'] for e in nlp['entidades_encontradas'][:3]])}")
        print(f"   Palavras-chave: {', '.join(nlp['palavras_chave'][:5])}")
        print()
        
        print("🔬 ANÁLISE SEMÂNTICA:")
        sem = resultado['analise_semantica']
        print(f"   Total analisado: {sem['total_analisados']}")
        print(f"   ✅ Confirmam forte: {sem['confirmam_forte']}")
        print(f"   ~ Confirmam parcial: {sem['confirmam_parcial']}")
        print(f"   • Apenas mencionam: {sem['apenas_mencionam']}")
        print()
        
        print("📊 FONTES QUE CONFIRMAM:")
        for i, fonte in enumerate(resultado['fontes_consultadas'][:5], 1):
            print(f"\n   {i}. {fonte['nome']} - Similaridade: {fonte['similaridade']:.4f}")
            print(f"      Status: {fonte['status']}")
            print(f"      {fonte['titulo'][:60]}...")
            print(f"      {fonte['url'][:70]}...")
        
        print()
        print("=" * 70)
        print("✅ TESTE COMPLETO!")
        print("=" * 70)
    
    else:
        print(f"❌ ERRO {response.status_code}:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

except Exception as e:
    print(f"❌ ERRO: {e}")

finally:
    Config.SEARCH_MODE = modo_original