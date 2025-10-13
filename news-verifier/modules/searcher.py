"""
searcher.py - Módulo de Busca em Fontes Confiáveis

Responsabilidade:
    Buscar notícias relacionadas nas 5 fontes confiáveis usando:
    1. Mock (dados simulados para desenvolvimento)
    2. SerpAPI (API oficial do Google - recomendado)
    3. googlesearch-python (scraping do Google - fallback)
    4. Busca direta nos sites (scraping - último recurso)

Estratégia Híbrida:
    - Tenta múltiplos métodos automaticamente
    - Sistema de cache para economizar requisições
    - Fallback automático se um método falhar

Autor: Projeto Acadêmico
Data: 2025
"""

import requests
import time
import json
import os
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from config import Config
import random

# Importações condicionais (podem não estar instaladas)
try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False
    print("⚠️  SerpAPI não disponível. Instale com: pip install google-search-results")

try:
    from googlesearch import search as google_search
    GOOGLESEARCH_AVAILABLE = True
except ImportError:
    GOOGLESEARCH_AVAILABLE = False
    print("⚠️  googlesearch-python não disponível. Instale com: pip install googlesearch-python")


# ============================================================================
# CLASSE DE CACHE
# ============================================================================

class SearchCache:
    """
    Gerencia cache de resultados de busca para economizar requisições.
    """
    
    def __init__(self, cache_dir='cache_searches'):
        """
        Inicializa cache.
        
        Args:
            cache_dir (str): Diretório para armazenar cache
        """
        self.cache_dir = cache_dir
        
        # Criar diretório se não existir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    
    def _gerar_chave(self, query, site):
        """
        Gera chave única para query + site.
        
        Args:
            query (str): Query de busca
            site (str): Domínio do site
            
        Returns:
            str: Hash MD5 como chave
        """
        texto = f"{query}_{site}".lower()
        return hashlib.md5(texto.encode()).hexdigest()
    
    
    def obter(self, query, site):
        """
        Obtém resultado do cache se existir e não expirou.
        
        Args:
            query (str): Query de busca
            site (str): Domínio do site
            
        Returns:
            dict ou None: Resultado em cache ou None
        """
        if not Config.ENABLE_CACHE:
            return None
        
        chave = self._gerar_chave(query, site)
        cache_file = os.path.join(self.cache_dir, f"{chave}.json")
        
        # Verificar se arquivo existe
        if not os.path.exists(cache_file):
            return None
        
        # Ler cache
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Verificar se expirou
            timestamp = cache_data.get('timestamp', 0)
            now = datetime.now().timestamp()
            
            if (now - timestamp) > Config.CACHE_EXPIRATION:
                # Cache expirado, deletar
                os.remove(cache_file)
                return None
            
            return cache_data.get('resultados')
        
        except Exception as e:
            print(f"⚠️  Erro ao ler cache: {e}")
            return None
    
    
    def salvar(self, query, site, resultados):
        """
        Salva resultado no cache.
        
        Args:
            query (str): Query de busca
            site (str): Domínio do site
            resultados (list): Lista de resultados
        """
        if not Config.ENABLE_CACHE:
            return
        
        chave = self._gerar_chave(query, site)
        cache_file = os.path.join(self.cache_dir, f"{chave}.json")
        
        cache_data = {
            'query': query,
            'site': site,
            'timestamp': datetime.now().timestamp(),
            'resultados': resultados
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  Erro ao salvar cache: {e}")


# ============================================================================
# CLASSE PRINCIPAL - SEARCH ENGINE
# ============================================================================

class SearchEngine:
    """
    Motor de busca híbrido que tenta múltiplos métodos automaticamente.
    """
    
    def __init__(self):
        """Inicializa motor de busca com cache"""
        self.cache = SearchCache()
        self.serpapi_count = 0  # Contador de requisições SerpAPI
    
    
    def buscar_em_todas_fontes(self, query):
        """
        Busca query em todas as fontes confiáveis.
        
        Args:
            query (str): Query de busca gerada pelo NLP
            
        Returns:
            dict: {
                'fonte1': [resultados],
                'fonte2': [resultados],
                ...
                'metadata': {
                    'total_resultados': int,
                    'fontes_com_sucesso': int,
                    'metodo_usado': str
                }
            }
        """
        print(f"\n🔍 Iniciando busca nas {len(Config.TRUSTED_SOURCES)} fontes...")
        print(f"Query: {query}")
        print(f"Modo: {Config.SEARCH_MODE}")
        print()
        
        resultados_por_fonte = {}
        fontes_sucesso = 0
        total_resultados = 0
        
        for fonte in Config.TRUSTED_SOURCES:
            if not fonte['ativo']:
                continue
            
            nome_fonte = fonte['nome']
            dominio = fonte['dominio']
            
            print(f"  Buscando em: {nome_fonte}...")
            
            # Buscar nesta fonte
            resultados = self.buscar(query, dominio)
            
            if resultados:
                resultados_por_fonte[nome_fonte] = resultados
                fontes_sucesso += 1
                total_resultados += len(resultados)
                print(f"    ✅ {len(resultados)} resultados encontrados")
            else:
                resultados_por_fonte[nome_fonte] = []
                print(f"    ❌ Nenhum resultado")
            
            # Delay entre buscas
            time.sleep(Config.SEARCH_DELAY)
        
        print(f"\n✅ Busca concluída: {total_resultados} resultados em {fontes_sucesso} fontes")
        
        return {
            **resultados_por_fonte,
            'metadata': {
                'total_resultados': total_resultados,
                'fontes_com_sucesso': fontes_sucesso,
                'total_fontes': len([f for f in Config.TRUSTED_SOURCES if f['ativo']]),
                'query_original': query,
                'modo_busca': Config.SEARCH_MODE
            }
        }
    
    
    def buscar(self, query, site):
        """
        Busca em um site específico usando estratégia híbrida.
        
        Args:
            query (str): Query de busca
            site (str): Domínio do site
            
        Returns:
            list: Lista de resultados [{title, url, snippet}, ...]
        """
        # Verificar cache primeiro
        cache_result = self.cache.obter(query, site)
        if cache_result:
            print(f"    💾 Cache hit!")
            return cache_result
        
        # Determinar método(s) a usar
        if Config.SEARCH_MODE == 'mock':
            resultados = self._buscar_mock(query, site)
        
        elif Config.SEARCH_MODE == 'serpapi':
            resultados = self._buscar_serpapi(query, site)
        
        elif Config.SEARCH_MODE == 'googlesearch':
            resultados = self._buscar_googlesearch(query, site)
        
        elif Config.SEARCH_MODE == 'direct':
            resultados = self._buscar_direto(query, site)
        
        elif Config.SEARCH_MODE == 'hybrid':
            # Tentar métodos na ordem de prioridade
            resultados = self._buscar_hybrid(query, site)
        
        else:
            print(f"    ⚠️  Modo desconhecido: {Config.SEARCH_MODE}")
            resultados = []
        
        # Salvar no cache
        if resultados:
            self.cache.salvar(query, site, resultados)
        
        return resultados
    
    
    def _buscar_hybrid(self, query, site):
        """
        Tenta múltiplos métodos até obter sucesso.
        
        Args:
            query (str): Query de busca
            site (str): Domínio do site
            
        Returns:
            list: Resultados
        """
        for metodo in Config.SEARCH_METHODS_PRIORITY:
            try:
                print(f"      Tentando método: {metodo}")
                
                if metodo == 'serpapi':
                    resultados = self._buscar_serpapi(query, site)
                elif metodo == 'googlesearch':
                    resultados = self._buscar_googlesearch(query, site)
                elif metodo == 'direct':
                    resultados = self._buscar_direto(query, site)
                else:
                    continue
                
                if resultados:
                    print(f"      ✅ Sucesso com {metodo}")
                    return resultados
                
            except Exception as e:
                print(f"      ⚠️  {metodo} falhou: {str(e)[:50]}...")
                continue
        
        print(f"      ❌ Todos os métodos falharam")
        return []
    
    
    def _buscar_mock(self, query, site):
        """
        Retorna dados simulados para desenvolvimento.
        NÃO faz requisições reais.
        
        Args:
            query (str): Query de busca
            site (str): Domínio do site
            
        Returns:
            list: Resultados simulados
        """
        # Simular diferentes cenários
        num_resultados = random.randint(1, 3)
        
        resultados = []
        for i in range(num_resultados):
            resultados.append({
                'title': f'Notícia {i+1} sobre {query[:30]} - {site}',
                'url': f'https://{site}/noticia-simulada-{i+1}',
                'snippet': f'Este é um resultado simulado para testes. Query: {query}. '
                          f'Em produção, aqui aparecerá o snippet real da notícia encontrada.'
            })
        
        return resultados
    
    
    def _buscar_serpapi(self, query, site):
        """
        Busca usando SerpAPI (Google Search API oficial).
        Requer chave de API.
        
        Args:
            query (str): Query de busca
            site (str): Domínio do site
            
        Returns:
            list: Resultados
        """
        if not SERPAPI_AVAILABLE:
            raise Exception("SerpAPI não instalado")
        
        if not Config.SERPAPI_KEY:
            raise Exception("SERPAPI_KEY não configurada")
        
        # Verificar limite de requisições
        if self.serpapi_count >= Config.SERPAPI_REQUESTS_LIMIT:
            raise Exception(f"Limite de {Config.SERPAPI_REQUESTS_LIMIT} requisições atingido")
        
        # Construir query com operador site:
        search_query = f"site:{site} {query}"
        
        # Parâmetros da busca
        params = {
            "q": search_query,
            "api_key": Config.SERPAPI_KEY,
            "num": Config.MAX_SEARCH_RESULTS,
            "hl": "pt-br",
            "gl": "br"
        }
        
        # Fazer requisição
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Incrementar contador
        self.serpapi_count += 1
        
        # Extrair resultados orgânicos
        organic_results = results.get('organic_results', [])
        
        resultados = []
        for item in organic_results[:Config.MAX_SEARCH_RESULTS]:
            # GARANTIR que URL está completa
            url = item.get('link', '')
            
            # Validação: URL deve ser completa
            if not url or len(url) < 20:
                continue
            
            # Garantir que começa com http
            if not url.startswith('http'):
                url = 'https://' + url
            
            resultados.append({
                'title': item.get('title', ''),
                'url': url,  # URL COMPLETA E VALIDADA
                'snippet': item.get('snippet', '')
            })
        
        return resultados
    
    
    def _buscar_googlesearch(self, query, site):
        """
        Busca usando googlesearch-python (scraping do Google).
        Gratuito mas pode ser bloqueado.
        
        Args:
            query (str): Query de busca
            site (str): Domínio do site
            
        Returns:
            list: Resultados
        """
        if not GOOGLESEARCH_AVAILABLE:
            raise Exception("googlesearch-python não instalado")
        
        # Construir query
        search_query = f"site:{site} {query}"
        
        # Fazer busca
        try:
            urls = list(google_search(
                search_query,
                num_results=Config.MAX_SEARCH_RESULTS,
                lang='pt',
                sleep_interval=2  # Delay para não ser bloqueado
            ))
            
            # googlesearch retorna apenas URLs, precisamos buscar título/snippet
            resultados = []
            for url in urls:
                # Tentar extrair título fazendo requisição à página
                try:
                    response = requests.get(
                        url,
                        headers=Config.DEFAULT_HEADERS,
                        timeout=5
                    )
                    soup = BeautifulSoup(response.content, 'lxml')
                    
                    # Extrair título
                    title = ''
                    title_tag = soup.find('title')
                    if title_tag:
                        title = title_tag.get_text()
                    
                    # Extrair snippet (primeiro parágrafo)
                    snippet = ''
                    p_tags = soup.find_all('p', limit=3)
                    if p_tags:
                        snippet = ' '.join([p.get_text()[:100] for p in p_tags])
                    
                    resultados.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet[:200]
                    })
                
                except Exception as e:
                    # Se falhar ao extrair detalhes, adicionar apenas URL
                    resultados.append({
                        'title': url.split('/')[-1],
                        'url': url,
                        'snippet': ''
                    })
            
            return resultados
        
        except Exception as e:
            raise Exception(f"googlesearch falhou: {e}")
    
    
    def _buscar_direto(self, query, site):
        """
        Busca diretamente no site usando página de busca interna.
        Faz scraping da página de resultados.
        
        Args:
            query (str): Query de busca
            site (str): Domínio do site
            
        Returns:
            list: Resultados
        """
        # Encontrar configuração da fonte
        fonte = None
        for f in Config.TRUSTED_SOURCES:
            if f['dominio'] == site:
                fonte = f
                break
        
        if not fonte or not fonte.get('url_busca'):
            raise Exception(f"URL de busca não configurada para {site}")
        
        # Construir URL de busca
        search_url = fonte['url_busca'] + query.replace(' ', '+')
        
        # Fazer requisição
        headers = Config.DEFAULT_HEADERS.copy()
        headers['User-Agent'] = random.choice(Config.USER_AGENTS)
        
        response = requests.get(
            search_url,
            headers=headers,
            timeout=Config.SCRAPING_TIMEOUT
        )
        
        response.raise_for_status()
        
        # Parsear HTML
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Estratégia genérica de extração (funciona na maioria dos sites)
        resultados = []
        
        # Procurar por links que parecem ser notícias
        # Cada site tem estrutura diferente, aqui fazemos tentativa genérica
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            
            # Filtros básicos
            if not href or href.startswith('#'):
                continue
            
            # Construir URL completa se relativa
            if href.startswith('/'):
                href = f"https://{site}{href}"
            
            # Verificar se URL pertence ao site
            if site not in href:
                continue
            
            # Extrair título (texto do link ou title attribute)
            title = link.get_text().strip() or link.get('title', '')
            
            if not title or len(title) < 10:
                continue
            
            # Tentar encontrar snippet próximo
            snippet = ''
            parent = link.find_parent(['div', 'article', 'li'])
            if parent:
                snippet = parent.get_text()[:200]
            
            resultados.append({
                'title': title[:150],
                'url': href,
                'snippet': snippet
            })
            
            # Limitar resultados
            if len(resultados) >= Config.MAX_SEARCH_RESULTS:
                break
        
        return resultados


