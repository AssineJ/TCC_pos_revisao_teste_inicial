# modules/semantic_analyzer.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from config import Config
import time

# === NOVO: cache de embeddings ===
import os
import hashlib
import pickle

# Diretório de cache (persistente)
CACHE_DIR = os.path.join("cache", "embeddings")
os.makedirs(CACHE_DIR, exist_ok=True)


# ============================================================================
# DETECÇÃO INTELIGENTE DE CONTRADIÇÃO
# ============================================================================

# Palavras que indicam NEGAÇÃO FORTE (só estas contam)
STRONG_NEGATION_WORDS = [
    'não', 'nao', 'nunca', 'jamais', 'nenhum', 'nenhuma',
    'falso', 'falsa', 'mentira', 'fake', 'desmentido', 'desmente',
    'incorreto', 'incorreta', 'errado', 'errada',
    'boato', 'desinformação', 'fake news'
]

# Palavras NEUTRAS que NÃO são contradição (sinônimos, variações)
NEUTRAL_WORDS = [
    'quer', 'pretende', 'planeja', 'projeta', 'estuda', 'avalia',
    'confirma', 'anuncia', 'declara', 'afirma', 'diz', 'informa',
    'pode', 'deve', 'vai', 'irá', 'poderá', 'deverá'
]

# Padrões FORTES de desmentido (só estes ativam alerta)
STRONG_DEBUNK_PATTERNS = [
    r'é\s+falso\s+que',
    r'não\s+é\s+verdade\s+que',
    r'checagem.*conclu[ií].*falso',
    r'fact.*check.*falso',
    r'desmente.*completamente',
    r'totalmente\s+falso',
    r'não\s+há\s+nenhuma\s+evidência',
    r'completamente\s+sem\s+fundamento',
    r'boato\s+que\s+circula'
]


def extrair_numeros(texto):
    """
    Extrai números do texto para comparação.
    Exemplo: "R$ 1.631" → 1631.0
    """
    # Remove formatação e extrai números
    numeros = re.findall(r'[\d]+[.,]?[\d]*', texto.replace('.', '').replace(',', '.'))
    return [float(n.replace(',', '.')) for n in numeros if n]


def numeros_similares(nums1, nums2, tolerancia=0.05):
    """
    Verifica se números são similares (tolerância de 5% por padrão).
    Exemplo: 1631 e 1630 são similares (diferença < 5%)
    """
    if not nums1 or not nums2:
        return False
    
    for n1 in nums1:
        for n2 in nums2:
            if n1 > 0 and n2 > 0:
                diferenca = abs(n1 - n2) / max(n1, n2)
                if diferenca <= tolerancia:
                    return True
    return False


