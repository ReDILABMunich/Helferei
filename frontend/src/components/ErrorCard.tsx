type ErrorCardProps = {
  text: string;
  onRetry: () => void;
};

function ErrorCard({ text, onRetry }: ErrorCardProps) {
  return (
    <p className="error-card">
      {text} <button onClick={onRetry}>Try again</button>
    </p>
  );
}

export default ErrorCard;
