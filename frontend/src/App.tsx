import { FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import './App.css';

const API_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');

type CheckResponse = {
  verdict: string;
  probability: number;
  message: string;
};

type UrlCheckResponse = CheckResponse & {
  extracted_title: string | null;
  content_preview: string | null;
  url: string;
};

=======
type RecentNewsItem = {
  id: number | string;
  title: string;
  source_name: string | null;
  source_url: string | null;
  publish_date: string | null;
};

type VerdictTone = 'success' | 'warning' | 'danger';

type VerdictConfig = {
  tone: VerdictTone;
  headline: string;
  tips: string[];
};

type VerdictKey = 'VERDADEIRO' | 'INDETERMINADO' | 'PROVAVELMENTE FALSO' | 'DEFAULT';

const VERDICT_CONFIG: Record<VerdictKey, VerdictConfig> = {
  VERDADEIRO: {
    tone: 'success',
    headline: 'Sinais de conteúdo confiável',
    tips: [
      'Ainda assim, confirme a notícia em portais reconhecidos (G1, Agência Brasil, Folha, Estadão).',
      'Leia a matéria completa antes de compartilhar e confirme se outras fontes também publicaram o conteúdo.',
=======
      'Compartilhe somente após ler o texto completo e conferir se o título condiz com o corpo da matéria.',
      'Mantenha o hábito de acompanhar fontes oficiais relacionadas ao tema tratado.'
    ]
  },
  INDETERMINADO: {
    tone: 'warning',
    headline: 'Informações adicionais são necessárias',
    tips: [
      'Procure pelo assunto em diferentes portais jornalísticos e compare as versões.',
      'Verifique se a notícia cita fontes confiáveis, especialistas ou dados verificáveis.',
      'Desconfie de textos com tom extremamente alarmista ou que incentivem compartilhamentos urgentes.'
    ]
  },
  'PROVAVELMENTE FALSO': {
    tone: 'danger',
    headline: 'Alerta: fortes indícios de fake news',
    tips: [
      'Não compartilhe antes de buscar confirmação em agências de checagem (Lupa, Aos Fatos, Comprova).',
      'Pesquise trechos da notícia no Google para verificar se há desmentidos ou notas oficiais.',
      'Observe se o texto contém erros gramaticais graves, links suspeitos ou promessas de ganhos fáceis.'
    ]
  },
  DEFAULT: {
    tone: 'warning',
    headline: 'Verifique manualmente em fontes confiáveis',
    tips: [
      'Busque fontes adicionais e priorize veículos de comunicação consolidados.',
      'Evite compartilhar até ter certeza da procedência da informação.',
      'Cheque se a notícia possui data, autoria e referências claras.'
    ]
  }
};

const normalizeProbability = (value: number | null | undefined): number => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return 0;
  }
  if (!Number.isFinite(value)) {
    return value > 0 ? 1 : 0;
  }
  if (value < 0) {
    return 0;
  }
  if (value > 1) {
    return 1;
  }
  return value;
};

const extractErrorDetail = (payload: unknown): string | null => {
  if (payload && typeof payload === 'object' && 'detail' in payload) {
    const detail = (payload as { detail?: unknown }).detail;
    if (typeof detail === 'string') {
      return detail;
    }
  }
  return null;
};

