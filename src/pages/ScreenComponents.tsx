import { useEffect, useMemo, useState, type FormEvent } from "react";
import {
  Activity,
  ArrowLeft,
  ArrowRight,
  Bell,
  BookOpen,
  BriefcaseBusiness,
  Building2,
  CalendarDays,
  Check,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  ClipboardList,
  FileText,
  Filter,
  GraduationCap,
  Handshake,
  Heart,
  HeartHandshake,
  Home,
  Info,
  LifeBuoy,
  LockKeyhole,
  LogOut,
  Menu,
  MessageCircle,
  Search,
  ShieldCheck,
  Users,
  X,
  Zap,
  ChartNoAxesColumnIncreasing,
  Scale,
  Stethoscope,
  BookMarked,
  Settings,
  Landmark,
  UserRound,
  Sparkles,
} from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../features/auth/AuthContext";
import {
  activities,
  cases,
  discussions,
  mentors,
  metrics,
  navByRole,
  organisations,
  roles,
  supportOptions,
  type DemoRole,
} from "../data/demo";


function DownloadIcon() {
  return <ArrowRight size={15} />;
}

export function Brand({ compact = true }: { compact?: boolean }) {
  return (
    <div className="brand">
      <img
        className="brand-image"
        src={`${import.meta.env.BASE_URL}brand/gtdhub.png`}
        alt="GTD Hub"
      />
      {/* {!compact && <small>GENDER-TRANSFORMATIVE DIGITAL HUB</small>} */}
    </div>
  );
}
export function Welcome({ onStart }: { onStart: () => void }) {
  return (
    <div className="entry-screen">
      <div className="entry-top">
        <Brand />
        <span className="demo-pill">DEMO</span>
      </div>
      <div className="entry-hero">
        <div className="entry-copy">
          <p className="eyebrow">CONNECT · SUPPORT · TRANSFORM</p>
          <h1>A safer, more connected space for everyone.</h1>
          <p>
            Explore a concept for support, reporting, mentorship, learning and
            action on gender equality.
          </p>
          <button className="primary-button" onClick={onStart}>
            Sign in to GTD Hub <ArrowRight size={19} />
          </button>
          <div className="demo-warning">
            <Info size={17} /> Proposal demonstrator only. Fictional data. No
            real reporting or live services.
          </div>
        </div>
        <div
          className="entry-people"
          aria-label="Illustration of a diverse group of STEM community members"
        >
          <div className="people-orb orb-a" />
          <div className="people-orb orb-b" />
          <div className="people-caption">Belonging. Opportunity. Change.</div>
        </div>
      </div>
    </div>
  );
}
export function RoleSelection({
  onBack,
  onSelect,
}: {
  onBack: () => void;
  onSelect: (r: DemoRole) => void;
}) {
  const descriptions: Record<DemoRole, string> = {
    Member: "Access support, reporting, mentorship and learning.",
    Mentor: "Guide, support and connect with members.",
    Moderator: "Support safe and respectful community spaces.",
    "Case Handler": "Manage and refer fictional support cases.",
    "Organisation Administrator":
      "Oversee an organisation's GTD Hub workspace.",
    "Programme Administrator": "View programme insights across organisations.",
  };
  const icons = [
    Users,
    GraduationCap,
    ShieldCheck,
    BriefcaseBusiness,
    Landmark,
    ChartNoAxesColumnIncreasing,
  ];
  return (
    <div className="role-screen">
      <button className="back-link" onClick={onBack}>
        <ArrowLeft size={17} /> Back
      </button>
      <Brand />
      <p className="eyebrow mt-10">INTERACTIVE ROLE EXPLORATION</p>
      <h1>Explore GTD Hub as a different user</h1>
      <p className="lead">
        Choose a role to experience the key features and workflows in the demo.
      </p>
      <div className="role-grid">
        {roles.map((r, i) => {
          const Icon = icons[i];
          return (
            <button
              key={r}
              onClick={() => onSelect(r)}
              className={`role-card role-${i}`}
            >
              <Icon size={30} />
              <span>
                <b>{r}</b>
                <small>{descriptions[r]}</small>
              </span>
              <ArrowRight className="role-arrow" />
            </button>
          );
        })}
      </div>
      <div className="demo-warning">
        <Info size={17} /> All accounts, identities and records are fictional.
        This demonstration does not receive real reports.
      </div>
    </div>
  );
}
export function PageTitle({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="page-title">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="lead">{description}</p>
      </div>
      {action}
    </div>
  );
}
export function Dashboard({
  role,
  displayName,
  go,
  notify,
  overview,
  apiState,
}: {
  role: DemoRole;
  displayName: string;
  go: (p: string) => void;
  notify: (s: string) => void;
  overview: any;
  apiState: "local" | "connected" | "unavailable";
}) {
  const member = role === "Member";
  return (
    <div className="space-y-6">
      <section className="welcome-card">
        <div className="welcome-text">
          <p className="eyebrow">MONDAY, 23 NOVEMBER 2026</p>
          <h1>
            Good morning, <em>{displayName.split(" ")[0]}</em> 👋
          </h1>
          <p>
            Welcome to GTD Hub — a safe, inclusive space for support,
            mentorship, learning and action on gender equality in STEM.
          </p>
          <span className="gold-rule" />
        </div>
        <div className="welcome-image">
          <div className="image-placeholder">
            <Users size={76} />
            <span>A connected STEM community</span>
          </div>
        </div>
      </section>
      <section className="metric-grid">
        {metrics.map((m, i) => {
          const Icon = [
            Users,
            Handshake,
            BookOpen,
            ChartNoAxesColumnIncreasing,
          ][i];
          const values = overview
            ? [
                overview.members,
                overview.mentorship_connections,
                overview.resources,
                `${overview.engagement_percent}%`,
              ]
            : null;
          return (
            <div className={`metric-card ${m.tone}`} key={m.label}>
              <Icon size={31} />
              <div>
                <b>{values ? values[i] : m.value}</b>
                <span>{m.label}</span>
              </div>
            </div>
          );
        })}
      </section>
      <div className="metric-disclaimer">
        <Info size={15} /> Metrics are illustrative demonstration data only.{" "}
        {apiState === "connected"
          ? "Read from demo API."
          : apiState === "unavailable"
            ? "API unavailable; local demo data shown."
            : "Local demo data."}
      </div>
      <section className="dashboard-middle">
        <div className="support-hero">
          <ShieldCheck size={48} />
          <div>
            <h2>Need support?</h2>
            <p>Access trusted, confidential and inclusive support services.</p>
            <button className="white-button" onClick={() => go("Find support")}>
              Find support <ArrowRight size={17} />
            </button>
          </div>
        </div>
        <div className="activity-panel">
          <div className="panel-heading">
            <CalendarDays />
            <h2>Upcoming activities</h2>
          </div>
          {activities.map((a) => (
            <div className="activity-row" key={a.title}>
              <div className="date-box">
                <b>{a.month}</b>
                <strong>{a.date}</strong>
              </div>
              <div>
                <b>{a.title}</b>
                <small>{a.meta}</small>
              </div>
              <span className="tag">{a.type}</span>
            </div>
          ))}
        </div>
      </section>
      <section>
        <div className="section-heading">
          <h2>Explore your hub</h2>
          <p>Choose where you would like to begin.</p>
        </div>
        <div className="explore-grid">
          <ExploreCard
            icon={<Users />}
            title="Find a mentor"
            description="Connect with mentors and role models."
            tone="lilac"
            onClick={() => go("Mentorship")}
          />
          <ExploreCard
            icon={<MessageCircle />}
            title="Join the community"
            description="Share, learn and get support from peers."
            tone="cream"
            onClick={() => go("Community")}
          />
          <ExploreCard
            icon={<BookOpen />}
            title="Explore resources"
            description="Guides, toolkits and learning materials."
            tone="mint"
            onClick={() => go("Learning library")}
          />
        </div>
      </section>
      {!member && (
        <div className="notice">
          <Info size={17} /> You are viewing a role-specific demonstration
          workspace for {role}. All metrics and records are fictional.
        </div>
      )}
    </div>
  );
}
export function ExploreCard({
  icon,
  title,
  description,
  tone,
  onClick,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  tone: string;
  onClick: () => void;
}) {
  return (
    <button className={`explore-card ${tone}`} onClick={onClick}>
      <span>{icon}</span>
      <div>
        <b>{title}</b>
        <small>{description}</small>
      </div>
      <ArrowRight size={18} />
    </button>
  );
}
type SupportCategory = {
  id: string;
  title: string;
  description: string;
  icon: typeof Heart;
  tone: string;
  overview: string;
  examples: string[];
  access: string[];
  privacy: string;
  aliases: string[];
};

