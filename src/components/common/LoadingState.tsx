export default function LoadingState({ label = "Loading…" }: { label?: string }) {
  return <div className="metric-disclaimer" role="status">{label}</div>;
}
