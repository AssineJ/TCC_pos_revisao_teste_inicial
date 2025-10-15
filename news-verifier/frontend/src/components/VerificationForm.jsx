import { useMemo, useState } from 'react';
import { FiLink, FiFileText, FiRefreshCw, FiSend } from 'react-icons/fi';

const INPUT_TYPES = {
  url: {
    label: 'Validar por URL',
    placeholder: 'https://exemplo.com/noticia-importante'
  },
  text: {
    label: 'Validar por texto',
    placeholder: 'Cole o conteúdo da notícia que deseja analisar...'
  }
};

const INITIAL_FORM = {
  mode: 'url',
  value: ''
};

export default function VerificationForm({ status, onSubmit, onReset, lastRequest }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [touched, setTouched] = useState(false);

  const isLoading = status === 'loading';

  const charCount = useMemo(() => form.value.trim().length, [form.value]);
  const isFormValid = charCount >= (form.mode === 'url' ? 10 : 30);

  const handleModeChange = (mode) => {
    setForm({ mode, value: '' });
    setTouched(false);
    onReset?.();
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setTouched(true);

    if (!isFormValid || isLoading) {
      return;
    }

    onSubmit({
      type: form.mode,
      payload: form.value.trim()
    });
  };

  const handleReset = () => {
    setForm(INITIAL_FORM);
    setTouched(false);
    onReset?.();
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <header className="card__header">
        <h2>Valide uma notícia agora</h2>
        <p>
          Escolha validar por URL ou texto completo. O NewsTrust retornará um percentual de veracidade com justificativas baseadas em fontes confiáveis.
        </p>
      </header>

      <div className="toggle">
        {Object.entries(INPUT_TYPES).map(([mode, config]) => (
          <button
            key={mode}
            type="button"
            className={`toggle__option ${form.mode === mode ? 'toggle__option--active' : ''}`}
            onClick={() => handleModeChange(mode)}
            disabled={isLoading}
          >
            {mode === 'url' ? <FiLink /> : <FiFileText />} {config.label}
          </button>
        ))}
      </div>

      <label className="field">
        <span>
          {INPUT_TYPES[form.mode].label}
          <small>
            {form.mode === 'url'
              ? 'Informe o endereço completo da notícia que será analisada.'
              : 'Quanto mais detalhes, melhor. O mínimo recomendado são 30 caracteres.'}
          </small>
        </span>
        {form.mode === 'url' ? (
          <input
            type="url"
            placeholder={INPUT_TYPES.url.placeholder}
            value={form.value}
            onChange={(event) => setForm((prev) => ({ ...prev, value: event.target.value }))}
            disabled={isLoading}
            required
          />
        ) : (
          <textarea
            placeholder={INPUT_TYPES.text.placeholder}
            value={form.value}
            onChange={(event) => setForm((prev) => ({ ...prev, value: event.target.value }))}
            disabled={isLoading}
            minLength={30}
            rows={8}
            required
          />
        )}
      </label>

      <div className="form__footer">
        <div className="form__status">
          <strong>{charCount}</strong> caracteres
          {touched && !isFormValid && (
            <span className="form__warning">
              {form.mode === 'url'
                ? 'Informe uma URL válida com pelo menos 10 caracteres.'
                : 'Insira pelo menos 30 caracteres para permitir a análise.'}
            </span>
          )}
          {lastRequest && (
            <span className="form__last">
              Última análise: <time dateTime={lastRequest.toISOString()}>{lastRequest.toLocaleString('pt-BR')}</time>
            </span>
          )}
        </div>

        <div className="form__actions">
          <button type="button" className="ghost" onClick={handleReset} disabled={isLoading}>
            <FiRefreshCw /> Limpar
          </button>
          <button type="submit" className="primary" disabled={!isFormValid || isLoading}>
            <FiSend /> {isLoading ? 'Verificando...' : 'Verificar notícia'}
          </button>
        </div>
      </div>
    </form>
  );
}