const supportCategories: SupportCategory[] = [
  {
    id: "psychosocial", title: "Psychosocial Support",
    description: "Counselling, emotional wellbeing and supportive listening.", icon: HeartHandshake, tone: "lilac",
    overview: "Psychosocial support can help someone talk through a difficult experience, understand their options and identify support that feels appropriate to them. The type and availability of services varies by institution and provider.",
    examples: ["Individual counselling and supportive listening", "Wellbeing support and coping strategies", "Information about specialist or trauma-informed services", "Peer-support options where these are established and appropriately facilitated"],
    access: ["Check the institution's verified student or staff support channels.", "Ask what the service offers, how appointments are arranged and whether there are any eligibility requirements.", "You can ask questions about confidentiality before deciding whether to proceed."],
    privacy: "Confidentiality arrangements and any limits should be explained by the service provider before you share personal information.",
    aliases: ["psychosocial", "counselling", "wellbeing", "mental health"]
  },
  {
    id: "health", title: "Health Services",
    description: "General, reproductive, sexual and other health information and care.", icon: Stethoscope, tone: "mint",
    overview: "Health services may provide assessment, treatment, health information and referrals. The services available, costs, eligibility and opening hours depend on the provider.",
    examples: ["General health consultations", "Sexual and reproductive health information and services", "Clinical assessment and follow-up care", "Referral to an appropriate health professional"],
    access: ["Use a verified institutional clinic or recognised health provider.", "Confirm availability, fees, opening hours and whether an appointment is needed.", "For urgent medical needs, seek in-person medical assistance rather than relying on this directory."],
    privacy: "Ask the provider how health information is recorded, who can access it and how confidentiality is protected.",
    aliases: ["health", "clinic", "medical", "reproductive", "sexual health"]
  },
  {
    id: "legal", title: "Legal Information & Assistance",
    description: "General information about rights, options and access to legal advice.", icon: Scale, tone: "cream",
    overview: "Legal support can help a person understand relevant rights, procedures and possible options. This directory provides general information only and is not legal advice.",
    examples: ["General information about rights and available procedures", "Access to legal aid or an independent legal adviser", "Information about formal reporting options", "Guidance on where to seek qualified legal assistance"],
    access: ["Seek advice from a qualified legal practitioner or verified legal-aid provider.", "Ask whether the service is free, confidential and available to your circumstances.", "You can seek information without deciding to make a formal complaint."],
    privacy: "Before sharing details, ask the adviser about confidentiality, record keeping and any legal limits on disclosure.",
    aliases: ["legal", "law", "rights", "legal aid", "lawyer"]
  },
  {
    id: "institutional", title: "Institutional Support",
    description: "Campus support offices, student services and designated institutional contacts.", icon: Building2, tone: "blue",
    overview: "Each participating higher education institution is responsible for confirming its own support structures, designated personnel, policies and referral arrangements. The platform does not replace those institutional processes.",
    examples: ["Student affairs and student support offices", "Institutional gender desks or designated focal persons", "Academic support and reasonable study-related assistance", "Information about institutional policies and procedures"],
    access: ["Consult your institution's officially published channels.", "Confirm the correct office and the role of the person receiving an enquiry.", "Ask what information is recorded and what choices are available to you."],
    privacy: "Institution-specific confidentiality, record handling and formal procedures must be explained by the relevant institution.",
    aliases: ["institution", "campus", "student affairs", "gender desk", "university"]
  },
  {
    id: "peer", title: "Peer Support & Mentorship",
    description: "Peer connection, mentoring and supportive STEM communities.", icon: Users, tone: "teal",
    overview: "Peer and mentorship spaces can provide connection, encouragement and shared learning. They are not substitutes for professional health, legal or safeguarding services.",
    examples: ["Peer learning and support groups", "Mentorship and champion networks", "STEM community activities", "Signposting to appropriate professional support"],
    access: ["Check the programme or institution's available groups and mentorship opportunities.", "Review participation guidelines and expectations before joining.", "Avoid sharing another person's private information in group spaces."],
    privacy: "Peer settings may not provide the same confidentiality as professional services. Share only what you are comfortable sharing.",
    aliases: ["peer", "mentorship", "mentor", "champion", "community", "student group"]
  }
];

