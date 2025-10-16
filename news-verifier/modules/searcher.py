# modules/searcher.py
from __future__ import annotations

import os
import re
import time
import json
import hashlib
import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

from config import Config

# -----------------------------
# Opicionais (nem sempre instalados)
# -----------------------------
try:
    from serpapi import GoogleSearch  # google-search-results
    SERPAPI_AVAILABLE = True
except Exception:
    SERPAPI_AVAILABLE = False

try:
    # googlesearch-python
    from googlesearch import search as google_search
    GSEARCH_AVAILABLE = True
except Exception:
    GSEARCH_AVAILABLE = False


# ============================================================
# Utils de cache simples em arquivo (por query+site)
# ============================================================

def _cache_dir() -> str:
    d = os.path.join(".cache", "search")
    os.makedirs(d, exist_ok=True)
    return d

def _cache_key(query: str, site: str) -> str:
    key_str = f"{query}||{site}".lower().strip()
    return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

def _cache_path(query: str, site: str) -> str:
    return os.path.join(_cache_dir(), f"{_cache_key(query, site)}.json")

def cache_get(query: str, site: str) -> Optional[List[Dict[str, Any]]]:
    if not Config.ENABLE_CACHE:
        return None
    path = _cache_path(query, site)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        # expiração
        ttl = getattr(Config, "CACHE_EXPIRATION", 3600)
        if time.time() - payload.get("_ts", 0) > ttl:
            return None
        return payload.get("results", None)
    except Exception:
        return None

def cache_set(query: str, site: str, results: List[Dict[str, Any]]) -> None:
    if not Config.ENABLE_CACHE:
        return
    path = _cache_path(query, site)
    payload = {"_ts": time.time(), "results": results}
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ============================================================
# Normalização de resultados
# ============================================================

def _norm_result(title: str, url: str, snippet: str = "") -> Dict[str, Any]:
    return {
        "title": title.strip() if title else "",
        "url": url.strip() if url else "",
        "snippet": snippet.strip() if snippet else ""
    }

def _clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s


# ============================================================
# Mecanismo principal de busca
# ============================================================

