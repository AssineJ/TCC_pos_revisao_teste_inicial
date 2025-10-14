from modules.extractor import extrair_conteudo

print("=" * 70)
print("🧪 TESTE: EXTRACTOR MELHORADO (6 ESTRATÉGIAS)")
print("=" * 70)
print()

# URLs de teste (diferentes níveis de dificuldade)
urls_teste = [
    {
        "nome": "G1 (fácil)",
        "url": "https://g1.globo.com/"
    },
    {
        "nome": "Folha (paywall)",
        "url": "https://www.folha.uol.com.br/"
    },
    {
        "nome": "IstoÉ (médio)",
        "url": "https://istoe.com.br/"
    }
]

resultados = []

for i, teste in enumerate(urls_teste, 1):
    print(f"\nTeste {i}: {teste['nome']}")
    print(f"URL: {teste['url']}")
    print("-" * 70)
    
    resultado = extrair_conteudo(teste['url'])
    
    if resultado['sucesso']:
        print(f"✅ SUCESSO ({resultado['metodo_extracao']})")
        print(f"   Título: {resultado['titulo'][:60]}...")
        print(f"   Texto: {len(resultado['texto'])} caracteres")
        print(f"   Palavras: {len(resultado['texto'].split())} palavras")
        resultados.append(True)
    else:
        print(f"❌ FALHOU")
        print(f"   Erro: {resultado['erro']}")
        resultados.append(False)

print()
print("=" * 70)
print("📊 RESULTADO:")
print("=" * 70)
sucessos = sum(resultados)
total = len(resultados)
print(f"✅ Sucessos: {sucessos}/{total} ({sucessos/total*100:.0f}%)")
print()

if sucessos == total:
    print("🎉 EXTRACTOR MELHORADO FUNCIONANDO PERFEITAMENTE!")
elif sucessos >= total * 0.7:
    print("✅ Extractor funcionando bem!")
else:
    print("⚠️  Extractor precisa de ajustes")