export function Support({ notify }: { notify: (s: string) => void }) {
  const [directory, setDirectory] = useState<Array<{ id: number; category: string; title: string; description: string; contact_label: string | null; institution_id?: number | null }>>([]);
  const [directoryState, setDirectoryState] = useState<"loading" | "loaded" | "unavailable">("loading");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  useEffect(() => {
    let active = true;
    api.supportServices().then(rows => { if (active) { setDirectory(rows); setDirectoryState("loaded"); } })
      .catch(() => { if (active) setDirectoryState("unavailable"); });
    return () => { active = false; };
  }, []);
  const filtered = useMemo(() => supportCategories.filter(category => {
    const haystack = [category.title, category.description, category.overview, ...category.examples, ...category.aliases].join(" ").toLowerCase();
    return haystack.includes(query.trim().toLowerCase());
  }), [query]);
  const serviceCategoryMatches = (serviceCategory: string, category: SupportCategory) => {
    const value = serviceCategory.toLowerCase();
    return category.aliases.some(alias => value.includes(alias) || alias.includes(value));
  };
  return (
    <>
      <PageTitle eyebrow="SUPPORT DIRECTORY" title="Find support" description="Explore different kinds of support, understand what they may offer and decide what, if anything, you would like to do next." />
      <div className="notice">
        <ShieldCheck />
        <div><b>You are in control.</b><p>This is a proposal demonstrator. Service descriptions are general information; live contacts, eligibility, availability and referral pathways must be verified by each participating institution before publication.</p></div>
      </div>
      <div className="support-directory-tools">
        <label className="support-search"><Search size={18} /><input aria-label="Search support information" value={query} onChange={e => setQuery(e.target.value)} placeholder="Search support topics, services or rights" /></label>
        <span>{filtered.length} support {filtered.length === 1 ? "category" : "categories"}</span>
      </div>
      {filtered.length === 0 && <div className="empty-state"><Search size={24}/><b>No matching support topics</b><p>Try a different search term or clear your search.</p><button className="text-action" onClick={() => setQuery("")}>Clear search</button></div>}
      <div className="support-category-list">
        {filtered.map(category => {
          const Icon = category.icon;
          const isOpen = expanded === category.id;
          const services = directory.filter(service => serviceCategoryMatches(service.category, category));
          return <article className={`support-category ${category.tone} ${isOpen ? "is-expanded" : ""}`} key={category.id}>
            <button className="support-category-trigger" aria-expanded={isOpen} aria-controls={`support-detail-${category.id}`} onClick={() => setExpanded(isOpen ? null : category.id)}>
              <span className="support-category-icon"><Icon size={30}/></span>
              <span className="support-category-copy"><b>{category.title}</b><small>{category.description}</small><em>{isOpen ? "Hide information" : "View information"} <ArrowRight size={15}/></em></span>
              <ChevronDown className="support-chevron" size={19}/>
            </button>
            {isOpen && <div className="support-category-detail" id={`support-detail-${category.id}`}>
              <p>{category.overview}</p>
              <h4>What this may include</h4>
              <ul>{category.examples.map(item => <li key={item}>{item}</li>)}</ul>
              <h4>How to explore this support</h4>
              <ol>{category.access.map(item => <li key={item}>{item}</li>)}</ol>
              <div className="support-privacy-note"><ShieldCheck size={17}/><span><b>Privacy to consider</b>{category.privacy}</span></div>
              {services.length > 0 && <div className="support-published-services"><h4>Illustrative directory listings</h4>{services.map(service => <div className="support-service-entry" key={service.id}><b>{service.title}</b><p>{service.description}</p><small>{service.contact_label || "Contact and access details pending institutional verification"}</small><span>Illustrative entry · Institution verification pending</span></div>)}</div>}
            </div>}
          </article>;
        })}
      </div>
      {directoryState === "loading" && <p className="support-api-status">Loading institution directory listings…</p>}
      {directoryState === "unavailable" && <p className="support-api-status">Institution-specific listings are currently unavailable. General support information remains available above.</p>}
      <section className="emergency-card support-emergency">
        <div className="emergency-symbol"><LifeBuoy size={29}/></div>
        <div><b>Immediate danger or urgent medical need?</b><p>If you are in immediate danger, seek help from local emergency services or a trusted person. For urgent medical needs, go to an appropriate health facility. This demonstrator does not provide emergency response and its contacts have not been verified.</p></div>
        <button onClick={() => notify("Emergency contacts and escalation guidance must be confirmed by the project team and participating institutions before operational publication.")}>Read guidance <ArrowRight size={16}/></button>
      </section>
      <p className="support-footer-note">You do not have to use the reporting feature to read support information. Exploring these options does not submit a report or contact a service.</p>
    </>
  );
}