# ============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# ============================================================================

def buscar_noticias(query):
    """
    Função simplificada para buscar notícias em todas as fontes.
    
    Args:
        query (str): Query de busca
        
    Returns:
        dict: Resultados por fonte
        
    Exemplo:
        >>> resultados = buscar_noticias("Lula reforma tributária")
        >>> print(resultados['G1'])
        >>> print(resultados['metadata'])
    """
    engine = SearchEngine()
    return engine.buscar_em_todas_fontes(query)


# ============================================================================
# TESTE DO MÓDULO
# ============================================================================

if __name__ == "__main__":
    """
    Testes do módulo searcher.
    Execute: python modules/searcher.py
    """
    
    print("=" * 70)
    print("🧪 TESTANDO MÓDULO SEARCHER")
    print("=" * 70)
    print()
    
    # Query de teste
    query_teste = "Lula reforma tributária Brasil"
    
    print(f"📝 Query de teste: {query_teste}")
    print(f"🔧 Modo configurado: {Config.SEARCH_MODE}")
    print()
    
    # Buscar
    resultados = buscar_noticias(query_teste)
    
    # Mostrar resultados
    print("\n" + "=" * 70)
    print("✅ RESULTADOS:")
    print("=" * 70)
    print()
    
    for fonte_nome, fonte_resultados in resultados.items():
        if fonte_nome == 'metadata':
            continue
        
        print(f"📰 {fonte_nome}:")
        if fonte_resultados:
            for i, item in enumerate(fonte_resultados, 1):
                print(f"  {i}. {item['title'][:60]}...")
                print(f"     URL: {item['url']}")
                print(f"     Snippet: {item['snippet'][:80]}...")
                print()
        else:
            print("  (sem resultados)")
            print()
    
    # Metadata
    meta = resultados['metadata']
    print("📊 ESTATÍSTICAS:")
    print(f"  Total de resultados: {meta['total_resultados']}")
    print(f"  Fontes com sucesso: {meta['fontes_com_sucesso']}/{meta['total_fontes']}")
    print(f"  Modo usado: {meta['modo_busca']}")