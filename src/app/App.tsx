import { useEffect, useMemo, useState } from "react";
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
  DownloadIcon,
} from "lucide-react";
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
import { api, apiConfigured } from "../services/api";
import { Brand, Welcome, RoleSelection, Dashboard, Support, Reporting, Mentorship, Community, Learning, CaseWorkspace, Organisation, Programme, Administration, Help } from "../pages/ScreenComponents";
import { useAppRouter } from "./router";
import Footer from "../components/layout/Footer";

type Page = string;
const routeByPage: Record<string, string> = {
  Welcome: "/welcome", "Role selection": "/select-role", Overview: "/overview",
  "Find support": "/support", "Safe reporting": "/reporting", Mentorship: "/mentorship",
  Community: "/community", "Learning library": "/library", "Case workspace": "/cases",
  "Organisation overview": "/organisation", "Programme insights": "/insights",
  Administration: "/admin", "Help & guidance": "/help",
};
const pageByRoute = Object.fromEntries(Object.entries(routeByPage).map(([page, route]) => [route, page]));
const iconMap: Record<string, any> = {
  Overview: Home,
  "Find support": Search,
  "Safe reporting": ShieldCheck,
  Mentorship: HeartHandshake,
  Community: MessageCircle,
  "Learning library": BookOpen,
  "Case workspace": BriefcaseBusiness,
  "Organisation overview": Building2,
  "Programme insights": ChartNoAxesColumnIncreasing,
  Administration: Settings,
};
const navIcon = (name: string) => {
  const Icon = iconMap[name] || Home;
  return <Icon size={19} strokeWidth={2.1} />;
};