export function Reporting({
  step,
  setStep,
  anonymous,
  setAnonymous,
  consent,
  setConsent,
  notify,
  institutionId,
  submittedCaseRef,
  setSubmittedCaseRef,
}: {
  step: number;
  setStep: (n: number) => void;
  anonymous: boolean;
  setAnonymous: (v: boolean) => void;
  consent: boolean;
  setConsent: (v: boolean) => void;
  notify: (s: string) => void;
  institutionId?: number;
  submittedCaseRef: string;
  setSubmittedCaseRef: (v: string) => void;
}) {
  const [submitting, setSubmitting] = useState(false);
  const steps = ["Your choice", "Your options", "Review", "Confirmation"];
  return (
    <>
      <PageTitle
        eyebrow="SAFE REPORTING · CONCEPT JOURNEY"
        title="Make a report"
        description="Explore how a person could understand reporting options and make informed choices."
        action={
          <button
            className="outline-button"
            onClick={() => {
              setStep(0);
              setAnonymous(true);
              setConsent(false);
              setSubmittedCaseRef("");
            }}
          >
            Reset journey
          </button>
        }
      />
      <div className="notice warning">
        <LockKeyhole />
        <div>
          <b>Fictional demonstration only</b>
          <p>
            Do not enter real names, contact details, incidents or personal
            experiences. Only a predefined synthetic scenario is submitted to the encrypted demonstration API.
          </p>
        </div>
      </div>
      <div className="report-layout">
        <section className="report-card">
          <div className="stepper">
            {steps.map((s, i) => (
              <div
                className={step === i ? "current" : step > i ? "done" : ""}
                key={s}
              >
                <span>{step > i ? <Check size={14} /> : i + 1}</span>
                <small>{s}</small>
              </div>
            ))}
          </div>
          {step === 0 && (
            <div className="report-step">
              <div className="report-art">
                <ShieldCheck size={62} />
                <FileText size={48} />
              </div>
              <h2>Choose how you would like to proceed</h2>
              <p>
                Choose an account-linked or unlinked synthetic demonstration record. The demo does not accept real disclosures or free-text details.
              </p>
              <button
                className={`choice-row ${anonymous ? "chosen" : ""}`}
                onClick={() => setAnonymous(true)}
              >
                <span className="radio-dot" />
                <span>
                  <b>Anonymous report</b>
                  <small>The case record is not linked to your account. Network or device metadata may still exist outside the case record.</small>
                </span>
                <UserRound />
              </button>
              <button
                className={`choice-row ${!anonymous ? "chosen" : ""}`}
                onClick={() => setAnonymous(false)}
              >
                <span className="radio-dot" />
                <span>
                  <b>Identified report</b>
                  <small>
                    Explore a route where a case handler could follow up,
                    subject to consent and approved protocols.
                  </small>
                </span>
                <UserRound />
              </button>
            </div>
          )}
          {step === 1 && (
            <div className="report-step">
              <h2>
                {anonymous
                  ? "Understand the anonymous pathway"
                  : "Understand the identified pathway"}
              </h2>
              <p>This is a conceptual explanation, not a live intake form.</p>
              <div className="pathway-box">
                <b>1. Share only what you choose</b>
                <p>
                  A future service would explain what information is requested
                  and why.
                </p>
              </div>
              <div className="pathway-box">
                <b>2. Review available support options</b>
                <p>
                  Support information and referral choices would be shown before
                  any sharing.
                </p>
              </div>
              <label className="consent-row">
                <input
                  type="checkbox"
                  checked={consent}
                  onChange={(e) => setConsent(e.target.checked)}
                />
                <span>
                  <b>Demonstration consent choice</b>
                  <small>
                    Simulate choosing whether information may be shared for
                    referral. This setting has no real effect.
                  </small>
                </span>
              </label>
            </div>
          )}
          {step === 2 && (
            <div className="report-step">
              <h2>Review your demonstration choices</h2>
              <p>
                No incident details or personal information are collected in
                this prototype.
              </p>
              <div className="review-row">
                <span>Reporting route</span>
                <b>{anonymous ? "Anonymous" : "Identified"}</b>
              </div>
              <div className="review-row">
                <span>Referral sharing choice</span>
                <b>{consent ? "Consent indicated" : "No consent indicated"}</b>
              </div>
              <div className="notice">
                <Info />
                <p>
                  In the proposed production system, human safeguarding
                  personnel would make triage and referral decisions under
                  approved protocols. The software would not make those
                  decisions.
                </p>
              </div>
            </div>
          )}
          {step === 3 && (
            <div className="report-step success">
              <div className="success-icon">
                <Check size={35} />
              </div>
              <h2>Demonstration journey complete</h2>
              <p>
                A predefined synthetic demonstration scenario has been submitted and encrypted by the API. No free-text narrative or real contact details are accepted.
              </p>
              {submittedCaseRef && <div className="review-row"><span>Demonstration reference</span><b>{submittedCaseRef}</b></div>}
              <button
                className="primary-button"
                onClick={() => {
                  setStep(0);
                  setConsent(false);
                  setAnonymous(true);
                  setSubmittedCaseRef("");
                }}
              >
                Explore again <ArrowRight size={17} />
              </button>
            </div>
          )}
          <div className="step-actions">
            {step > 0 && step < 3 && (
              <button
                className="outline-button"
                onClick={() => setStep(step - 1)}
              >
                Back
              </button>
            )}
            {step < 3 && (
              <button
                className="primary-button"
                disabled={submitting}
                onClick={async () => {
                  if (step !== 2) { setStep(step + 1); return; }
                  if (!institutionId) { notify("This account has no institution assignment. A synthetic case cannot be submitted."); return; }
                  setSubmitting(true);
                  try {
                    const result = await api.createDemoCase({ institution_id: institutionId, scenario_code: "SCENARIO_SUPPORT", anonymous, consent_to_referral: consent });
                    setSubmittedCaseRef(result.case_ref);
                    setStep(3);
                    notify("Synthetic demonstration case encrypted and recorded.");
                  } catch (error) {
                    notify(error instanceof Error ? error.message : "The demonstration case could not be submitted.");
                  } finally { setSubmitting(false); }
                }}
              >
                {submitting ? "Submitting…" : step === 2 ? "Submit synthetic demo" : "Continue"}{" "}
                <ArrowRight size={17} />
              </button>
            )}
          </div>
        </section>
        <aside className="report-aside">
          <div className="aside-card">
            <ShieldCheck size={30} />
            <h3>Your safety and choices matter</h3>
            <p>
              The demonstrator records a consent choice and requires an authorised human handler for workflow actions. It does not make safeguarding decisions.
            </p>
          </div>
          <div className="aside-card">
            <HeartHandshake size={29} />
            <h3>Support is available</h3>
            <p>
              You can explore the support directory without starting a reporting
              journey.
            </p>
            <button
              className="text-action"
              onClick={() =>
                notify(
                  "Choose Find support from the navigation to explore the sample directory.",
                )
              }
            >
              Explore support <ArrowRight size={15} />
            </button>
          </div>
        </aside>
      </div>
    </>
  );
}
export function Mentorship({
  query,
  setQuery,
  activeTab,
  setActiveTab,
  list,
  listSource,
  requested,
  setRequested,
  notify,
}: {
  query: string;
  setQuery: (v: string) => void;
  activeTab: string;
  setActiveTab: (v: string) => void;
  list: typeof mentors;
  listSource: "local" | "connected" | "unavailable";
  requested: string[];
  setRequested: (v: string[]) => void;
  notify: (s: string) => void;
}) {
  const filters = [
    "All",
    "Research",
    "Career",
    "Academic",
    "Leadership",
    "Wellbeing",
  ];
  return (
    <>
      <PageTitle
        eyebrow="MENTORSHIP NETWORK"
        title="Find a mentor"
        description="Discover people who can share experience, encouragement and guidance."
      />
      <div className="mentor-tools">
        <label className="search-input">
          <Search />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search mentors, disciplines or interests"
          />
        </label>
        <button className="outline-button" onClick={() => setActiveTab("All")}>
          <Filter size={16} /> Clear filters
        </button>
      </div>
      <div className="filter-pills">
        {filters.map((f) => (
          <button
            key={f}
            className={activeTab === f ? "active" : ""}
            onClick={() => setActiveTab(f)}
          >
            {f}
          </button>
        ))}
      </div>
      <div className="metric-disclaimer">
        <Info size={15} />
        {listSource === "connected"
          ? "Mentor profiles loaded from the demonstration API."
          : listSource === "unavailable"
            ? "API unavailable; displaying local fictional mentor profiles."
            : "Displaying local fictional mentor profiles."}
      </div>
      <div className="mentor-grid">
        {list.map((m, i) => (
          <article className="mentor-card" key={m.id}>
            <div className={`mentor-avatar avatar-${i}`}>{m.initials}</div>
            <span className="verified">
              <Check size={13} /> Demo profile
            </span>
            <h3>{m.name}</h3>
            <p className="mentor-role">{m.role}</p>
            <p>{m.bio}</p>
            <div className="tag-row">
              {m.tags.map((t) => (
                <span key={t}>{t}</span>
              ))}
            </div>
            <button
              className={
                requested.includes(m.id) ? "outline-button" : "primary-button"
              }
              onClick={() => {
                setRequested(
                  requested.includes(m.id)
                    ? requested.filter((x) => x !== m.id)
                    : [...requested, m.id],
                );
                notify("Demo connection preference updated locally only.");
              }}
            >
              {requested.includes(m.id)
                ? "Request noted"
                : "Explore connection"}{" "}
              <ArrowRight size={15} />
            </button>
          </article>
        ))}
      </div>
    </>
  );
}
export function Community({ notify }: { notify: (s: string) => void }) {
  return (
    <>
      <PageTitle
        eyebrow="PEER COMMUNITY"
        title="Join the conversation"
        description="Explore supportive spaces for sharing ideas, learning and connection."
        action={
          <button
            className="primary-button"
            onClick={() =>
              notify("Posting is disabled in this proposal demonstrator.")
            }
          >
            Start a discussion <ArrowRight size={16} />
          </button>
        }
      />
      <div className="community-layout">
        <div className="discussion-list">
          {discussions.map((d) => (
            <article className="discussion-card" key={d.title}>
              <div className="discussion-avatar">{d.author.slice(0, 1)}</div>
              <div>
                <small>
                  {d.category} · {d.author}
                </small>
                <h3>{d.title}</h3>
                <p>
                  Explore perspectives and learn from the experiences of the
                  community.
                </p>
                <span>{d.replies} replies · Fictional discussion</span>
              </div>
              <ChevronRight />
            </article>
          ))}
        </div>
        <aside className="aside-card">
          <ShieldCheck size={28} />
          <h3>Community guidelines</h3>
          <ul>
            <li>Respect different experiences and identities.</li>
            <li>Do not share another person's private information.</li>
            <li>Keep discussions constructive and supportive.</li>
            <li>Use moderation and reporting tools responsibly.</li>
          </ul>
        </aside>
      </div>
    </>
  );
}
export function Learning({ notify }: { notify: (s: string) => void }) {
  const items = [
    [
      "Gender-Responsive Mentorship Toolkit",
      "Toolkit",
      "Practical guidance for mentors and champions.",
    ],
    [
      "Understanding consent and support pathways",
      "Learning module",
      "Explore key concepts and support options.",
    ],
    [
      "Creating inclusive STEM spaces",
      "Guide",
      "Ideas for building safer, more inclusive communities.",
    ],
    [
      "Advocacy and change-making",
      "Resource pack",
      "Tools for constructive institutional engagement.",
    ],
  ];
  return (
    <>
      <PageTitle
        eyebrow="LEARNING & ADVOCACY"
        title="Explore resources"
        description="Discover practical resources, learning materials and advocacy content."
      />
      <div className="resource-grid">
        {items.map((x, i) => (
          <article className={`resource-card resource-${i}`} key={x[0]}>
            <div className="resource-cover">
              <span>{x[1]}</span>
              <BookOpen size={38} />
              <small>GTD HUB · DEMO</small>
            </div>
            <div className="resource-body">
              <span className="eyebrow">FEATURED RESOURCE</span>
              <h3>{x[0]}</h3>
              <p>{x[2]}</p>
              <button
                className="text-action"
                onClick={() =>
                  notify(
                    "Resource preview is illustrative; no external document is opened.",
                  )
                }
              >
                Preview resource <ArrowRight size={15} />
              </button>
            </div>
          </article>
        ))}
      </div>
    </>
  );
}
export function CaseWorkspace() {
  const [records, setRecords] = useState<import("../services/api").CaseRecord[]>([]);
  const [dashboard, setDashboard] = useState<{ total: number; assigned_to_me: number; unassigned: number; by_status: Record<string, number> } | null>(null);
  const [handlers, setHandlers] = useState<Array<{ id: number; full_name: string; institution_id: number }>>([]);
  const [selected, setSelected] = useState("");
  const [detail, setDetail] = useState<any>(null);
  const [notes, setNotes] = useState<Array<{ id: number; label: string; created_at: string }>>([]);
  const [audit, setAudit] = useState<{ integrity_valid: boolean; events: Array<{ sequence: number; action: string; actor_user_id: number | null; created_at: string }> } | null>(null);
  const [filter, setFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const refresh = async () => {
    const [summary, queue, availableHandlers] = await Promise.all([
      api.caseDashboard(), api.caseQueue(statusFilter, filter), api.caseHandlers(),
    ]);
    setDashboard(summary); setRecords(queue); setHandlers(availableHandlers);
    if (!selected && queue.length) setSelected(queue[0].case_ref);
    if (selected && !queue.some((row) => row.case_ref === selected)) setSelected(queue[0]?.case_ref || "");
  };
  useEffect(() => { refresh().catch((e) => setError(e.message)); }, [filter, statusFilter]);
  useEffect(() => {
    if (!selected) { setDetail(null); setNotes([]); setAudit(null); return; }
    Promise.all([api.caseDetail(selected), api.caseNotes(selected)])
      .then(([record, caseNotes]) => { setDetail(record); setNotes(caseNotes); setAudit(null); })
      .catch((e) => setError(e.message));
  }, [selected]);
  const run = async (action: () => Promise<unknown>) => {
    setBusy(true); setError("");
    try { await action(); await refresh(); if (selected) { const [record, caseNotes] = await Promise.all([api.caseDetail(selected), api.caseNotes(selected)]); setDetail(record); setNotes(caseNotes); } }
    catch (e) { setError(e instanceof Error ? e.message : "The action could not be completed."); }
    finally { setBusy(false); }
  };
  const statusLabel = (status: string) => status.replace(/_/g, " ");
  const selectedRecord = records.find((row) => row.case_ref === selected);
  return (
    <>
      <PageTitle eyebrow="RESTRICTED CASE MANAGEMENT" title="Case management" description="Institution-scoped work queues and human-recorded case workflows. Synthetic demonstration data only." />
      <div className="notice warning"><LockKeyhole /><div><b>Demonstration environment — fictional records only</b><p>Do not enter real disclosures, identities or contact details. The system records authorised human actions; it does not assess risk, make safeguarding decisions, contact providers or send emergency alerts.</p></div></div>
      {error && <div className="notice warning" role="alert"><Info /><p>{error}</p></div>}
      <div className="metric-grid">
        {[{label:"Visible cases",value:dashboard?.total ?? "—"},{label:"Assigned to me",value:dashboard?.assigned_to_me ?? "—"},{label:"Unassigned",value:dashboard?.unassigned ?? "—"}].map((m) => <div className="admin-metric" key={m.label}><b>{m.value}</b><span>{m.label}</span></div>)}
      </div>
      <div className="case-toolbar" style={{display:"flex",gap:12,flexWrap:"wrap",margin:"18px 0"}}>
        <label>Assignment <select value={filter} onChange={(e) => setFilter(e.target.value)}><option value="all">All cases</option><option value="mine">Assigned to me</option><option value="unassigned">Unassigned</option></select></label>
        <label>Status <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}><option value="">All statuses</option>{["received","acknowledged","under_review","information_only","referral_pending_human_action","institutional_action_pending_human_action","emergency_escalation_pending_human_action","closed"].map((v) => <option key={v} value={v}>{statusLabel(v)}</option>)}</select></label>
        <button disabled={busy} onClick={() => run(refresh)}>Refresh queue</button>
      </div>
      <div className="case-layout">
        <div className="case-list">
          {records.map((row) => <button key={row.case_ref} className={selected === row.case_ref ? "selected" : ""} onClick={() => setSelected(row.case_ref)}><b>{row.case_ref.slice(0, 13).toUpperCase()}</b><span>{row.scenario_code.replace("SCENARIO_", "").toLowerCase()}</span><small>Institution {row.institution_id} · {row.anonymous ? "Anonymous" : "Identified"}</small><em>{statusLabel(row.workflow_status)} · {row.priority}</em></button>)}
          {!records.length && <div className="panel-box"><p>No cases match these filters.</p></div>}
        </div>
        {detail && selectedRecord && <div className="case-detail">
          <div className="case-head"><div><span className="eyebrow">SECURE CASE RECORD</span><h2>{detail.case_ref}</h2></div><span className="status-pill">{statusLabel(detail.workflow_status)}</span></div>
          <div className="case-fields"><div><small>Institution</small><b>{detail.institution_id}</b></div><div><small>Report type</small><b>{detail.scenario?.label || selectedRecord.scenario_code}</b></div><div><small>Consent</small><b>{detail.consent_status}</b></div><div><small>Priority · human-set</small><b>{selectedRecord.priority}</b></div><div><small>Assignment</small><b>{selectedRecord.assigned_to_user_id ? (handlers.find((h) => h.id === selectedRecord.assigned_to_user_id)?.full_name || `Handler #${selectedRecord.assigned_to_user_id}`) : "Unassigned"}</b></div><div><small>Received</small><b>{new Date(selectedRecord.created_at).toLocaleString()}</b></div></div>
          <div className="notice"><Info /><p>{detail.scenario?.narrative || "Encrypted report content is available to authorised case handlers."} All workflow decisions remain human-led.</p></div>
          <div className="case-actions" style={{display:"flex",gap:8,flexWrap:"wrap"}}>
            {detail.workflow_status === "received" && <button disabled={busy} onClick={() => run(() => api.caseWorkflow(selected,"acknowledge"))}>Acknowledge</button>}
            {(["acknowledged","information_only","referral_pending_human_action","institutional_action_pending_human_action","emergency_escalation_pending_human_action"].includes(detail.workflow_status)) && <button disabled={busy} onClick={() => run(() => api.caseWorkflow(selected,"start_review"))}>Start review</button>}
            {detail.workflow_status === "acknowledged" && <button disabled={busy} onClick={() => run(() => api.caseWorkflow(selected,"information_only","info_provided"))}>Information provided</button>}
            {detail.workflow_status === "under_review" && <>
              {detail.consent_status === "granted" && <button disabled={busy} onClick={() => run(() => api.caseWorkflow(selected,"refer","referral_requested"))}>Record referral decision</button>}
              <button disabled={busy} onClick={() => run(() => api.caseWorkflow(selected,"institutional_action","institutional_process_requested"))}>Institutional process</button>
              <button disabled={busy} onClick={() => run(() => api.caseWorkflow(selected,"emergency_escalation","human_escalation_recorded"))}>Record escalation</button>
              <button disabled={busy} onClick={() => run(() => api.caseWorkflow(selected,"close","resolved"))}>Close — resolved</button>
            </>}
            {detail.workflow_status === "closed" && <button disabled={busy} onClick={() => run(() => api.caseWorkflow(selected,"reopen","reopened"))}>Reopen for review</button>}
          </div>
          <div className="panel-box" style={{marginTop:16}}><h3>Assignment</h3><div style={{display:"flex",gap:8,flexWrap:"wrap"}}><select aria-label="Assign case handler" id="case-handler-select"><option value="">Select case handler</option>{handlers.filter((h) => h.institution_id === selectedRecord.institution_id).map((h) => <option key={h.id} value={h.id}>{h.full_name}</option>)}</select><button disabled={busy || !handlers.some((h) => h.institution_id === selectedRecord.institution_id)} onClick={() => { const el = document.getElementById("case-handler-select") as HTMLSelectElement | null; if (el?.value) run(() => api.assignCase(selected,Number(el.value))); }}>Assign</button></div><label style={{display:"block",marginTop:12}}>Priority <select value={selectedRecord.priority} onChange={(e) => run(() => api.setCasePriority(selected,e.target.value))}><option value="low">Low</option><option value="normal">Normal</option><option value="high">High</option><option value="urgent">Urgent</option></select></label></div>
          <div className="panel-box" style={{marginTop:16}}><h3>Structured activity notes</h3><p>Predefined synthetic activity markers only; no free-text narratives are accepted in this demonstrator.</p><div style={{display:"flex",gap:8,flexWrap:"wrap"}}>{[{code:"information_provided",label:"Information provided"},{code:"consent_checked",label:"Consent checked"},{code:"referral_discussed",label:"Referral discussed"},{code:"follow_up_required",label:"Follow-up required"},{code:"closure_reviewed",label:"Closure reviewed"}].map((n) => <button key={n.code} disabled={busy} onClick={() => run(() => api.addCaseNote(selected,n.code))}>{n.label}</button>)}</div><ul>{notes.map((n) => <li key={n.id}>{n.label} · {new Date(n.created_at).toLocaleString()}</li>)}</ul><button disabled={busy} onClick={() => run(async () => { const result = await api.caseAudit(selected); setAudit(result); })}>Verify audit trail</button>{audit && <div className="notice"><b>Audit integrity: {audit.integrity_valid ? "Valid" : "Failed"}</b><ul>{audit.events.map((event) => <li key={event.sequence}>{event.action} · {new Date(event.created_at).toLocaleString()}</li>)}</ul></div>}</div>
        </div>}
      </div>
    </>
  );
}
export function Organisation({
  selected,
  setSelected,
}: {
  selected: string;
  setSelected: (v: string) => void;
}) {
  const [metrics, setMetrics] = useState<any>(null);
  const [error, setError] = useState("");
  useEffect(() => { api.adminInsights().then(setMetrics).catch((e) => setError(e instanceof Error ? e.message : "Unable to load institutional indicators.")); }, []);
  const values = metrics ? [
    [metrics.registered_users, "Registered accounts"], [metrics.active_accounts, "Active accounts"],
    [metrics.mentors, "Active mentors"], [metrics.active_mentorship_connections, "Active mentorship connections"],
    [metrics.mentorship_requests, "Mentorship requests"], [metrics.community_discussions, "Community discussions"],
    [metrics.published_learning_resources, "Published learning resources"],
  ] : [];
  return <>
    <PageTitle eyebrow="INSTITUTIONAL WORKSPACE" title="Institution overview" description="Institution-scoped aggregate indicators and administrative workspace." />
    {error && <div className="notice"><Info /><p>{error}</p></div>}
    {!metrics && !error && <div className="panel-box">Loading institutional indicators…</div>}
    {metrics && <>
      <div className="metric-grid">{values.map(([v, label]) => <div className="admin-metric" key={label}><b>{v}</b><span>{label}</span></div>)}</div>
      <div className="panel-box"><h2>Institutional activity</h2><p>Counts reflect available records assigned to this institution. They are not outcome or impact measures.</p><p className="muted">{metrics.data_label}</p></div>
    </>}
    <div className="notice"><Info /><p>Only aggregate non-case indicators are displayed. GBV narratives, contact information and identifiable case-level records are excluded.</p></div>
  </>;
}

