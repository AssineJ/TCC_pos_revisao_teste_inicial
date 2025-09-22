const form = document.getElementById("check-form");
const urlInput = document.getElementById("news-url");
const feedback = document.getElementById("form-feedback");
const resultCard = document.getElementById("result-card");
const resultVerdict = document.getElementById("result-verdict");
const resultMessage = document.getElementById("result-message");
const probabilityWrapper = document.getElementById("probability-wrapper");
const probabilityValue = document.getElementById("probability-value");
const probabilityText = document.getElementById("probability-text");
const articleInfo = document.getElementById("article-info");
const articleTitle = document.getElementById("article-title");
const articleExcerpt = document.getElementById("article-excerpt");
const articleLink = document.getElementById("article-link");
const apiBaseInput = document.getElementById("api-base");
const submitButton = form.querySelector("button[type='submit']");

const STORAGE_KEY = "fake-news-detector:api-base";

const verdictStyles = {
  VERDADEIRO: {
    className: "truth",
    label: "Notícia provavelmente verdadeira",
  },
  INDETERMINADO: {
    className: "warning",
    label: "Resultado indeterminado",
  },
  "PROVAVELMENTE FALSO": {
    className: "danger",
    label: "Alerta de possível fake news",
  },
};

const safeStorage = {
  get(key) {
    try {
      return window.localStorage.getItem(key);
    } catch (error) {
      console.warn("LocalStorage indisponível", error);
      return null;
    }
  },
  set(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (error) {
      console.warn("Não foi possível salvar a configuração da API", error);
    }
  },
};

const inferApiBase = () => {
  if (typeof window !== "undefined") {
    if (window.API_BASE_URL) {
      return window.API_BASE_URL;
    }

    const origin = window.location.origin;
    if (origin && !origin.startsWith("file")) {
      return origin;
    }
  }

  return "http://localhost:8000";
};

const DEFAULT_API_BASE = inferApiBase();

const initialiseApiBaseField = () => {
  const saved = safeStorage.get(STORAGE_KEY);
  const value = saved || DEFAULT_API_BASE;
  if (apiBaseInput) {
    apiBaseInput.value = value;
  }
  return value;
};

const getApiBase = () => {
  const fieldValue = apiBaseInput?.value?.trim();
  if (fieldValue) {
    safeStorage.set(STORAGE_KEY, fieldValue);
    return fieldValue.replace(/\/$/, "");
  }
  const saved = safeStorage.get(STORAGE_KEY);
  if (saved) {
    return saved.replace(/\/$/, "");
  }
  return DEFAULT_API_BASE.replace(/\/$/, "");
};

const setLoadingState = (isLoading) => {
  submitButton.disabled = isLoading;
  if (isLoading) {
    feedback.classList.remove("error", "success");
    feedback.textContent = "Analisando a notícia...";
  }
};

const normaliseUrl = (input) => {
  if (!input) return null;

  try {
    return new URL(input).toString();
  } catch (error) {
    try {
      return new URL(`https://${input}`).toString();
    } catch (innerError) {
      return null;
    }
  }
};

const resetResultCard = () => {
  resultCard.classList.add("hidden");
  resultCard.classList.remove("truth", "warning", "danger", "visible");
  resultVerdict.textContent = "";
  resultMessage.textContent = "";
  probabilityWrapper.classList.add("hidden");
  probabilityValue.style.width = "0";
  probabilityText.textContent = "";
  articleInfo.classList.add("hidden");
  articleTitle.textContent = "";
  articleExcerpt.textContent = "";
  articleLink.textContent = "";
  articleLink.removeAttribute("href");
};

const renderResult = (payload) => {
  if (!payload) return;

  const verdictStyle = verdictStyles[payload.verdict] || {
    className: "warning",
    label: payload.verdict || "Resultado disponível",
  };

  resultCard.classList.remove("hidden", "truth", "warning", "danger");
  resultCard.classList.add("visible", verdictStyle.className);
  resultVerdict.textContent = verdictStyle.label;
  resultMessage.textContent = payload.message || "";

  if (typeof payload.probability === "number" && !Number.isNaN(payload.probability)) {
    const percentage = Math.max(0, Math.min(100, Math.round(payload.probability * 100)));
    probabilityWrapper.classList.remove("hidden");
    probabilityValue.style.width = `${percentage}%`;
    probabilityText.textContent = `${percentage}%`;
  } else {
    probabilityWrapper.classList.add("hidden");
  }

  const hasArticleDetails = Boolean(
    payload.resolved_title || payload.resolved_excerpt || payload.source_url,
  );

  if (hasArticleDetails) {
    articleInfo.classList.remove("hidden");
    articleTitle.textContent = payload.resolved_title || "Título não identificado";
    if (payload.resolved_excerpt) {
      articleExcerpt.textContent = payload.resolved_excerpt;
      articleExcerpt.classList.remove("hidden");
    } else {
      articleExcerpt.textContent = "";
      articleExcerpt.classList.add("hidden");
    }

    if (payload.source_url) {
      articleLink.href = payload.source_url;
      articleLink.textContent = "Abrir notícia original";
      articleLink.classList.remove("hidden");
    } else {
      articleLink.removeAttribute("href");
      articleLink.textContent = "";
      articleLink.classList.add("hidden");
    }
  } else {
    articleInfo.classList.add("hidden");
  }
};

initialiseApiBaseField();
resetResultCard();

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const inputValue = urlInput.value.trim();
  const normalised = normaliseUrl(inputValue);

  if (!normalised) {
    feedback.classList.add("error");
    feedback.classList.remove("success");
    feedback.textContent = "Insira um link válido de notícia.";
    resetResultCard();
    urlInput.focus();
    return;
  }

  setLoadingState(true);
  resetResultCard();

  const apiBase = getApiBase();
  const endpoint = `${apiBase}/check-news-url`;

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: normalised }),
    });

    const raw = await response.text();
    let result = null;

    if (raw) {
      try {
        result = JSON.parse(raw);
      } catch (parseError) {
        console.warn("Resposta inesperada da API", parseError);
      }
    }

    if (!response.ok) {
      const errorMessage = result?.detail || "Não foi possível analisar a notícia.";
      throw new Error(errorMessage);
    }

    if (!result) {
      throw new Error("Resposta inválida recebida da API.");
    }

    renderResult(result);
    feedback.classList.remove("error");
    feedback.classList.add("success");
    feedback.textContent = "Análise concluída com sucesso.";
  } catch (error) {
    console.error(error);
    feedback.classList.remove("success");
    feedback.classList.add("error");
    feedback.textContent = error.message || "Ocorreu um erro inesperado.";
  } finally {
    setLoadingState(false);
  }
});
