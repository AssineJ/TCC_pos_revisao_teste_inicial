"""
config.py - Configurações Centralizadas do Sistema

Este arquivo contém todas as configurações do projeto:
- Fontes confiáveis de notícias
- Timeouts e limites
- URLs de APIs
- Modelos de IA
- Mensagens de erro padrão

Autor: Projeto Acadêmico
Data: 2025
"""

import os
from dotenv import load_dotenv

# ============================================================================
# CARREGAR VARIÁVEIS DE AMBIENTE DO ARQUIVO .env
# ============================================================================

# Carregar variáveis do arquivo .env
load_dotenv()


# ============================================================================
# CLASSE DE CONFIGURAÇÃO
# ============================================================================

class Config:
    """
    Classe que centraliza todas as configurações do sistema.
    Usa variáveis de ambiente quando disponíveis, senão usa valores padrão.
    """
    
    # ========================================================================
    # CONFIGURAÇÕES DO FLASK
    # ========================================================================
    
    # Modo debug (True para desenvolvimento, False para produção)
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Ambiente (development, production, testing)
    ENV = os.getenv('FLASK_ENV', 'development')
    
    # Configurações de JSON
    JSON_AS_ASCII = False  # Permite acentos e caracteres especiais
    JSON_SORT_KEYS = False  # Mantém ordem original das chaves
    
    # Porta do servidor
    PORT = int(os.getenv('PORT', 5000))
    
    # Host (0.0.0.0 permite acesso externo, 127.0.0.1 apenas local)
    HOST = os.getenv('HOST', '0.0.0.0')
    
    
    # ========================================================================
    # FONTES CONFIÁVEIS DE NOTÍCIAS
    # ========================================================================
    
    TRUSTED_SOURCES = [
        {
            "nome": "G1",
            "dominio": "g1.globo.com",
            "url_base": "https://g1.globo.com",
            "url_busca": "https://g1.globo.com/busca/?q=",
            "confiabilidade": 0.95,  # Peso desta fonte no cálculo (0-1)
            "ativo": True
        },
        {
            "nome": "Folha de S.Paulo",
            "dominio": "folha.uol.com.br",
            "url_base": "https://www.folha.uol.com.br",
            "url_busca": "https://busca.folha.uol.com.br/?q=",
            "confiabilidade": 0.95,
            "ativo": True
        },
        {
            "nome": "UOL Notícias",
            "dominio": "noticias.uol.com.br",
            "url_base": "https://noticias.uol.com.br",
            "url_busca": "https://noticias.uol.com.br/busca/?q=",
            "confiabilidade": 0.90,
            "ativo": True
        },
        {
            "nome": "IstoÉ",
            "dominio": "istoe.com.br",
            "url_base": "https://istoe.com.br",
            "url_busca": "https://istoe.com.br/?s=",
            "confiabilidade": 0.92,
            "ativo": True
        },
        {
            "nome": "Estadão",
            "dominio": "estadao.com.br",
            "url_base": "https://www.estadao.com.br",
            "url_busca": "https://www.estadao.com.br/busca/?q=",
            "confiabilidade": 0.93,
            "ativo": True
        }
    ]
    
    # Lista apenas dos domínios (útil para validações)
    TRUSTED_DOMAINS = [fonte["dominio"] for fonte in TRUSTED_SOURCES]
    
    # Fontes com paywall/bloqueio que devem usar apenas título+snippet
    SOURCES_WITH_PAYWALL = ['Folha de S.Paulo', 'UOL Notícias', 'Estadão']
    
    # Número máximo de resultados por fonte
    MAX_RESULTS_PER_SOURCE = 2
    
    
    # ========================================================================
    # TIMEOUTS E LIMITES
    # ========================================================================
    
    # Timeout para requisições HTTP (segundos)
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 5))
    
    # Timeout para scraping de páginas (segundos)
    SCRAPING_TIMEOUT = int(os.getenv('SCRAPING_TIMEOUT', 10))
    
    # Timeout máximo para análise completa (segundos)
    ANALYSIS_TIMEOUT = int(os.getenv('ANALYSIS_TIMEOUT', 30))
    
    # Delay entre requisições (para não sobrecarregar sites)
    DELAY_BETWEEN_REQUESTS = 1.0  # segundos
    
    # Número de tentativas em caso de falha
    MAX_RETRIES = 3
    
    # Delay entre tentativas (backoff exponencial)
    RETRY_DELAY = 2  # segundos
    
    
    # ========================================================================
    # LIMITES DE CONTEÚDO
    # ========================================================================
    
    # Tamanho mínimo do conteúdo para análise (caracteres)
    MIN_CONTENT_LENGTH = int(os.getenv('MIN_CONTENT_LENGTH', 50))
    
    # Tamanho máximo do conteúdo (caracteres)
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 10000))
    
    # Número máximo de palavras-chave a extrair
    MAX_KEYWORDS = 10
    
    # Número máximo de entidades nomeadas a considerar
    MAX_ENTITIES = 15
    
    
    # ========================================================================
    # CONFIGURAÇÕES DE IA E NLP
    # ========================================================================
    
    # Modelo do spaCy para português
    SPACY_MODEL = "pt_core_news_lg"
    
    # Modelo de sentence transformers para similaridade semântica
    SENTENCE_TRANSFORMER_MODEL = "paraphrase-multilingual-mpnet-base-v2"
    
    # Threshold de similaridade para considerar textos relacionados
    # Valores entre 0 e 1 (quanto maior, mais similar)
    SIMILARITY_THRESHOLD_HIGH = 0.65      # Confirma fortemente
    SIMILARITY_THRESHOLD_MEDIUM = 0.45    # Confirma parcialmente
    SIMILARITY_THRESHOLD_LOW = 0.30       # Apenas menciona o tema
    
    # Tipos de entidades nomeadas a extrair
    ENTITY_TYPES = ['PERSON', 'ORG', 'LOC', 'DATE', 'GPE', 'EVENT']
    
    
    # ========================================================================
    # CONFIGURAÇÕES DE SCORING (CÁLCULO DE VERACIDADE)
    # ========================================================================
    
    # Percentuais mínimo e máximo de veracidade
    MIN_VERACITY_SCORE = 10
    MAX_VERACITY_SCORE = 95
    
    # Pesos para cálculo do score
    WEIGHT_STRONG_CONFIRMATION = 1.0   # Fonte confirma fortemente
    WEIGHT_PARTIAL_CONFIRMATION = 0.5  # Fonte confirma parcialmente
    WEIGHT_MENTION = 0.2               # Fonte apenas menciona
    
    # Penalidades
    PENALTY_NO_SOURCES = 0.8           # Se nenhuma fonte encontrada
    PENALTY_CONTRADICTION = 0.6        # Se fontes se contradizem
    PENALTY_VERY_RECENT = 0.9          # Se notícia < 1 hora (fontes podem não ter coberto)
    
    
    # ========================================================================
    # HEADERS HTTP (para web scraping)
    # ========================================================================
    
    # User-Agent que simula navegador real (evita bloqueios)
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]
    
    # Headers padrão para requisições
    DEFAULT_HEADERS = {
        'User-Agent': USER_AGENTS[0],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    
    # ========================================================================
    # CACHE
    # ========================================================================
    
    # Habilitar cache de requisições
    ENABLE_CACHE = True
    
    # Tempo de expiração do cache (segundos)
    CACHE_EXPIRATION = 3600  # 1 hora
    
    # Nome do arquivo de cache
    CACHE_DB_NAME = 'news_verifier_cache'
    
    
    # ========================================================================
    # RATE LIMITING (controle de requisições)
    # ========================================================================
    
    # Limite de requisições por minuto (por IP)
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 5))
    
    # Limite de requisições por hora (por IP)
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', 30))
    
    
    # ========================================================================
    # CONFIGURAÇÕES DE BUSCA
    # ========================================================================
    
    # Modo de busca: 'mock', 'serpapi', 'googlesearch', 'direct', 'hybrid'
    SEARCH_MODE = os.getenv('SEARCH_MODE', 'mock')
    
    # Habilitar fallback automático (se um método falhar, tenta próximo)
    ENABLE_SEARCH_FALLBACK = True
    
    # Ordem de prioridade dos métodos (usado no modo hybrid)
    SEARCH_METHODS_PRIORITY = ['serpapi', 'googlesearch', 'direct']
    
    # Número máximo de resultados por busca
    MAX_SEARCH_RESULTS = 3
    
    # Delay entre buscas (para não sobrecarregar)
    SEARCH_DELAY = 1.5  # segundos
    
    
    # ========================================================================
    # CHAVES DE API (quando necessário)
    # ========================================================================
    
    # SerpAPI (para busca no Google)
    SERPAPI_KEY = os.getenv('SERPAPI_KEY', None)
    
    # Contador de requisições SerpAPI (para monitorar uso)
    SERPAPI_REQUESTS_COUNT = 0
    SERPAPI_REQUESTS_LIMIT = 100  # Limite do plano gratuito
    
    # Outras APIs podem ser adicionadas aqui
    # OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
    
    
    # ========================================================================
    # MENSAGENS DE ERRO PADRONIZADAS
    # ========================================================================
    
    ERROR_MESSAGES = {
        'INVALID_JSON': 'Nenhum dado JSON foi enviado',
        'MISSING_FIELDS': "Campos obrigatórios: 'tipo' e 'conteudo'",
        'INVALID_TYPE': "Tipo deve ser 'url' ou 'texto'",
        'EMPTY_CONTENT': 'Conteúdo não pode estar vazio',
        'CONTENT_TOO_SHORT': f'Conteúdo muito curto para análise (mínimo {MIN_CONTENT_LENGTH} caracteres)',
        'CONTENT_TOO_LONG': f'Conteúdo muito longo (máximo {MAX_CONTENT_LENGTH} caracteres)',
        'INVALID_URL': 'URL inválida ou inacessível',
        'TIMEOUT': 'Tempo limite excedido durante a análise',
        'NO_CONTENT_EXTRACTED': 'Não foi possível extrair conteúdo da URL',
        'ALL_SOURCES_FAILED': 'Todas as fontes falharam. Tente novamente mais tarde',
        'INTERNAL_ERROR': 'Erro interno do servidor',
        'RATE_LIMIT_EXCEEDED': 'Limite de requisições excedido. Tente novamente mais tarde'
    }
    
    
    # ========================================================================
    # MENSAGENS DE JUSTIFICATIVA (templates)
    # ========================================================================
    
    JUSTIFICATION_TEMPLATES = {
        'high_veracity': 'Informação amplamente confirmada por múltiplas fontes confiáveis.',
        'medium_veracity': 'Informação parcialmente confirmada. Algumas fontes mencionam o tema.',
        'low_veracity': 'Pouca ou nenhuma confirmação encontrada em fontes confiáveis.',
        'no_sources': 'Tema não encontrado em portais de notícias confiáveis. Possível desinformação.',
        'contradiction': 'ATENÇÃO: Fontes apresentam informações contraditórias sobre o tema.',
        'very_recent': 'Notícia muito recente. Aguarde confirmação de fontes estabelecidas.',
        'satire_detected': 'ATENÇÃO: Conteúdo possivelmente satírico ou humorístico.',
        'ambiguous': 'Conteúdo vago ou ambíguo, dificultando verificação precisa.'
    }
    
    
    # ========================================================================
    # CONFIGURAÇÕES DE LOGGING (para debug)
    # ========================================================================
    
    # Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOG_LEVEL = 'INFO' if ENV == 'production' else 'DEBUG'
    
    # Formato das mensagens de log
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    
    # ========================================================================
    # PALAVRAS-CHAVE E STOPWORDS
    # ========================================================================
    
    # Stopwords customizadas (além das do NLTK)
    CUSTOM_STOPWORDS = [
        'disse', 'afirmou', 'anunciou', 'informou', 'segundo',
        'acordo', 'através', 'ainda', 'apenas', 'assim',
        'hoje', 'ontem', 'amanhã', 'agora', 'então'
    ]
    
    # Palavras que indicam possível sátira
    SATIRE_INDICATORS = [
        'sensacionalista', 'piauí herald', 'the piauí',
        'infake news', 'velho oeste', 'satiria'
    ]


