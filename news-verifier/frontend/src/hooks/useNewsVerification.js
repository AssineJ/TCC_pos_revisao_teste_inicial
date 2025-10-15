import { useCallback, useMemo, useRef, useState } from 'react';
import { verifyNewsRequest } from '../services/api.js';

const STATUS = {
  idle: 'idle',
  loading: 'loading',
  success: 'success',
  error: 'error'
};

export default function useNewsVerification() {
  const [status, setStatus] = useState(STATUS.idle);
  const [result, setResult] = useState(null);
  const lastRequestRef = useRef(null);

  const verifyNews = useCallback(async ({ type, payload }) => {
    setStatus(STATUS.loading);
    setResult(null);

    try {
      const response = await verifyNewsRequest(type, payload);

      // Garante que o formato esteja sempre pronto para o componente
      setResult({
        veracity: Number(response.veracity_score ?? 0) || 0,
        summary: response.summary ?? 'Análise concluída com sucesso.',
        sources: response.related_sources ?? [],
        confidence: response.confidence_level ?? 'Desconhecido',
        mainSource: response.main_source ?? ''
      });

      setStatus(STATUS.success);
      lastRequestRef.current = new Date();
    } catch (error) {
      console.error('Erro ao verificar notícia:', error);
      setStatus(STATUS.error);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setStatus(STATUS.idle);
  }, []);

  const lastRequest = useMemo(() => lastRequestRef.current, [status]);

  return {
    verifyNews,
    reset,
    status,
    result,
    lastRequest
  };
}
