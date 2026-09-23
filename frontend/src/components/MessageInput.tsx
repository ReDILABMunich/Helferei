type MessageInputProps = {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled: boolean;
};

function MessageInput({ value, onChange, onSend, disabled }: MessageInputProps) {
  return (
    <div className="message-input">
      <input
        placeholder="Type a message"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      <button onClick={onSend} disabled={disabled}>
        Send
      </button>
    </div>
  );
}

export default MessageInput;
