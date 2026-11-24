type ToastProps = { message: string; onDismiss?: () => void };
export default function Toast({ message, onDismiss }: ToastProps) {
  if (!message) return null;
  return <div className="toast" role="status" onClick={onDismiss}>{message}</div>;
}