def detectar_contradicao_inteligente(texto_original, texto_fonte, similaridade_semantica):
    """
    Detecta contradição de forma INTELIGENTE, evitando falsos positivos.
    """
    texto_fonte_lower = texto_fonte.lower()
    texto_original_lower = texto_original.lower()
    
    evidencias = []
    score_contradicao = 0.0
    
    # REGRA 1: Alta similaridade => não contradiz
    if similaridade_semantica >= 0.55:
        return {
            "contradiz": False,
            "confianca": 0.0,
            "motivo": f"Alta similaridade semântica ({similaridade_semantica:.2f}) indica confirmação",
            "evidencias": []
        }
    
    # REGRA 2: Números similares => não contradiz
    nums_original = extrair_numeros(texto_original)
    nums_fonte = extrair_numeros(texto_fonte)
    if nums_original and nums_fonte:
        if numeros_similares(nums_original, nums_fonte, tolerancia=0.05):
            return {
                "contradiz": False,
                "confianca": 0.0,
                "motivo": f"Números similares encontrados: {nums_original} ≈ {nums_fonte}",
                "evidencias": []
            }
    
    # REGRA 3: Padrões fortes de desmentido
    for pattern in STRONG_DEBUNK_PATTERNS:
        match = re.search(pattern, texto_fonte_lower)
        if match:
            score_contradicao += 0.5
            evidencias.append(f"Padrão de desmentido: '{match.group(0)}'")
    
    # REGRA 4: Negações fortes próximas de palavras-chave
    palavras_chave = [w for w in texto_original_lower.split() if len(w) > 4 and w not in NEUTRAL_WORDS][:5]
    negacoes_contextuais = 0
    for palavra_chave in palavras_chave:
        posicoes = [m.start() for m in re.finditer(re.escape(palavra_chave), texto_fonte_lower)]
        for pos in posicoes:
            inicio = max(0, pos - 50)
            fim = min(len(texto_fonte_lower), pos + len(palavra_chave) + 50)
            contexto = texto_fonte_lower[inicio:fim]
            for negacao in STRONG_NEGATION_WORDS:
                if negacao in contexto:
                    negacoes_contextuais += 1
                    evidencias.append(f"Negação '{negacao}' próxima de '{palavra_chave}'")
    if negacoes_contextuais >= 2:
        score_contradicao += min(negacoes_contextuais * 0.15, 0.3)
    
    # REGRA 5: Similaridade média reduz score
    if similaridade_semantica >= 0.40:
        score_contradicao *= 0.3
        evidencias.append(f"Score reduzido devido à similaridade moderada ({similaridade_semantica:.2f})")
    
    # Decisão final (limiar alto)
    contradiz = score_contradicao >= 0.6
    motivo = f"Contradição detectada (confiança: {score_contradicao:.2f})" if contradiz else "Sem contradição clara detectada"
    
    return {
        "contradiz": contradiz,
        "confianca": min(score_contradicao, 1.0),
        "motivo": motivo,
        "evidencias": evidencias
    }


# ============================================================================
# CARREGAR MODELO (LAZY LOADING)
# ============================================================================

_semantic_model = None