const formatDate = (value: string | null): string => {
  if (!value) {
    return 'Data não informada';
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleString('pt-BR', {
    dateStyle: 'medium',
    timeStyle: 'short'
  });
};

const toneClassMap: Record<VerdictTone, string> = {
  success: 'badge--success',
  warning: 'badge--warning',
  danger: 'badge--danger'
};

const meterClassMap: Record<VerdictTone, string> = {
  success: 'probability-meter__fill probability-meter__fill--success',
  warning: 'probability-meter__fill probability-meter__fill--warning',
  danger: 'probability-meter__fill probability-meter__fill--danger'
};

function App(): JSX.Element {
  const [url, setUrl] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [requestError, setRequestError] = useState<string | null>(null);
  const [result, setResult] = useState<UrlCheckResponse | null>(null);
=======
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [requestError, setRequestError] = useState<string | null>(null);
  const [result, setResult] = useState<CheckResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [newsLoading, setNewsLoading] = useState(false);
  const [newsItems, setNewsItems] = useState<RecentNewsItem[]>([]);
  const [collecting, setCollecting] = useState(false);
  const [collectMessage, setCollectMessage] = useState<string | null>(null);

  const fetchRecentNews = useCallback(async () => {
    setNewsLoading(true);
    setRequestError(null);
    try {
      const response = await fetch(`${API_URL}/recent-news?limit=6`);
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        const detail = extractErrorDetail(payload);
        throw new Error(detail ?? 'Não foi possível carregar as notícias recentes.');
      }

      const data = (payload as { news?: RecentNewsItem[] } | null)?.news;
      setNewsItems(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error(error);
      setRequestError(
        error instanceof Error
          ? error.message
          : 'Erro inesperado ao carregar as notícias recentes.'
      );
    } finally {
      setNewsLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchRecentNews();
  }, [fetchRecentNews]);

  const verdictKey = useMemo<VerdictKey>(() => {
    if (!result?.verdict) {
      return 'DEFAULT';
    }
    return (result.verdict in VERDICT_CONFIG ? result.verdict : 'DEFAULT') as VerdictKey;
  }, [result]);

  const verdictConfig = VERDICT_CONFIG[verdictKey];
  const tone = verdictConfig.tone;
  const normalizedProbability = normalizeProbability(result?.probability);
  const probabilityPercent = (normalizedProbability * 100).toLocaleString('pt-BR', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  });

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError(null);
    setRequestError(null);
    setCollectMessage(null);

    const sanitizedUrl = url.trim();
    if (!sanitizedUrl) {
      setFormError('Informe a URL completa da notícia que deseja validar.');
      return;
    }

    let normalizedUrl: string;
    try {
      const parsed = new URL(sanitizedUrl);
      if (!['http:', 'https:'].includes(parsed.protocol)) {
        throw new Error('Protocol inválido');
      }
      normalizedUrl = parsed.toString();
    } catch (error) {
      console.error(error);
      setFormError('Informe uma URL válida iniciando com http:// ou https://.');
=======
    const sanitizedTitle = title.trim();
    const sanitizedContent = content.trim();

    if (!sanitizedTitle || !sanitizedContent) {
      setFormError('Informe o título e o conteúdo da notícia para realizar a verificação.');
      return;
    }

    if (sanitizedContent.length < 60) {
      setFormError('Insira pelo menos 60 caracteres no conteúdo para obter uma análise consistente.');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/check-news-url`, {
=======
      const response = await fetch(`${API_URL}/check-news`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: normalizedUrl
=======
          title: sanitizedTitle,
          content: sanitizedContent
        })
      });

      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        const detail = extractErrorDetail(payload);
        throw new Error(detail ?? 'Não foi possível verificar a notícia.');
      }

      setResult(payload as UrlCheckResponse);
=======
      setResult(payload as CheckResponse);
    } catch (error) {
      console.error(error);
      setResult(null);
      setRequestError(
        error instanceof Error ? error.message : 'Erro inesperado ao verificar a notícia.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setUrl('');
=======
    setTitle('');
    setContent('');
    setFormError(null);
    setRequestError(null);
    setCollectMessage(null);
    setResult(null);
  };

  const handleCollectNews = async () => {
    setCollecting(true);
    setCollectMessage(null);
    setRequestError(null);
    try {
      const response = await fetch(`${API_URL}/collect-news`, {
        method: 'POST'
      });

      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        const detail = extractErrorDetail(payload);
        throw new Error(detail ?? 'Não foi possível iniciar a coleta de notícias.');
      }

      const message = (payload as { message?: string } | null)?.message ??
        'Coleta concluída com sucesso.';
      setCollectMessage(message);
      await fetchRecentNews();
    } catch (error) {
      console.error(error);
      setRequestError(
        error instanceof Error ? error.message : 'Erro inesperado ao coletar notícias.'
      );
    } finally {
      setCollecting(false);
    }
  };

  return (
    <div className="app">
      <div className="app__wrapper">
        <header>
          <h1>Detector de Fake News BR</h1>
          <p>
            Cole uma URL de notícia para que o sistema faça a leitura automática do conteúdo e aponte o grau de confiabilidade.
=======
            Analise notícias em segundos com o suporte da nossa API FastAPI treinada com conteúdos brasileiros.
          </p>
        </header>

        <section className="card">
          <form className="check-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="news-url">URL da notícia</label>
              <input
                id="news-url"
                name="url"
                type="url"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                placeholder="https://www.exemplo.com/noticia-importante"
                autoComplete="off"
                inputMode="url"
              />
              <small className="form-hint">Cole o link completo começando com http:// ou https://.</small>
=======
              <label htmlFor="news-title">Título da notícia</label>
              <input
                id="news-title"
                name="title"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="Ex.: Governo anuncia novo programa de incentivo à energia solar"
                autoComplete="off"
              />
            </div>

            <div className="form-group">
              <label htmlFor="news-content">Conteúdo da notícia</label>
              <textarea
                id="news-content"
                name="content"
                value={content}
                onChange={(event) => setContent(event.target.value)}
                placeholder="Cole aqui o corpo completo da notícia para obter uma análise mais precisa"
              />
            </div>

            {formError && <div className="alert alert--error">{formError}</div>}
            {requestError && <div className="alert alert--error">{requestError}</div>}
            {collectMessage && <div className="alert alert--info">{collectMessage}</div>}

            <div className="button-group">
              <button className="button button--primary" type="submit" disabled={loading}>
                {loading ? 'Analisando...' : 'Verificar notícia'}
              </button>
              <button
                className="button button--ghost"
                type="button"
                onClick={handleClear}
                disabled={loading}
              >
                Limpar
=======
                Limpar campos
              </button>
            </div>
          </form>
        </section>

        {result && (
          <section className="card">
            <div className="result-header">
              <span className={`badge ${toneClassMap[tone]}`}>
                {result.verdict}
              </span>
              <h2>{verdictConfig.headline}</h2>
              <p>{result.message}</p>
            </div>

            <div className="article-preview">
              <h3>Matéria analisada</h3>
              <p className="article-preview__title">
                {result.extracted_title ?? 'Título não identificado'}
              </p>
              {result.content_preview && (
                <p className="article-preview__snippet">{result.content_preview}</p>
              )}
              <a
                className="article-preview__link"
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                Ler notícia original
              </a>
            </div>

=======
            <div className="probability-meter">
              <div className="probability-meter__label">
                <span>Probabilidade de ser fake</span>
                <strong>{probabilityPercent}%</strong>
              </div>
              <div className="probability-meter__track">
                <div
                  className={meterClassMap[tone]}
                  style={{ width: `${Math.round(normalizedProbability * 100)}%` }}
                />
              </div>
            </div>

            <div className="analysis-section">
              <div className="analysis-card">
                <h3>Como interpretar este resultado</h3>
                <ul>
                  {verdictConfig.tips.map((tip) => (
                    <li key={tip}>{tip}</li>
                  ))}
                </ul>
              </div>
              <div className="analysis-card">
                <h3>Boas práticas de verificação</h3>
                <ul>
                  <li>Pesquise o assunto em mais de uma fonte jornalística.</li>
                  <li>Confirme a data, autoria e referências da notícia.</li>
                  <li>Desconfie de mensagens que pedem compartilhamentos imediatos.</li>
                </ul>
              </div>
            </div>
          </section>
        )}

        <section className="card news-section">
          <div className="news-header">
            <h2>Últimas notícias coletadas</h2>
            <div className="button-group">
              <button
                className="button button--outline"
                type="button"
                onClick={fetchRecentNews}
                disabled={newsLoading}
              >
                {newsLoading ? 'Atualizando...' : 'Atualizar lista'}
              </button>
              <button
                className="button button--primary"
                type="button"
                onClick={handleCollectNews}
                disabled={collecting}
              >
                {collecting ? 'Coletando...' : 'Rodar coleta automática'}
              </button>
            </div>
          </div>

          {newsLoading && <div className="loading-indicator">Carregando notícias...</div>}

          {!newsLoading && newsItems.length === 0 && (
            <p>Sem notícias cadastradas até o momento. Utilize a coleta automática para alimentar o banco.</p>
          )}

          {newsItems.length > 0 && (
            <div className="news-grid">
              {newsItems.map((item) => (
                <article className="news-card" key={item.id}>
                  <h4>{item.title}</h4>
                  <p>
                    <strong>Fonte:</strong> {item.source_name ?? 'Não informada'}
                  </p>
                  <p>
                    <strong>Publicado em:</strong> {formatDate(item.publish_date)}
                  </p>
                  {item.source_url && item.source_url.startsWith('http') && (
                    <p>
                      <a href={item.source_url} target="_blank" rel="noopener noreferrer">
                        Ler matéria original
                      </a>
                    </p>
                  )}
                </article>
              ))}
            </div>
          )}
        </section>

        <p className="footer">
          A API aceita requisições REST padrão. Defina a variável de ambiente <code>VITE_API_URL</code> para apontar o front-end
          para outra origem.
=======
          A API aceita requisições REST padrão. Defina a variável de ambiente <code>VITE_API_URL</code> para apontar o front-end para outra origem.
        </p>
      </div>
    </div>
  );
}

export default App;
