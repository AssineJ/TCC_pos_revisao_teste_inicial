import os
from typing import Any, Dict, Optional

import requests
import streamlit as st

# Configurar a URL da API (substitua pela sua URL em produção, se necessário)
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Detector de Fake News - Brasil", page_icon="📰")

if "url_result" not in st.session_state:
    st.session_state["url_result"] = None

if "manual_result" not in st.session_state:
    st.session_state["manual_result"] = None


def _format_error_detail(detail: Any) -> str:
    if not detail:
        return ""

    if isinstance(detail, list):
        return "; ".join(_format_error_detail(item) for item in detail if item)

    if isinstance(detail, dict):
        msg = detail.get("msg")
        if msg:
            return str(msg)
        return "; ".join(f"{key}: {value}" for key, value in detail.items())

    return str(detail)


def _render_verdict_block(verdict: str, message: str) -> None:
    verdict = verdict.upper()

    if verdict == "VERDADEIRO":
        st.success(f"✅ **{verdict}** - {message}")
    elif verdict == "INDETERMINADO":
        st.warning(f"⚠️ **{verdict}** - {message}")
    else:
        st.error(f"❌ **{verdict}** - {message}")


def _render_common_feedback(probability: float) -> None:
    safe_probability = min(max(probability, 0.0), 1.0)
    st.progress(safe_probability)
    st.caption(f"Probabilidade de ser falsa: {safe_probability * 100:.2f}%")

    if safe_probability >= 0.5:
        st.info(
            """
            **Dicas de checagem:**
            - Busque confirmar o conteúdo em portais confiáveis (G1, UOL, Folha de S.Paulo).
            - Consulte agências de fact-checking (Aos Fatos, Lupa, Estadão Verifica).
            - Tenha cuidado com títulos sensacionalistas e URLs pouco confiáveis.
            """
        )


def display_result_block(result: Dict[str, Any], *, is_url_result: bool) -> None:
    verdict = result.get("verdict", "DESCONHECIDO")
    probability = float(result.get("probability", 0.0))
    message = result.get("message", "Verifique a notícia em outras fontes confiáveis.")

    _render_verdict_block(verdict, message)
    _render_common_feedback(probability)

    if is_url_result:
        extracted_title = result.get("extracted_title")
        if extracted_title:
            st.subheader(extracted_title)

        preview = result.get("content_preview")
        if preview:
            st.write(preview)

        article_url = result.get("url")
        if article_url:
            st.markdown(f"**Fonte analisada:** [{article_url}]({article_url})")


def set_result_state(key: str, value: Optional[Dict[str, Any]]) -> None:
    st.session_state[key] = value


st.title("📰 Detector de Fake News - Notícias Brasileiras")

st.write(
    """
    Informe a URL completa de uma matéria para que nossa IA colete o conteúdo automaticamente,
    analise o texto e informe a probabilidade de ser uma notícia falsa.
    Caso deseje validar manualmente um título e conteúdo, utilize a aba "Verificação manual".
    """
)

url_tab, manual_tab = st.tabs(["Verificar por URL", "Verificação manual"])

with url_tab:
    url_input = st.text_input("Cole a URL da notícia a ser verificada", key="url_input")

    if st.button("Verificar URL", type="primary", key="verify_url_button"):
        if not url_input:
            st.warning("Por favor, insira a URL completa da notícia.")
        else:
            with st.spinner("Analisando a notícia diretamente da fonte..."):
                try:
                    response = requests.post(
                        f"{API_URL}/check-news-url",
                        json={"url": url_input.strip()},
                        timeout=30,
                    )
                except Exception as exc:  # noqa: BLE001 - exibir erro diretamente ao usuário
                    set_result_state(
                        "url_result",
                        {
                            "type": "error",
                            "message": f"Erro ao conectar com a API: {exc}",
                        },
                    )
                else:
                    if response.status_code == 200:
                        set_result_state(
                            "url_result",
                            {
                                "type": "success",
                                "payload": response.json(),
                            },
                        )
                    else:
                        message = _format_error_detail(response.json().get("detail")) if response.headers.get("content-type", "").startswith("application/json") else response.text
                        set_result_state(
                            "url_result",
                            {
                                "type": "error",
                                "message": message or "Não foi possível verificar a URL informada.",
                            },
                        )

    url_result = st.session_state.get("url_result")
    if url_result:
        if url_result.get("type") == "error":
            st.error(url_result.get("message", "Falha ao analisar a notícia."))
        else:
            payload = url_result.get("payload", {})
            display_result_block(payload, is_url_result=True)

with manual_tab:
    title = st.text_input("Título da notícia", key="manual_title")
    content = st.text_area("Conteúdo completo", height=200, key="manual_content")

    if st.button("Verificar texto", key="verify_manual_button"):
        if title and content:
            with st.spinner("Analisando o texto informado..."):
                try:
                    response = requests.post(
                        f"{API_URL}/check-news",
                        json={"title": title, "content": content},
                        timeout=30,
                    )
                except Exception as exc:  # noqa: BLE001
                    set_result_state(
                        "manual_result",
                        {
                            "type": "error",
                            "message": f"Erro ao conectar com a API: {exc}",
                        },
                    )
                else:
                    if response.status_code == 200:
                        set_result_state(
                            "manual_result",
                            {
                                "type": "success",
                                "payload": response.json(),
                            },
                        )
                    else:
                        message = _format_error_detail(response.json().get("detail")) if response.headers.get("content-type", "").startswith("application/json") else response.text
                        set_result_state(
                            "manual_result",
                            {
                                "type": "error",
                                "message": message or "Não foi possível verificar o texto informado.",
                            },
                        )
        else:
            st.warning("Informe o título e o conteúdo da notícia para realizar a verificação manual.")

    manual_result = st.session_state.get("manual_result")
    if manual_result:
        if manual_result.get("type") == "error":
            st.error(manual_result.get("message", "Falha ao analisar a notícia."))
        else:
            payload = manual_result.get("payload", {})
            display_result_block(payload, is_url_result=False)

st.divider()

st.subheader("🗞️ Últimas notícias coletadas pela API")

if st.button("Atualizar lista", key="refresh_recent_news"):
    with st.spinner("Buscando notícias coletadas recentemente..."):
        try:
            response = requests.get(f"{API_URL}/recent-news?limit=6", timeout=30)
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Não foi possível carregar as notícias recentes: {exc}")
        else:
            news_items = response.json().get("news", [])

            if not news_items:
                st.info("Nenhuma notícia coletada até o momento.")
            else:
                for item in news_items:
                    title = item.get("title") or "Título não informado"
                    source_name = item.get("source_name") or "Fonte desconhecida"
                    publish_date = item.get("publish_date") or "Data não disponível"

                    with st.expander(f"{title} — {source_name}"):
                        st.write(f"**Fonte:** {source_name}")
                        st.write(f"**Data de publicação:** {publish_date}")
                        source_url = item.get("source_url")
                        if source_url and source_url.startswith("http"):
                            st.markdown(f"[Acessar notícia original]({source_url})")

st.divider()

st.markdown(
    """
    **Sobre este projeto**  \
    Esta ferramenta usa inteligência artificial para detectar possíveis fake news em notícias brasileiras.\
    Utilize os resultados como apoio à checagem, sempre confirmando a informação em fontes oficiais.
    """
)
