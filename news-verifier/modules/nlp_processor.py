import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import re
from config import Config


# ============================================================================
# CARREGAR MODELOS (LAZY LOADING)
# ============================================================================

# Variáveis globais para armazenar modelos carregados
_nlp_model = None
_stopwords_pt = None


def _carregar_spacy():
    """
    Carrega o modelo spaCy apenas uma vez (lazy loading).
    Importante: Carregar modelo é pesado, fazemos apenas 1 vez.
    
    Returns:
        spacy.Language: Modelo carregado
    """
    global _nlp_model
    
    if _nlp_model is None:
        print("📚 Carregando modelo spaCy (pt_core_news_lg)...")
        try:
            _nlp_model = spacy.load(Config.SPACY_MODEL)
            print("✅ Modelo spaCy carregado!")
        except OSError:
            print("❌ ERRO: Modelo spaCy não encontrado!")
            print("Execute: python -m spacy download pt_core_news_lg")
            raise
    
    return _nlp_model


def _carregar_stopwords():
    """
    Carrega stopwords do NLTK + customizadas do config.
    
    Returns:
        set: Conjunto de stopwords
    """
    global _stopwords_pt
    
    if _stopwords_pt is None:
        print("📚 Carregando stopwords...")
        try:
            # Stopwords do NLTK
            nltk_stopwords = set(stopwords.words('portuguese'))
            
            # Adicionar stopwords customizadas do config
            custom_stopwords = set(Config.CUSTOM_STOPWORDS)
            
            # Combinar
            _stopwords_pt = nltk_stopwords.union(custom_stopwords)
            print(f"✅ {len(_stopwords_pt)} stopwords carregadas!")
        
        except LookupError:
            print("❌ ERRO: Stopwords do NLTK não encontradas!")
            print("Execute: python -c \"import nltk; nltk.download('stopwords')\"")
            raise
    
    return _stopwords_pt


# ============================================================================
# CLASSE PRINCIPAL - NLP PROCESSOR
# ============================================================================

