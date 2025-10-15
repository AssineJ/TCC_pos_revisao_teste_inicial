import { useState } from 'react';
import { FiExternalLink, FiInfo, FiShield } from 'react-icons/fi';
import VerificationForm from './components/VerificationForm.jsx';
import VerificationResult from './components/VerificationResult.jsx';
import useNewsVerification from './hooks/useNewsVerification.js';
import './App.css';

const FEATURE_HIGHLIGHTS = [
  {
    icon: <FiShield />,
    title: 'Verificação Inteligente',
    description: 'Combina análise textual, comparação com fontes confiáveis e heurísticas de veracidade para entregar resultados consistentes.'
  },
  {
    icon: <FiInfo />,
    title: 'Insights Transparentes',
    description: 'Receba justificativas claras, links de apoio e recomendações para aprofundar a apuração da notícia.'
  },
  {
    icon: <FiExternalLink />,
    title: 'Pronto para Integrar',
    description: 'Arquitetura pensada para evoluir com IA, banco de dados e integração contínua com o backend existente.'
  }
];

export default function App() {
  const [showFeatures, setShowFeatures] = useState(false);
  const {
    verifyNews,
    result,
    status,
    reset,
    lastRequest
  } = useNewsVerification();

  return (
    <div className="page">
      <header className="hero">
        <div className="hero__content">
          <span className="hero__pill">NewsTrust Platform</span>
          <h1>
            Avalie a veracidade de notícias com uma experiência interativa e confiável.
          </h1>
          <p>
            Insira a URL ou o texto da notícia e receba uma análise instantânea com percentual de confiança, justificativas detalhadas e links de apoio.
          </p>
          <div className="hero__actions">
            <button className="primary" onClick={() => setShowFeatures(true)}>
              Conheça os recursos
            </button>
            <a className="secondary" href="#verifier">
              Começar agora
            </a>
          </div>
        </div>
        <div className="hero__visual" aria-hidden>
          <div className={`orb ${status === 'loading' ? 'orb--pulse' : ''}`}>
            <div className="orb__glow" />
            <div className="orb__core">
              <span>{status === 'loading' ? 'Analisando...' : 'NewsTrust'}</span>
            </div>
          </div>
        </div>
      </header>

      <main>
        <section id="verifier" className="verifier">
          <VerificationForm status={status} onSubmit={verifyNews} onReset={reset} lastRequest={lastRequest} />
          <VerificationResult status={status} result={result} />
        </section>

        <section className={`features ${showFeatures ? 'features--visible' : ''}`}>
          <h2>Por que usar o NewsTrust?</h2>
          <div className="features__grid">
            {FEATURE_HIGHLIGHTS.map(({ icon, title, description }) => (
              <article key={title} className="feature-card">
                <div className="feature-card__icon">{icon}</div>
                <h3>{title}</h3>
                <p>{description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="cta">
          <h2>Pronto para levar a validação ao próximo nível?</h2>
          <p>
            O backend já está preparado para receber integrações avançadas. Implante esta interface em qualquer serviço de hospedagem estática e conecte-se ao seu webservice para entregar confiança ao usuário final.
          </p>
          <a className="primary" href="mailto:contato@newstrust.ai">Fale com a equipe</a>
        </section>
      </main>

      <footer>
        <p>
          Desenvolvido como parte da plataforma NewsTrust. Conecte-se ao backend FastAPI para resultados em tempo real.
        </p>
      </footer>
    </div>
  );
}