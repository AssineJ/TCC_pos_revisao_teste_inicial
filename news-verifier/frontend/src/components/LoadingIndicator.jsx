import { useEffect, useState } from 'react';

const LOADING_STAGES = [
  { time: 0, message: 'Extraindo conteúdo e processando com IA...', emoji: '🤖' },
  { time: 30, message: 'Buscando em múltiplas fontes confiáveis...', emoji: '🔍' },
  { time: 60, message: 'Analisando similaridade semântica...', emoji: '🔬' },
  { time: 90, message: 'Detectando contradições e padrões...', emoji: '🧪' },
  { time: 120, message: 'Calculando veracidade final...', emoji: '🎯' },
  { time: 150, message: 'Finalizando análise detalhada...', emoji: '✨' },
  { time: 180, message: 'Aguarde, processamento complexo em andamento...', emoji: '⏳' }
];

export default function LoadingIndicator() {
  const [currentStage, setCurrentStage] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    // Atualiza o tempo decorrido a cada segundo
    const timer = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // Atualiza o estágio baseado no tempo decorrido
    const stage = LOADING_STAGES.findIndex((s, i) => {
      const nextStage = LOADING_STAGES[i + 1];
      return elapsedTime >= s.time && (!nextStage || elapsedTime < nextStage.time);
    });
    
    if (stage !== -1 && stage !== currentStage) {
      setCurrentStage(stage);
    }
  }, [elapsedTime, currentStage]);

  const currentMessage = LOADING_STAGES[currentStage];
  const progress = Math.min((elapsedTime / 180) * 100, 95); // Máximo 95% até terminar

  return (
    <div className="loading">
      <div className="loading__spinner">
        {Array.from({ length: 12 }).map((_, index) => (
          <span key={index} style={{ '--index': index }} />
        ))}
      </div>
      
      <div className="loading__text">
        <strong style={{ fontSize: '1.1rem' }}>
          {currentMessage.emoji} Verificando autenticidade
        </strong>
        <p style={{ margin: '0.5rem 0', color: '#475569' }}>
          {currentMessage.message}
        </p>
        
        {/* Barra de progresso */}
        <div style={{
          width: '100%',
          height: '8px',
          background: 'rgba(148, 163, 184, 0.2)',
          borderRadius: '999px',
          overflow: 'hidden',
          margin: '1rem 0 0.5rem'
        }}>
          <div style={{
            width: `${progress}%`,
            height: '100%',
            background: 'linear-gradient(90deg, #38bdf8 0%, #6366f1 100%)',
            borderRadius: '999px',
            transition: 'width 1s ease'
          }} />
        </div>
        
        <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: '0' }}>
          {elapsedTime}s decorridos • Tempo estimado: 1-3 minutos
        </p>
        
        {elapsedTime > 120 && (
          <p style={{ 
            fontSize: '0.9rem', 
            color: '#f59e0b', 
            margin: '0.5rem 0 0',
            fontWeight: '600'
          }}>
            ⏳ Análise mais demorada que o normal, aguarde...
          </p>
        )}
      </div>
    </div>
  );
}