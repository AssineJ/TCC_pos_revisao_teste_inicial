const DEFAULT_HEADERS = {
  'Content-Type': 'application/json'
};

// URL base da API Flask
const baseURL = 'http://127.0.0.1:5000/api';

/**
 * Corpo esperado pelo backend:
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
 * POST /api/verificar → normaliza e devolve o resultado.
 */
export async function verifyNewsRequest(type, payload) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

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
    if (!data) throw new Error('Resposta inválida da API');

    // --- Normalização blindada do score ---
    const raw = data?.veracidade ?? data?.score ?? data?.veracity ?? 0;
    const veracidade =
      typeof raw === 'number'
        ? raw
        : parseFloat(String(raw).replace(',', '.').replace(/[^\d.-]/g, '')) || 0;

    // Garante faixa 0..100 e inteiro auxiliar
    const veracityClamped = Math.max(0, Math.min(100, veracidade));
    const veracityInt = Math.round(veracityClamped);

    // --- Mapeamento amplo (compat com vários componentes) ---
    return {
      // numéricos
      veracity_score: veracityClamped, // principal
      veracity: veracityClamped,       // alias
      score: veracityClamped,          // alias
      percent: veracityClamped,        // alias
      percentage: veracityClamped,     // alias
      percent_int: veracityInt,        // inteiro

      // textos/listas
      summary: data?.justificativa ?? data?.mensagem ?? 'Análise concluída.',
      confidence_level: data?.nivel_confianca ?? 'Desconhecido',
      related_sources: data?.related_sources ?? [],
      main_source: data?.titulo_analisado ?? '',

      // extras (caso sua UI use)
      metadata: data?.metadata ?? {},
      nlp: data?.analise_nlp ?? {},
      semantic: data?.analise_semantica ?? {},

      // payload bruto (debug/telemetria)
      raw: data
    };
  } catch (err) {
    console.error('Erro ao verificar notícia:', err);
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}
