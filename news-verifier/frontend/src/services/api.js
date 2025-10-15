const DEFAULT_HEADERS = {
  'Content-Type': 'application/json'
};

// URL base da API Flask
const baseURL = 'http://127.0.0.1:5000/api';

/**
 * Monta o corpo da requisição no formato esperado pelo backend:
 * {
 *   "tipo": "url" | "texto",
 *   "conteudo": "..."
 * }
 */
function buildPayload(type, payload) {
  return {
    tipo: type,
    conteudo: payload
  };
}

/**
 * Faz POST para /api/verificar e retorna o resultado mapeado
 * para o formato que o frontend consome.
 */
export async function verifyNewsRequest(type, payload) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s

  try {
    const response = await fetch(`${baseURL}/verificar`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(buildPayload(type, payload)),
      signal: controller.signal
    });

    if (!response.ok) {
      throw new Error(`Falha na API: ${response.status}`);
    }

    const data = await response.json();
    if (!data) {
      throw new Error('Resposta inválida da API');
    }

    // Normaliza "veracidade" vindo como número, "47%", "47,0", etc.
    const vRaw = data?.veracidade ?? data?.score ?? data?.veracity ?? 0;
    const veracidade =
      typeof vRaw === 'number'
        ? vRaw
        : parseFloat(String(vRaw).replace(',', '.').replace(/[^\d.-]/g, '')) || 0;

    return {
      veracity_score: veracidade, // sempre número
      summary: data?.justificativa ?? data?.mensagem ?? 'Análise concluída.',
      confidence_level: data?.nivel_confianca ?? 'Desconhecido',
      related_sources: data?.fontes_consultadas ?? [],
      main_source: data?.titulo_analisado ?? '',
      metadata: data?.metadata ?? {},
      nlp: data?.analise_nlp ?? {},
      semantic: data?.analise_semantica ?? {}
    };
  } catch (error) {
    console.error('Erro ao verificar notícia:', error);
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}
