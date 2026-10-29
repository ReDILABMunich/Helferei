type UserMessageProps = {
  text: string;
};

function UserMessage({ text }: UserMessageProps) {
  return <p>{text}</p>;
}

export default UserMessage;
