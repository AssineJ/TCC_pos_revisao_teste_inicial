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

      // ✅ LOG: Mostra o que foi recebido
      console.log('✅ Resposta processada:', response);

      // ✅ CORREÇÃO: Mantém a estrutura exata retornada pela API
      setResult({
        veracity_score: response.veracity_score,
        summary: response.summary,
        related_sources: response.related_sources,
        signals: response.signals,
        confidence_level: response.confidence_level,
        main_source: response.main_source,
        metadata: response.metadata,
        nlp: response.nlp,
        semantic: response.semantic
      });

      setStatus(STATUS.success);
      lastRequestRef.current = new Date();
    } catch (error) {
      console.error('Erro ao verificar notícia:', error);
      
      // ✅ Detectar se foi timeout
      const isTimeout = error.name === 'AbortError' || error.message.includes('aborted');
      
      // ✅ CORREÇÃO: Define um result de erro para mostrar mensagem adequada
      setResult({
        veracity_score: 0,
        summary: isTimeout 
          ? '⏱️ A análise excedeu o tempo limite de 4 minutos. Isso pode ocorrer com textos muito longos ou quando há muitas fontes para consultar. Tente novamente com um texto mais curto.'
          : 'Não foi possível concluir a análise. ' + (error.message || 'Erro desconhecido. Verifique se o backend está rodando em http://127.0.0.1:5000'),
        related_sources: [],
        signals: [
          isTimeout 
            ? 'Timeout: A análise demorou mais de 4 minutos'
            : 'Erro durante a verificação: ' + error.message
        ],
        confidence_level: 'Baixo',
        main_source: '',
        metadata: {},
        nlp: {},
        semantic: {}
      });
      
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