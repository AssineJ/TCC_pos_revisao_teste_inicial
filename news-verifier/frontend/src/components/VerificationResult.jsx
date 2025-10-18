import { useState } from 'react';
import VeracityGauge from './VeracityGauge.jsx';
import LoadingIndicator from './LoadingIndicator.jsx';

const STATUS_COPY = {
  idle: {
    title: 'O resultado aparecerá aqui após a verificação.',
    description: ''
  },
  error: {
    title: 'Não foi possível concluir a análise',
    description: 'A análise pode ter excedido o tempo limite ou houve um erro. Tente novamente.'
  }
};

// Logos dos portais (base64 ou URL)
export const PORTAL_LOGOS = {
  'G1': { src: '/assets/g1-logo.png', alt: 'G1' },
  'Folha de S.Paulo': { src: '/assets/logo-folha.png', alt: 'Folha de S.Paulo' },
  'UOL Notícias': { src: '/assets/uol-logo.jpg', alt: 'UOL Notícias' },
  'IstoÉ': { src: '/assets/istoe-logo.jpeg', alt: 'IstoÉ' },
  'Estadão': { src: '/assets/estadao-logo.png', alt: 'Estadão' }
};

function SourceModal({ source, onClose }) {
  if (!source) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Fechar">
          ✕
        </button>
        
        <div className="modal-header">
          <div className="modal-logo">
            {PORTAL_LOGOS[source.name] || '🌐'}
          </div>
          <div>
            <h3>{source.name}</h3>
            <p className="modal-similarity">
              Similaridade {Math.round(source.similarity * 100)}%
            </p>
          </div>
        </div>

        <div className="modal-body">
          <div className="modal-field">
            <label>Título</label>
            <p>{source.title || 'Sem título disponível'}</p>
          </div>

          <div className="modal-field">
            <label>URL</label>
            <a 
              href={source.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="modal-url"
            >
              {source.url}
            </a>
          </div>
        </div>

        <div className="modal-footer">
          <button className="modal-button" onClick={onClose}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}

export default function VerificationResult({ status, result }) {
  const [selectedSource, setSelectedSource] = useState(null);

  if (status === 'loading') {
    return (
      <div className="card card--glass">
        <LoadingIndicator />
      </div>
    );
  }

  // Se não há resultado, mostrar estado vazio
  if (!result) {
    const { title, description } = STATUS_COPY[status] ?? STATUS_COPY.idle;
    return (
      <div className="card card--glass empty">
        <div>
          {status === 'error' ? (
            <>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
              <h3 style={{ color: '#dc2626', marginBottom: '0.5rem' }}>{title}</h3>
              {description && <p style={{ color: '#64748b' }}>{description}</p>}
            </>
          ) : (
            <>
              <h3>{title}</h3>
              {description && <p>{description}</p>}
            </>
          )}
        </div>
      </div>
    );
  }

  // ✅ CORREÇÃO: Extrair veracity_score do result (estava faltando!)
  const {
    veracity_score,
    summary,
    signals,
    related_sources,
    confidence_level
  } = result;

  // ✅ NOVO: Se score é 0 ou muito baixo, mostrar como erro sem roda
  if (veracity_score === 0 || (veracity_score < 15 && summary && summary.includes('insuficientes'))) {
    return (
      <div className="card card--result">
        <div className="result__content">
          <div className="result__label">RESULTADO DA ANÁLISE</div>
          
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '1rem',
            padding: '1.5rem',
            background: 'rgba(239, 68, 68, 0.05)',
            borderRadius: '12px',
            border: '1px solid rgba(239, 68, 68, 0.2)',
            marginTop: '1rem'
          }}>
            <div style={{ fontSize: '2.5rem' }}>⚠️</div>
            <div>
              <h3 style={{ margin: 0, color: '#dc2626', fontSize: '1.1rem' }}>
                Dados insuficientes para validação
              </h3>
              <p style={{ margin: '0.5rem 0 0', color: '#64748b', fontSize: '0.9rem' }}>
                {summary}
              </p>
            </div>
          </div>

          {Array.isArray(signals) && signals.length > 0 && (
            <ul className="result__signals" style={{ marginTop: '1rem' }}>
              {signals.map((signal, index) => (
                <li key={index}>{signal}</li>
              ))}
            </ul>
          )}

          <div className="confidence-badge confidence-badge--baixo" style={{ marginTop: '1rem' }}>
            O texto fornecido não atende aos requisitos mínimos para análise
          </div>
        </div>
      </div>
    );
  }

  // Determinar nível baseado no score
  const getConfidenceLevel = (score) => {
    if (score >= 70) return 'alto';
    if (score >= 40) return 'medio';
    return 'baixo';
  };

  const nivel = getConfidenceLevel(veracity_score);

  return (
    <>
      <div className="card card--result">
        <div className="result__content">
          {/* Título */}
          <div className="result__label">PERCENTUAL DE VERACIDADE</div>
          
          {/* Porcentagem grande + Gauge */}
          <div className="result__score-section">
            <h2 className="result__score">{Math.round(veracity_score)}%</h2>
            <VeracityGauge score={veracity_score} nivel={nivel} />
          </div>

          {/* Justificativa */}
          <p className="result__summary">
            {summary || 'Análise concluída.'}
          </p>

          {/* Sinais/Signals */}
          {Array.isArray(signals) && signals.length > 0 && (
            <ul className="result__signals">
              {signals.map((signal, index) => (
                <li key={index}>{signal}</li>
              ))}
            </ul>
          )}

          {/* Fontes consultadas */}
          {Array.isArray(related_sources) && related_sources.length > 0 && (
            <div className="result__sources">
              <h3>Fontes consultadas</h3>
              <div className="sources-grid">
                {related_sources.slice(0, 6).map((source, index) => (
                  <button
                    key={index}
                    className="source-card"
                    onClick={() => setSelectedSource(source)}
                  >
                    <div className="source-logo">
                      {PORTAL_LOGOS[source.name] || '🌐'}
                    </div>
                    <div className="source-name">{source.name}</div>
                    <div className="source-similarity">
                      {Math.round(source.similarity * 100)}%
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Nível de confiança */}
          <div className={`confidence-badge confidence-badge--${nivel}`}>
            Nível de confiança: <strong>{confidence_level || nivel.toUpperCase()}</strong>
          </div>
        </div>
      </div>

      {/* Modal */}
      {selectedSource && (
        <SourceModal 
          source={selectedSource} 
          onClose={() => setSelectedSource(null)} 
        />
      )}
    </>
  );
}