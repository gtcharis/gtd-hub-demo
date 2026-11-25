
import { useState, type FormEvent } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ShieldCheck,
  Users,
  Copy,
  Check,
} from "lucide-react";
import { Brand } from "../../pages/ScreenComponents";
import { useAuth } from "./AuthContext";

const DEMO_PASSWORD = "ChangeThisDemoPassword!";

const DEMO_ACCOUNTS = [
  { role: "Member", email: "member@gtdhub.demo" },
  { role: "Mentor", email: "mentor@gtdhub.demo" },
  { role: "Moderator", email: "moderator@gtdhub.demo" },
  { role: "Case Handler", email: "casehandler@gtdhub.demo" },
  { role: "Organisation Administrator", email: "orgadmin@gtdhub.demo" },
  { role: "Programme Administrator", email: "programmeadmin@gtdhub.demo" },
];

export default function LoginPage({
  onBack,
  onSuccess,
}: {
  onBack: () => void;
  onSuccess: (user: import("./authTypes").AuthUser) => void;
}) {
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showDemoPassword, setShowDemoPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  async function signIn() {
    if (busy) return;

    setError("");
    setBusy(true);

    try {
      const signedInUser = await login(email.trim(), password);
      onSuccess(signedInUser);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to sign in. Please try again.",
      );
    } finally {
      setBusy(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void signIn();
  }

  function selectDemoAccount(accountEmail: string) {
    setEmail(accountEmail);
    setPassword(DEMO_PASSWORD);
    setError("");
  }

  async function copyDemoPassword() {
    try {
      await navigator.clipboard.writeText(DEMO_PASSWORD);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setShowDemoPassword(true);
    }
  }

  return (
    <main className="auth-screen">
      <div className="auth-card">
        <button className="back-link" onClick={onBack}>
          <ArrowLeft size={17} /> Back to welcome
        </button>

        <Brand />

        <p className="eyebrow">WELCOME BACK</p>
        <h1>Sign in to GTD Hub</h1>

        <p className="lead">
          Use your assigned account to access your organisation's workspace.
        </p>

        <form className="auth-form" onSubmit={submit}>
          <label htmlFor="auth-email">Email address</label>

          <div className="auth-input-wrap">
            <Mail size={18} />
            <input
              id="auth-email"
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.org"
            />
          </div>

          <label htmlFor="auth-password">Password</label>

          <div className="auth-input-wrap">
            <LockKeyhole size={18} />
            <input
              id="auth-password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
            />
            <button
              type="button"
              aria-label={showPassword ? "Hide password" : "Show password"}
              onClick={() => setShowPassword((v) => !v)}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {error && (
            <div className="auth-error" role="alert">
              {error}
            </div>
          )}

          <button
            className="primary-button auth-submit"
            type="submit"
            disabled={busy}
          >
            {busy ? "Signing in…" : "Sign in"} <ArrowRight size={18} />
          </button>
        </form>

        <div className="auth-assurance">
          <ShieldCheck size={17} />
          Your access is determined by your assigned account permissions.
        </div>

        {/* Demonstration account access */}
        <section className="auth-demo-access">
          <div className="auth-demo-heading">
            <div className="auth-demo-icon">
              <Users size={19} />
            </div>
            <div>
              <h2>Demonstration Accounts</h2>
              <p>Explore the platform using the accounts below.</p>
            </div>
          </div>

          <div className="auth-demo-password">
            <div>
              <span className="auth-demo-label">Shared demo password</span>
              <strong>
                {showDemoPassword
                  ? DEMO_PASSWORD
                  : "••••••••••••••••••"}
              </strong>
            </div>

            <div className="auth-demo-password-actions">
              <button
                type="button"
                onClick={() => setShowDemoPassword((v) => !v)}
                aria-label={
                  showDemoPassword ? "Hide demo password" : "Show demo password"
                }
              >
                {showDemoPassword ? <EyeOff size={17} /> : <Eye size={17} />}
              </button>

              <button
                type="button"
                onClick={() => void copyDemoPassword()}
                aria-label="Copy demo password"
              >
                {copied ? <Check size={17} /> : <Copy size={17} />}
              </button>
            </div>
          </div>

          <div className="auth-demo-account-list">
            {DEMO_ACCOUNTS.map((account) => (
              <div className="auth-demo-account" key={account.email}>
                <div className="auth-demo-account-info">
                  <strong>{account.role}</strong>
                  <span>{account.email}</span>
                </div>

                <button
                  type="button"
                  className="auth-demo-select"
                  onClick={() => selectDemoAccount(account.email)}
                >
                  Use account
                </button>
              </div>
            ))}
          </div>

          <p className="auth-demo-disclaimer">
            These are fictional demonstration accounts for evaluation purposes.
            Please do not enter real personal or sensitive information.
          </p>
        </section>

        <p className="auth-demo-note">
          Proposal demonstrator · Fictional accounts only
        </p>
      </div>
    </main>
  );
}
