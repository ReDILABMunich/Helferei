type UserMessageProps = {
  text: string;
};

function UserMessage({ text }: UserMessageProps) {
  return (
    <div className="flex justify-end">
      <p className="max-w-full rounded-12 rounded-br-0 bg-brand-300 px-5 py-3 text-body break-words shadow-normal md:max-w-[85%] lg:max-w-[66%]">
        {text}
      </p>
    </div>
  );
}

export default UserMessage;
