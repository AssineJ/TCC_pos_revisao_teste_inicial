import VeracityGauge from './VeracityGauge.jsx';
import LoadingIndicator from './LoadingIndicator.jsx';

const STATUS_COPY = {
  idle: {
    title: 'Pronto para começar',
    description: 'Aguardando uma notícia para validar. Insira a URL ou texto e clique em Verificar.'
  },
  error: {
    title: 'Não foi possível concluir a análise',
    description: 'A análise pode ter excedido o tempo limite de 4 minutos ou houve um erro. Tente com um texto mais curto ou URL diferente.'
  }
};

export default function VerificationResult({ status, result }) {
  if (status === 'loading') {
    return (
      <section className="card card--glass">
        <LoadingIndicator />
      </section>
    );
  }

  if (!result) {
    const { title, description } = STATUS_COPY[status] ?? STATUS_COPY.idle;
    return (
      <section className="card card--glass empty">
        <h3>{title}</h3>
        <p>{description}</p>
      </section>
    );
  }

  // ✅ CORREÇÃO: Acessa os campos corretos do objeto result
  const {
    veracity_score,
    summary,
    signals,
    related_sources,
    confidence_level,
    main_source
  } = result;

  return (
    <section className="card card--result">
      <header className="result__header">
        <div>
          <span className="result__label">Percentual de veracidade</span>
          <h2>{Math.round(veracity_score)}%</h2>
          {main_source && (
            <p style={{ fontSize: '0.9rem', color: '#64748b', marginTop: '0.5rem' }}>
              {main_source}
            </p>
          )}
        </div>
        <VeracityGauge score={veracity_score} />
      </header>

      <div className="result__content">
        <p className="result__summary">
          {summary || 'O backend não enviou um resumo para esta análise.'}
        </p>

        {confidence_level && (
          <p style={{ color: '#475569', fontSize: '0.95rem', marginTop: '0.5rem' }}>
            <strong>Nível de confiança:</strong> {confidence_level}
          </p>
        )}

        {Array.isArray(signals) && signals.length > 0 && (
          <ul className="result__signals">
            {signals.map((signal, index) => (
              <li key={index}>{signal}</li>
            ))}
          </ul>
        )}

        {/* ✅ CORREÇÃO: Agora mostra as fontes corretamente */}
        {Array.isArray(related_sources) && related_sources.length > 0 && (
          <div className="result__sources">
            <h3>Fontes consultadas ({related_sources.length})</h3>
            <ul>
              {related_sources.map((source, index) => (
                <li key={index}>
                  {source.url ? (
                    <a 
                      href={source.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      title={source.title || source.name}
                    >
                      <strong>{source.name}</strong>
                      {source.similarity > 0 && (
                        <span style={{ color: '#94a3b8', fontSize: '0.85rem', marginLeft: '0.5rem' }}>
                          ({Math.round(source.similarity * 100)}% similaridade)
                        </span>
                      )}
                    </a>
                  ) : (
                    <span>{source.name || 'Fonte não especificada'}</span>
                  )}
                  {source.title && source.title !== source.name && (
                    <div style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '0.2rem' }}>
                      {source.title}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}