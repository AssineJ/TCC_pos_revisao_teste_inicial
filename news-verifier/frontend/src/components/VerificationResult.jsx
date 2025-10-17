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

export const PORTAL_LOGOS = {
  'G1': { src: '/assets/g1-logo.png', alt: 'G1' },
  'Folha de S.Paulo': { src: '/assets/logo-folha.png', alt: 'Folha de S.Paulo' },
  'UOL Notícias': { src: '/assets/uol-logo.jpg', alt: 'UOL Notícias' },
  'IstoÉ': { src: '/assets/istoe-logo.jpeg', alt: 'IstoÉ' },
  'Estadão': { src: '/assets/estadao-logo.png', alt: 'Estadão' }
};

const renderPortalLogo = (name) => {
  const logo = PORTAL_LOGOS[name];

  if (!logo) {
    return '🌐';
  }

  return (
    <img
      src={logo.src}
      alt={logo.alt || name}
      className="portal-logo-image"
      loading="lazy"
    />
  );
};

function SourceModal({ source, onClose }) {
  if (!source) return null;

  const publishedYear = extractSourceYear(source);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Fechar">
          ✕
        </button>
        
        <div className="modal-header">
          <div className="modal-logo">
            {renderPortalLogo(source.name)}
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
            <label>Ano da notícia</label>
            <p>{publishedYear || 'Não disponível'}</p>
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

  if (!result) {
    const { title, description } = STATUS_COPY[status] ?? STATUS_COPY.idle;
    return (
      <div className="card card--glass empty">
        <div>
          <h3>{title}</h3>
          {description && <p>{description}</p>}
        </div>
      </div>
    );
  }

  const isLowQualityError = result?.error_code === 'LOW_TEXT_QUALITY';

  if (isLowQualityError) {
    const issues = Array.isArray(result.signals) ? result.signals : [];
    const qualityScore = result.quality_validation?.score_qualidade;
    const hasQualityScore = typeof qualityScore === 'number';

    return (
      <div className="card card--result">
        <div className="result__content">
          <div className="result__label">RESULTADO DA ANÁLISE</div>

          <div className="result__alert result__alert--error">
            <div className="result__alert-header">
              <h2>Dados insuficientes para validação</h2>

              {hasQualityScore && (
                <span className="result__alert-score">
                  Nível de qualidade identificado: {(qualityScore * 100).toFixed(0)}%
                </span>
              )}
            </div>

            <div className="result__alert-grid">
              <div className="result__alert-section">
                <p className="result__alert-summary">{result.summary}</p>
                <p className="result__alert-help">
                  Forneça um texto com contexto suficiente, evitando repetições ou palavras desconexas, e tente novamente.
                </p>
              </div>

              {issues.length > 0 && (
                <div className="result__alert-section">
                  <h3>Problemas identificados</h3>
                  <ul className="result__alert-list">
                    {issues.map((issue, index) => (
                      <li key={index}>{issue}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const {
    veracity_score,
    summary,
    signals,
    related_sources,
    confidence_level
  } = result;

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
          <div className="result__label">PERCENTUAL DE VERACIDADE</div>
          
          <div className="result__score-section">
            <h2 className="result__score">{Math.round(veracity_score)}%</h2>
            <VeracityGauge score={veracity_score} nivel={nivel} />
          </div>

          <p className="result__summary">
            {summary || 'Análise concluída.'}
          </p>

          {Array.isArray(signals) && signals.length > 0 && (
            <ul className="result__signals">
              {signals.map((signal, index) => (
                <li key={index}>{signal}</li>
              ))}
            </ul>
          )}

          {Array.isArray(related_sources) && related_sources.length > 0 && (
            <div className="result__sources">
              <h3>Fontes consultadas</h3>
              <div className="sources-grid">
                {related_sources.slice(0, 6).map((source, index) => (
                  <button
                    key={index}
                    className="source-card"
                    type="button"
                    onClick={() => setSelectedSource(source)}
                  >
                    <div className="source-logo">
                      {renderPortalLogo(source.name)}
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