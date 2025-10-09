from modules.extractor import extrair_conteudo

url = "https://g1.globo.com/rj/rio-de-janeiro/noticia/2025/10/08/secretaria-de-seguranca-publica-do-rj-alerta-para-golpe-com-uso-de-voz.ghtml"

print("🔍 TESTANDO EXTRAÇÃO DA URL:")
print(url)
print()

resultado = extrair_conteudo(url)

if resultado['sucesso']:
    print(f"✅ Método: {resultado['metodo_extracao']}")
    print(f"✅ Título: {resultado['titulo']}")
    print(f"✅ Tamanho do texto: {len(resultado['texto'])} caracteres")
    print(f"\n📄 Primeiros 300 caracteres do texto:")
    print(resultado['texto'][:300])
    print("\n...")
    print(f"\n📄 Últimos 200 caracteres:")
    print("..." + resultado['texto'][-200:])
else:
    print(f"❌ Falhou: {resultado['erro']}")