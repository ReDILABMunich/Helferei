type UserMessageProps = {
  text: string;
};

function UserMessage({ text }: UserMessageProps) {
  return (
    <p className="self-end min-w-50 max-w-150 p-5 bg-brand-300 shadow-small rounded-16 rounded-br-0 text-neutral-900 wrap-anywhere">
      {text}
    </p>
  );
}

export default UserMessage;
