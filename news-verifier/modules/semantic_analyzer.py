"""
semantic_analyzer.py - Módulo de Análise Semântica com IA

Responsabilidade:
    Comparar o texto original da notícia com os textos extraídos das fontes
    confiáveis usando IA (sentence-transformers) para determinar similaridade
    semântica.

Como funciona:
    1. Carrega modelo de IA (sentence-transformers)
    2. Transforma textos em vetores (embeddings)
    3. Calcula similaridade coseno entre vetores
    4. Classifica: confirma, parcial, menciona, não relacionado

Modelo usado:
    paraphrase-multilingual-mpnet-base-v2
    - Suporta português
    - 768 dimensões
    - Treinado em milhões de pares de sentenças

Autor: Projeto Acadêmico
Data: 2025
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import Config
import time


# ============================================================================
# CARREGAR MODELO (LAZY LOADING)
# ============================================================================

_semantic_model = None


def _carregar_modelo():
    """
    Carrega o modelo sentence-transformers apenas uma vez.
    Modelo é pesado (~400MB), carregamos apenas 1 vez.
    
    Returns:
        SentenceTransformer: Modelo carregado
    """
    global _semantic_model
    
    if _semantic_model is None:
        print("📚 Carregando modelo sentence-transformers...")
        print(f"   Modelo: {Config.SENTENCE_TRANSFORMER_MODEL}")
        print("   ⏳ Isso pode demorar 30-60s na primeira vez...")
        
        inicio = time.time()
        
        try:
            _semantic_model = SentenceTransformer(Config.SENTENCE_TRANSFORMER_MODEL)
            tempo = time.time() - inicio
            print(f"   ✅ Modelo carregado em {tempo:.1f}s!")
        
        except Exception as e:
            print(f"   ❌ ERRO ao carregar modelo: {e}")
            print("   Verifique se sentence-transformers está instalado:")
            print("   pip install sentence-transformers")
            raise
    
    return _semantic_model


# ============================================================================
# CLASSE PRINCIPAL - SEMANTIC ANALYZER
# ============================================================================

class SemanticAnalyzer:
    """
    Analisador semântico que compara textos usando IA.
    """
    
    def __init__(self):
        """Inicializa analyzer com modelo de IA"""
        self.model = _carregar_modelo()
    
    
    def analisar_noticias(self, texto_original, conteudos_scraping):
        """
        Analisa todas as notícias extraídas comparando com o texto original.
        
        Args:
            texto_original (str): Texto da notícia a verificar
            conteudos_scraping (dict): Resultado do scraper.scrape_noticias()
            {
                'G1': [{'url': ..., 'titulo': ..., 'texto': ..., 'sucesso': ...}],
                'Folha': [...],
                'metadata': {...}
            }
            
        Returns:
            dict: {
                'G1': [{'url': ..., 'similaridade': 0.78, 'status': 'confirma', ...}],
                'Folha': [...],
                'metadata': {
                    'total_analisados': int,
                    'confirmam_forte': int,
                    'confirmam_parcial': int,
                    'apenas_mencionam': int,
                    'nao_relacionados': int
                }
            }
        """
        print(f"\n🔬 Iniciando análise semântica com IA...")
        
        # Gerar embedding do texto original
        print(f"   📊 Gerando embedding do texto original...")
        embedding_original = self._gerar_embedding(texto_original)
        
        resultados_analise = {}
        total_analisados = 0
        confirmam_forte = 0
        confirmam_parcial = 0
        apenas_mencionam = 0
        nao_relacionados = 0
        
        # Para cada fonte
        for fonte_nome, fonte_conteudos in conteudos_scraping.items():
            if fonte_nome == 'metadata':
                continue
            
            if not fonte_conteudos:
                resultados_analise[fonte_nome] = []
                continue
            
            print(f"\n   📰 Analisando {fonte_nome}: {len(fonte_conteudos)} notícia(s)")
            
            analises_fonte = []
            
            for conteudo in fonte_conteudos:
                # Apenas analisar se extração foi sucesso
                if not conteudo['sucesso']:
                    analises_fonte.append({
                        **conteudo,
                        'similaridade': 0.0,
                        'status': 'erro_extracao',
                        'motivo': conteudo['erro']
                    })
                    continue
                
                # Analisar similaridade
                analise = self._analisar_similaridade(
                    embedding_original,
                    conteudo['texto'],
                    conteudo
                )
                
                analises_fonte.append(analise)
                total_analisados += 1
                
                # Contabilizar status
                if analise['status'] == 'confirma_forte':
                    confirmam_forte += 1
                elif analise['status'] == 'confirma_parcial':
                    confirmam_parcial += 1
                elif analise['status'] == 'menciona':
                    apenas_mencionam += 1
                else:
                    nao_relacionados += 1
            
            resultados_analise[fonte_nome] = analises_fonte
            
            # Mostrar resumo da fonte
            sucessos = sum(1 for a in analises_fonte if a.get('similaridade', 0) > 0)
            print(f"      ✅ {sucessos} análise(s) concluída(s)")
        
        # Metadata
        print(f"\n✅ Análise semântica concluída!")
        print(f"   Total analisado: {total_analisados}")
        print(f"   Confirmam forte: {confirmam_forte}")
        print(f"   Confirmam parcial: {confirmam_parcial}")
        print(f"   Apenas mencionam: {apenas_mencionam}")
        print(f"   Não relacionados: {nao_relacionados}")
        
        return {
            **resultados_analise,
            'metadata': {
                'total_analisados': total_analisados,
                'confirmam_forte': confirmam_forte,
                'confirmam_parcial': confirmam_parcial,
                'apenas_mencionam': apenas_mencionam,
                'nao_relacionados': nao_relacionados
            }
        }
    
    
    def _analisar_similaridade(self, embedding_original, texto_fonte, conteudo):
        """
        Calcula similaridade entre texto original e texto da fonte.
        
        Args:
            embedding_original (np.array): Embedding do texto original
            texto_fonte (str): Texto da notícia da fonte
            conteudo (dict): Dados completos do conteúdo
            
        Returns:
            dict: Conteúdo + similaridade + status
        """
        # Gerar embedding do texto da fonte
        embedding_fonte = self._gerar_embedding(texto_fonte)
        
        # Calcular similaridade coseno
        similaridade = cosine_similarity(
            embedding_original.reshape(1, -1),
            embedding_fonte.reshape(1, -1)
        )[0][0]
        
        # Classificar status baseado em thresholds
        if similaridade >= Config.SIMILARITY_THRESHOLD_HIGH:
            status = 'confirma_forte'
            motivo = 'Alta similaridade semântica com o texto original'
        
        elif similaridade >= Config.SIMILARITY_THRESHOLD_MEDIUM:
            status = 'confirma_parcial'
            motivo = 'Similaridade moderada, confirma parcialmente'
        
        elif similaridade >= Config.SIMILARITY_THRESHOLD_LOW:
            status = 'menciona'
            motivo = 'Baixa similaridade, apenas menciona o tema'
        
        else:
            status = 'nao_relacionado'
            motivo = 'Similaridade muito baixa, não parece relacionado'
        
        return {
            **conteudo,
            'similaridade': round(float(similaridade), 4),
            'status': status,
            'motivo': motivo
        }
    
    
    def _gerar_embedding(self, texto):
        """
        Gera embedding (vetor) de um texto usando o modelo.
        
        Args:
            texto (str): Texto para gerar embedding
            
        Returns:
            np.array: Vetor de 768 dimensões
        """
        # Limitar tamanho do texto (modelos têm limite)
        # sentence-transformers suporta ~512 tokens (~2000 caracteres)
        texto_limitado = texto[:2000]
        
        # Gerar embedding
        embedding = self.model.encode(texto_limitado, convert_to_numpy=True)
        
        return embedding
    
    
    def comparar_dois_textos(self, texto1, texto2):
        """
        Método auxiliar para comparar diretamente dois textos.
        Útil para testes.
        
        Args:
            texto1 (str): Primeiro texto
            texto2 (str): Segundo texto
            
        Returns:
            float: Similaridade entre 0 e 1
        """
        emb1 = self._gerar_embedding(texto1)
        emb2 = self._gerar_embedding(texto2)
        
        similaridade = cosine_similarity(
            emb1.reshape(1, -1),
            emb2.reshape(1, -1)
        )[0][0]
        
        return float(similaridade)


# ============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# ============================================================================

def analisar_semantica(texto_original, conteudos_scraping):
    """
    Função simplificada para análise semântica.
    
    Args:
        texto_original (str): Texto da notícia original
        conteudos_scraping (dict): Resultado do scraper
        
    Returns:
        dict: Análise completa com similaridades
        
    Exemplo:
        >>> from modules.scraper import scrape_noticias
        >>> from modules.semantic_analyzer import analisar_semantica
        >>> 
        >>> conteudos = scrape_noticias(resultados_busca)
        >>> analise = analisar_semantica(texto_original, conteudos)
        >>> 
        >>> for fonte, resultados in analise.items():
        >>>     if fonte != 'metadata':
        >>>         for r in resultados:
        >>>             print(f"{r['titulo']}: {r['similaridade']}")
    """
    analyzer = SemanticAnalyzer()
    return analyzer.analisar_noticias(texto_original, conteudos_scraping)


# ============================================================================
# TESTE DO MÓDULO
# ============================================================================

if __name__ == "__main__":
    """
    Testes do módulo semantic_analyzer.
    Execute: python modules/semantic_analyzer.py
    """
    
    print("=" * 70)
    print("🧪 TESTANDO MÓDULO SEMANTIC ANALYZER")
    print("=" * 70)
    print()
    
    # Teste 1: Comparar textos similares
    print("Teste 1: Textos similares")
    print("-" * 70)
    
    texto1 = "O presidente Lula anunciou reforma tributária em Brasília"
    texto2 = "Presidente confirma mudanças nos impostos na capital federal"
    
    analyzer = SemanticAnalyzer()
    similaridade = analyzer.comparar_dois_textos(texto1, texto2)
    
    print(f"Texto 1: {texto1}")
    print(f"Texto 2: {texto2}")
    print(f"\n✅ Similaridade: {similaridade:.4f}")
    
    if similaridade > 0.65:
        print("   Status: CONFIRMA FORTE")
    elif similaridade > 0.45:
        print("   Status: CONFIRMA PARCIAL")
    else:
        print("   Status: NÃO RELACIONADO")
    
    print()
    
    # Teste 2: Textos diferentes
    print("Teste 2: Textos não relacionados")
    print("-" * 70)
    
    texto3 = "O presidente Lula anunciou reforma tributária"
    texto4 = "O time de futebol venceu o campeonato brasileiro"
    
    similaridade2 = analyzer.comparar_dois_textos(texto3, texto4)
    
    print(f"Texto 1: {texto3}")
    print(f"Texto 2: {texto4}")
    print(f"\n✅ Similaridade: {similaridade2:.4f}")
    
    if similaridade2 > 0.65:
        print("   Status: CONFIRMA FORTE")
    elif similaridade2 > 0.45:
        print("   Status: CONFIRMA PARCIAL")
    else:
        print("   Status: NÃO RELACIONADO")
    
    print()
    print("=" * 70)
    print("✅ TESTES CONCLUÍDOS!")
    print("=" * 70)