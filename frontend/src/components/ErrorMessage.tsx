import { en } from "../content/en";

function ErrorMessage() {
  return (
    <div role="alert">
      <p>{en.error.title}</p>
      <p>{en.error.body}</p>
    </div>
  );
}

export default ErrorMessage;