# ============================================================================
# CONFIGURAÇÕES ESPECÍFICAS POR AMBIENTE
# ============================================================================

class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento"""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Configurações para ambiente de produção"""
    DEBUG = False
    ENV = 'production'
    # Em produção, desabilitar informações sensíveis em erros
    PROPAGATE_EXCEPTIONS = False


class TestingConfig(Config):
    """Configurações para testes"""
    TESTING = True
    DEBUG = True
    # Usar timeouts menores em testes
    REQUEST_TIMEOUT = 2
    SCRAPING_TIMEOUT = 3


# ============================================================================
# SELEÇÃO AUTOMÁTICA DE CONFIGURAÇÃO
# ============================================================================

# Mapear nome do ambiente para classe de configuração
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

# Pegar configuração atual baseada na variável de ambiente
current_config = config_by_name.get(
    os.getenv('FLASK_ENV', 'development'),
    DevelopmentConfig
)


# ============================================================================
# FUNÇÃO AUXILIAR PARA OBTER CONFIGURAÇÕES
# ============================================================================

def get_config():
    """
    Retorna a configuração atual do sistema.
    
    Returns:
        Config: Objeto de configuração (DevelopmentConfig, ProductionConfig, etc)
    
    Exemplo:
        from config import get_config
        config = get_config()
        print(config.TRUSTED_SOURCES)
    """
    return current_config


