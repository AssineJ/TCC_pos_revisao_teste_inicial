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
  // ✅ CORREÇÃO: Mapeia 'text' (inglês) para 'texto' (português)
  const tipoBackend = type === 'text' ? 'texto' : 'url';
  
  return {
    tipo: tipoBackend,
    conteudo: payload
  };
}

/**
 * Faz POST para /api/verificar e retorna o resultado mapeado
 * para o formato que o frontend consome.
 */
export async function verifyNewsRequest(type, payload) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 240000); // ✅ AUMENTADO: 4 minutos (240s)

  try {
    const requestBody = buildPayload(type, payload);
    
    // ✅ LOG: Mostra o que está sendo enviado
    console.log('🔵 Enviando para API:', {
      url: `${baseURL}/verificar`,
      typeRecebido: type,
      tipoEnviado: requestBody.tipo,
      body: requestBody,
      timeout: '240 segundos (4 minutos)'  // ✅ NOVO
    });

    const response = await fetch(`${baseURL}/verificar`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(requestBody),
      signal: controller.signal
    });

    // ✅ LOG: Status da resposta
    console.log('🔵 Status da resposta:', response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('🔴 Erro do backend:', errorData);
      throw new Error(errorData.erro || `Falha na API: ${response.status}`);
    }

    const data = await response.json();
    if (!data) {
      throw new Error('Resposta inválida da API');
    }

    // ✅ LOG COMPLETO: Mostra TODA a resposta do backend
    console.log('🟢 Resposta completa do backend:', JSON.stringify(data, null, 2));

    // ✅ CORREÇÃO: Mapeia corretamente os campos do backend
    const vRaw = data?.veracidade ?? 0;
    const veracidade =
      typeof vRaw === 'number'
        ? vRaw
        : parseFloat(String(vRaw).replace(',', '.').replace(/[^\d.-]/g, '')) || 0;

    // ✅ Monta os "signals" a partir da justificativa
    const signals = [];
    if (data?.justificativa) {
      signals.push(data.justificativa);
    }
    
    // ✅ Adiciona informações semânticas como signals
    if (data?.analise_semantica) {
      const sem = data.analise_semantica;
      if (sem.confirmam_forte > 0) {
        signals.push(`${sem.confirmam_forte} fonte(s) confirmam fortemente a informação`);
      }
      if (sem.confirmam_parcial > 0) {
        signals.push(`${sem.confirmam_parcial} fonte(s) confirmam parcialmente`);
      }
      if (sem.apenas_mencionam > 0) {
        signals.push(`${sem.apenas_mencionam} fonte(s) apenas mencionam o tema`);
      }
    }

    // ✅ CORREÇÃO PRINCIPAL: Mapeia "fontes_consultadas" para "related_sources"
    const fontes = (data?.fontes_consultadas || []).map(fonte => ({
      name: fonte.nome || 'Fonte desconhecida',
      url: fonte.url || '',
      title: fonte.titulo || '',
      similarity: fonte.similaridade || 0,
      status: fonte.status || ''
    }));

    return {
      veracity_score: veracidade,
      summary: data?.justificativa || 'Análise concluída.',
      confidence_level: data?.nivel_confianca || 'Desconhecido',
      related_sources: fontes, // ✅ Agora mapeia corretamente
      signals: signals.length > 0 ? signals : ['Nenhum sinal adicional identificado'],
      main_source: data?.titulo_analisado || '',
      metadata: data?.metadata || {},
      nlp: data?.analise_nlp || {},
      semantic: data?.analise_semantica || {}
    };
  } catch (error) {
    console.error('Erro ao verificar notícia:', error);
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}