export function Programme({
  selected,
  setSelected,
}: {
  selected: string;
  setSelected: (v: string) => void;
}) {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    setLoading(true); setError("");
    api.adminInsights().then(setMetrics).catch((e) => setError(e instanceof Error ? e.message : "Unable to load programme indicators.")).finally(() => setLoading(false));
  }, []);
  const cards = metrics ? [
    [metrics.registered_users, "Registered accounts"],
    [metrics.active_accounts, "Active accounts"],
    [metrics.mentors, "Active mentors"],
    [metrics.active_mentorship_connections, "Active mentorship connections"],
    [metrics.mentorship_requests, "Mentorship requests"],
    [metrics.community_discussions, "Community discussions"],
    [metrics.published_learning_resources, "Published learning resources"],
  ] : [];
  const download = async () => {
    try { const blob = await api.downloadMeReport(); const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href = url; a.download = "gtdhub-me-aggregate-report.csv"; a.click(); URL.revokeObjectURL(url); }
    catch (e) { setError(e instanceof Error ? e.message : "Report export failed."); }
  };
  return <>
    <PageTitle eyebrow="PROGRAMME MONITORING & LEARNING" title="Programme insights" description="De-identified aggregate indicators calculated from available demonstrator records." />
    <div className="admin-toolbar"><span className="muted">Programme-wide scope · aggregate records only</span><button className="primary-button" onClick={() => void download()}>Export M&E CSV</button></div>
    {loading && <div className="panel-box">Loading programme indicators…</div>}
    {error && <div className="notice"><Info /><p>{error}</p></div>}
    {!loading && metrics && <>
      <div className="metric-grid">{cards.map(([value, label]) => <div className="admin-metric" key={label}><b>{value}</b><span>{label}</span></div>)}</div>
      <div className="panel-box"><h2>Indicator interpretation</h2><p>These are counts of records currently available in the demonstrator. They do not measure participant outcomes, wellbeing, institutional change or programme impact.</p><p className="muted">{metrics.data_label}</p></div>
    </>}
    <div className="notice"><Info /><p>GBV case narratives, contact details and identifiable case-level information are excluded from these indicators and exports. Safeguarding decisions remain with authorised human personnel.</p></div>
  </>;
}

