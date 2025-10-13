import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 70)
print("🧪 TESTE COM URL PROBLEMÁTICA (STF)")
print("=" * 70)
print()

url_noticia = "https://g1.globo.com/politica/blog/valdo-cruz/post/2025/10/10/de-olho-na-eleicao-lula-vai-insistir-em-tributar-mais-bets-e-fintechs-para-acuar-oposicao.ghtml"

print(f"📰 URL: {url_noticia}")
print()
print("⏳ Processando... (pode demorar 60-90s)")
print()

dados = {
    "tipo": "url",
    "conteudo": url_noticia
}

try:
    response = requests.post(f'{BASE_URL}/api/verificar', json=dados, timeout=120)
    
    if response.status_code == 200:
        resultado = response.json()
        
        print("=" * 70)
        print("✅ ANÁLISE CONCLUÍDA")
        print("=" * 70)
        print()
        
        print(f"🎯 VERACIDADE: {resultado['veracidade']}%")
        print()
        
        print(f"📰 TÍTULO:")
        print(f"   {resultado['titulo_analisado'][:80]}...")
        print()
        
        print("=" * 70)
        print("🔗 VERIFICAÇÃO DE URLs")
        print("=" * 70)
        print()
        
        fontes = resultado.get('fontes_consultadas', [])
        
        if not fontes:
            print("❌ NENHUMA FONTE ENCONTRADA!")
        else:
            print(f"✅ {len(fontes)} fontes encontradas")
            print()
            
            urls_completas = 0
            urls_truncadas = 0
            
            for i, fonte in enumerate(fontes[:10], 1):
                url = fonte.get('url', '')
                tamanho = len(url)
                
                # Verificar se URL está completa
                completa = url.startswith('http') and tamanho > 50
                
                if completa:
                    urls_completas += 1
                    status = "✅"
                else:
                    urls_truncadas += 1
                    status = "❌"
                
                print(f"{i}. {status} {fonte['nome']} - {tamanho} caracteres")
                print(f"   Similaridade: {fonte['similaridade']:.4f}")
                print(f"   URL: {url}")
                print(f"   Título: {fonte['titulo'][:60]}...")
                print()
            
            print("=" * 70)
            print(f"📊 RESULTADO:")
            print(f"   ✅ URLs completas: {urls_completas}")
            print(f"   ❌ URLs truncadas: {urls_truncadas}")
            print("=" * 70)
            
            if urls_truncadas > 0:
                print()
                print("⚠️  AINDA HÁ URLs TRUNCADAS!")
                print("   Vamos investigar mais...")
            else:
                print()
                print("🎉 TODAS AS URLs ESTÃO COMPLETAS!")
    
    else:
        print(f"❌ ERRO {response.status_code}:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

except requests.exceptions.Timeout:
    print("⏱️  TIMEOUT - Requisição demorou mais de 120s")

except Exception as e:
    print(f"❌ ERRO: {e}")