class NLPProcessor:
    """
    Classe responsável por processar texto usando IA.
    
    Atributos:
        nlp: Modelo spaCy carregado
        stopwords: Conjunto de stopwords
    """
    
    def __init__(self):
        """Inicializa processador com modelos de IA"""
        self.nlp = _carregar_spacy()
        self.stopwords = _carregar_stopwords()
    
    
    def processar(self, texto):
        """
        Processa texto completo e extrai todas as informações.
        
        Args:
            texto (str): Texto da notícia
            
        Returns:
            dict: {
                'entidades': list,           # Entidades nomeadas encontradas
                'palavras_chave': list,      # Palavras-chave mais relevantes
                'query_busca': str,          # Query otimizada para busca
                'texto_limpo': str,          # Texto sem stopwords
                'estatisticas': dict         # Estatísticas do processamento
            }
        """
        
        # ====================================================================
        # ETAPA 1: LIMPAR E NORMALIZAR TEXTO
        # ====================================================================
        
        texto_limpo = self._limpar_texto(texto)
        
        
        # ====================================================================
        # ETAPA 2: PROCESSAR COM SPACY (IA!)
        # ====================================================================
        
        print("🤖 Processando texto com IA (spaCy)...")
        doc = self.nlp(texto_limpo)
        
        
        # ====================================================================
        # ETAPA 3: EXTRAIR ENTIDADES NOMEADAS
        # ====================================================================
        
        entidades = self._extrair_entidades(doc)
        
        
        # ====================================================================
        # ETAPA 4: EXTRAIR PALAVRAS-CHAVE
        # ====================================================================
        
        palavras_chave = self._extrair_palavras_chave(doc)
        
        
        # ====================================================================
        # ETAPA 5: GERAR QUERY DE BUSCA
        # ====================================================================
        
        query_busca = self._gerar_query_busca(entidades, palavras_chave)
        
        
        # ====================================================================
        # ETAPA 6: REMOVER STOPWORDS DO TEXTO
        # ====================================================================
        
        texto_sem_stopwords = self._remover_stopwords(texto_limpo)
        
        
        # ====================================================================
        # ETAPA 7: COLETAR ESTATÍSTICAS
        # ====================================================================
        
        estatisticas = {
            'total_tokens': len(doc),
            'total_entidades': len(entidades),
            'total_palavras_chave': len(palavras_chave),
            'tamanho_texto_original': len(texto),
            'tamanho_texto_limpo': len(texto_limpo)
        }
        
        
        # ====================================================================
        # RETORNAR RESULTADO
        # ====================================================================
        
        return {
            'entidades': entidades,
            'palavras_chave': palavras_chave,
            'query_busca': query_busca,
            'texto_limpo': texto_sem_stopwords,
            'estatisticas': estatisticas
        }
    
    
    def _limpar_texto(self, texto):
        """
        Limpa texto removendo caracteres especiais, múltiplos espaços, etc.
        
        Args:
            texto (str): Texto original
            
        Returns:
            str: Texto limpo
        """
        # Remover URLs
        texto = re.sub(r'http\S+|www\S+', '', texto)
        
        # Remover emails
        texto = re.sub(r'\S+@\S+', '', texto)
        
        # Remover múltiplos espaços
        texto = re.sub(r'\s+', ' ', texto)
        
        # Remover espaços no início e fim
        texto = texto.strip()
        
        return texto
    
    
    def _extrair_entidades(self, doc):
        """
        Extrai entidades nomeadas do texto usando spaCy.
        
        Entidades são: pessoas, lugares, organizações, datas, etc.
        Essas são as informações mais importantes para buscar nas fontes.
        
        Args:
            doc (spacy.tokens.Doc): Documento processado pelo spaCy
            
        Returns:
            list: Lista de dicionários com entidades
            [
                {'texto': 'Lula', 'tipo': 'PERSON'},
                {'texto': 'Brasil', 'tipo': 'LOC'},
                ...
            ]
        """
        entidades = []
        
        for ent in doc.ents:
            # Filtrar apenas tipos de entidades relevantes
            if ent.label_ in Config.ENTITY_TYPES:
                entidades.append({
                    'texto': ent.text,
                    'tipo': ent.label_,
                    'importancia': self._calcular_importancia_entidade(ent)
                })
        
        # Remover duplicatas (manter a com maior importância)
        entidades_unicas = {}
        for ent in entidades:
            texto_lower = ent['texto'].lower()
            if texto_lower not in entidades_unicas or ent['importancia'] > entidades_unicas[texto_lower]['importancia']:
                entidades_unicas[texto_lower] = ent
        
        # Converter de volta para lista e ordenar por importância
        entidades = list(entidades_unicas.values())
        entidades.sort(key=lambda x: x['importancia'], reverse=True)
        
        # Limitar ao máximo configurado
        entidades = entidades[:Config.MAX_ENTITIES]
        
        return entidades
    
    
    def _calcular_importancia_entidade(self, ent):
        """
        Calcula importância de uma entidade (0-1).
        Entidades no início do texto têm mais importância.
        
        Args:
            ent (spacy.tokens.Span): Entidade do spaCy
            
        Returns:
            float: Importância entre 0 e 1
        """
        # Posição no documento (quanto mais no início, maior a importância)
        posicao_relativa = ent.start / len(ent.doc)
        importancia_posicao = 1 - (posicao_relativa * 0.5)  # Máximo 50% de redução
        
        # Tamanho da entidade (entidades maiores tendem a ser mais específicas)
        tamanho = len(ent.text.split())
        importancia_tamanho = min(tamanho / 3, 1.0)  # Max 1.0
        
        # Média ponderada
        importancia = (importancia_posicao * 0.7) + (importancia_tamanho * 0.3)
        
        return round(importancia, 2)
    
    
    def _extrair_palavras_chave(self, doc):
        """
        Extrai palavras-chave mais relevantes do texto.
        
        Usa estratégia de frequência + importância gramatical:
        - Substantivos e verbos são mais importantes
        - Palavras mais frequentes são mais relevantes
        - Remove stopwords
        
        Args:
            doc (spacy.tokens.Doc): Documento processado
            
        Returns:
            list: Lista de palavras-chave ordenadas por relevância
        """
        # Coletar palavras relevantes (substantivos, verbos, adjetivos)
        palavras_relevantes = []
        
        for token in doc:
            # Filtros:
            # - Não é stopword
            # - É substantivo, verbo ou adjetivo
            # - Tem pelo menos 3 caracteres
            # - É alfabético (não número ou pontuação)
            if (not token.is_stop and 
                token.pos_ in ['NOUN', 'VERB', 'PROPN', 'ADJ'] and
                len(token.text) >= 3 and
                token.is_alpha):
                
                # Usar lema (forma base da palavra)
                # Exemplo: "correr", "correndo", "correu" -> "correr"
                palavra = token.lemma_.lower()
                palavras_relevantes.append(palavra)
        
        # Contar frequências
        contador = Counter(palavras_relevantes)
        
        # Pegar as mais frequentes
        palavras_chave = [palavra for palavra, freq in contador.most_common(Config.MAX_KEYWORDS)]
        
        return palavras_chave
    
    
    def _gerar_query_busca(self, entidades, palavras_chave):
        """
        Gera query otimizada para busca nas fontes.
        
        Combina entidades + palavras-chave de forma inteligente.
        
        Args:
            entidades (list): Lista de entidades extraídas
            palavras_chave (list): Lista de palavras-chave
            
        Returns:
            str: Query de busca otimizada
        """
        # Pegar top 3 entidades mais importantes
        top_entidades = [ent['texto'] for ent in entidades[:3]]
        
        # Pegar top 5 palavras-chave
        top_palavras = palavras_chave[:5]
        
        # Combinar (priorizar entidades)
        termos_busca = top_entidades + top_palavras
        
        # Remover duplicatas mantendo ordem
        termos_unicos = []
        for termo in termos_busca:
            if termo.lower() not in [t.lower() for t in termos_unicos]:
                termos_unicos.append(termo)
        
        # Limitar a 6 termos no máximo (queries muito longas não funcionam bem)
        termos_unicos = termos_unicos[:6]
        
        # Juntar com espaços
        query = ' '.join(termos_unicos)
        
        return query
    
    
    def _remover_stopwords(self, texto):
        """
        Remove stopwords do texto mantendo apenas palavras relevantes.
        
        Args:
            texto (str): Texto original
            
        Returns:
            str: Texto sem stopwords
        """
        # Tokenizar
        palavras = word_tokenize(texto.lower(), language='portuguese')
        
        # Filtrar stopwords
        palavras_filtradas = [
            palavra for palavra in palavras 
            if palavra.isalpha() and palavra not in self.stopwords and len(palavra) >= 3
        ]
        
        # Juntar de volta
        texto_filtrado = ' '.join(palavras_filtradas)
        
        return texto_filtrado


