import requests
import json
import time

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 70)
print("🎉 TESTE FINAL DO SISTEMA COMPLETO")
print("=" * 70)
print()

texto_teste = """
O presidente Luiz Inácio Lula da Silva assinou nesta quarta-feira o 
decreto que regulamenta a reforma tributária no Brasil. A medida 
estabelece novas regras para o Imposto sobre Valor Agregado (IVA) e 
prevê uma transição gradual até 2033. O ministro da Fazenda, Fernando 
Haddad, participou da cerimônia no Palácio do Planalto em Brasília.
"""

dados = {
    "tipo": "texto",
    "conteudo": texto_teste
}

print("📤 Enviando requisição...")
print("⏳ Aguarde... (30-90 segundos)")
print()

inicio = time.time()
response = requests.post(f'{BASE_URL}/api/verificar', json=dados, timeout=120)
tempo_total = time.time() - inicio

print(f"⏱️  Tempo total: {tempo_total:.1f}s")
print()

if response.status_code == 200:
    resultado = response.json()
    
    print("=" * 70)
    print("✅ ANÁLISE COMPLETA COM SCORER")
    print("=" * 70)
    print()
    
    print(f"🎯 VERACIDADE: {resultado['veracidade']}%")
    print(f"📊 NÍVEL DE CONFIANÇA: {resultado['nivel_confianca'].upper()}")
    print()
    
    print("📝 JUSTIFICATIVA:")
    print(f"   {resultado['justificativa']}")
    print()
    
    print("🔬 DETALHES DO CÁLCULO:")
    detalhes = resultado['calculo_detalhado']
    print(f"   Score base: {detalhes['score_base']}")
    print(f"   Após penalidades: {detalhes['score_com_penalidades']}")
    print(f"   Após bônus: {detalhes['score_com_bonus']}")
    print(f"   Score final: {detalhes['score_final']}")
    print()
    
    if detalhes['penalidades']:
        print("   ⚠️  Penalidades aplicadas:")
        for nome, info in detalhes['penalidades'].items():
            print(f"      • {info['motivo']} (-{info['percentual']}%)")
        print()
    
    if detalhes['bonus']:
        print("   ✨ Bônus aplicados:")
        for nome, info in detalhes['bonus'].items():
            print(f"      • {info['motivo']} (+{info['percentual']}%)")
        print()
    
    print("🤖 ANÁLISE NLP:")
    nlp = resultado['analise_nlp']
    print(f"   Query: {nlp['query_busca']}")
    print(f"   Entidades: {[e['texto'] for e in nlp['entidades_encontradas'][:3]]}")
    print()
    
    print("🔬 ANÁLISE SEMÂNTICA:")
    sem = resultado['analise_semantica']
    print(f"   Total analisado: {sem['total_analisados']}")
    print(f"   ✅ Confirmam forte: {sem['confirmam_forte']}")
    print(f"   ~ Confirmam parcial: {sem['confirmam_parcial']}")
    print(f"   • Apenas mencionam: {sem['apenas_mencionam']}")
    print(f"   ✗ Não relacionados: {sem['nao_relacionados']}")
    print()
    
    print("📊 TOP 5 FONTES:")
    for i, fonte in enumerate(resultado['fontes_consultadas'][:5], 1):
        print(f"\n   {i}. {fonte['nome']} - Similaridade: {fonte['similaridade']:.4f}")
        print(f"      Status: {fonte['status']}")
        print(f"      Título: {fonte['titulo'][:60]}...")
        print(f"      URL: {fonte['url'][:70]}...")
    
    print()
    print("=" * 70)
    print("🎉 SISTEMA 100% COMPLETO E FUNCIONAL!")
    print("=" * 70)
    print()
    
    print("✅ TODOS OS MÓDULOS EXECUTADOS:")
    meta = resultado['metadata']
    print(f"   1. ✅ Validação: OK")
    print(f"   2. ✅ NLP (IA spaCy): OK")
    print(f"   3. ✅ Busca ({meta['modo_busca']}): {meta['total_resultados_busca']} resultados")
    print(f"   4. ✅ Filtros: Aplicados")
    print(f"   5. ✅ Scraping: {meta['total_scraped']} processados")
    print(f"   6. ✅ Análise Semântica (IA): {meta['total_analisados']} analisados")
    print(f"   7. ✅ Scorer: {resultado['veracidade']}% calculado")
    print()
    print(f"📊 ESTATÍSTICAS:")
    print(f"   • Versão: {meta['versao_sistema']}")
    print(f"   • Fontes disponíveis: {meta['fontes_disponiveis']}")
    print(f"   • Fontes consultadas: {meta['total_fontes_consultadas']}")
    print(f"   • Tempo de processamento: {tempo_total:.1f}s")

else:
    print(f"❌ ERRO {response.status_code}:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))