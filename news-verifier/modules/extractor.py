"""
extractor.py - Módulo de Extração de Conteúdo (Melhorado)

Responsabilidade:
    Extrair conteúdo textual de URLs de notícias com múltiplas estratégias:
    - newspaper3k (principal)
    - trafilatura (fallback 1)
    - readability (fallback 2)
    - BeautifulSoup genérico (fallback 3)
    - AMP pages (fallback especial)
    - Globo-specific (fallback específico)

Autor: Projeto Acadêmico
Data: 2025
"""

import requests
from newspaper import Article
from bs4 import BeautifulSoup
import validators
from datetime import datetime
from config import Config
import time
import random

# Novas bibliotecas
try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False
    print("⚠️  trafilatura não disponível. Instale com: pip install trafilatura")

try:
    from readability import Document
    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False
    print("⚠️  readability-lxml não disponível. Instale com: pip install readability-lxml")


# ============================================================================
# CLASSE PRINCIPAL - EXTRACTOR
# ============================================================================

class ContentExtractor:
    """
    Classe responsável por extrair conteúdo de URLs de notícias.
    
    Atributos:
        timeout (int): Tempo máximo para requisição HTTP
        headers (dict): Headers HTTP para simular navegador
        retry_attempts (int): Número de tentativas em caso de falha
    """
    
    def __init__(self):
        """Inicializa o extrator com configurações do config.py"""
        self.timeout = Config.REQUEST_TIMEOUT
        self.headers = Config.DEFAULT_HEADERS.copy()
        self.retry_attempts = Config.MAX_RETRIES
        self.retry_delay = Config.RETRY_DELAY
    
    
    def extract(self, url):
        """
        Método principal para extrair conteúdo de uma URL.
        Agora com 6 estratégias de fallback!
        
        Args:
            url (str): URL da notícia
            
        Returns:
            dict: Dicionário com conteúdo extraído
        """
        
        # ETAPA 1: VALIDAR URL
        if not self._validar_url(url):
            return {
                'url': url, 'titulo': None, 'texto': None,
                'data_publicacao': None, 'autor': None,
                'metodo_extracao': None, 'sucesso': False,
                'erro': 'URL inválida'
            }
    
    
    def _validar_url(self, url):
        
        # ETAPA 2: Obter HTML
        html = self._obter_html(url)
        if not html:
            return {
                'url': url, 'titulo': None, 'texto': None,
                'data_publicacao': None, 'autor': None,
                'metodo_extracao': None, 'sucesso': False,
                'erro': 'Não foi possível obter HTML'
            }
        
        # ESTRATÉGIA 1: newspaper3k
        resultado = self._extrair_com_newspaper(url)
        if resultado['sucesso'] and len(resultado['texto'].split()) >= 80:
            return resultado
        
        melhor_resultado = resultado  # Guardar para comparar
        
        # ESTRATÉGIA 2: trafilatura
        if TRAFILATURA_AVAILABLE:
            print(f"⚠️  Newspaper3k insuficiente, tentando trafilatura...")
            resultado = self._extrair_com_trafilatura(html, url)
            if resultado['sucesso'] and len(resultado['texto'].split()) > len(melhor_resultado.get('texto', '').split()):
                melhor_resultado = resultado
                if len(resultado['texto'].split()) >= 80:
                    return resultado
        
        # ESTRATÉGIA 3: AMP fallback
        print(f"⚠️  Tentando versão AMP...")
        resultado = self._extrair_amp(html, url)
        if resultado['sucesso'] and len(resultado['texto'].split()) > len(melhor_resultado.get('texto', '').split()):
            melhor_resultado = resultado
            if len(resultado['texto'].split()) >= 80:
                return resultado
        
        # ESTRATÉGIA 4: readability
        if READABILITY_AVAILABLE:
            print(f"⚠️  Tentando readability...")
            resultado = self._extrair_com_readability(html)
            if resultado['sucesso'] and len(resultado['texto'].split()) > len(melhor_resultado.get('texto', '').split()):
                melhor_resultado = resultado
                if len(resultado['texto'].split()) >= 80:
                    return resultado
        
        # ESTRATÉGIA 5: Globo-specific
        if 'globo.com' in url.lower():
            print(f"⚠️  Site Globo detectado, tentando extrator específico...")
            resultado = self._extrair_globo(html)
            if resultado['sucesso'] and len(resultado['texto'].split()) > len(melhor_resultado.get('texto', '').split()):
                melhor_resultado = resultado
                if len(resultado['texto'].split()) >= 80:
                    return resultado
        
        # ESTRATÉGIA 6: BeautifulSoup genérico (último recurso)
        print(f"⚠️  Tentando BeautifulSoup genérico...")
        resultado = self._extrair_com_beautifulsoup(url)
        if resultado['sucesso'] and len(resultado['texto'].split()) > len(melhor_resultado.get('texto', '').split()):
            melhor_resultado = resultado
        
        return melhor_resultado
    
    
    def _obter_html(self, url):
        """
        Obtém HTML da URL com retry.
        
        Args:
            url (str): URL
            
        Returns:
            str: HTML ou vazio
        """
        for tentativa in range(self.retry_attempts):
            try:
                headers = self.headers.copy()
                headers['User-Agent'] = random.choice(Config.USER_AGENTS)
                
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response.text
            
            except Exception as e:
                if tentativa < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                    continue
        
        return ""
    
    
    def _extrair_com_trafilatura(self, html, url):
        """
        Extrai conteúdo usando trafilatura.
        Biblioteca especializada em extração de texto de artigos.
        
        Args:
            html (str): HTML da página
            url (str): URL original
            
        Returns:
            dict: Resultado da extração
        """
        try:
            # Extrair metadata
            metadata = trafilatura.extract_metadata(html, url=url)
            
            # Extrair conteúdo
            content = trafilatura.extract(
                html,
                include_comments=False,
                include_formatting=False,
                favor_recall=True,
                url=url
            )
            
            titulo = metadata.title if metadata and hasattr(metadata, 'title') else ""
            texto = content or ""
            
            if not texto or len(texto.split()) < Config.MIN_CONTENT_LENGTH:
                raise Exception("Texto insuficiente")
            
            return {
                'url': url,
                'titulo': (titulo or "").strip(),
                'texto': texto.strip(),
                'data_publicacao': None,
                'autor': None,
                'metodo_extracao': 'trafilatura',
                'sucesso': True,
                'erro': None
            }
        
        except Exception as e:
            return {
                'url': url,
                'titulo': None,
                'texto': None,
                'data_publicacao': None,
                'autor': None,
                'metodo_extracao': 'trafilatura',
                'sucesso': False,
                'erro': f"Trafilatura falhou: {str(e)}"
            }
    
    
    def _extrair_amp(self, html, url):
        """
        Tenta encontrar e extrair versão AMP (Accelerated Mobile Pages).
        
        Args:
            html (str): HTML original
            url (str): URL original
            
        Returns:
            dict: Resultado da extração
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Procurar link AMP
            amp_link = soup.find('link', rel=lambda x: x and 'amphtml' in str(x).lower())
            
            if amp_link and amp_link.get('href'):
                amp_url = amp_link['href']
                
                # Garantir URL completa
                if amp_url.startswith('/'):
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    amp_url = f"{parsed.scheme}://{parsed.netloc}{amp_url}"
                
                # Buscar HTML da versão AMP
                amp_html = self._obter_html(amp_url)
                
                if amp_html and TRAFILATURA_AVAILABLE:
                    # Extrair com trafilatura
                    return self._extrair_com_trafilatura(amp_html, amp_url)
            
            raise Exception("Link AMP não encontrado")
        
        except Exception as e:
            return {
                'url': url,
                'titulo': None,
                'texto': None,
                'data_publicacao': None,
                'autor': None,
                'metodo_extracao': 'amp',
                'sucesso': False,
                'erro': f"AMP falhou: {str(e)}"
            }
    
    
    def _extrair_com_readability(self, html):
        """
        Extrai conteúdo usando readability-lxml.
        Biblioteca focada em extrair conteúdo principal.
        
        Args:
            html (str): HTML da página
            
        Returns:
            dict: Resultado da extração
        """
        try:
            doc = Document(html)
            
            # Extrair título
            titulo = (doc.short_title() or "").strip()
            
            # Extrair conteúdo principal
            summary_html = doc.summary(html_partial=True)
            soup = BeautifulSoup(summary_html, 'lxml')
            texto = soup.get_text("\n").strip()
            
            if not texto or len(texto.split()) < Config.MIN_CONTENT_LENGTH:
                raise Exception("Texto insuficiente")
            
            return {
                'url': '',
                'titulo': titulo,
                'texto': texto,
                'data_publicacao': None,
                'autor': None,
                'metodo_extracao': 'readability',
                'sucesso': True,
                'erro': None
            }
        
        except Exception as e:
            return {
                'url': '',
                'titulo': None,
                'texto': None,
                'data_publicacao': None,
                'autor': None,
                'metodo_extracao': 'readability',
                'sucesso': False,
                'erro': f"Readability falhou: {str(e)}"
            }
    
    
    def _extrair_globo(self, html):
        """
        Extrator específico para sites da Globo (G1, etc).
        
        Args:
            html (str): HTML da página
            
        Returns:
            dict: Resultado da extração
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Buscar título
            titulo = ""
            h1 = soup.find('h1')
            if h1:
                titulo = h1.get_text(" ", strip=True)
            
            # Buscar corpo do artigo
            body = None
            
            # Tentar schema.org articleBody
            body = soup.find(attrs={"itemprop": "articleBody"})
            
            # Tentar tag article
            if not body:
                body = soup.find('article')
            
            # Tentar divs conhecidas do G1
            if not body:
                body = soup.select_one("div[class*='content-text'], div[class*='mc-body']")
            
            if not body:
                raise Exception("Corpo do artigo não encontrado")
            
            # Extrair parágrafos
            paragrafos = []
            for tag in body.find_all(['p', 'li']):
                texto = tag.get_text(" ", strip=True)
                if texto and len(texto) > 20:
                    paragrafos.append(texto)
            
            texto_completo = "\n\n".join(paragrafos).strip()
            
            if not texto_completo or len(texto_completo.split()) < Config.MIN_CONTENT_LENGTH:
                raise Exception("Texto insuficiente")
            
            return {
                'url': '',
                'titulo': titulo,
                'texto': texto_completo,
                'data_publicacao': None,
                'autor': None,
                'metodo_extracao': 'globo_specific',
                'sucesso': True,
                'erro': None
            }
        
        except Exception as e:
            return {
                'url': '',
                'titulo': None,
                'texto': None,
                'data_publicacao': None,
                'autor': None,
                'metodo_extracao': 'globo_specific',
                'sucesso': False,
                'erro': f"Globo extractor falhou: {str(e)}"
            }
        """
        Valida se a URL está no formato correto.
        
        Args:
            url (str): URL a validar
            
        Returns:
            bool: True se válida, False caso contrário
        """
        if not url:
            return False
        
        # Usar biblioteca validators
        if not validators.url(url):
            return False
        
        # Verificar se começa com http:// ou https://
        if not url.startswith(('http://', 'https://')):
            return False
        
        return True
    
    
    def _extrair_com_newspaper(self, url):
        """
        Extrai conteúdo usando a biblioteca newspaper3k.
        
        newspaper3k é especializada em artigos de notícias e consegue
        identificar automaticamente título, texto, data, autor, etc.
        
        Args:
            url (str): URL da notícia
            
        Returns:
            dict: Resultado da extração
        """
        
        for tentativa in range(1, self.retry_attempts + 1):
            try:
                # Criar objeto Article
                article = Article(url, language='pt')
                
                # Configurar timeout
                article.config.request_timeout = self.timeout
                
                # Adicionar headers customizados
                article.config.headers = self.headers
                
                # Baixar conteúdo
                article.download()
                
                # Parsear HTML
                article.parse()
                
                # Extrair informações
                titulo = article.title
                texto = article.text
                data_publicacao = article.publish_date
                autores = article.authors
                
                # Validar se conseguiu extrair conteúdo mínimo
                if not titulo or not texto:
                    raise Exception("Título ou texto não encontrados")
                
                if len(texto.strip()) < Config.MIN_CONTENT_LENGTH:
                    raise Exception(f"Texto muito curto: {len(texto)} caracteres")
                
                # Formatar data (se disponível)
                data_formatada = None
                if data_publicacao:
                    try:
                        data_formatada = data_publicacao.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        data_formatada = str(data_publicacao)
                
                # Formatar autores (pegar primeiro autor se houver vários)
                autor = autores[0] if autores else None
                
                # Retornar sucesso
                return {
                    'url': url,
                    'titulo': titulo.strip(),
                    'texto': texto.strip(),
                    'data_publicacao': data_formatada,
                    'autor': autor,
                    'metodo_extracao': 'newspaper3k',
                    'sucesso': True,
                    'erro': None
                }
            
            except Exception as e:
                erro_msg = str(e)
                
                # Se não é a última tentativa, aguardar e tentar novamente
                if tentativa < self.retry_attempts:
                    print(f"⚠️  Tentativa {tentativa} falhou: {erro_msg}. Tentando novamente em {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                    continue
                
                # Última tentativa falhou
                return {
                    'url': url,
                    'titulo': None,
                    'texto': None,
                    'data_publicacao': None,
                    'autor': None,
                    'metodo_extracao': 'newspaper3k',
                    'sucesso': False,
                    'erro': f"Newspaper3k falhou: {erro_msg}"
                }
    
    
    def _extrair_com_beautifulsoup(self, url):
        """
        Extrai conteúdo usando BeautifulSoup (fallback).
        
        Método mais genérico, tenta identificar título e texto através
        de tags HTML comuns em sites de notícias.
        
        Args:
            url (str): URL da notícia
            
        Returns:
            dict: Resultado da extração
        """
        
        for tentativa in range(1, self.retry_attempts + 1):
            try:
                # Rotacionar User-Agent para evitar bloqueios
                headers = self.headers.copy()
                headers['User-Agent'] = random.choice(Config.USER_AGENTS)
                
                # Fazer requisição HTTP
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                # Verificar status code
                response.raise_for_status()  # Lança exceção se 4xx ou 5xx
                
                # Parsear HTML
                soup = BeautifulSoup(response.content, 'lxml')
                
                # ============================================================
                # EXTRAIR TÍTULO
                # ============================================================
                
                titulo = None
                
                # Tentar meta tags primeiro (mais confiável)
                meta_title = soup.find('meta', property='og:title')
                if meta_title and meta_title.get('content'):
                    titulo = meta_title.get('content')
                
                # Se não encontrou, tentar tag <title>
                if not titulo:
                    title_tag = soup.find('title')
                    if title_tag:
                        titulo = title_tag.get_text()
                
                # Se ainda não encontrou, tentar <h1>
                if not titulo:
                    h1_tag = soup.find('h1')
                    if h1_tag:
                        titulo = h1_tag.get_text()
                
                
                # ============================================================
                # EXTRAIR TEXTO
                # ============================================================
                
                texto = None
                
                # Estratégia 1: Procurar por tags article
                article_tag = soup.find('article')
                if article_tag:
                    paragrafos = article_tag.find_all('p')
                    texto = '\n\n'.join([p.get_text().strip() for p in paragrafos if p.get_text().strip()])
                
                # Estratégia 2: Procurar por divs comuns de conteúdo
                if not texto or len(texto) < Config.MIN_CONTENT_LENGTH:
                    content_divs = soup.find_all('div', class_=['content', 'article-content', 'post-content', 'entry-content'])
                    for div in content_divs:
                        paragrafos = div.find_all('p')
                        texto_temp = '\n\n'.join([p.get_text().strip() for p in paragrafos if p.get_text().strip()])
                        if len(texto_temp) > len(texto or ''):
                            texto = texto_temp
                
                # Estratégia 3: Pegar todos os <p> da página (menos confiável)
                if not texto or len(texto) < Config.MIN_CONTENT_LENGTH:
                    paragrafos = soup.find_all('p')
                    texto = '\n\n'.join([p.get_text().strip() for p in paragrafos if len(p.get_text().strip()) > 50])
                
                
                # ============================================================
                # VALIDAR RESULTADO
                # ============================================================
                
                if not titulo or not texto:
                    raise Exception("Título ou texto não encontrados no HTML")
                
                if len(texto.strip()) < Config.MIN_CONTENT_LENGTH:
                    raise Exception(f"Texto muito curto: {len(texto)} caracteres")
                
                
                # ============================================================
                # TENTAR EXTRAIR DATA (opcional)
                # ============================================================
                
                data_publicacao = None
                
                # Tentar meta tag de data
                meta_date = soup.find('meta', property='article:published_time')
                if not meta_date:
                    meta_date = soup.find('meta', attrs={'name': 'publish-date'})
                
                if meta_date and meta_date.get('content'):
                    data_publicacao = meta_date.get('content')
                
                
                # ============================================================
                # RETORNAR SUCESSO
                # ============================================================
                
                return {
                    'url': url,
                    'titulo': titulo.strip(),
                    'texto': texto.strip()[:Config.MAX_CONTENT_LENGTH],  # Limitar tamanho
                    'data_publicacao': data_publicacao,
                    'autor': None,  # BeautifulSoup genérico não extrai autor confiavel
                    'metodo_extracao': 'beautifulsoup',
                    'sucesso': True,
                    'erro': None
                }
            
            except requests.exceptions.Timeout:
                erro_msg = "Timeout ao acessar URL"
                if tentativa < self.retry_attempts:
                    print(f"⚠️  Timeout na tentativa {tentativa}. Tentando novamente...")
                    time.sleep(self.retry_delay)
                    continue
            
            except requests.exceptions.RequestException as e:
                erro_msg = f"Erro na requisição: {str(e)}"
                if tentativa < self.retry_attempts:
                    print(f"⚠️  Erro na tentativa {tentativa}: {erro_msg}. Tentando novamente...")
                    time.sleep(self.retry_delay)
                    continue
            
            except Exception as e:
                erro_msg = str(e)
                if tentativa < self.retry_attempts:
                    print(f"⚠️  Tentativa {tentativa} falhou: {erro_msg}. Tentando novamente...")
                    time.sleep(self.retry_delay)
                    continue
        
        # Todas as tentativas falharam
        return {
            'url': url,
            'titulo': None,
            'texto': None,
            'data_publicacao': None,
            'autor': None,
            'metodo_extracao': 'beautifulsoup',
            'sucesso': False,
            'erro': f"BeautifulSoup falhou após {self.retry_attempts} tentativas: {erro_msg}"
        }


# ============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# ============================================================================

def extrair_conteudo(url):
    """
    Função simplificada para extrair conteúdo de uma URL.
    
    Esta é a função que será chamada por outros módulos.
    
    Args:
        url (str): URL da notícia
        
    Returns:
        dict: Resultado da extração
        
    Exemplo:
        >>> resultado = extrair_conteudo('https://g1.globo.com/exemplo')
        >>> if resultado['sucesso']:
        >>>     print(resultado['titulo'])
        >>>     print(resultado['texto'])
    """
    extractor = ContentExtractor()
    return extractor.extract(url)


# ============================================================================
# TESTE DO MÓDULO (executar diretamente)
# ============================================================================

if __name__ == "__main__":
    """
    Testes do módulo extractor.
    Execute: python modules/extractor.py
    """
    
    print("=" * 70)
    print("🧪 TESTANDO MÓDULO EXTRACTOR")
    print("=" * 70)
    print()
    
    # URLs de teste (notícias reais)
    urls_teste = [
        "https://g1.globo.com/politica/noticia/2024/01/15/governo-anuncia-novas-medidas-economicas.ghtml",
        "https://www.bbc.com/portuguese/articles/c3g3g3g3g3g",  # URL inválida para testar erro
        "https://exemplo-invalido.com"  # URL inválida
    ]
    
    for i, url in enumerate(urls_teste, 1):
        print(f"Teste {i}: {url}")
        print("-" * 70)
        
        resultado = extrair_conteudo(url)
        
        if resultado['sucesso']:
            print(f"✅ SUCESSO ({resultado['metodo_extracao']})")
            print(f"Título: {resultado['titulo'][:80]}...")
            print(f"Texto: {resultado['texto'][:150]}...")
            print(f"Data: {resultado['data_publicacao']}")
            print(f"Autor: {resultado['autor']}")
        else:
            print(f"❌ FALHOU")
            print(f"Erro: {resultado['erro']}")
        
        print()