@dataclass
class SearchEngine:
    headers: Dict[str, str] = None
    max_per_source: int = Config.MAX_RESULTS_PER_SOURCE
    delay_between: float = getattr(Config, "SEARCH_DELAY", 1.0)

    def __post_init__(self):
        if self.headers is None:
            self.headers = dict(Config.DEFAULT_HEADERS)

    # --------------- API ---------------

    def buscar(self, query: str, dominio: str) -> List[Dict[str, Any]]:
        """Busca resultados para um domínio específico."""
        query = _clean_text(query)
        if not query or not dominio:
            return []

        # cache
        cached = cache_get(query, dominio)
        if cached is not None:
            return cached[: self.max_per_source]

        # ordem de prioridade
        methods = getattr(Config, "SEARCH_METHODS_PRIORITY", ["serpapi", "googlesearch", "direct"])
        mode = getattr(Config, "SEARCH_MODE", "mock").lower()

        results: List[Dict[str, Any]] = []

        if mode == "mock":
            results = self._mock_results(dominio, query)
        else:
            for m in methods:
                try:
                    if m == "serpapi":
                        res = self._search_serpapi(query, dominio)
                    elif m == "googlesearch":
                        res = self._search_googlesearch(query, dominio)
                    else:
                        res = self._search_direct(query, dominio)
                    res = [r for r in res if r.get("url")]
                    for r in res:
                        if len(results) >= self.max_per_source:
                            break
                        # evitar duplicatas
                        if not any(r["url"] == x["url"] for x in results):
                            results.append(r)
                    if results:
                        break  # satisfação: achamos algo nesta camada
                except Exception:
                    # tenta próxima estratégia
                    continue

        # salvar no cache e devolver
        cache_set(query, dominio, results)
        # respeitar delay entre sites (para evitar rate limit)
        time.sleep(self.delay_between)
        return results[: self.max_per_source]

    # --------------- providers ---------------

    def _search_serpapi(self, query: str, dominio: str) -> List[Dict[str, Any]]:
        key = getattr(Config, "SERPAPI_KEY", None)
        if not SERPAPI_AVAILABLE or not key:
            return []
        params = {
            "engine": "google",
            "q": f"site:{dominio} " + query,
            "hl": "pt-BR",
            "num": max(5, self.max_per_source),
            "api_key": key
        }
        search = GoogleSearch(params)
        data = search.get_dict()
        out = []
        for item in data.get("organic_results", [])[: max(5, self.max_per_source)]:
            title = item.get("title", "")
            link = item.get("link", "")
            snippet = item.get("snippet", "")
            if link and dominio in link:
                out.append(_norm_result(title, link, snippet))
        return out

    def _search_googlesearch(self, query: str, dominio: str) -> List[Dict[str, Any]]:
        if not GSEARCH_AVAILABLE:
            return []
        # googlesearch-python já implementa paginação/UA
        q = f"site:{dominio} {query}"
        out = []
        try:
            for url in google_search(q, lang="pt", num=10, stop=10, pause=1.5):
                if dominio not in url:
                    continue
                title, snippet = self._fetch_title_snippet(url)
                out.append(_norm_result(title or url, url, snippet))
                if len(out) >= max(5, self.max_per_source):
                    break
        except Exception:
            pass
        return out

    def _search_direct(self, query: str, dominio: str) -> List[Dict[str, Any]]:
        """
        Tentativa simples: se a fonte tem 'url_busca' configurado, usa.
        Caso contrário, tenta homepage + filtro por query na âncora.
        """
        url_busca = None
        for f in Config.TRUSTED_SOURCES:
            if f.get("dominio") == dominio:
                url_busca = f.get("url_busca")
                break

        out = []
        session = requests.Session()
        session.headers.update(self.headers)

        try:
            if url_busca:
                resp = session.get(url_busca + requests.utils.quote(query), timeout=Config.REQUEST_TIMEOUT)
                if resp.ok:
                    out.extend(self._parse_links_from_html(resp.text, dominio))
            else:
                # fallback: homepage
                resp = session.get(f"https://{dominio}", timeout=Config.REQUEST_TIMEOUT)
                if resp.ok:
                    out.extend(self._parse_links_from_html(resp.text, dominio))

            # enriquecer com título/snippet
            final = []
            for r in out:
                title, snippet = self._fetch_title_snippet(r["url"], session=session)
                final.append(_norm_result(title or r["title"], r["url"], snippet))
                if len(final) >= max(5, self.max_per_source):
                    break
            return final
        except Exception:
            return []

    # --------------- helpers ---------------

    def _fetch_title_snippet(self, url: str, session: Optional[requests.Session] = None) -> (str, str):
        sess = session or requests.Session()
        sess.headers.update(self.headers)
        try:
            r = sess.get(url, timeout=Config.REQUEST_TIMEOUT, allow_redirects=True)
            if not r.ok:
                return "", ""
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("title").get_text(strip=True) if soup.find("title") else url
            ogdesc = soup.find("meta", attrs={"property": "og:description"})
            desc = ogdesc["content"] if ogdesc and ogdesc.get("content") else ""
            if not desc:
                mdesc = soup.find("meta", attrs={"name": "description"})
                desc = mdesc["content"] if mdesc and mdesc.get("content") else ""
            return _clean_text(title), _clean_text(desc)
        except Exception:
            return "", ""

    def _parse_links_from_html(self, html: str, dominio: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        out = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href.startswith("http"):
                continue
            if dominio not in href:
                continue
            title = a.get_text(" ", strip=True)[:120]
            out.append(_norm_result(title or href, href, ""))
            if len(out) >= 20:
                break
        return out

    def _mock_results(self, dominio: str, query: str) -> List[Dict[str, Any]]:
        # Gera alguns resultados simulados úteis para testes offline
        base = f"https://{dominio}"
        seeds = [
            ("Matéria relacionada: " + query[:50], f"{base}/noticia-simulada-1", "Resumo simulado 1"),
            ("Análise sobre " + query[:40], f"{base}/noticia-simulada-2", "Resumo simulado 2"),
            ("Entrevista: " + query[:40], f"{base}/noticia-simulada-3", "Resumo simulado 3"),
        ]
        random.shuffle(seeds)
        return [_norm_result(t, u, s) for (t, u, s) in seeds[: self.max_per_source]]


# ============================================================
# Funções de alto nível usadas pelo app
# ============================================================

def buscar_noticias(query_busca: str) -> Dict[str, Any]:
    """
    Realiza busca SEQUENCIAL nas fontes confiáveis e devolve
    um dicionário por fonte + metadata consolidada.
    """
    engine = SearchEngine()
    resultados: Dict[str, Any] = {}
    total = 0
    fontes_ok = 0

    fontes = [f for f in Config.TRUSTED_SOURCES if f.get("ativo", True)]

    for fonte in fontes:
        dominio = fonte["dominio"]
        nome = fonte["nome"]
        res = engine.buscar(query_busca, dominio) or []
        resultados[nome] = res
        if res:
            fontes_ok += 1
            total += len(res)

    resultados["metadata"] = {
        "total_resultados": total,
        "fontes_com_sucesso": fontes_ok,
        "total_fontes": len(fontes),
        "query_original": query_busca,
        "modo_busca": getattr(Config, "SEARCH_MODE", "mock")
    }
    return resultados


# ============================================================
# VERSÃO PARALELA (adição solicitada)
# ============================================================

def _buscar_em_fonte(fonte: Dict[str, Any], query_busca: str) -> (str, List[Dict[str, Any]]):
    engine = SearchEngine()
    dominio = fonte.get("dominio")
    nome = fonte.get("nome", dominio)
    if not dominio:
        return nome, []
    res = engine.buscar(query_busca, dominio) or []
    return nome, res

def buscar_noticias_paralelo(query_busca: str) -> Dict[str, Any]:
    """
    Busca em TODAS as fontes simultaneamente, retornando no mesmo formato
    de buscar_noticias(), mas com 'modo_busca' indicando 'parallel/...'.
    """
    fontes = [f for f in Config.TRUSTED_SOURCES if f.get("ativo", True)]
    inicio = time.time()
    resultados: Dict[str, Any] = {}
    total = 0
    fontes_ok = 0

    max_workers = min(5, len(fontes) or 1)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_buscar_em_fonte, f, query_busca): f for f in fontes}
        for fut in as_completed(futures):
            nome, res = fut.result()
            resultados[nome] = res
            if res:
                fontes_ok += 1
                total += len(res)

    dur = time.time() - inicio
    resultados["metadata"] = {
        "total_resultados": total,
        "fontes_com_sucesso": fontes_ok,
        "total_fontes": len(fontes),
        "query_original": query_busca,
        "modo_busca": f"parallel/{getattr(Config, 'SEARCH_MODE', 'mock')}",
        "duracao_s": round(dur, 2)
    }
    return resultados


# ============================================================
# CLI rápido para teste manual
# ============================================================

if __name__ == "__main__":
    q = "Lula ONU FAO Roma"
    print("🔎 Teste de buscar_noticias()")
    out = buscar_noticias(q)
    print(json.dumps(out["metadata"], ensure_ascii=False, indent=2))
    for fonte, itens in out.items():
        if fonte == "metadata":
            continue
        print(f"\n== {fonte} ==")
        for it in itens:
            print("-", it["title"], "|", it["url"])

    print("\n🔎 Teste de buscar_noticias_paralelo()")
    outp = buscar_noticias_paralelo(q)
    print(json.dumps(outp["metadata"], ensure_ascii=False, indent=2))