def _carregar_modelo():
    """
    Carrega o modelo sentence-transformers apenas uma vez.
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
            raise
    
    return _semantic_model


# ============================================================================
# CLASSE PRINCIPAL - SEMANTIC ANALYZER
# ============================================================================

class SemanticAnalyzer:
    """
    Analisador semântico com detecção INTELIGENTE de contradições.
    """
    def __init__(self):
        """Inicializa analyzer com modelo de IA"""
        self.model = _carregar_modelo()

    # === NOVO: geração de embedding com cache em disco ===
    def _gerar_embedding_com_cache(self, texto: str) -> np.ndarray:
        """
        Gera embedding com cache em disco. Usa hash do texto + id do modelo.
        Limita o texto a 2000 chars (mesma heurística do pipeline).
        """
        if not texto:
            return np.zeros((384,), dtype=np.float32)  # tamanho típico all-MiniLM; evita crash

        texto_lim = texto[:2000]

        # incluir modelo na chave para evitar colisão ao trocar de modelo
        model_id = getattr(Config, "SENTENCE_TRANSFORMER_MODEL", "default-model")
        key_src = f"{model_id}||{texto_lim}".encode("utf-8", "ignore")
        texto_hash = hashlib.md5(key_src).hexdigest()
        cache_path = os.path.join(CACHE_DIR, f"{texto_hash}.pkl")

        # cache hit
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "rb") as f:
                    emb = pickle.load(f)
                if isinstance(emb, np.ndarray):
                    return emb
            except Exception:
                pass  # prossegue para recálculo

        # gerar e salvar
        emb = self.model.encode(texto_lim, convert_to_numpy=True)
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(emb, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            pass
        return emb

    def analisar_noticias(self, texto_original, conteudos_scraping):
        """
        Analisa todas as notícias extraídas comparando com o texto original.
        """
        print(f"\n🔬 Iniciando análise semântica INTELIGENTE...")
        
        # Gerar embedding do texto original (com cache)
        embedding_original = self._gerar_embedding_com_cache(texto_original)
        
        resultados_analise = {}
        total_analisados = 0
        confirmam_forte = 0
        confirmam_parcial = 0
        apenas_mencionam = 0
        nao_relacionados = 0
        contradizem = 0
        
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
                if not conteudo['sucesso']:
                    analises_fonte.append({
                        **conteudo,
                        'similaridade': 0.0,
                        'status': 'erro_extracao',
                        'motivo': conteudo['erro'],
                        'contradiz': False,
                        'confianca_contradicao': 0.0
                    })
                    continue
                
                # Calcular similaridade primeiro (embedding com cache)
                embedding_fonte = self._gerar_embedding_com_cache(conteudo['texto'])
                similaridade = cosine_similarity(
                    embedding_original.reshape(1, -1),
                    embedding_fonte.reshape(1, -1)
                )[0][0]
                
                # ✅ Detecção INTELIGENTE de contradição (passa similaridade)
                contradicao = detectar_contradicao_inteligente(
                    texto_original, 
                    conteudo['texto'],
                    float(similaridade)
                )
                
                # Analisar status
                analise = self._analisar_similaridade(
                    float(similaridade),
                    conteudo,
                    contradicao
                )
                
                analises_fonte.append(analise)
                total_analisados += 1
                
                # Contabilizar status
                if analise['status'] == 'CONTRADIZ':
                    contradizem += 1
                elif analise['status'] == 'confirma_forte':
                    confirmam_forte += 1
                elif analise['status'] == 'confirma_parcial':
                    confirmam_parcial += 1
                elif analise['status'] == 'menciona':
                    apenas_mencionam += 1
                else:
                    nao_relacionados += 1
            
            resultados_analise[fonte_nome] = analises_fonte
            
            # Resumo
            sucessos = sum(1 for a in analises_fonte if a.get('similaridade', 0) > 0)
            contrad = sum(1 for a in analises_fonte if a.get('status') == 'CONTRADIZ')
            print(f"      ✅ {sucessos} análise(s) concluída(s)")
            if contrad > 0:
                print(f"      ⚠️  {contrad} contradição(ões) detectada(s)")
        
        # Metadata final
        print(f"\n✅ Análise semântica concluída!")
        print(f"   Total analisado: {total_analisados}")
        if contradizem > 0:
            print(f"   ⚠️  CONTRADIZEM: {contradizem}")
        print(f"   ✓ Confirmam forte: {confirmam_forte}")
        print(f"   ✓ Confirmam parcial: {confirmam_parcial}")
        print(f"   ~ Apenas mencionam: {apenas_mencionam}")
        print(f"   ✗ Não relacionados: {nao_relacionados}")
        
        return {
            **resultados_analise,
            'metadata': {
                'total_analisados': total_analisados,
                'contradizem': contradizem,
                'confirmam_forte': confirmam_forte,
                'confirmam_parcial': confirmam_parcial,
                'apenas_mencionam': apenas_mencionam,
                'nao_relacionados': nao_relacionados
            }
        }
    
    
    def _analisar_similaridade(self, similaridade, conteudo, contradicao):
        """
        Classifica status baseado em similaridade e contradição.
        """
        if contradicao['contradiz'] and contradicao['confianca'] >= 0.7:
            status = 'CONTRADIZ'
            motivo = f"⚠️ {contradicao['motivo']}"
        elif similaridade >= Config.SIMILARITY_THRESHOLD_HIGH:
            status = 'confirma_forte'
            motivo = f'Alta similaridade ({similaridade:.1%}) - confirma informação'
        elif similaridade >= Config.SIMILARITY_THRESHOLD_MEDIUM:
            status = 'confirma_parcial'
            motivo = f'Similaridade moderada ({similaridade:.1%})'
        elif similaridade >= Config.SIMILARITY_THRESHOLD_LOW:
            status = 'menciona'
            motivo = f'Baixa similaridade ({similaridade:.1%}), apenas menciona'
        else:
            status = 'nao_relacionado'
            motivo = f'Similaridade muito baixa ({similaridade:.1%})'
        
        return {
            **conteudo,
            'similaridade': round(float(similaridade), 4),
            'status': status,
            'motivo': motivo,
            'contradiz': contradicao['contradiz'],
            'confianca_contradicao': contradicao['confianca'],
            'evidencias_contradicao': contradicao.get('evidencias', [])
        }
    
    
    # (mantido para compatibilidade, agora só redireciona ao método com cache)
    def _gerar_embedding(self, texto):
        """Compat: mantém a assinatura antiga, mas usa o cache novo."""
        return self._gerar_embedding_com_cache(texto)
    
    
    def comparar_dois_textos(self, texto1, texto2):
        """Compara dois textos."""
        emb1 = self._gerar_embedding_com_cache(texto1)
        emb2 = self._gerar_embedding_com_cache(texto2)
        
        similaridade = cosine_similarity(
            emb1.reshape(1, -1),
            emb2.reshape(1, -1)
        )[0][0]
        
        contradicao = detectar_contradicao_inteligente(texto1, texto2, float(similaridade))
        
        return {
            'similaridade': float(similaridade),
            'contradiz': contradicao['contradiz'],
            'confianca_contradicao': contradicao['confianca'],
            'motivo': contradicao['motivo'],
            'evidencias': contradicao.get('evidencias', [])
        }


# ============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# ============================================================================

def analisar_semantica(texto_original, conteudos_scraping):
    """Função simplificada para análise semântica."""
    analyzer = SemanticAnalyzer()
    return analyzer.analisar_noticias(texto_original, conteudos_scraping)


# ============================================================================
# TESTE DO MÓDULO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TESTANDO DETECÇÃO INTELIGENTE DE CONTRADIÇÃO")
    print("=" * 70)
    print()
    
    analyzer = SemanticAnalyzer()
    
    # Teste 1: NOTÍCIA VERDADEIRA (não deve contradizer)
    print("Teste 1: Notícia VERDADEIRA sobre salário mínimo")
    print("-" * 70)
    
    texto_real = "Governo Lula diz que quer salário mínimo acima de R$ 1.631 em 2026"
    texto_fonte_real = "Governo Lula projeta salário mínimo de R$ 1630 em 2026"
    
    resultado_real = analyzer.comparar_dois_textos(texto_real, texto_fonte_real)
    
    print(f"Original: {texto_real}")
    print(f"Fonte: {texto_fonte_real}")
    print(f"\n✅ Similaridade: {resultado_real['similaridade']:.4f}")
    print(f"❌ Contradiz: {resultado_real['contradiz']}")
    print(f"📊 Confiança: {resultado_real['confianca_contradicao']:.2f}")
    print(f"💬 Motivo: {resultado_real['motivo']}")
    if resultado_real['evidencias']:
        print(f"🔍 Evidências: {resultado_real['evidencias']}")
    print()
    
    # Teste 2: FAKE NEWS (deve contradizer)
    print("Teste 2: FAKE NEWS sobre vacinas")
    print("-" * 70)
    
    texto_fake = "Vacinas contra COVID-19 matam instantaneamente"
    texto_fonte_fake = "É falso que vacinas matam. Não há evidências científicas"
    
    resultado_fake = analyzer.comparar_dois_textos(texto_fake, texto_fonte_fake)
    
    print(f"Original: {texto_fake}")
    print(f"Fonte: {texto_fonte_fake}")
    print(f"\n✅ Similaridade: {resultado_fake['similaridade']:.4f}")
    print(f"❌ Contradiz: {resultado_fake['contradiz']}")
    print(f"📊 Confiança: {resultado_fake['confianca_contradicao']:.2f}")
    print(f"💬 Motivo: {resultado_fake['motivo']}")
    if resultado_fake['evidencias']:
        print(f"🔍 Evidências: {resultado_fake['evidencias']}")
    
    print()
    print("=" * 70)
    print("✅ TESTES CONCLUÍDOS!")
    print("=" * 70)
