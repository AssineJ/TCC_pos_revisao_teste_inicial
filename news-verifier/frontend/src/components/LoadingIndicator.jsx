export default function LoadingIndicator({ message }) {
  return (
    <div className="loading">
      <div className="loading__spinner">
        {Array.from({ length: 12 }).map((_, index) => (
          <span key={index} style={{ '--index': index }} />
        ))}
      </div>
      <div className="loading__text">
        <strong>Verificando autenticidade</strong>
        <p>{message}</p>
      </div>
    </div>
  );
}