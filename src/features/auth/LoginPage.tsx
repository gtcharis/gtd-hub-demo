import { useState, type FormEvent } from "react";
import { ArrowLeft, ArrowRight, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck } from "lucide-react";
import { Brand } from "../../pages/ScreenComponents";
import { useAuth } from "./AuthContext";

export default function LoginPage({ onBack, onSuccess }: { onBack: () => void; onSuccess: (user: import("./authTypes").AuthUser) => void }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function signIn() {
    if (busy) return;
    setError("");
    setBusy(true);
    try {
      const signedInUser = await login(email.trim(), password);
      onSuccess(signedInUser);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void signIn();
  }

  return (
    <main className="auth-screen">
      <div className="auth-card">
        <button className="back-link" onClick={onBack}><ArrowLeft size={17} /> Back to welcome</button>
        <Brand />
        <p className="eyebrow">WELCOME BACK</p>
        <h1>Sign in to GTD Hub</h1>
        <p className="lead">Use your assigned account to access your organisation's workspace.</p>
        <form className="auth-form" onSubmit={submit}>
          <label htmlFor="auth-email">Email address</label>
          <div className="auth-input-wrap"><Mail size={18}/><input id="auth-email" type="email" autoComplete="username" required value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.org"/></div>
          <label htmlFor="auth-password">Password</label>
          <div className="auth-input-wrap"><LockKeyhole size={18}/><input id="auth-password" type={showPassword ? "text" : "password"} autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} placeholder="Enter your password"/><button type="button" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword(v => !v)}>{showPassword ? <EyeOff size={18}/> : <Eye size={18}/>}</button></div>
          {error && <div className="auth-error" role="alert">{error}</div>}
          <button className="primary-button auth-submit" type="button" disabled={busy} onClick={() => void signIn()}>{busy ? "Signing in…" : "Sign in"} <ArrowRight size={18}/></button>
        </form>
        <div className="auth-assurance"><ShieldCheck size={17}/> Your access is determined by your assigned account permissions.</div>
        <p className="auth-demo-note">Proposal demonstrator · Fictional accounts only</p>
      </div>
    </main>
  );
}
