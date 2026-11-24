import { useCallback, useEffect, useMemo, useState } from "react";
import { ArrowRight, Check, Clock3, Filter, HeartHandshake, RefreshCw, Search, X } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { api, type MentorProfile, type MentorshipConnection, type MentorshipRequest } from "../../services/api";

type Props = { notify: (message: string) => void };

export default function MentorshipPage({ notify }: Props) {
  const { user } = useAuth();
  const [mentors, setMentors] = useState<MentorProfile[]>([]);
  const [requests, setRequests] = useState<MentorshipRequest[]>([]);
  const [connections, setConnections] = useState<MentorshipConnection[]>([]);
  const [query, setQuery] = useState("");
  const [expertise, setExpertise] = useState("All");
  const [tab, setTab] = useState<"discover" | "requests" | "connections">("discover");
  const [selected, setSelected] = useState<MentorProfile | null>(null);
  const [message, setMessage] = useState("");
  const [goals, setGoals] = useState("");
  const [response, setResponse] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const canRequest = user?.role === "Member";
  const canReview = user?.role === "Mentor" || user?.role === "Programme Administrator";

  const load = useCallback(async () => {
    setError("");
    try {
      const [mentorRows, requestRows, connectionRows] = await Promise.all([
        api.mentorshipMentors(),
        api.mentorshipRequests(),
        api.mentorshipConnections(),
      ]);
      setMentors(mentorRows);
      setRequests(requestRows);
      setConnections(connectionRows);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load mentorship data.");
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  const categories = useMemo(
    () => ["All", ...new Set(mentors.flatMap((m) => m.expertise))],
    [mentors],
  );
  const visible = useMemo(() => mentors.filter((m) => {
    const text = `${m.name} ${m.title} ${m.discipline} ${m.bio} ${m.expertise.join(" ")}`.toLowerCase();
    return text.includes(query.toLowerCase()) && (expertise === "All" || m.expertise.includes(expertise));
  }), [mentors, query, expertise]);

  const submitRequest = async () => {
    if (!selected || message.trim().length < 10) {
      setError("Please provide a message of at least 10 characters.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await api.createMentorshipRequest({ mentor_profile_id: selected.id, message: message.trim(), goals: goals.trim() });
      setSelected(null); setMessage(""); setGoals("");
      await load();
      setTab("requests");
      notify("Mentorship request submitted.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to submit request.");
    } finally { setBusy(false); }
  };

  const decide = async (item: MentorshipRequest, decision: "accepted" | "declined") => {
    setBusy(true); setError("");
    try {
      await api.decideMentorshipRequest(item.id, decision, response);
      setResponse("");
      await load();
      notify(decision === "accepted" ? "Request accepted and connection created." : "Request declined.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update request.");
    } finally { setBusy(false); }
  };

  const cancel = async (id: number) => {
    setBusy(true); setError("");
    try {
      await api.cancelMentorshipRequest(id);
      await load();
      notify("Pending request cancelled.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to cancel request.");
    } finally { setBusy(false); }
  };

  return (
    <section className="mentorship-workflow">
      <div className="mentorship-heading">
        <div>
          <span className="eyebrow">MENTORSHIP NETWORK</span>
          <h1>{canReview ? "Mentorship workspace" : "Find a mentor"}</h1>
          <p>Discover expertise, request guidance and manage mentorship connections.</p>
        </div>
        <button className="outline-button" onClick={() => void load()} disabled={busy}><RefreshCw size={16}/> Refresh</button>
      </div>

      <div className="mentorship-tabs" role="tablist" aria-label="Mentorship sections">
        <button className={tab === "discover" ? "active" : ""} onClick={() => setTab("discover")}>Discover mentors</button>
        <button className={tab === "requests" ? "active" : ""} onClick={() => setTab("requests")}>Requests <span>{requests.length}</span></button>
        <button className={tab === "connections" ? "active" : ""} onClick={() => setTab("connections")}>Connections <span>{connections.length}</span></button>
      </div>

      {error && <div className="mentorship-alert" role="alert">{error}</div>}

      {tab === "discover" && <>
        <div className="mentor-tools">
          <label className="search-input"><Search/><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search mentors, disciplines or interests"/></label>
          <label className="mentorship-filter"><Filter size={16}/><select value={expertise} onChange={(e) => setExpertise(e.target.value)}>{categories.map((c) => <option key={c}>{c}</option>)}</select></label>
        </div>
        <div className="mentor-grid">
          {visible.map((m, i) => <article className="mentor-card" key={m.id}>
            <div className={`mentor-avatar avatar-${i % 3}`}>{m.name.split(/\s+/).map((x) => x[0]).join("").slice(0,2).toUpperCase()}</div>
            <span className="verified"><Check size={13}/> {m.accepting_requests ? "Accepting requests" : "Not accepting requests"}</span>
            <h3>{m.name}</h3><p className="mentor-role">{m.title} · {m.discipline}</p><p>{m.bio}</p>
            <div className="tag-row">{m.expertise.map((tag) => <span key={tag}>{tag}</span>)}</div>
            <small className="mentorship-institution">{m.institution}</small>
            {canRequest && <button className="primary-button" disabled={!m.accepting_requests} onClick={() => { setSelected(m); setError(""); }}>Request mentorship <ArrowRight size={15}/></button>}
          </article>)}
          {visible.length === 0 && <div className="mentorship-empty">No mentor profiles match these filters.</div>}
        </div>
      </>}

      {tab === "requests" && <div className="mentorship-record-list">
        {requests.length === 0 && <div className="mentorship-empty">No mentorship requests yet.</div>}
        {requests.map((item) => <article className="mentorship-record" key={item.id}>
          <div className="mentorship-record-head"><div><span className="eyebrow">REQUEST #{item.id}</span><h3>{canReview ? item.member_name : item.mentor_name}</h3></div><span className={`mentorship-status status-${item.status}`}>{item.status}</span></div>
          <p>{item.message}</p>{item.goals && <p><b>Goals:</b> {item.goals}</p>}
          {item.mentor_response && <p><b>Mentor response:</b> {item.mentor_response}</p>}
          <small><Clock3 size={13}/> {new Date(item.created_at).toLocaleString()}</small>
          {canReview && item.status === "pending" && <div className="mentorship-decision">
            <input value={response} onChange={(e) => setResponse(e.target.value)} placeholder="Optional response to the member"/>
            <button className="primary-button" disabled={busy} onClick={() => void decide(item, "accepted")}>Accept</button>
            <button className="outline-button" disabled={busy} onClick={() => void decide(item, "declined")}>Decline</button>
          </div>}
          {canRequest && item.status === "pending" && <button className="text-action" disabled={busy} onClick={() => void cancel(item.id)}>Cancel request <X size={14}/></button>}
        </article>)}
      </div>}

      {tab === "connections" && <div className="mentorship-record-list">
        {connections.length === 0 && <div className="mentorship-empty">No active mentorship connections yet. Accepted requests will appear here.</div>}
        {connections.map((c) => <article className="mentorship-record" key={c.id}>
          <div className="mentorship-record-head"><div><span className="eyebrow">CONNECTION #{c.id}</span><h3>{canReview ? c.member_name : c.mentor_name}</h3></div><span className="mentorship-status status-active">{c.status}</span></div>
          <p><HeartHandshake size={16}/> {c.member_name} ↔ {c.mentor_name}</p>
          <small>Created {new Date(c.created_at).toLocaleDateString()}</small>
        </article>)}
      </div>}

      {selected && <div className="mentorship-modal-backdrop" role="presentation" onClick={() => setSelected(null)}>
        <div className="mentorship-modal" role="dialog" aria-modal="true" aria-labelledby="mentorship-request-title" onClick={(e) => e.stopPropagation()}>
          <div className="mentorship-record-head"><div><span className="eyebrow">NEW REQUEST</span><h2 id="mentorship-request-title">{selected.name}</h2></div><button className="icon-button" onClick={() => setSelected(null)} aria-label="Close"><X/></button></div>
          <p>{selected.title} · {selected.discipline}</p>
          <label>Your message<textarea rows={4} maxLength={2000} value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Introduce yourself and explain why you would like this mentorship."/></label>
          <label>What would you like to achieve?<textarea rows={3} maxLength={1000} value={goals} onChange={(e) => setGoals(e.target.value)} placeholder="Describe your learning or career goals."/></label>
          <div className="mentorship-modal-actions"><button className="outline-button" onClick={() => setSelected(null)}>Cancel</button><button className="primary-button" disabled={busy || message.trim().length < 10} onClick={() => void submitRequest()}>{busy ? "Submitting…" : "Send request"}</button></div>
        </div>
      </div>}
    </section>
  );
}