# ============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# ============================================================================

def processar_texto(texto):
    """
    Função simplificada para processar texto.
    Esta é a função que será chamada por outros módulos.
    
    Args:
        texto (str): Texto a processar
        
    Returns:
        dict: Resultado do processamento
        
    Exemplo:
        >>> resultado = processar_texto("O presidente anunciou reforma...")
        >>> print(resultado['entidades'])
        >>> print(resultado['query_busca'])
    """
    processor = NLPProcessor()
    return processor.processar(texto)


# ============================================================================
# TESTE DO MÓDULO
# ============================================================================

if __name__ == "__main__":
    """
    Testes do módulo nlp_processor.
    Execute: python modules/nlp_processor.py
    """
    
    print("=" * 70)
    print("🧪 TESTANDO MÓDULO NLP PROCESSOR")
    print("=" * 70)
    print()
    
    # Texto de teste
    texto_teste = """
    O presidente Luiz Inácio Lula da Silva anunciou ontem em Brasília uma 
    importante reforma tributária que reduzirá os impostos sobre alimentos 
    básicos em todo o Brasil. A medida, que será implementada pelo Ministério 
    da Fazenda a partir de janeiro de 2025, deve beneficiar milhões de 
    brasileiros de baixa renda. Segundo especialistas econômicos, a reforma 
    pode reduzir a inflação e estimular o consumo das famílias.
    """
    
    print("📝 Texto de teste:")
    print(texto_teste.strip())
    print()
    print("-" * 70)
    print()
    
    # Processar
    resultado = processar_texto(texto_teste)
    
    # Mostrar resultados
    print("✅ RESULTADO DO PROCESSAMENTO:")
    print()
    
    print("🏷️  ENTIDADES ENCONTRADAS:")
    for ent in resultado['entidades']:
        print(f"  • {ent['texto']} ({ent['tipo']}) - Importância: {ent['importancia']}")
    print()
    
    print("🔑 PALAVRAS-CHAVE:")
    print(f"  {', '.join(resultado['palavras_chave'])}")
    print()
    
    print("🔍 QUERY DE BUSCA OTIMIZADA:")
    print(f"  {resultado['query_busca']}")
    print()
    
    print("📊 ESTATÍSTICAS:")
    for chave, valor in resultado['estatisticas'].items():
        print(f"  • {chave}: {valor}")
    print()
    
    print("📄 TEXTO LIMPO (primeiros 200 caracteres):")
    print(f"  {resultado['texto_limpo'][:200]}...")