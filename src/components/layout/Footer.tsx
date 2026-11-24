import { Zap } from "lucide-react";

export default function Footer({ onQuickExit }: { onQuickExit: () => void }) {
  return (
    <footer className="app-footer">
      <img
        className="footer-partner-logo"
        src={`${import.meta.env.BASE_URL}brand/progen-gtdhub-footer.png`}
        alt="PROGEN-Hub for STEM and GTD Hub"
      />
      <span className="footer-accessibility-note">
        Responsive · Mobile-first · WCAG 2.1 AA design target
      </span>
      <button onClick={onQuickExit}>
        <Zap size={14} /> Quick Exit
      </button>
    </footer>
  );
}
