"""
scraper.py - Módulo de Scraping de Notícias

Responsabilidade:
    Extrair conteúdo completo das URLs encontradas pelo searcher.
    Usa o mesmo sistema do extractor.py, mas em batch (múltiplas URLs).

Estratégia:
    - Usar newspaper3k (principal)
    - Fallback para BeautifulSoup
    - Processamento paralelo para velocidade
    - Cache de resultados
    - Tratamento robusto de erros

Autor: Projeto Acadêmico
Data: 2025
"""

from modules.extractor import ContentExtractor
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import Config
import time
import json
import os
import hashlib
from datetime import datetime


# ============================================================================
# CLASSE DE CACHE PARA SCRAPING
# ============================================================================

class ScraperCache:
    """
    Cache específico para resultados de scraping.
    Similar ao SearchCache, mas para conteúdo extraído.
    """
    
    def __init__(self, cache_dir='cache_scraping'):
        """
        Inicializa cache de scraping.
        
        Args:
            cache_dir (str): Diretório para cache
        """
        self.cache_dir = cache_dir
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    
    def _gerar_chave(self, url):
        """
        Gera chave única para URL.
        
        Args:
            url (str): URL da notícia
            
        Returns:
            str: Hash MD5
        """
        return hashlib.md5(url.encode()).hexdigest()
    
    
    def obter(self, url):
        """
        Obtém conteúdo do cache se existir.
        
        Args:
            url (str): URL da notícia
            
        Returns:
            dict ou None: Conteúdo ou None
        """
        if not Config.ENABLE_CACHE:
            return None
        
        chave = self._gerar_chave(url)
        cache_file = os.path.join(self.cache_dir, f"{chave}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Verificar expiração
            timestamp = cache_data.get('timestamp', 0)
            now = datetime.now().timestamp()
            
            if (now - timestamp) > Config.CACHE_EXPIRATION:
                os.remove(cache_file)
                return None
            
            return cache_data.get('conteudo')
        
        except Exception as e:
            print(f"⚠️  Erro ao ler cache de scraping: {e}")
            return None
    
    
    def salvar(self, url, conteudo):
        """
        Salva conteúdo no cache.
        
        Args:
            url (str): URL da notícia
            conteudo (dict): Conteúdo extraído
        """
        if not Config.ENABLE_CACHE:
            return
        
        chave = self._gerar_chave(url)
        cache_file = os.path.join(self.cache_dir, f"{chave}.json")
        
        cache_data = {
            'url': url,
            'timestamp': datetime.now().timestamp(),
            'conteudo': conteudo
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  Erro ao salvar cache de scraping: {e}")


# ============================================================================
# CLASSE PRINCIPAL - NEWS SCRAPER
# ============================================================================

class NewsScraper:
    """
    Scraper especializado em extrair conteúdo de múltiplas notícias.
    Otimizado para processar resultados do searcher.
    """
    
    def __init__(self):
        """Inicializa scraper com extractor e cache"""
        self.extractor = ContentExtractor()
        self.cache = ScraperCache()
    
    
    def scrape_resultados_busca(self, resultados_busca):
        """
        Extrai conteúdo de todos os resultados da busca.
        
        Args:
            resultados_busca (dict): Resultado do searcher.buscar_em_todas_fontes()
            
        Returns:
            dict: Conteúdos extraídos ou dados da busca (título+snippet)
        """
        print(f"\n📥 Iniciando scraping de notícias encontradas...")
        
        # Fontes problemáticas que devem usar apenas título+snippet
        fontes_problematicas = Config.SOURCES_WITH_PAYWALL
        
        resultados_scraping = {}
        total_urls = 0
        total_sucesso = 0
        
        # Para cada fonte
        for fonte_nome, fonte_resultados in resultados_busca.items():
            if fonte_nome == 'metadata':
                continue
            
            if not fonte_resultados:
                resultados_scraping[fonte_nome] = []
                continue
            
            print(f"\n  📰 {fonte_nome}: {len(fonte_resultados)} URL(s)")
            
            # Verificar se é fonte problemática
            if fonte_nome in fontes_problematicas:
                print(f"    ⚠️  Fonte com paywall detectada - usando título+snippet")
                conteudos = self._usar_titulo_snippet(fonte_resultados)
                sucessos = len([c for c in conteudos if c['sucesso']])
            else:
                # Extrair conteúdo normalmente
                urls = [item['url'] for item in fonte_resultados]
                conteudos = self.scrape_urls(urls)
                sucessos = sum(1 for c in conteudos if c['sucesso'])
            
            resultados_scraping[fonte_nome] = conteudos
            
            total_urls += len(fonte_resultados)
            total_sucesso += sucessos
            
            print(f"    ✅ {sucessos}/{len(fonte_resultados)} processados")
        
        # Calcular taxa de sucesso
        taxa_sucesso = (total_sucesso / total_urls * 100) if total_urls > 0 else 0
        
        print(f"\n✅ Scraping concluído: {total_sucesso}/{total_urls} ({taxa_sucesso:.1f}%)")
        
        return {
            **resultados_scraping,
            'metadata': {
                'total_scraped': total_urls,
                'total_sucesso': total_sucesso,
                'total_falhas': total_urls - total_sucesso,
                'taxa_sucesso': round(taxa_sucesso, 2)
            }
        }
    
    
    def _usar_titulo_snippet(self, resultados_busca):
        """
        Usa título + snippet como "conteúdo" sem fazer scraping.
        Para fontes com paywall que bloqueiam acesso.
        
        Args:
            resultados_busca (list): Lista de resultados da busca
            
        Returns:
            list: Lista com "conteúdo" montado a partir de título+snippet
        """
        conteudos = []
        
        for resultado in resultados_busca:
            titulo = resultado.get('title', '')
            snippet = resultado.get('snippet', '')
            url = resultado.get('url', '')
            
            # Montar "texto" a partir de título + snippet
            texto_completo = f"{titulo}. {snippet}"
            
            # Se o texto for muito curto, marcar como falha
            if len(texto_completo.strip()) < 30:
                conteudos.append({
                    'url': url,
                    'titulo': titulo,
                    'texto': '',
                    'data_publicacao': None,
                    'autor': None,
                    'metodo_extracao': 'titulo_snippet',
                    'sucesso': False,
                    'erro': 'Título+snippet muito curto'
                })
                continue
            
            conteudos.append({
                'url': url,
                'titulo': titulo,
                'texto': texto_completo,
                'data_publicacao': None,
                'autor': None,
                'metodo_extracao': 'titulo_snippet',
                'sucesso': True,
                'erro': None
            })
        
        return conteudos
    
    
    def scrape_urls(self, urls):
        """
        Extrai conteúdo de múltiplas URLs em paralelo.
        
        Args:
            urls (list): Lista de URLs
            
        Returns:
            list: Lista de dicionários com conteúdo extraído
        """
        if not urls:
            return []
        
        resultados = []
        
        # Verificar cache primeiro
        urls_para_scrape = []
        for url in urls:
            cache_result = self.cache.obter(url)
            if cache_result:
                print(f"      💾 Cache hit: {url[:50]}...")
                resultados.append(cache_result)
            else:
                urls_para_scrape.append(url)
        
        # Se não há URLs para scrape (tudo em cache)
        if not urls_para_scrape:
            return resultados
        
        # Processar URLs em paralelo (máximo 3 threads simultâneas)
        max_workers = min(3, len(urls_para_scrape))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submeter tarefas
            future_to_url = {
                executor.submit(self._scrape_url_single, url): url 
                for url in urls_para_scrape
            }
            
            # Coletar resultados conforme completam
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    resultado = future.result()
                    resultados.append(resultado)
                    
                    # Salvar no cache se sucesso
                    if resultado['sucesso']:
                        self.cache.salvar(url, resultado)
                
                except Exception as e:
                    print(f"      ❌ Erro ao processar {url[:50]}: {e}")
                    resultados.append({
                        'url': url,
                        'titulo': None,
                        'texto': None,
                        'data_publicacao': None,
                        'autor': None,
                        'sucesso': False,
                        'erro': str(e)
                    })
        
        return resultados
    
    
    def _scrape_url_single(self, url):
        """
        Extrai conteúdo de uma única URL.
        Wrapper para usar com ThreadPoolExecutor.
        
        Args:
            url (str): URL da notícia
            
        Returns:
            dict: Conteúdo extraído
        """
        # Garantir que URL está completa e não truncada
        if not url.startswith('http'):
            url = 'https://' + url
        
        print(f"      🔄 Extraindo: {url[:80]}...")
        
        # Usar o extractor que já criamos
        resultado = self.extractor.extract(url)
        
        # IMPORTANTE: Manter URL original completa no resultado
        resultado['url'] = url  # Garantir que URL não seja truncada
        
        if resultado['sucesso']:
            print(f"      ✅ Sucesso: {resultado['titulo'][:40]}...")
        else:
            print(f"      ❌ Falha: {resultado['erro'][:40]}...")
        
        # Pequeno delay para não sobrecarregar
        time.sleep(0.5)
        
        return resultado
    
    
    def scrape_url(self, url):
        """
        Método de conveniência para extrair uma única URL.
        
        Args:
            url (str): URL da notícia
            
        Returns:
            dict: Conteúdo extraído
        """
        # Verificar cache
        cache_result = self.cache.obter(url)
        if cache_result:
            return cache_result
        
        # Extrair
        resultado = self._scrape_url_single(url)
        
        # Salvar cache se sucesso
        if resultado['sucesso']:
            self.cache.salvar(url, resultado)
        
        return resultado


# ============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# ============================================================================

def scrape_noticias(resultados_busca):
    """
    Função simplificada para scrape de resultados de busca.
    
    Args:
        resultados_busca (dict): Resultado do searcher
        
    Returns:
        dict: Conteúdos extraídos
        
    Exemplo:
        >>> from modules.searcher import buscar_noticias
        >>> from modules.scraper import scrape_noticias
        >>> 
        >>> # Buscar
        >>> resultados = buscar_noticias("Lula reforma")
        >>> 
        >>> # Extrair conteúdo
        >>> conteudos = scrape_noticias(resultados)
        >>> 
        >>> # Acessar
        >>> for noticia in conteudos['G1']:
        >>>     if noticia['sucesso']:
        >>>         print(noticia['titulo'])
        >>>         print(noticia['texto'][:200])
    """
    scraper = NewsScraper()
    return scraper.scrape_resultados_busca(resultados_busca)


# ============================================================================
# TESTE DO MÓDULO
# ============================================================================

if __name__ == "__main__":
    """
    Testes do módulo scraper.
    Execute: python modules/scraper.py
    """
    
    print("=" * 70)
    print("🧪 TESTANDO MÓDULO SCRAPER")
    print("=" * 70)
    print()
    
    # Simular resultado de busca (normalmente viria do searcher)
    resultados_busca_mock = {
        'G1': [
            {
                'title': 'Notícia teste 1',
                'url': 'https://g1.globo.com/',  # URL real para testar
                'snippet': 'Snippet de teste'
            }
        ],
        'Folha de S.Paulo': [
            {
                'title': 'Notícia teste 2',
                'url': 'https://www.folha.uol.com.br/',  # URL real para testar
                'snippet': 'Snippet de teste'
            }
        ],
        'metadata': {
            'total_resultados': 2,
            'fontes_com_sucesso': 2
        }
    }
    
    print("📝 Simulando busca com 2 URLs...")
    print()
    
    # Fazer scraping
    conteudos = scrape_noticias(resultados_busca_mock)
    
    # Mostrar resultados
    print("\n" + "=" * 70)
    print("✅ RESULTADOS DO SCRAPING:")
    print("=" * 70)
    print()
    
    for fonte_nome, fonte_conteudos in conteudos.items():
        if fonte_nome == 'metadata':
            continue
        
        print(f"📰 {fonte_nome}:")
        for i, conteudo in enumerate(fonte_conteudos, 1):
            print(f"\n  {i}. URL: {conteudo['url'][:60]}...")
            if conteudo['sucesso']:
                print(f"     ✅ Título: {conteudo['titulo'][:50]}...")
                print(f"     📄 Texto: {len(conteudo['texto'])} caracteres")
                print(f"     📅 Data: {conteudo['data_publicacao']}")
                print(f"     ✍️  Autor: {conteudo['autor']}")
            else:
                print(f"     ❌ Erro: {conteudo['erro']}")
        print()
    
    # Metadata
    meta = conteudos['metadata']
    print("📊 ESTATÍSTICAS:")
    print(f"  Total processado: {meta['total_scraped']}")
    print(f"  Sucessos: {meta['total_sucesso']}")
    print(f"  Falhas: {meta['total_falhas']}")
    print(f"  Taxa de sucesso: {meta['taxa_sucesso']:.1f}%")