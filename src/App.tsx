import { useMemo, useState, type ReactNode } from "react";
import {
  Activity,
  ArrowRight,
  Bell,
  BookOpen,
  CalendarDays,
  Check,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  ClipboardList,
  Compass,
  FileText,
  HeartHandshake,
  Home,
  LifeBuoy,
  LockKeyhole,
  LogOut,
  Menu,
  MessageCircle,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Users,
  X,
  Zap,
} from "lucide-react";
import {
  cases,
  discussions,
  institutions,
  mentors,
  roles,
  type Role,
} from "./data/mock";

type Page =
  | "Overview"
  | "Find support"
  | "Safe reporting"
  | "Mentorship"
  | "Community"
  | "Learning library"
  | "Case workspace"
  | "Institution overview"
  | "Programme insights"
  | "Administration";
const studentNav: Page[] = [
  "Overview",
  "Find support",
  "Safe reporting",
  "Mentorship",
  "Community",
  "Learning library",
];
const roleNav: Record<Role, Page[]> = {
  Student: studentNav,
  Mentor: ["Overview", "Mentorship", "Community", "Learning library"],
  Moderator: ["Overview", "Community", "Learning library"],
  "Case handler": ["Overview", "Case workspace", "Find support"],
  "HEI administrator": ["Overview", "Institution overview", "Administration"],
  "Programme administrator": [
    "Overview",
    "Programme insights",
    "Institution overview",
    "Administration",
  ],
};
const pageIcon: Record<string, ReactNode> = {
  Overview: <Home size={17} />,
  "Find support": <LifeBuoy size={17} />,
  "Safe reporting": <ShieldCheck size={17} />,
  Mentorship: <HeartHandshake size={17} />,
  Community: <MessageCircle size={17} />,
  "Learning library": <BookOpen size={17} />,
  "Case workspace": <ClipboardList size={17} />,
  "Institution overview": <Users size={17} />,
  "Programme insights": <Activity size={17} />,
  Administration: <Settings size={17} />,
};
function App() {
  const [role, setRole] = useState<Role>("Student");
  const [page, setPage] = useState<Page>("Overview");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [roleMenu, setRoleMenu] = useState(false);
  const [search, setSearch] = useState("");
  const [reportStep, setReportStep] = useState(0);
  const [anonymous, setAnonymous] = useState(true);
  const [consent, setConsent] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [mentorQuery, setMentorQuery] = useState("");
  const [requested, setRequested] = useState<string[]>([]);
  const [caseStatuses, setCaseStatuses] = useState<Record<string, string>>({});
  const [selectedInstitution, setSelectedInstitution] = useState(
    institutions[0],
  );
  const [toast, setToast] = useState("");
  const nav = roleNav[role];
  const filteredMentors = useMemo(
    () =>
      mentors.filter((m) =>
        `${m.name} ${m.field} ${m.focus}`
          .toLowerCase()
          .includes(mentorQuery.toLowerCase()),
      ),
    [mentorQuery],
  );
  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2600);
  };
  const changeRole = (r: Role) => {
    setRole(r);
    setPage("Overview");
    setMobileOpen(false);
    setRoleMenu(false);
  };
  const openPage = (p: Page) => {
    setPage(p);
    setMobileOpen(false);
  };
  const quickExit = () => {
    setPage("Overview");
    setMobileOpen(false);
    notify(
      "Quick exit demonstrated. This prototype does not connect to a live service.",
    );
  };
  const title =
    page === "Overview"
      ? role === "Student"
        ? "Your space to grow and thrive"
        : role === "Programme administrator"
          ? "Programme overview"
          : `${role} workspace`
      : page;
  return (
    <div className="app-shell">
      <div className="demo-banner">
        <span className="demo-dot" /> PROPOSAL DEMONSTRATOR{" "}
        <span className="banner-divider">·</span> Fictional data only{" "}
        <span className="banner-right">
          Concept experience — not a live support service
        </span>
      </div>
      <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
        <div className="brand-lockup">
          <div className="brand-mark">
            <span>G</span>
            <i />
          </div>
          <div>
            <div className="brand-name">
              gtd<span>hub</span>
            </div>
            <div className="brand-caption">CONNECT · SUPPORT · TRANSFORM</div>
          </div>
          <button
            className="icon-btn mobile-close"
            onClick={() => setMobileOpen(false)}
            aria-label="Close menu"
          >
            <X size={19} />
          </button>
        </div>
        <div className="workspace-label">DEMO WORKSPACE</div>
        <button className="role-select" onClick={() => setRoleMenu(!roleMenu)}>
          <div className="role-avatar">
            {role
              .split(" ")
              .map((x) => x[0])
              .join("")
              .slice(0, 2)}
          </div>
          <div className="role-select-text">
            <strong>{role}</strong>
            <small>Explore as a demo user</small>
          </div>
          <ChevronDown size={16} />
        </button>
        {roleMenu && (
          <div className="role-menu">
            {roles.map((r) => (
              <button
                key={r}
                className={role === r ? "chosen" : ""}
                onClick={() => changeRole(r)}
              >
                {r}
                {role === r && <Check size={14} />}
              </button>
            ))}
          </div>
        )}
        <div className="nav-label">WORKSPACE</div>
        <nav className="main-nav">
          {nav.map((item) => (
            <button
              key={item}
              className={`nav-item ${page === item ? "active" : ""}`}
              onClick={() => openPage(item)}
            >
              {pageIcon[item]}
              <span>{item}</span>
              {item === "Safe reporting" && (
                <span className="nav-safe">SAFE</span>
              )}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon">
              <HeartHandshake size={18} />
            </div>
            <strong>You're not alone.</strong>
            <p>Explore trusted support options and resources.</p>
            <button onClick={() => openPage("Find support")}>
              Find support <ArrowRight size={14} />
            </button>
          </div>
          <button
            className="nav-item"
            onClick={() =>
              notify("Help centre is a demonstration placeholder.")
            }
          >
            <CircleHelp size={17} /> Help & guidance
          </button>
          <div className="sidebar-foot">
            <span className="online-dot" /> Interactive concept v0.1
          </div>
        </div>
      </aside>
      {mobileOpen && (
        <div className="scrim" onClick={() => setMobileOpen(false)} />
      )}
      <main className="main-area">
        <header className="topbar">
          <button
            className="icon-btn menu-toggle"
            onClick={() => setMobileOpen(true)}
            aria-label="Open menu"
          >
            <Menu size={20} />
          </button>
          <div className="crumb">
            GTD Hub <ChevronRight size={14} /> <strong>{page}</strong>
          </div>
          <div className="top-actions">
            <div className="top-search">
              <Search size={15} />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search the hub"
                onKeyDown={(e) =>
                  e.key === "Enter" &&
                  notify(
                    search
                      ? `Demo search for “${search}”`
                      : "Enter a search term",
                  )
                }
              />
              <kbd>⌘ K</kbd>
            </div>
            <button
              className="icon-btn notification-btn"
              onClick={() => notify("You are all caught up in this demo.")}
              aria-label="Notifications"
            >
              <Bell size={18} />
              <i />
            </button>
            <div className="user-chip">
              <div className="user-avatar">
                {role === "Student"
                  ? "TM"
                  : role === "Mentor"
                    ? "RM"
                    : role === "Case handler"
                      ? "CH"
                      : "AD"}
              </div>
              <div>
                <strong>
                  {role === "Student"
                    ? "Tadiwa M."
                    : role === "Mentor"
                      ? "Rudo M."
                      : role === "Case handler"
                        ? "Case handler"
                        : "Demo admin"}
                </strong>
                <small>{role}</small>
              </div>
              <ChevronDown size={14} />
            </div>
          </div>
        </header>
        <div className="content-wrap">
          {page === "Overview" && (
            <Overview role={role} openPage={openPage} notify={notify} />
          )}
          {page === "Find support" && <Support notify={notify} />}
          {page === "Safe reporting" && (
            <Reporting
              step={reportStep}
              setStep={setReportStep}
              anonymous={anonymous}
              setAnonymous={setAnonymous}
              consent={consent}
              setConsent={setConsent}
              submitted={submitted}
              setSubmitted={setSubmitted}
              notify={notify}
            />
          )}
          {page === "Mentorship" && (
            <Mentorship
              query={mentorQuery}
              setQuery={setMentorQuery}
              mentors={filteredMentors}
              requested={requested}
              setRequested={setRequested}
              notify={notify}
            />
          )}
          {page === "Community" && <Community notify={notify} />}
          {page === "Learning library" && <Library notify={notify} />}
          {page === "Case workspace" && (
            <CaseWorkspace
              statuses={caseStatuses}
              setStatuses={setCaseStatuses}
              notify={notify}
            />
          )}
          {page === "Institution overview" && (
            <Institution
              selected={selectedInstitution}
              setSelected={setSelectedInstitution}
            />
          )}
          {page === "Programme insights" && (
            <Insights
              selected={selectedInstitution}
              setSelected={setSelectedInstitution}
            />
          )}
          {page === "Administration" && <Administration notify={notify} />}
        </div>
        <footer className="page-footer">
          <span>GTD Hub · PROGEN-Hub for STEM</span>
          <span>Designed for inclusive, institution-connected support</span>
          <button onClick={quickExit}>
            <Zap size={13} /> Quick exit
          </button>
        </footer>
      </main>
      {toast && (
        <div className="toast">
          <Check size={16} />
          {toast}
        </div>
      )}
      <div className="prototype-disclaimer">
        <ShieldCheck size={13} /> Demonstration environment · Fictional users
        and records · No real reports are submitted
      </div>
    </div>
  );
}
function PageHeading({
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
    <div className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </div>
  );
}
function Overview({
  role,
  openPage,
  notify,
}: {
  role: Role;
  openPage: (p: Page) => void;
  notify: (s: string) => void;
}) {
  const admin =
    role === "Programme administrator" ||
    role === "HEI administrator" ||
    role === "Case handler" ||
    role === "Moderator";
  return (
    <>
      <div className="welcome-strip">
        <div>
          <div className="eyebrow light">MONDAY, 23 NOVEMBER 2026</div>
          <h1>
            {role === "Student"
              ? "Good morning, Tadiwa."
              : `Welcome to your ${role.toLowerCase()} space.`}
          </h1>
          <p>
            {role === "Student"
              ? "A place to find support, build connections and shape your STEM journey."
              : "Your workspace brings together the tools and information relevant to your role."}
          </p>
        </div>
        <div className="welcome-art">
          <div className="art-orbit orbit-one" />
          <div className="art-orbit orbit-two" />
          <div className="art-core">
            <HeartHandshake size={35} />
          </div>
          <span className="art-star star-a">✳</span>
          <span className="art-star star-b">✦</span>
        </div>
      </div>
      <div className="section-head">
        <div>
          <h2>{admin ? "Workspace at a glance" : "Your hub at a glance"}</h2>
          <p>Small steps. Stronger connections. Meaningful change.</p>
        </div>
        <span className="updated">
          <span className="online-dot" /> Demo data
        </span>
      </div>
      <div className="stat-grid">
        <Stat
          icon={<Users />}
          label="Community members"
          value={admin ? "1,284" : "1,284"}
          change="Across participating spaces"
        />
        <Stat
          icon={<HeartHandshake />}
          label="Mentorship connections"
          value="326"
          change="Active connections"
        />
        <Stat
          icon={<BookOpen />}
          label="Learning resources"
          value="48"
          change="Guides, toolkits and modules"
        />
        <Stat
          icon={<Activity />}
          label="Community activity"
          value="82%"
          change="Illustrative engagement"
        />
      </div>
      <div className="dashboard-grid">
        <div className="panel feature-panel">
          <div className="panel-top">
            <div>
              <span className="eyebrow">A SAFE PLACE TO START</span>
              <h3>Support is available.</h3>
              <p>
                Explore confidential support information, understand your
                options and choose what feels right for you.
              </p>
            </div>
            <div className="feature-icon">
              <ShieldCheck size={27} />
            </div>
          </div>
          <div className="feature-actions">
            <button
              className="btn btn-primary"
              onClick={() => openPage("Find support")}
            >
              Explore support <ArrowRight size={15} />
            </button>
            <button
              className="btn btn-soft"
              onClick={() => openPage("Safe reporting")}
            >
              Understand reporting options
            </button>
          </div>
          <div className="privacy-note">
            <LockKeyhole size={14} /> Your choices matter. The platform is
            designed around privacy, consent and human support.
          </div>
        </div>
        <div className="panel upcoming-panel">
          <div className="panel-title">
            <div>
              <h3>Coming up</h3>
              <p>Opportunities to connect and learn</p>
            </div>
            <CalendarDays size={19} />
          </div>
          <div className="event-row">
            <div className="event-date">
              <b>26</b>
              <small>NOV</small>
            </div>
            <div>
              <strong>STEM mentorship circle</strong>
              <small>Online · 14:00 CAT</small>
            </div>
            <span className="event-tag">Mentorship</span>
          </div>
          <div className="event-row">
            <div className="event-date">
              <b>30</b>
              <small>NOV</small>
            </div>
            <div>
              <strong>Research confidence workshop</strong>
              <small>Online · 10:00 CAT</small>
            </div>
            <span className="event-tag green">Learning</span>
          </div>
          <button
            className="text-link"
            onClick={() =>
              notify("The events calendar is a demonstration placeholder.")
            }
          >
            View all activities <ArrowRight size={14} />
          </button>
        </div>
      </div>
      <div className="section-head lower">
        <div>
          <h2>Explore your hub</h2>
          <p>Choose where you would like to begin.</p>
        </div>
      </div>
      <div className="quick-grid">
        {[
          {
            icon: <HeartHandshake />,
            title: "Find a mentor",
            desc: "Connect with people who can support your journey.",
            page: "Mentorship" as Page,
          },
          {
            icon: <MessageCircle />,
            title: "Join the conversation",
            desc: "Learn and exchange ideas with your peers.",
            page: "Community" as Page,
          },
          {
            icon: <BookOpen />,
            title: "Explore resources",
            desc: "Discover practical tools and learning materials.",
            page: "Learning library" as Page,
          },
        ].map((x) => (
          <button
            className="quick-card"
            key={x.title}
            onClick={() => openPage(x.page)}
          >
            <span className="quick-icon">{x.icon}</span>
            <strong>{x.title}</strong>
            <p>{x.desc}</p>
            <span className="quick-arrow">
              <ArrowRight size={16} />
            </span>
          </button>
        ))}
      </div>
    </>
  );
}
function Stat({
  icon,
  label,
  value,
  change,
}: {
  icon: ReactNode;
  label: string;
  value: string;
  change: string;
}) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-change">{change}</div>
    </div>
  );
}
function Support({ notify }: { notify: (s: string) => void }) {
  return (
    <>
      <PageHeading
        eyebrow="SUPPORT DIRECTORY"
        title="Find the support you need"
        description="Explore options available to students and staff. You can review information before deciding whether to take a next step."
      />
      <div className="notice notice-info">
        <ShieldCheck size={18} />
        <div>
          <strong>You are in control.</strong>
          <p>
            This directory is illustrative. In the live Hub, referral details
            and contact information will be confirmed with each participating
            institution.
          </p>
        </div>
      </div>
      <div className="support-grid">
        {[
          {
            icon: "♡",
            title: "Psychosocial support",
            desc: "Explore emotional wellbeing support and counselling options.",
            meta: "Wellbeing & counselling",
          },
          {
            icon: "✚",
            title: "Health services",
            desc: "Find information about medical support and health services.",
            meta: "Health & wellbeing",
          },
          {
            icon: "§",
            title: "Legal information",
            desc: "Understand available legal information and support pathways.",
            meta: "Information & guidance",
          },
          {
            icon: "◎",
            title: "Institutional support",
            desc: "Learn about designated offices and institutional processes.",
            meta: "Campus-based support",
          },
        ].map((x) => (
          <div className="support-card" key={x.title}>
            <div className="support-symbol">{x.icon}</div>
            <span className="eyebrow">{x.meta}</span>
            <h3>{x.title}</h3>
            <p>{x.desc}</p>
            <button
              className="text-link"
              onClick={() =>
                notify(
                  "This sample directory entry would open verified institution-specific information.",
                )
              }
            >
              View information <ArrowRight size={14} />
            </button>
          </div>
        ))}
      </div>
      <div className="panel callout-panel">
        <div className="callout-icon">
          <LifeBuoy />
        </div>
        <div>
          <h3>Not sure where to begin?</h3>
          <p>
            You can explore information without submitting a report. If there is
            immediate danger, use the emergency services and contacts confirmed
            by your institution.
          </p>
        </div>
        <button
          className="btn btn-outline"
          onClick={() =>
            notify(
              "Emergency contacts will be configured and validated with each institution.",
            )
          }
        >
          View emergency guidance
        </button>
      </div>
    </>
  );
}
function Reporting({
  step,
  setStep,
  anonymous,
  setAnonymous,
  consent,
  setConsent,
  submitted,
  setSubmitted,
  notify,
}: {
  step: number;
  setStep: (n: number) => void;
  anonymous: boolean;
  setAnonymous: (b: boolean) => void;
  consent: boolean;
  setConsent: (b: boolean) => void;
  submitted: boolean;
  setSubmitted: (b: boolean) => void;
  notify: (s: string) => void;
}) {
  const reset = () => {
    setStep(0);
    setSubmitted(false);
    setConsent(false);
    setAnonymous(true);
  };
  return (
    <>
      <PageHeading
        eyebrow="SAFE REPORTING · CONCEPT JOURNEY"
        title="Choose what feels right for you"
        description="The proposed reporting experience is designed to explain options clearly and keep people in control of their choices."
        action={
          <button
            className="btn btn-outline"
            onClick={() => {
              reset();
              notify("Demo journey reset.");
            }}
          >
            Reset journey
          </button>
        }
      />
      <div className="notice notice-warning">
        <LockKeyhole size={18} />
        <div>
          <strong>Fictional demonstration only</strong>
          <p>
            This is not a live reporting channel. Do not enter real names,
            incidents, contact details or personal experiences.
          </p>
        </div>
      </div>
      <div className="report-layout">
        <div className="report-main panel">
          <div className="stepper">
            {["Your choice", "Your options", "Review", "Confirmation"].map(
              (s, i) => (
                <div
                  className={`step ${step === i ? "current" : step > i ? "complete" : ""}`}
                  key={s}
                >
                  <span>{step > i ? <Check size={13} /> : i + 1}</span>
                  <small>{s}</small>
                </div>
              ),
            )}
          </div>
          {submitted ? (
            <div className="success-state">
              <div className="success-mark">
                <Check size={30} />
              </div>
              <span className="eyebrow">DEMONSTRATION COMPLETE</span>
              <h2>Your sample journey is complete.</h2>
              <p>
                No report has been sent or stored. In the production Hub,
                authorised personnel and institution-approved procedures would
                govern any real report and response.
              </p>
              <div className="reference-box">
                <span>Sample reference</span>
                <strong>DEMO-GTD-2026-014</strong>
              </div>
              <button className="btn btn-primary" onClick={reset}>
                Explore journey again
              </button>
            </div>
          ) : (
            <>
              {step === 0 && (
                <div className="form-step">
                  <span className="eyebrow">STEP 01 · YOUR CHOICE</span>
                  <h2>How would you like to continue?</h2>
                  <p className="muted">
                    You can explore the process anonymously or choose to provide
                    contact details in a real implementation.
                  </p>
                  <button
                    className={`choice-card ${anonymous ? "selected" : ""}`}
                    onClick={() => setAnonymous(true)}
                  >
                    <span className="choice-radio">{anonymous && <i />}</span>
                    <div>
                      <strong>Continue anonymously</strong>
                      <small>
                        Do not attach identifying contact details to this sample
                        journey.
                      </small>
                    </div>
                    <ShieldCheck size={21} />
                  </button>
                  <button
                    className={`choice-card ${!anonymous ? "selected" : ""}`}
                    onClick={() => setAnonymous(false)}
                  >
                    <span className="choice-radio">{!anonymous && <i />}</span>
                    <div>
                      <strong>Continue with contact details</strong>
                      <small>
                        Explore the identified pathway using fictional
                        information only.
                      </small>
                    </div>
                    <Users size={21} />
                  </button>
                  {!anonymous && (
                    <div className="form-grid">
                      <label>
                        Display name <input placeholder="Example: Demo User" />
                      </label>
                      <label>
                        Sample contact <input placeholder="demo@example.org" />
                      </label>
                    </div>
                  )}
                  <div className="form-actions">
                    <button
                      className="btn btn-primary"
                      onClick={() => setStep(1)}
                    >
                      Continue <ArrowRight size={15} />
                    </button>
                  </div>
                </div>
              )}
              {step === 1 && (
                <div className="form-step">
                  <span className="eyebrow">STEP 02 · YOUR OPTIONS</span>
                  <h2>Understand what happens next</h2>
                  <p className="muted">
                    The live platform will present institution-approved support
                    pathways and explain the implications of each choice.
                  </p>
                  <div className="pathway-list">
                    <div>
                      <span className="path-icon">01</span>
                      <section>
                        <strong>Information and support</strong>
                        <p>
                          Explore support resources and options without
                          requesting further action.
                        </p>
                      </section>
                    </div>
                    <div>
                      <span className="path-icon">02</span>
                      <section>
                        <strong>Referral support</strong>
                        <p>
                          Choose whether you would like an authorised person to
                          help connect you to a service.
                        </p>
                      </section>
                    </div>
                    <div>
                      <span className="path-icon">03</span>
                      <section>
                        <strong>Institutional process</strong>
                        <p>
                          Learn about formal institutional processes and the
                          relevant designated office.
                        </p>
                      </section>
                    </div>
                  </div>
                  <label className="consent-control">
                    <input
                      type="checkbox"
                      checked={consent}
                      onChange={(e) => setConsent(e.target.checked)}
                    />
                    <span>
                      <strong>Sample referral consent</strong>
                      <small>
                        I want to demonstrate the referral-consent option. This
                        selection has no real-world effect.
                      </small>
                    </span>
                  </label>
                  <div className="form-actions">
                    <button
                      className="btn btn-outline"
                      onClick={() => setStep(0)}
                    >
                      Back
                    </button>
                    <button
                      className="btn btn-primary"
                      onClick={() => setStep(2)}
                    >
                      Review choices <ArrowRight size={15} />
                    </button>
                  </div>
                </div>
              )}
              {step === 2 && (
                <div className="form-step">
                  <span className="eyebrow">STEP 03 · REVIEW</span>
                  <h2>Review your demonstration choices</h2>
                  <p className="muted">
                    In production, this screen would give users a final
                    opportunity to review their choices before submitting.
                  </p>
                  <div className="review-list">
                    <div>
                      <span>Submission mode</span>
                      <strong>
                        {anonymous ? "Anonymous" : "Identified (fictional)"}
                      </strong>
                    </div>
                    <div>
                      <span>Referral consent</span>
                      <strong>{consent ? "Selected" : "Not selected"}</strong>
                    </div>
                    <div>
                      <span>Next step</span>
                      <strong>Show support options and guidance</strong>
                    </div>
                  </div>
                  <div className="notice notice-info">
                    <LockKeyhole size={17} />
                    <p>
                      Consent is specific and can be withdrawn. Any real
                      case-management decisions are made by authorised human
                      personnel, not by the platform.
                    </p>
                  </div>
                  <div className="form-actions">
                    <button
                      className="btn btn-outline"
                      onClick={() => setStep(1)}
                    >
                      Back
                    </button>
                    <button
                      className="btn btn-primary"
                      onClick={() => {
                        setSubmitted(true);
                        notify(
                          "Sample journey completed — no report transmitted.",
                        );
                      }}
                    >
                      Complete sample journey <Check size={15} />
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
        <aside className="report-aside">
          <div className="panel">
            <div className="aside-icon">
              <HeartHandshake />
            </div>
            <h3>Designed around your choices</h3>
            <p>
              The proposed Hub will make information accessible, explain choices
              and support confidential referral pathways.
            </p>
            <ul>
              <li>
                <Check size={14} /> Clear information
              </li>
              <li>
                <Check size={14} /> Consent-aware design
              </li>
              <li>
                <Check size={14} /> Human-led decisions
              </li>
              <li>
                <Check size={14} /> Privacy by design
              </li>
            </ul>
          </div>
          <div className="panel mini-note">
            <strong>Important</strong>
            <p>
              The platform records and routes information. It does not determine
              whether a report is valid, decide a referral or make disciplinary
              decisions.
            </p>
          </div>
        </aside>
      </div>
    </>
  );
}
function Mentorship({
  query,
  setQuery,
  mentors,
  requested,
  setRequested,
  notify,
}: {
  query: string;
  setQuery: (s: string) => void;
  mentors: typeof import("./data/mock").mentors;
  requested: string[];
  setRequested: (v: string[]) => void;
  notify: (s: string) => void;
}) {
  return (
    <>
      <PageHeading
        eyebrow="MENTORSHIP NETWORK"
        title="Grow with guidance"
        description="Discover mentors, explore shared interests and build connections across the STEM community."
      />
      <div className="mentor-toolbar">
        <div className="search-field">
          <Search size={17} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by name, discipline or interest"
          />
        </div>
        <span className="result-count">{mentors.length} sample mentors</span>
      </div>
      <div className="mentor-grid">
        {mentors.map((m) => (
          <div className="mentor-card" key={m.name}>
            <div className={`mentor-avatar ${m.tone}`}>{m.initials}</div>
            <span className="mentor-verified">
              <ShieldCheck size={13} /> Sample profile
            </span>
            <h3>{m.name}</h3>
            <div className="mentor-field">{m.field}</div>
            <p>{m.institution}</p>
            <div className="mentor-focus">
              <span>AREAS OF SUPPORT</span>
              <strong>{m.focus}</strong>
            </div>
            <button
              className={`btn ${requested.includes(m.name) ? "btn-success" : "btn-primary"} full-btn`}
              onClick={() => {
                if (requested.includes(m.name)) {
                  notify("Sample mentorship request already added.");
                  return;
                }
                setRequested([...requested, m.name]);
                notify("Sample mentorship request added locally.");
              }}
            >
              {requested.includes(m.name) ? (
                <>
                  <Check size={15} /> Request noted
                </>
              ) : (
                "Request a connection"
              )}
            </button>
          </div>
        ))}
      </div>
      <div className="notice notice-info space-top">
        <HeartHandshake size={18} />
        <div>
          <strong>Mentorship is built on mutual choice.</strong>
          <p>
            In the live platform, matching preferences, availability,
            safeguarding expectations and institutional guidance will be
            confirmed during co-design.
          </p>
        </div>
      </div>
    </>
  );
}
function Community({ notify }: { notify: (s: string) => void }) {
  const [tab, setTab] = useState("All discussions");
  return (
    <>
      <PageHeading
        eyebrow="PEER COMMUNITY"
        title="Ideas grow when shared"
        description="A welcoming space for STEM students, staff and mentors to exchange experiences and learn together."
        action={
          <button
            className="btn btn-primary"
            onClick={() =>
              notify("Post creation is a simulated prototype interaction.")
            }
          >
            ＋ Start a discussion
          </button>
        }
      />
      <div className="community-layout">
        <div>
          <div className="tabs">
            {["All discussions", "My spaces", "Popular"].map((t) => (
              <button
                className={tab === t ? "tab-active" : ""}
                onClick={() => setTab(t)}
                key={t}
              >
                {t}
              </button>
            ))}
          </div>
          <div className="discussion-list">
            {discussions.map((d, i) => (
              <div className="discussion-card" key={d.title}>
                <div className="discussion-avatar">{["MN", "TN", "KD"][i]}</div>
                <div className="discussion-body">
                  <div className="discussion-meta">
                    <span>{d.category}</span>
                    <i>·</i>
                    {d.time}
                  </div>
                  <h3>{d.title}</h3>
                  <p>Started by {d.author}</p>
                  <div className="discussion-bottom">
                    <span>
                      <MessageCircle size={14} /> {d.replies} replies
                    </span>
                    <span className="pill-tag">{d.tag}</span>
                  </div>
                </div>
                <button
                  className="icon-btn"
                  onClick={() =>
                    notify("Discussion detail is a prototype placeholder.")
                  }
                >
                  <ChevronRight />
                </button>
              </div>
            ))}
          </div>
        </div>
        <aside className="panel community-aside">
          <div className="aside-icon">
            <Users />
          </div>
          <h3>Community guidelines</h3>
          <p>Help make this a respectful and supportive space for everyone.</p>
          <ul className="guideline-list">
            <li>Respect different experiences.</li>
            <li>Protect personal information.</li>
            <li>Challenge ideas, not people.</li>
            <li>Report harmful content to moderators.</li>
          </ul>
          <button
            className="text-link"
            onClick={() =>
              notify("Full community guidelines would be published here.")
            }
          >
            Read community guidelines <ArrowRight size={14} />
          </button>
        </aside>
      </div>
    </>
  );
}
function Library({ notify }: { notify: (s: string) => void }) {
  const items = [
    [
      "Toolkit",
      "Gender-Responsive Mentorship and Change Champions Toolkit",
      "Practical guidance for building inclusive mentorship.",
      "PDF · 24 pages",
    ],
    [
      "Guide",
      "Creating inclusive STEM learning environments",
      "Ideas and approaches for student-centred practice.",
      "Guide · 12 pages",
    ],
    [
      "Learning module",
      "Understanding gender-transformative approaches",
      "A short introduction to core concepts and practice.",
      "Module · 15 min",
    ],
    [
      "Resource pack",
      "Peer support conversation guide",
      "Prompts for constructive and supportive conversations.",
      "Resource pack · 8 pages",
    ],
  ];
  return (
    <>
      <PageHeading
        eyebrow="RESOURCE LIBRARY"
        title="Learn, reflect and take action"
        description="A curated collection of learning materials, practical tools and resources for a more inclusive STEM environment."
      />
      <div className="library-toolbar">
        <div className="search-field">
          <Search size={17} />
          <input placeholder="Search learning resources" />
        </div>
        <span className="result-count">48 sample resources</span>
      </div>
      <div className="resource-grid">
        {items.map((x, i) => (
          <div className="resource-card" key={x[1]}>
            <div className={`resource-cover cover-${i}`}>
              <span>{x[0]}</span>
              <BookOpen size={27} />
              <small>GTD HUB LEARNING</small>
            </div>
            <div className="resource-content">
              <span className="eyebrow">{x[0].toUpperCase()}</span>
              <h3>{x[1]}</h3>
              <p>{x[2]}</p>
              <div className="resource-foot">
                <span>{x[3]}</span>
                <button
                  className="text-link"
                  onClick={() =>
                    notify(
                      "This sample resource would open in the learning library.",
                    )
                  }
                >
                  Explore <ArrowRight size={14} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
function CaseWorkspace({
  statuses,
  setStatuses,
  notify,
}: {
  statuses: Record<string, string>;
  setStatuses: (v: Record<string, string>) => void;
  notify: (s: string) => void;
}) {
  const [selected, setSelected] = useState(cases[0].id);
  const current = cases.find((c) => c.id === selected)!;
  return (
    <>
      <PageHeading
        eyebrow="RESTRICTED DEMONSTRATION WORKSPACE"
        title="Case handling overview"
        description="A fictional view of how authorised personnel may review and manage workflow records within their institution."
      />
      <div className="notice notice-warning">
        <LockKeyhole size={18} />
        <div>
          <strong>Fictional case records only</strong>
          <p>
            No real case data is present. Access to real case information would
            be strictly limited, institution-scoped and audited.
          </p>
        </div>
      </div>
      <div className="case-layout">
        <div className="panel case-list">
          <div className="panel-title">
            <div>
              <h3>Sample case inbox</h3>
              <p>3 fictional records</p>
            </div>
            <span className="count-badge">03</span>
          </div>
          {cases.map((c) => (
            <button
              className={`case-row ${selected === c.id ? "selected" : ""}`}
              key={c.id}
              onClick={() => setSelected(c.id)}
            >
              <div className="case-row-top">
                <strong>{c.id}</strong>
                <span className="case-priority">{c.priority}</span>
              </div>
              <div className="case-row-type">{c.type}</div>
              <div className="case-row-bottom">
                <span>{c.institution.split(" ").slice(0, 3).join(" ")}</span>
                <span className="status-dot" /> {statuses[c.id] || c.status}
              </div>
            </button>
          ))}
        </div>
        <div className="panel case-detail">
          <div className="case-detail-head">
            <div>
              <span className="eyebrow">FICTIONAL RECORD</span>
              <h2>{current.id}</h2>
            </div>
            <span className="case-status">
              {statuses[current.id] || current.status}
            </span>
          </div>
          <div className="case-facts">
            <div>
              <span>Institution</span>
              <strong>{current.institution}</strong>
            </div>
            <div>
              <span>Received</span>
              <strong>{current.received}</strong>
            </div>
            <div>
              <span>Record type</span>
              <strong>{current.type}</strong>
            </div>
            <div>
              <span>Consent status</span>
              <strong>{current.consent}</strong>
            </div>
          </div>
          <div className="case-section">
            <h3>Workflow guidance</h3>
            <p>
              The authorised case handler reviews the information, acknowledges
              receipt and determines the appropriate pathway under the
              institution's approved protocol. The system supports recording and
              routing; it does not make decisions.
            </p>
          </div>
          <div className="case-section">
            <h3>Demonstration actions</h3>
            <p>
              Choose a simulated workflow state to see how the case workspace
              may respond.
            </p>
            <div className="case-actions">
              <button
                className="btn btn-outline"
                onClick={() => {
                  setStatuses({ ...statuses, [current.id]: "Acknowledged" });
                  notify("Fictional record marked acknowledged.");
                }}
              >
                Acknowledge
              </button>
              <button
                className="btn btn-primary"
                onClick={() => {
                  setStatuses({ ...statuses, [current.id]: "Under review" });
                  notify("Fictional record moved to review.");
                }}
              >
                Mark under review
              </button>
              <button
                className="btn btn-soft"
                onClick={() =>
                  notify(
                    "Referral action is simulated only; no service is contacted.",
                  )
                }
              >
                Record referral
              </button>
            </div>
          </div>
          <div className="audit-line">
            <ShieldCheck size={15} /> Simulated audit event · Demo user · No
            real record changed
          </div>
        </div>
      </div>
    </>
  );
}
function Institution({
  selected,
  setSelected,
}: {
  selected: string;
  setSelected: (s: string) => void;
}) {
  return (
    <>
      <PageHeading
        eyebrow="INSTITUTIONAL ADMINISTRATION"
        title="Institution overview"
        description="A sample institution-level view for authorised HEI administrators."
        action={
          <select
            className="select-control"
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
          >
            {institutions.map((i) => (
              <option key={i}>{i}</option>
            ))}
          </select>
        }
      />
      <div className="institution-banner">
        <div className="institution-seal">
          {selected === "All institutions"
            ? "11"
            : selected
                .split(" ")
                .map((x) => x[0])
                .join("")
                .slice(0, 3)}
        </div>
        <div>
          <span className="eyebrow">SELECTED INSTITUTION</span>
          <h2>{selected}</h2>
          <p>Institution-scoped sample dashboard · Fictional data</p>
        </div>
        <span className="institution-state">Demo configured</span>
      </div>
      <div className="stat-grid">
        <Stat
          icon={<Users />}
          label="Registered users"
          value="246"
          change="Illustrative sample"
        />
        <Stat
          icon={<HeartHandshake />}
          label="Mentorship links"
          value="64"
          change="Illustrative sample"
        />
        <Stat
          icon={<BookOpen />}
          label="Resource engagement"
          value="78%"
          change="Illustrative sample"
        />
        <Stat
          icon={<Activity />}
          label="Weekly active users"
          value="142"
          change="Illustrative sample"
        />
      </div>
      <div className="dashboard-grid">
        <div className="panel">
          <div className="panel-title">
            <div>
              <h3>Engagement trend</h3>
              <p>Illustrative weekly activity</p>
            </div>
            <span className="pill-tag">Sample</span>
          </div>
          <MiniChart />
        </div>
        <div className="panel">
          <div className="panel-title">
            <div>
              <h3>Institution administration</h3>
              <p>Common management tasks</p>
            </div>
            <Settings size={18} />
          </div>
          {[
            "Manage institution users",
            "Review role assignments",
            "Update support directory",
            "View institution reports",
          ].map((x, i) => (
            <button className="admin-action" key={x}>
              <span className="admin-action-icon">
                {[<Users />, <ShieldCheck />, <LifeBuoy />, <FileText />][i]}
              </span>
              {x}
              <ChevronRight size={15} />
            </button>
          ))}
        </div>
      </div>
    </>
  );
}
function Insights({
  selected,
  setSelected,
}: {
  selected: string;
  setSelected: (s: string) => void;
}) {
  return (
    <>
      <PageHeading
        eyebrow="PROGRAMME MONITORING & EVALUATION"
        title="Evidence for collective progress"
        description="A central, privacy-conscious view of platform adoption and engagement across participating institutions."
        action={
          <select
            className="select-control"
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
          >
            {institutions.map((i) => (
              <option key={i}>{i}</option>
            ))}
          </select>
        }
      />
      <div className="notice notice-info">
        <ShieldCheck size={18} />
        <div>
          <strong>Aggregated reporting by design.</strong>
          <p>
            Programme dashboards should use de-identified, aggregated
            information. Identifiable GBV case details are not displayed here.
          </p>
        </div>
      </div>
      <div className="stat-grid">
        <Stat
          icon={<Users />}
          label="Registered participants"
          value="1,284"
          change="Across 11 sample HEIs"
        />
        <Stat
          icon={<Activity />}
          label="Weekly active users"
          value="836"
          change="Illustrative WAU"
        />
        <Stat
          icon={<CalendarDays />}
          label="Monthly active users"
          value="1,046"
          change="Illustrative MAU"
        />
        <Stat
          icon={<HeartHandshake />}
          label="Mentorship connections"
          value="326"
          change="Illustrative total"
        />
      </div>
      <div className="dashboard-grid insight-grid">
        <div className="panel">
          <div className="panel-title">
            <div>
              <h3>Platform engagement</h3>
              <p>Illustrative active users over six weeks</p>
            </div>
            <span className="pill-tag">Sample data</span>
          </div>
          <MiniChart />
        </div>
        <div className="panel">
          <div className="panel-title">
            <div>
              <h3>Engagement by area</h3>
              <p>Illustrative distribution</p>
            </div>
          </div>
          <div className="bar-list">
            {[
              ["Learning resources", 82],
              ["Mentorship", 68],
              ["Peer community", 56],
              ["Support directory", 42],
            ].map(([name, v]) => (
              <div key={name as string}>
                <div>
                  <span>{name}</span>
                  <strong>{v}%</strong>
                </div>
                <div className="bar-track">
                  <i style={{ width: `${v}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="panel metric-definition">
        <strong>Measurement note</strong>
        <p>
          WAU/MAU definitions and adoption targets should be agreed with the
          project M&E team. An active user should represent a meaningful
          activity, not merely an app opening or background request. Anonymous
          reporting activity should be counted separately using
          privacy-preserving aggregate events.
        </p>
      </div>
    </>
  );
}
function MiniChart() {
  return (
    <div className="chart-wrap">
      <div className="chart-y">
        <span>1,000</span>
        <span>750</span>
        <span>500</span>
        <span>250</span>
        <span>0</span>
      </div>
      <div className="chart">
        <div className="chart-gridlines">
          <i />
          <i />
          <i />
          <i />
          <i />
        </div>
        <svg
          viewBox="0 0 600 190"
          preserveAspectRatio="none"
          aria-label="Illustrative engagement trend chart"
        >
          <defs>
            <linearGradient id="area" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0" stopColor="#4b9385" stopOpacity=".25" />
              <stop offset="1" stopColor="#4b9385" stopOpacity="0" />
            </linearGradient>
          </defs>
          <path
            d="M0 145 C55 137 70 115 120 121 S190 105 240 110 S310 70 360 83 S420 58 480 66 S550 30 600 35 L600 190 L0 190Z"
            fill="url(#area)"
          />
          <path
            d="M0 145 C55 137 70 115 120 121 S190 105 240 110 S310 70 360 83 S420 58 480 66 S550 30 600 35"
            fill="none"
            stroke="#397d70"
            strokeWidth="3"
            strokeLinecap="round"
          />
        </svg>
        <div className="chart-x">
          <span>Wk 1</span>
          <span>Wk 2</span>
          <span>Wk 3</span>
          <span>Wk 4</span>
          <span>Wk 5</span>
          <span>Wk 6</span>
        </div>
      </div>
    </div>
  );
}
function Administration({ notify }: { notify: (s: string) => void }) {
  return (
    <>
      <PageHeading
        eyebrow="PLATFORM CONFIGURATION"
        title="Administration"
        description="A central place for authorised administrators to manage the platform's configuration and governance."
      />
      <div className="admin-grid">
        {[
          {
            icon: <Users />,
            title: "User management",
            desc: "User accounts, invitations and account status.",
          },
          {
            icon: <ShieldCheck />,
            title: "Roles & permissions",
            desc: "Role definitions and institution-scoped access.",
          },
          {
            icon: <Building2 />,
            title: "Institutions",
            desc: "Participating HEI configuration and onboarding.",
          },
          {
            icon: <LifeBuoy />,
            title: "Support directory",
            desc: "Institution-approved referral and support information.",
          },
          {
            icon: <Bell />,
            title: "Notifications",
            desc: "Email, SMS and notification configuration.",
          },
          {
            icon: <ClipboardList />,
            title: "Audit & governance",
            desc: "System activity and access review.",
          },
        ].map((x) => (
          <button
            className="admin-card"
            key={x.title}
            onClick={() =>
              notify(
                `${x.title} is represented as a configuration area in this prototype.`,
              )
            }
          >
            <span className="admin-card-icon">{x.icon}</span>
            <strong>{x.title}</strong>
            <p>{x.desc}</p>
            <span className="admin-card-link">
              Explore <ArrowRight size={14} />
            </span>
          </button>
        ))}
      </div>
      <div className="notice notice-info space-top">
        <LockKeyhole size={18} />
        <div>
          <strong>Production governance principle</strong>
          <p>
            Administrative privileges will be limited, protected with MFA,
            logged and scoped according to approved responsibilities. This demo
            does not implement production access controls.
          </p>
        </div>
      </div>
    </>
  );
}
function Building2() {
  return <Users size={20} />;
}
export default App;