# ============================================================================
# VALIDAÇÃO DE CONFIGURAÇÕES
# ============================================================================

def validate_config():
    """
    Valida se todas as configurações necessárias estão corretas.
    Útil para rodar na inicialização e detectar problemas.
    
    Returns:
        tuple: (bool, list) - (sucesso, lista de erros)
    """
    errors = []
    
    # Validar timeouts
    if Config.REQUEST_TIMEOUT < 1:
        errors.append("REQUEST_TIMEOUT deve ser >= 1 segundo")
    
    if Config.MIN_CONTENT_LENGTH < 10:
        errors.append("MIN_CONTENT_LENGTH deve ser >= 10 caracteres")
    
    if Config.MAX_CONTENT_LENGTH < Config.MIN_CONTENT_LENGTH:
        errors.append("MAX_CONTENT_LENGTH deve ser maior que MIN_CONTENT_LENGTH")
    
    # Validar scores
    if not (0 <= Config.MIN_VERACITY_SCORE < Config.MAX_VERACITY_SCORE <= 100):
        errors.append("MIN_VERACITY_SCORE e MAX_VERACITY_SCORE devem estar entre 0-100")
    
    # Validar thresholds de similaridade
    if not (0 <= Config.SIMILARITY_THRESHOLD_LOW < Config.SIMILARITY_THRESHOLD_MEDIUM < Config.SIMILARITY_THRESHOLD_HIGH <= 1):
        errors.append("Thresholds de similaridade devem estar em ordem crescente entre 0-1")
    
    # Validar fontes confiáveis
    if len(Config.TRUSTED_SOURCES) == 0:
        errors.append("Deve haver pelo menos uma fonte confiável configurada")
    
    return (len(errors) == 0, errors)


# ============================================================================
# EXECUTAR VALIDAÇÃO AO IMPORTAR (apenas em desenvolvimento)
# ============================================================================

if __name__ == "__main__":
    # Validar configurações
    success, errors = validate_config()
    
    if success:
        print("✅ Todas as configurações estão corretas!")
        print(f"\n📋 Ambiente: {current_config.ENV}")
        print(f"📋 Debug: {current_config.DEBUG}")
        print(f"📋 Fontes confiáveis: {len(current_config.TRUSTED_SOURCES)}")
        print(f"📋 Timeout de requisições: {current_config.REQUEST_TIMEOUT}s")
    else:
        print("❌ Erros encontrados nas configurações:")
        for error in errors:
            print(f"  - {error}")