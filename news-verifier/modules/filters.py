"""
filters.py - Módulo de Filtros Inteligentes

Responsabilidade:
    Filtrar resultados de busca e scraping para melhorar qualidade:
    - Remover URLs problemáticas (404, paywall, etc)
    - Filtrar notícias antigas
    - Verificar correlação de título
    - Blacklist de domínios problemáticos

Autor: Projeto Acadêmico
Data: 2025
"""

from datetime import datetime, timedelta
from urllib.parse import urlparse
import re
from config import Config


class ContentFilter:
    """
    Filtros para melhorar qualidade dos resultados.
    """
    
    def __init__(self):
        """Inicializa filtros"""
        
        # Domínios/paths conhecidos com problemas
        self.problematic_patterns = [
            'paywall',
            'assinante',
            'premium',
            'exclusivo',
            '/tv/',  # Vídeos geralmente não têm texto
            '/audio/',
            '/podcast/',
            '/galeria/',  # Galerias de fotos
            '/tempo-real/',  # Live blogs (estrutura diferente)
        ]
        
        # Palavras que indicam paywall no título
        self.paywall_indicators = [
            'exclusivo para assinantes',
            'assine',
            'conteúdo exclusivo',
            'apenas assinantes'
        ]
        
        # Domínios problemáticos conhecidos (podem ser atualizados)
        self.problematic_domains = [
            # Adicionar domínios que causam muito problema
        ]
    
    
    def filtrar_resultados_busca(self, resultados_busca):
        """
        Filtra resultados de busca antes do scraping.
        Remove URLs problemáticas conhecidas.
        
        Args:
            resultados_busca (dict): Resultado do searcher
            
        Returns:
            dict: Resultados filtrados
        """
        print("\n🔍 Aplicando filtros nos resultados de busca...")
        
        resultados_filtrados = {}
        total_original = 0
        total_filtrado = 0
        
        for fonte_nome, fonte_resultados in resultados_busca.items():
            if fonte_nome == 'metadata':
                continue
            
            if not fonte_resultados:
                resultados_filtrados[fonte_nome] = []
                continue
            
            total_original += len(fonte_resultados)
            
            # Filtrar cada resultado
            filtrados = []
            for resultado in fonte_resultados:
                if self._validar_resultado_busca(resultado, fonte_nome):
                    filtrados.append(resultado)
                else:
                    print(f"   ⚠️  Filtrado: {resultado['url'][:60]}...")
            
            resultados_filtrados[fonte_nome] = filtrados
            total_filtrado += len(filtrados)
        
        # Atualizar metadata
        metadata_original = resultados_busca.get('metadata', {})
        resultados_filtrados['metadata'] = {
            **metadata_original,
            'total_resultados': total_filtrado,
            'total_filtrados': total_original - total_filtrado
        }
        
        print(f"   ✅ Mantidos: {total_filtrado}/{total_original}")
        print(f"   ⚠️  Filtrados: {total_original - total_filtrado}")
        
        return resultados_filtrados
    
    
    def filtrar_conteudos_scraping(self, conteudos_scraping, texto_original):
        """
        Filtra conteúdos após scraping.
        Remove conteúdos de baixa qualidade ou não correlatos.
        
        Args:
            conteudos_scraping (dict): Resultado do scraper
            texto_original (str): Texto original para comparar
            
        Returns:
            dict: Conteúdos filtrados
        """
        print("\n🔍 Aplicando filtros nos conteúdos extraídos...")
        
        conteudos_filtrados = {}
        total_original = 0
        total_filtrado = 0
        
        # Extrair termos principais do texto original
        termos_principais = self._extrair_termos_principais(texto_original)
        
        for fonte_nome, fonte_conteudos in conteudos_scraping.items():
            if fonte_nome == 'metadata':
                continue
            
            if not fonte_conteudos:
                conteudos_filtrados[fonte_nome] = []
                continue
            
            total_original += len(fonte_conteudos)
            
            # Filtrar cada conteúdo
            filtrados = []
            for conteudo in fonte_conteudos:
                motivo_filtro = self._validar_conteudo_scraping(conteudo, termos_principais)
                
                if not motivo_filtro:
                    filtrados.append(conteudo)
                else:
                    print(f"   ⚠️  {fonte_nome}: {motivo_filtro}")
                    print(f"      {conteudo.get('titulo', conteudo.get('url', ''))[:50]}...")
            
            conteudos_filtrados[fonte_nome] = filtrados
            total_filtrado += len(filtrados)
        
        # Atualizar metadata
        metadata_original = conteudos_scraping.get('metadata', {})
        conteudos_filtrados['metadata'] = {
            **metadata_original,
            'total_sucesso': total_filtrado,
            'total_filtrados': total_original - total_filtrado
        }
        
        print(f"   ✅ Mantidos: {total_filtrado}/{total_original}")
        print(f"   ⚠️  Filtrados: {total_original - total_filtrado}")
        
        return conteudos_filtrados
    
    
    def _validar_resultado_busca(self, resultado, fonte_nome):
        """
        Valida se um resultado de busca deve ser mantido.
        
        Args:
            resultado (dict): {'title': ..., 'url': ..., 'snippet': ...}
            fonte_nome (str): Nome da fonte
            
        Returns:
            bool: True se válido, False se deve filtrar
        """
        url = resultado.get('url', '')
        titulo = resultado.get('title', '').lower()
        snippet = resultado.get('snippet', '').lower()
        
        # Filtro 1: URL vazia
        if not url:
            return False
        
        # Filtro 2: Padrões problemáticos na URL
        url_lower = url.lower()
        for pattern in self.problematic_patterns:
            if pattern in url_lower:
                return False
        
        # Filtro 3: Domínio problemático
        domain = urlparse(url).netloc
        if domain in self.problematic_domains:
            return False
        
        # Filtro 4: Indicadores de paywall no título
        for indicator in self.paywall_indicators:
            if indicator in titulo:
                return False
        
        # Filtro 5: Título muito curto (provavelmente não é notícia)
        if len(titulo) < 20:
            return False
        
        # Filtro 6: URL de homepage (não é notícia específica)
        path = urlparse(url).path
        if path in ['/', '']:
            return False
        
        # Filtro especial: Folha (conhecida por ter paywall)
        if fonte_nome == 'Folha de S.Paulo':
            # Aceitar apenas URLs que não tenham indicadores de paywall
            if any(ind in url_lower for ind in ['assinante', 'premium']):
                return False
        
        return True
    
    
    def _validar_conteudo_scraping(self, conteudo, termos_principais):
        """
        Valida se um conteúdo extraído deve ser mantido.
        
        Args:
            conteudo (dict): Conteúdo extraído
            termos_principais (set): Termos do texto original
            
        Returns:
            str ou None: Motivo da filtragem ou None se válido
        """
        # Se extração falhou, manter (erro já registrado)
        if not conteudo.get('sucesso'):
            # Verificar se é erro 404
            erro = conteudo.get('erro', '').lower()
            if '404' in erro or 'not found' in erro:
                return "Erro 404 (URL não existe)"
            return None  # Outros erros, manter para análise
        
        titulo = conteudo.get('titulo', '').lower()
        texto = conteudo.get('texto', '').lower()
        
        # Filtro 1: Texto muito curto
        if len(texto) < Config.MIN_CONTENT_LENGTH:
            return f"Texto muito curto ({len(texto)} chars)"
        
        # Filtro 2: Título muito curto ou genérico
        if len(titulo) < 20:
            return "Título muito curto"
        
        # Filtro 3: Verificar se há correlação mínima com texto original
        # Pelo menos 20% dos termos principais devem aparecer
        if termos_principais:
            termos_encontrados = sum(1 for termo in termos_principais if termo in texto or termo in titulo)
            correlacao = termos_encontrados / len(termos_principais)
            
            if correlacao < 0.2:
                return f"Baixa correlação ({correlacao*100:.0f}% dos termos)"
        
        # Filtro 4: Detectar paywall no conteúdo
        paywall_texts = [
            'este conteúdo é exclusivo',
            'assine para continuar',
            'conteúdo restrito',
            'faça login para ler',
            'exclusivo para assinantes'
        ]
        
        for paywall_text in paywall_texts:
            if paywall_text in texto[:500]:  # Verificar início do texto
                return "Conteúdo com paywall"
        
        return None  # Válido
    
    
    def _extrair_termos_principais(self, texto):
        """
        Extrai termos principais do texto para comparação.
        
        Args:
            texto (str): Texto original
            
        Returns:
            set: Conjunto de termos principais
        """
        # Remover pontuação e converter para minúsculas
        texto_limpo = re.sub(r'[^\w\s]', ' ', texto.lower())
        
        # Pegar palavras com mais de 4 caracteres (filtrar artigos, preposições)
        palavras = [p for p in texto_limpo.split() if len(p) > 4]
        
        # Pegar as 15 palavras mais relevantes (únicas)
        termos = set(palavras[:15])
        
        return termos


