import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from newspaper import Article
from bs4 import BeautifulSoup
import validators
from datetime import datetime
from config import Config
import time
import random


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
        
        Args:
            url (str): URL da notícia
            
        Returns:
            dict: Dicionário com conteúdo extraído ou None se falhar
            {
                'url': str,
                'titulo': str,
                'texto': str,
                'data_publicacao': str ou None,
                'autor': str ou None,
                'metodo_extracao': 'newspaper' ou 'beautifulsoup',
                'sucesso': bool,
                'erro': str ou None
            }
            
        Raises:
            Exception: Captura e retorna erro no dicionário, não lança exceção
        """
        
        # ====================================================================
        # ETAPA 1: VALIDAR URL
        # ====================================================================
        
        if not self._validar_url(url):
            return {
                'url': url,
                'titulo': None,
                'texto': None,
                'data_publicacao': None,
                'autor': None,
                'metodo_extracao': None,
                'sucesso': False,
                'erro': 'URL inválida'
            }
        
        
        # ====================================================================
        # ETAPA 2: TENTAR EXTRAIR COM NEWSPAPER3K (Método Principal)
        # ====================================================================
        
        resultado = self._extrair_com_newspaper(url)
        
        # Se teve sucesso, retornar
        if resultado['sucesso']:
            return resultado
        
        
        # ====================================================================
        # ETAPA 3: FALLBACK - TENTAR COM BEAUTIFULSOUP
        # ====================================================================
        
        print(f"⚠️  Newspaper3k falhou, tentando BeautifulSoup...")
        resultado = self._extrair_com_beautifulsoup(url)
        
        return resultado
    
    
    def _validar_url(self, url):
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
        "https://g1.globo.com/economia/censo/noticia/2025/10/09/mais-de-um-terco-dos-trabalhadores-do-pais-recebe-ate-um-salario-minimo-diz-ibge.ghtml",
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