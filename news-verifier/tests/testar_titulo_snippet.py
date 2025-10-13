import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 70)
print("🧪 TESTE: TÍTULO + SNIPPET PARA FONTES COM PAYWALL")
print("=" * 70)
print()

texto = """
O presidente Luiz Inácio Lula da Silva assinou nesta quarta-feira o 
decreto que regulamenta a reforma tributária no Brasil. A medida 
estabelece novas regras para o Imposto sobre Valor Agregado (IVA) e 
prevê uma transição gradual até 2033. O ministro da Fazenda, Fernando 
Haddad, participou da cerimônia no Palácio do Planalto em Brasília.
"""

dados = {
    "tipo": "texto",
    "conteudo": texto
}

print("📤 Enviando requisição...")
print("⏳ Aguarde...")
print()

response = requests.post(f'{BASE_URL}/api/verificar', json=dados, timeout=120)

if response.status_code == 200:
    resultado = response.json()
    
    print("=" * 70)
    print("✅ RESULTADO COM TÍTULO+SNIPPET")
    print("=" * 70)
    print()
    
    print(f"🎯 VERACIDADE: {resultado['veracidade']}%")
    print(f"📊 NÍVEL: {resultado['nivel_confianca'].upper()}")
    print()
    
    print("📰 FONTES:")
    fontes_paywall = ['Folha de S.Paulo', 'UOL Notícias', 'Estadão']
    
    for i, fonte in enumerate(resultado['fontes_consultadas'][:10], 1):
        nome = fonte['nome']
        metodo = "📋 título+snippet" if nome in fontes_paywall else "🌐 scraping completo"
        
        print(f"\n{i}. {nome} {metodo}")
        print(f"   Similaridade: {fonte['similaridade']:.4f}")
        print(f"   Status: {fonte['status']}")
        print(f"   Título: {fonte['titulo'][:60]}...")
        print(f"   URL: {fonte['url']}")
    
    print()
    print("=" * 70)
    print("📊 ANÁLISE:")
    print("=" * 70)
    
    sem = resultado['analise_semantica']
    print(f"Total analisado: {sem['total_analisados']}")
    print(f"✅ Confirmam forte: {sem['confirmam_forte']}")
    print(f"~ Confirmam parcial: {sem['confirmam_parcial']}")
    print()
    
    # Verificar se fontes com paywall funcionaram
    fontes_com_paywall_ok = 0
    for fonte in resultado['fontes_consultadas']:
        if fonte['nome'] in fontes_paywall and fonte['similaridade'] > 0:
            fontes_com_paywall_ok += 1
    
    print(f"✅ Fontes com paywall funcionando: {fontes_com_paywall_ok}/3")
    print()
    
    if fontes_com_paywall_ok >= 2:
        print("🎉 SOLUÇÃO FUNCIONANDO!")
        print("   Fontes com paywall agora usam título+snippet")
    else:
        print("⚠️  Poucas fontes com paywall funcionando")
        print("   Pode precisar de ajustes")

else:
    print(f"❌ Erro: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))