# ============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# ============================================================================

def filtrar_busca(resultados_busca):
    """
    Filtra resultados de busca.
    
    Args:
        resultados_busca (dict): Resultado do searcher
        
    Returns:
        dict: Resultados filtrados
    """
    filtro = ContentFilter()
    return filtro.filtrar_resultados_busca(resultados_busca)


def filtrar_scraping(conteudos_scraping, texto_original):
    """
    Filtra conteúdos extraídos.
    
    Args:
        conteudos_scraping (dict): Resultado do scraper
        texto_original (str): Texto original
        
    Returns:
        dict: Conteúdos filtrados
    """
    filtro = ContentFilter()
    return filtro.filtrar_conteudos_scraping(conteudos_scraping, texto_original)


# ============================================================================
# TESTE DO MÓDULO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TESTANDO MÓDULO FILTERS")
    print("=" * 70)
    print()
    
    # Teste 1: Filtrar URLs problemáticas
    print("Teste 1: Filtrar URLs problemáticas")
    print("-" * 70)
    
    resultados_mock = {
        'G1': [
            {'title': 'Notícia válida sobre economia', 'url': 'https://g1.globo.com/economia/noticia/2025/01/valida.ghtml', 'snippet': '...'},
            {'title': 'Vídeo', 'url': 'https://g1.globo.com/tv/video.html', 'snippet': '...'},  # FILTRAR
            {'title': 'Home', 'url': 'https://g1.globo.com/', 'snippet': '...'},  # FILTRAR
        ],
        'Folha': [
            {'title': 'Exclusivo para assinantes', 'url': 'https://folha.uol.com.br/paywall/noticia.shtml', 'snippet': '...'},  # FILTRAR
            {'title': 'Notícia pública válida', 'url': 'https://folha.uol.com.br/poder/noticia.shtml', 'snippet': '...'},
        ],
        'metadata': {'total_resultados': 5}
    }
    
    filtro = ContentFilter()
    filtrados = filtro.filtrar_resultados_busca(resultados_mock)
    
    print(f"\nOriginal: {resultados_mock['metadata']['total_resultados']} resultados")
    print(f"Filtrado: {filtrados['metadata']['total_resultados']} resultados")
    print(f"Removidos: {filtrados['metadata']['total_filtrados']}")
    
    print()
    print("=" * 70)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 70)