export default function App() {
  const [role, setRole] = useState<DemoRole>("Member");
  const { pathname, navigate } = useAppRouter();
  const page: Page = pageByRoute[pathname] || "Welcome";
  const [menuOpen, setMenuOpen] = useState(false);
  const [roleOpen, setRoleOpen] = useState(false);
  const [toast, setToast] = useState("");
  const [search, setSearch] = useState("");
  const [reportStep, setReportStep] = useState(0);
  const [anonymous, setAnonymous] = useState(true);
  const [consent, setConsent] = useState(false);
  const [mentorQuery, setMentorQuery] = useState("");
  const [requested, setRequested] = useState<string[]>([]);
  const [caseStatus, setCaseStatus] = useState<Record<string, string>>({});
  const [selectedCase, setSelectedCase] = useState(cases[0].id);
  const [organisation, setOrganisation] = useState(organisations[1]);
  const [activeTab, setActiveTab] = useState("All");
  const [installPrompt, setInstallPrompt] = useState<any>(null);
  const [apiState, setApiState] = useState<
    "local" | "connected" | "unavailable"
  >("local");
  const [apiOverview, setApiOverview] = useState<any>(null);
  const [mentorList, setMentorList] = useState(mentors);
  const [mentorSource, setMentorSource] = useState<
    "local" | "connected" | "unavailable"
  >("local");

  useEffect(() => {
    setMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "auto" });
  }, [pathname]);

  useEffect(() => {
    if (!apiConfigured) return;
    Promise.all([api.health(), api.demoOverview()])
      .then(([, overview]) => {
        setApiOverview(overview);
        setApiState("connected");
      })
      .catch(() => setApiState("unavailable"));
  }, []);

  useEffect(() => {
    if (!apiConfigured) return;

    let active = true;

    api
      .demoMentors()
      .then((data) => {
        if (!active) return;

        const mappedMentors = data.map((mentor) => {
          const focusParts = mentor.focus
            .split("·")
            .map((part) => part.trim())
            .filter(Boolean);

          const searchableText =
            `${mentor.field} ${mentor.focus}`.toLowerCase();

          const categories = [
            "Research",
            "Career",
            "Academic",
            "Leadership",
            "Wellbeing",
          ].filter((category) =>
            searchableText.includes(category.toLowerCase()),
          );

          return {
            id: mentor.id,
            name: mentor.name,
            role: mentor.field,
            bio: `${mentor.focus}. Institution: ${mentor.institution}.`,
            initials: mentor.name
              .replace(/^(Dr\\.?|Mr\\.?|Mrs\\.?|Ms\\.?|Eng\\.?)\\s*/i, "")
              .split(/\\s+/)
              .map((part) => part[0])
              .join("")
              .slice(0, 2)
              .toUpperCase(),
            tags: [
              ...new Set([...categories, ...focusParts, mentor.institution]),
            ],
          };
        });

        setMentorList(mappedMentors);
        setMentorSource("connected");
      })
      .catch(() => {
        if (!active) return;
        setMentorSource("unavailable");
        // Keep the existing local mentor records as fallback.
      });

    return () => {
      active = false;
    };
  }, []);

  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2800);
  };
  const open = (next: string) => {
    navigate(routeByPage[next] || "/overview");
    setMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };
  const switchRole = (next: DemoRole) => {
    setRole(next);
    navigate("/overview");
    setRoleOpen(false);
    setMenuOpen(false);
  };
  const visibleMentors = useMemo(
    () =>
      mentorList.filter(
        (m) =>
          `${m.name} ${m.role} ${m.tags.join(" ")}`
            .toLowerCase()
            .includes(mentorQuery.toLowerCase()) &&
          (activeTab === "All" || m.tags.includes(activeTab)),
      ),
    [mentorList, mentorQuery, activeTab],
  );

  (window as any).onbeforeinstallprompt = (event: any) => {
    event.preventDefault();
    setInstallPrompt(event);
  };
  const install = async () => {
    if (!installPrompt) {
      notify(
        "Use your browser menu to install or add GTD Hub to your home screen.",
      );
      return;
    }
    await installPrompt.prompt();
    setInstallPrompt(null);
  };

  const quickExit = () => {
    open("Overview");
    setRoleOpen(false);
    notify(
      "Quick Exit demonstration activated. This concept does not contact an external service.",
    );
  };

  if (page === "Welcome")
    return <Welcome onStart={() => open("Role selection")} />;
  if (page === "Role selection")
    return (
      <RoleSelection
        onBack={() => open("Welcome")}
        onSelect={(r) => switchRole(r)}
      />
    );

  const nav = navByRole[role];
  return (
    <div className="min-h-screen bg-[#f7f8fc] text-brand-ink">
      <div className="demo-ribbon">
        PROPOSAL DEMONSTRATOR <span>·</span> FICTIONAL DATA ONLY{" "}
        <span className="hidden sm:inline ml-auto">
          Concept experience — not a live support service
        </span>
      </div>
      <div className="app-frame">
        <aside className={`sidebar ${menuOpen ? "sidebar-open" : ""}`}>
          <div className="brand-lockup">
            <Brand compact={false} />
            <button
              className="icon-button mobile-only"
              onClick={() => setMenuOpen(false)}
              aria-label="Close navigation"
            >
              <X />
            </button>
          </div>
          <div className="role-label">MY ROLE (DEMO)</div>
          <button
            className="role-picker"
            onClick={() => setRoleOpen(!roleOpen)}
            aria-expanded={roleOpen}
          >
            <UserRound size={18} />
            <span>
              <b>{role}</b>
              <small>
                {role === "Member"
                  ? "Help seeker · Primary user"
                  : "Explore demo workspace"}
              </small>
            </span>
            <ChevronDown size={16} />
          </button>
          {roleOpen && (
            <div className="role-popover">
              {roles.map((r) => (
                <button
                  key={r}
                  onClick={() => switchRole(r)}
                  className={r === role ? "selected" : ""}
                >
                  {r}
                  {r === role && <Check size={15} />}
                </button>
              ))}
            </div>
          )}
          <div className="nav-label">WORKSPACE</div>
          <nav className="side-nav" aria-label="Main navigation">
            {nav.map((item) => (
              <button
                key={item}
                onClick={() => open(item)}
                className={`side-link ${page === item ? "active" : ""}`}
              >
                {navIcon(item)}
                <span>{item}</span>
              </button>
            ))}
          </nav>
          <div className="sidebar-bottom">
            <button className="quick-exit" onClick={quickExit}>
              <LogOut size={17} /> Quick Exit
            </button>
            <button
              className="help-link"
              onClick={() => open("Help & guidance")}
            >
              <CircleHelp size={17} /> Help & guidance
            </button>
            <div className="sidebar-wave" />
          </div>
        </aside>
        {menuOpen && (
          <button
            className="mobile-scrim"
            aria-label="Close navigation overlay"
            onClick={() => setMenuOpen(false)}
          />
        )}
        <main className="main-column">
          <header className="topbar">
            <button
              className="icon-button mobile-only"
              onClick={() => setMenuOpen(true)}
              aria-label="Open navigation"
            >
              <Menu />
            </button>
            <div className="breadcrumbs">
              <Home size={16} />
              <ChevronRight size={14} />
              <b>{page}</b>
            </div>
            <div className="top-tools">
              <label className="search-box">
                <Search size={17} />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search support, resources, events..."
                />
                <kbd>Ctrl K</kbd>
              </label>
              <button
                className="icon-button"
                aria-label="Notifications"
                onClick={() =>
                  notify("You are all caught up in this fictional demo.")
                }
              >
                <Bell />
                <i />
              </button>
              <button
                className="profile-chip"
                onClick={() => setRoleOpen(!roleOpen)}
              >
                <span className="profile-avatar">TM</span>
                <span>
                  <b>Tadiwa M.</b>
                  <small>{role}</small>
                </span>
                <ChevronDown size={15} />
              </button>
              <button
                className="install-button"
                onClick={install}
                title="Install GTD Hub"
              >
                <span>Install</span>
                <DownloadIcon />
              </button>
            </div>
          </header>
          <div className="page-content">
            {page === "Overview" && (
              <Dashboard
                role={role}
                go={open}
                notify={notify}
                overview={apiOverview}
                apiState={apiState}
              />
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
                notify={notify}
              />
            )}
            {page === "Mentorship" && (
              <Mentorship
                query={mentorQuery}
                setQuery={setMentorQuery}
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                list={visibleMentors}
                listSource={mentorSource}
                requested={requested}
                setRequested={setRequested}
                notify={notify}
              />
            )}
            {page === "Community" && <Community notify={notify} />}
            {page === "Learning library" && <Learning notify={notify} />}
            {page === "Case workspace" && (
              <CaseWorkspace
                selected={selectedCase}
                setSelected={setSelectedCase}
                statuses={caseStatus}
                setStatuses={setCaseStatus}
              />
            )}
            {page === "Organisation overview" && (
              <Organisation
                selected={organisation}
                setSelected={setOrganisation}
              />
            )}
            {page === "Programme insights" && (
              <Programme
                selected={organisation}
                setSelected={setOrganisation}
              />
            )}
            {page === "Administration" && <Administration notify={notify} />}
            {page === "Help & guidance" && <Help />}
            {![
              "Overview",
              "Find support",
              "Safe reporting",
              "Mentorship",
              "Community",
              "Learning library",
              "Case workspace",
              "Organisation overview",
              "Programme insights",
              "Administration",
              "Help & guidance",
            ].includes(page) && (
              <Dashboard
                role={role}
                go={open}
                notify={notify}
                overview={apiOverview}
                apiState={apiState}
              />
            )}
          </div>
          <Footer onQuickExit={quickExit} />
        </main>
      </div>
      <div className="prototype-note">
        <ShieldCheck size={14} /> Demonstration environment · Fictional users
        and records · No real reports are submitted
      </div>
      {toast && (
        <div className="toast" role="status">
          <Check size={17} />
          {toast}
        </div>
      )}
    </div>
  );
}