export function Administration({ notify }: { notify: (s: string) => void }) {
  const { user } = useAuth();
  const [tab, setTab] = useState("users");
  const [users, setUsers] = useState<any[]>([]);
  const [institutions, setInstitutions] = useState<any[]>([]);
  const [dashboard, setDashboard] = useState<any>(null);
  const [audit, setAudit] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [newUser, setNewUser] = useState({ email: "", full_name: "", password: "", role: "Member", institution_id: user?.institution_id ?? 0 });
  const [newInstitution, setNewInstitution] = useState({ name: "", code: "" });
  const isProgrammeAdmin = user?.role === "Programme Administrator";
  const canAudit = user?.permissions.includes("administration:audit");
  const load = async () => {
    setLoading(true);
    try {
      const [u, i, a, d] = await Promise.all([
        api.adminUsers(search), api.adminInstitutions(), canAudit ? api.adminAudit() : Promise.resolve([]), api.adminDashboard(),
      ]);
      setUsers(u.items); setInstitutions(i.items); setAudit(a); setDashboard(d);
    } catch (error) { notify(error instanceof Error ? error.message : "Could not load administration data."); }
    finally { setLoading(false); }
  };
  useEffect(() => { void load(); }, [search]);
  const submitUser = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await api.createAdminUser({ ...newUser, institution_id: newUser.role === "Programme Administrator" ? null : Number(newUser.institution_id) });
      setNewUser({ email: "", full_name: "", password: "", role: "Member", institution_id: user?.institution_id ?? 0 });
      setFormOpen(false); await load(); notify("User account created.");
    } catch (error) { notify(error instanceof Error ? error.message : "Could not create user."); }
  };
  const changeUser = async (id: number, patch: Record<string, unknown>) => {
    try { await api.updateAdminUser(id, patch as any); await load(); notify("User updated. Existing sessions were revoked where access changed."); }
    catch (error) { notify(error instanceof Error ? error.message : "Could not update user."); }
  };
  const submitInstitution = async (event: FormEvent) => {
    event.preventDefault();
    try { await api.createAdminInstitution(newInstitution); setNewInstitution({ name: "", code: "" }); await load(); notify("Institution created."); }
    catch (error) { notify(error instanceof Error ? error.message : "Could not create institution."); }
  };
  const downloadReport = async () => {
    try {
      const blob = await api.downloadMeReport(); const url = URL.createObjectURL(blob);
      const link = document.createElement("a"); link.href = url; link.download = "gtdhub-me-aggregate-report.csv"; link.click(); URL.revokeObjectURL(url);
    } catch (error) { notify(error instanceof Error ? error.message : "Report export failed."); }
  };
  return <>
    <PageTitle eyebrow="PLATFORM GOVERNANCE" title="Administration" description="Manage demonstrator accounts and institutions, and review administrative activity within your authorised scope." />
    {dashboard && <div className="metric-grid admin-summary-grid">{[[dashboard.users_total, "Accounts"], [dashboard.users_active, "Active accounts"], [dashboard.institutions_total, "Institutions in scope"], [dashboard.mentors_active, "Active mentors"], [dashboard.mentorship_connections, "Mentorship connections"], [dashboard.published_learning_resources, "Published resources"]].map(([v, label]) => <div className="admin-metric" key={label}><b>{v}</b><span>{label}</span></div>)}</div>}
    <div className="admin-tabs">
      {["users", "institutions", "audit"].filter((x) => x !== "audit" || canAudit).map((x) => <button key={x} className={tab === x ? "active" : ""} onClick={() => setTab(x)}>{x === "users" ? "Users & roles" : x === "institutions" ? "Institutions" : "Audit trail"}</button>)}
    </div>
    {tab === "users" && <section className="panel-box">
      <div className="admin-toolbar"><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search name or email" /><button className="primary-button" onClick={() => setFormOpen(!formOpen)}>Add user</button></div>
      {formOpen && <form className="admin-form" onSubmit={submitUser}>
        <input required type="text" placeholder="Full name" value={newUser.full_name} onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })} />
        <input required type="email" placeholder="Email address" value={newUser.email} onChange={(e) => setNewUser({ ...newUser, email: e.target.value })} />
        <input required type="password" minLength={12} placeholder="Temporary password (12+ characters)" value={newUser.password} onChange={(e) => setNewUser({ ...newUser, password: e.target.value })} />
        <select value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}>{["Member", "Mentor", "Moderator", "Case Handler", ...(isProgrammeAdmin ? ["Organisation Administrator", "Programme Administrator"] : [])].map((r) => <option key={r}>{r}</option>)}</select>
        {isProgrammeAdmin && <select value={newUser.institution_id} onChange={(e) => setNewUser({ ...newUser, institution_id: Number(e.target.value) })}><option value={0}>Select institution</option>{institutions.map((i) => <option key={i.id} value={i.id}>{i.name}</option>)}</select>}
        <button className="primary-button" type="submit">Create account</button>
      </form>}
      {loading ? <p>Loading accounts…</p> : <div className="admin-table-wrap"><table className="admin-table"><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Institution</th><th>Status</th><th>Action</th></tr></thead><tbody>{users.map((u) => <tr key={u.id}><td>{u.full_name}</td><td>{u.email}</td><td><select aria-label={`Role for ${u.full_name}`} value={u.role} disabled={u.id === user?.id || u.role === "Programme Administrator" || (!isProgrammeAdmin && u.role === "Organisation Administrator")} onChange={(e) => void changeUser(u.id, { role: e.target.value })}>{["Member", "Mentor", "Moderator", "Case Handler", ...(isProgrammeAdmin ? ["Organisation Administrator", "Programme Administrator"] : [])].map((r) => <option key={r}>{r}</option>)}</select></td><td>{isProgrammeAdmin && u.role !== "Programme Administrator" ? <select aria-label={`Institution for ${u.full_name}`} value={u.institution_id ?? ""} onChange={(e) => void changeUser(u.id, { institution_id: Number(e.target.value) })}>{institutions.map((i) => <option key={i.id} value={i.id}>{i.name}</option>)}</select> : (u.institution_name || "Programme")}</td><td>{u.is_active ? "Active" : "Inactive"}</td><td><button disabled={u.id === user?.id} onClick={() => void changeUser(u.id, { is_active: !u.is_active })}>{u.is_active ? "Deactivate" : "Activate"}</button></td></tr>)}</tbody></table></div>}
      <p className="muted">Password values are never displayed. Account access changes revoke existing sessions.</p>
    </section>}
    {tab === "institutions" && <section className="panel-box"><h2>Participating institutions</h2>{isProgrammeAdmin && <form className="admin-form" onSubmit={submitInstitution}><input required placeholder="Institution name" value={newInstitution.name} onChange={(e) => setNewInstitution({ ...newInstitution, name: e.target.value })} /><input required placeholder="Institution code" value={newInstitution.code} onChange={(e) => setNewInstitution({ ...newInstitution, code: e.target.value.toUpperCase() })} /><button className="primary-button">Add institution</button></form>}<div className="admin-table-wrap"><table className="admin-table"><thead><tr><th>Institution</th><th>Code</th><th>Status</th>{isProgrammeAdmin && <th>Action</th>}</tr></thead><tbody>{institutions.map((i) => <tr key={i.id}><td>{i.name}</td><td>{i.code}</td><td>{i.is_active ? "Active" : "Inactive"}</td>{isProgrammeAdmin && <td><button onClick={async () => { const name = window.prompt("Institution name", i.name); if (name === null) return; const code = window.prompt("Institution code", i.code); if (code === null) return; try { await api.updateAdminInstitution(i.id, { name, code }); await load(); notify("Institution updated."); } catch (e) { notify(e instanceof Error ? e.message : "Update failed"); } }}>Edit</button> <button onClick={async () => { try { await api.updateAdminInstitution(i.id, { is_active: !i.is_active }); await load(); } catch (e) { notify(e instanceof Error ? e.message : "Update failed"); } }}>{i.is_active ? "Deactivate" : "Activate"}</button></td>}</tr>)}</tbody></table></div></section>}
    {tab === "audit" && <section className="panel-box"><h2>Administrative audit events</h2><div className="admin-table-wrap"><table className="admin-table"><thead><tr><th>Time</th><th>Actor ID</th><th>Action</th><th>Target</th><th>Institution</th></tr></thead><tbody>{audit.map((e) => <tr key={e.id}><td>{new Date(e.created_at).toLocaleString()}</td><td>{e.actor_user_id ?? "System"}</td><td>{e.action}</td><td>{e.target_type} · {e.target_id}</td><td>{e.institution_id ?? "Programme"}</td></tr>)}</tbody></table></div></section>}
    <p className="notice">Administrative actions are logged. This demonstrator uses synthetic data; do not enter real participant or GBV case information.</p>
  </>;
}

export function Help() {
  return (
    <>
      <PageTitle
        eyebrow="HELP & GUIDANCE"
        title="Using GTD Hub safely"
        description="Information about the demonstrator and the principles guiding the proposed product."
      />
      <div className="help-grid">
        <div className="panel-box">
          <ShieldCheck />
          <h2>Privacy and confidentiality</h2>
          <p>
            The demonstrator uses fictional identities, organisations and
            records. It is not connected to a live safeguarding service.
          </p>
        </div>
        <div className="panel-box">
          <AccessibilityIcon />
          <h2>Accessibility</h2>
          <p>
            The proposed interface targets WCAG 2.1 AA and will be validated
            through accessibility testing.
          </p>
        </div>
        <div className="panel-box">
          <LifeBuoy />
          <h2>Support options</h2>
          <p>
            Use the Find Support area to explore illustrative service
            categories. Live details require partner verification.
          </p>
        </div>
      </div>
    </>
  );
}
function AccessibilityIcon() {
  return <Users />;
}
