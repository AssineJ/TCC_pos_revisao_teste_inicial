import VeracityGauge from './VeracityGauge.jsx';
import LoadingIndicator from './LoadingIndicator.jsx';

const LOADING_TIP = [
  'Buscando fontes confiáveis e comparando dados... ',
  'Checando indicadores de clickbait e linguagem tendenciosa... ',
  'Avaliando reputação das fontes e divergências factuais... '
];

const STATUS_COPY = {
  idle: {
    title: 'Pronto para começar',
    description: 'Aguardando uma notícia para validar. Insira a URL ou texto e clique em Verificar.'
  },
  error: {
    title: 'Não foi possível concluir a análise',
    description: 'Verifique os dados informados ou tente novamente em alguns instantes.'
  }
};

export default function VerificationResult({ status, result }) {
  if (status === 'loading') {
    return (
      <section className="card card--glass">
        <LoadingIndicator message={LOADING_TIP[Math.floor(Math.random() * LOADING_TIP.length)]} />
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

  const {
    veracity_score: score,
    summary,
    signals,
    related_sources: sources
  } = result;

  return (
    <section className="card card--result">
      <header className="result__header">
        <div>
          <span className="result__label">Percentual de veracidade</span>
          <h2>{Math.round(score)}%</h2>
        </div>
        <VeracityGauge score={score} />
      </header>

      <div className="result__content">
        <p className="result__summary">{summary ?? 'O backend não enviou um resumo para esta análise.'}</p>

        {Array.isArray(signals) && signals.length > 0 && (
          <ul className="result__signals">
            {signals.map((signal, index) => (
              <li key={index}>{signal}</li>
            ))}
          </ul>
        )}

        {Array.isArray(sources) && sources.length > 0 && (
          <div className="result__sources">
            <h3>Fontes consultadas</h3>
            <ul>
              {sources.map((source, index) => (
                <li key={index}>
                  {source.url ? (
                    <a href={source.url} target="_blank" rel="noopener noreferrer">
                      {source.name ?? source.url}
                    </a>
                  ) : (
                    source.name ?? 'Fonte não especificada'
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