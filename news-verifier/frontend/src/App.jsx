import VerificationForm from './components/VerificationForm.jsx';
import VerificationResult from './components/VerificationResult.jsx';
import useNewsVerification from './hooks/useNewsVerification.js';
import './App.css';

export default function App() {
  const {
    verifyNews,
    result,
    status,
    reset,
    lastRequest
  } = useNewsVerification();

  return (
    <div className="app">
      {/* Header Minimalista */}
      <header className="header">
        <div className="header__content">
          <h1 className="header__title">NewsTrust</h1>
          <p className="header__subtitle">
            Verificador de Veracidade de Notícias com IA
          </p>
        </div>
      </header>

      {/* Conteúdo Principal */}
      <main className="main">
        <div className="container">
          {/* Verificador */}
          <section className="verifier">
            <VerificationForm 
              status={status} 
              onSubmit={verifyNews} 
              onReset={reset} 
              lastRequest={lastRequest} 
            />
            <VerificationResult status={status} result={result} />
          </section>

          {/* Como Utilizar */}
          <section className="how-to">
            <h2>Como utilizar</h2>
            <ol className="how-to__list">
              <li>
                Escolha <strong>URL</strong> ou <strong>Texto</strong> e cole o conteúdo.
              </li>
              <li>
                Clique em <strong>Verificar notícia</strong>.
              </li>
              <li>
                Veja o percentual, confiança e fontes à direita.
              </li>
              <li>
                Abra as fontes para checar os detalhes.
              </li>
            </ol>
          </section>
        </div>
      </main>

      {/* Footer Minimalista */}
      <footer className="footer">
        <p>
          NewsTrust © {new Date().getFullYear()} • Verificação com IA e Fontes Confiáveis
        </p>
      </footer>
    </div>
  );
}