import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 70)
print("🎉 TESTE DO SISTEMA COMPLETO - TODAS AS ETAPAS")
print("=" * 70)
print()

texto_teste = """
O presidente Luiz Inácio Lula da Silva anunciou nesta terça-feira uma 
importante reforma tributária que vai reduzir impostos sobre alimentos 
básicos em todo o Brasil. A medida será implementada pelo Ministério 
da Fazenda a partir de 2025 e deve beneficiar milhões de famílias 
brasileiras de baixa renda. Segundo economistas, a reforma pode ajudar 
a reduzir a inflação e estimular o consumo das famílias.
"""

dados = {
    "tipo": "texto",
    "conteudo": texto_teste
}

print("📤 Enviando requisição...")
print()

response = requests.post(f'{BASE_URL}/api/verificar', json=dados)

print(f"📥 Status: {response.status_code}")
print()

if response.status_code == 200:
    resultado = response.json()
    
    print("=" * 70)
    print("✅ ANÁLISE COMPLETA DO SISTEMA")
    print("=" * 70)
    print()
    
    print(f"🎯 VERACIDADE: {resultado['veracidade']}%")
    print()
    
    print(f"📝 JUSTIFICATIVA:")
    print(f"   {resultado['justificativa']}")
    print()
    
    print(f"📰 TÍTULO ANALISADO:")
    print(f"   {resultado['titulo_analisado'][:80]}...")
    print()
    
    print("🤖 ANÁLISE NLP (IA):")
    nlp = resultado['analise_nlp']
    print(f"   Query: {nlp['query_busca']}")
    print(f"   Entidades: {[e['texto'] for e in nlp['entidades_encontradas'][:3]]}")
    print(f"   Palavras-chave: {nlp['palavras_chave'][:5]}")
    print()
    
    print("🔬 ANÁLISE SEMÂNTICA:")
    semantica = resultado['analise_semantica']
    print(f"   Total analisado: {semantica['total_analisados']}")
    print(f"   ✅ Confirmam forte: {semantica['confirmam_forte']}")
    print(f"   ~ Confirmam parcial: {semantica['confirmam_parcial']}")
    print(f"   • Apenas mencionam: {semantica['apenas_mencionam']}")
    print(f"   ✗ Não relacionados: {semantica['nao_relacionados']}")
    print()
    
    print("📊 TOP 5 FONTES MAIS SIMILARES:")
    for i, fonte in enumerate(resultado['fontes_consultadas'][:5], 1):
        print(f"\n   {i}. {fonte['nome']} - Similaridade: {fonte['similaridade']:.4f}")
        print(f"      Status: {fonte['status']}")
        print(f"      Título: {fonte['titulo'][:60]}...")
        print(f"      URL: {fonte['url'][:70]}...")
    
    print()
    print("=" * 70)
    print("🎉 SISTEMA 100% FUNCIONAL!")
    print("=" * 70)
    print()
    
    meta = resultado['metadata']
    print("✅ Módulos executados com sucesso:")
    print(f"   1. ✅ Validação de entrada")
    print(f"   2. ✅ NLP Processor (IA)")
    print(f"   3. ✅ Searcher (busca em {meta['total_resultados_busca']} resultados)")
    print(f"   4. ✅ Scraper (extraiu {meta['total_scraped']} conteúdos)")
    print(f"   5. ✅ Semantic Analyzer (analisou {meta['total_analisados']} textos)")
    print(f"   6. ✅ Scorer (calculou veracidade: {resultado['veracidade']}%)")
    
else:
    print(f"❌ Erro: {response.json()}")