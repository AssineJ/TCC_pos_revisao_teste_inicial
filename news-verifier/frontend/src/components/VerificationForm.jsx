import { useMemo, useState, useEffect } from 'react';
import { FiLink, FiFileText, FiRefreshCw, FiSend } from 'react-icons/fi';

const INPUT_TYPES = {
  url: {
    label: 'Validar por URL',
    placeholder: 'https://exemplo.com/noticia-importante',
    minLength: 10,
    maxLength: 500,  // URLs podem ser maiores
    helpText: 'Informe o endereço completo da notícia que será analisada.',
    errorText: 'Informe uma URL válida com pelo menos 10 caracteres.'
  },
  text: {
    label: 'Validar por texto',
    placeholder: 'Cole o conteúdo da notícia que deseja analisar...',
    minLength: 50,
    maxLength: 300,  // ✅ LIMITE DE 300 CARACTERES
    helpText: 'Insira o texto completo da notícia. Mínimo 50, máximo 300 caracteres.',
    errorText: 'Insira entre 50 e 300 caracteres para análise.'
  }
};

const INITIAL_FORM = {
  mode: 'url',
  value: ''
};

export default function VerificationForm({ status, onSubmit, onReset, lastRequest }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [touched, setTouched] = useState(false);
  const [textQualityWarning, setTextQualityWarning] = useState('');

  const isLoading = status === 'loading';

  const charCount = useMemo(() => form.value.trim().length, [form.value]);
  const isFormValid = charCount >= INPUT_TYPES[form.mode].minLength;

  // Validação de qualidade em tempo real
  useEffect(() => {
    if (form.mode === 'text' && charCount >= 50) {
      const text = form.value.trim();
      
      // Detectar repetições excessivas
      const hasExcessiveRepetition = /(.)\1{5,}/.test(text);
      
      // Detectar poucas palavras únicas
      const words = text.toLowerCase().match(/\b\w+\b/g) || [];
      const uniqueWords = new Set(words).size;
      const repetitionRatio = words.length > 0 ? uniqueWords / words.length : 1;
      
      if (hasExcessiveRepetition) {
        setTextQualityWarning('⚠️ Texto com caracteres repetidos excessivamente');
      } else if (repetitionRatio < 0.3 && words.length > 5) {
        setTextQualityWarning('⚠️ Texto parece ter muitas palavras repetidas');
      } else {
        setTextQualityWarning('');
      }
    } else {
      setTextQualityWarning('');
    }
  }, [form.value, form.mode, charCount]);

  const handleModeChange = (mode) => {
    setForm({ mode, value: '' });
    setTouched(false);
    setTextQualityWarning('');
    if (onReset) onReset();
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setTouched(true);

    if (!isFormValid || isLoading) {
      return;
    }

    console.log('📤 Enviando verificação:', {
      mode: form.mode,
      type: form.mode,
      payload: form.value.trim(),
      length: form.value.trim().length
    });

    onSubmit({
      type: form.mode,
      payload: form.value.trim()
    });
  };

  const handleReset = () => {
    setForm(INITIAL_FORM);
    setTouched(false);
    setTextQualityWarning('');
    if (onReset) onReset();
  };

  const currentConfig = INPUT_TYPES[form.mode];

  return (
    <form className="card" onSubmit={handleSubmit}>
      <header className="card__header">
        <h2>Valide uma notícia agora</h2>
        <p>
          Escolha validar por URL ou texto completo. O NewsTrust retornará um percentual de veracidade com justificativas baseadas em fontes confiáveis.
        </p>
        {isLoading && (
          <p style={{ 
            background: 'rgba(59, 130, 246, 0.1)', 
            padding: '0.75rem 1rem', 
            borderRadius: '12px',
            color: '#1e40af',
            fontSize: '0.9rem',
            margin: '0.5rem 0 0',
            border: '1px solid rgba(59, 130, 246, 0.2)'
          }}>
            ⏳ <strong>Tempo estimado:</strong> 1-3 minutos. Aguarde enquanto analisamos múltiplas fontes confiáveis.
          </p>
        )}
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
          {currentConfig.label}
          <small>{currentConfig.helpText}</small>
        </span>
        {form.mode === 'url' ? (
          <input
            type="url"
            placeholder={currentConfig.placeholder}
            value={form.value}
            onChange={(event) => setForm((prev) => ({ ...prev, value: event.target.value }))}
            disabled={isLoading}
            required
          />
        ) : (
          <textarea
            placeholder={currentConfig.placeholder}
            value={form.value}
            onChange={(event) => setForm((prev) => ({ ...prev, value: event.target.value }))}
            disabled={isLoading}
            minLength={currentConfig.minLength}
            rows={8}
            required
          />
        )}
      </label>

      <div className="form__footer">
        <div className="form__status">
          <strong>{charCount}</strong> caracteres
          <span style={{ color: '#64748b', fontSize: '0.9rem' }}>
            (mínimo: {currentConfig.minLength})
          </span>
          {touched && !isFormValid && (
            <span className="form__warning">
              {currentConfig.errorText}
            </span>
          )}
          {textQualityWarning && (
            <span className="form__warning">
              {textQualityWarning}
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