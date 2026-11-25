import { useEffect, useState } from "react";
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
  metrics,
  organisations,
  supportOptions,
  type DemoRole,
} from "../data/demo";
import { api, apiConfigured } from "../services/api";
import {
  Brand,
  Welcome,
  Dashboard,
  Support,
  Reporting,
  Learning,
  CaseWorkspace,
  Organisation,
  Programme,
  Administration,
  Help,
} from "../pages/ScreenComponents";
import { useAppRouter } from "./router";
import { useAuth } from "../features/auth/AuthContext";
import LoginPage from "../features/auth/LoginPage";
import Footer from "../components/layout/Footer";
import MentorshipPage from "../features/mentorship/MentorshipPage";
import CommunityPage from "../features/community/CommunityPage";

type Page = string;
const routeByPage: Record<string, string> = {
  Welcome: "/welcome",
  "Role selection": "/select-role",
  Overview: "/overview",
  "Find support": "/support",
  "Safe reporting": "/reporting",
  Mentorship: "/mentorship",
  Community: "/community",
  "Learning library": "/library",
  "Case workspace": "/cases",
  "Organisation overview": "/organisation",
  "Programme insights": "/insights",
  Administration: "/admin",
  "Help & guidance": "/help",
};
const pageByRoute = Object.fromEntries(
  Object.entries(routeByPage).map(([page, route]) => [route, page]),
);
const landingByRole: Record<DemoRole, string> = {
  Member: "/overview",
  Mentor: "/overview",
  Moderator: "/community",
  "Case Handler": "/cases",
  "Organisation Administrator": "/organisation",
  "Programme Administrator": "/insights",
};
const pagePermissions: Array<[string, string]> = [
  ["Overview", "dashboard:read"],
  ["Find support", "support:read"],
  ["Safe reporting", "reporting:create"],
  ["Mentorship", "mentorship:read"],
  ["Community", "community:read"],
  ["Learning library", "learning:read"],
  ["Case workspace", "cases:read"],
  ["Organisation overview", "organisation:read"],
  ["Programme insights", "programme:read"],
  ["Administration", "administration:read"],
];
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
  const { user, loading: authLoading, logout } = useAuth();
  const role: DemoRole = user?.role ?? "Member";
  const { pathname, navigate } = useAppRouter();
  const page: Page = pageByRoute[pathname] || "Welcome";
  const [menuOpen, setMenuOpen] = useState(false);
  const [toast, setToast] = useState("");
  const [search, setSearch] = useState("");
  const [reportStep, setReportStep] = useState(0);
  const [submittedCaseRef, setSubmittedCaseRef] = useState("");
  const [anonymous, setAnonymous] = useState(true);
  const [consent, setConsent] = useState(false);
  const [organisation, setOrganisation] = useState(organisations[1]);
  const [installPrompt, setInstallPrompt] = useState<any>(null);
  const [apiState, setApiState] = useState<
    "local" | "connected" | "unavailable"
  >("local");
  const [apiOverview, setApiOverview] = useState<any>(null);

  useEffect(() => {
    setMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "auto" });
  }, [pathname]);

  useEffect(() => {
    if (authLoading) return;
    const publicPage = page === "Welcome" || pathname === "/login";
    if (!user && !publicPage) navigate("/login");
  }, [authLoading, user, page, pathname, navigate]);

  useEffect(() => {
    if (authLoading || !user) return;
    const requestedPage = pageByRoute[pathname];
    if (!requestedPage || pathname === "/login") {
      navigate(landingByRole[user.role]);
      return;
    }
    if (
      requestedPage !== "Help & guidance" &&
      !user.permissions.includes(pagePermissions.find(([name]) => name === requestedPage)?.[1] ?? "__denied__")
    ) {
      navigate(landingByRole[user.role]);
    }
  }, [authLoading, user, pathname, navigate]);

  useEffect(() => {
    if (!apiConfigured || !user) return;
    Promise.all([api.health(), api.demoOverview()])
      .then(([, overview]) => {
        setApiOverview(overview);
        setApiState("connected");
      })
      .catch(() => setApiState("unavailable"));
  }, [user?.id]);

  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2800);
  };
  const nav = user
    ? pagePermissions.filter(([, permission]) => user.permissions.includes(permission)).map(([name]) => name)
    : [];
  const open = (next: string) => {
    if (!nav.includes(next) && next !== "Help & guidance") {
      notify("This screen is not available to your account role.");
      return;
    }
    navigate(routeByPage[next] || "/overview");
    setMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };
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
    open(nav.includes("Overview") ? "Overview" : nav[0]);
    notify(
      "Quick Exit demonstration activated. This concept does not contact an external service.",
    );
  };

  if (authLoading) {
    return <div className="auth-loading">Loading your GTD Hub workspace…</div>;
  }
  if (page === "Welcome" && pathname !== "/login" && !user)
    return <Welcome onStart={() => navigate("/login")} />;
  if (pathname === "/login" && !user) {
    return (
      <LoginPage
        onBack={() => navigate("/welcome")}
        onSuccess={(signedInUser) =>
          navigate(
            (
              {
                Member: "/overview",
                Mentor: "/overview",
                Moderator: "/community",
                "Case Handler": "/cases",
                "Organisation Administrator": "/organisation",
                "Programme Administrator": "/insights",
              } as const
            )[signedInUser.role],
          )
        }
      />
    );
  }
  if (!user) return <div className="auth-loading">Redirecting to sign in…</div>;
  if (
    page === "Welcome" ||
    pathname === "/login" ||
    (page !== "Help & guidance" && !nav.includes(page))
  ) {
    return (
      <div className="auth-loading">Opening your authorised workspace…</div>
    );
  }
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
          <div className="role-label">SIGNED IN AS</div>
          <div className="role-picker account-identity">
            <UserRound size={18} />
            <span>
              <b>{user.full_name}</b>
              <small>
                {role}
                {user.institution_name ? ` · ${user.institution_name}` : ""}
              </small>
            </span>
          </div>
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
                onClick={async () => {
                  await logout();
                  navigate("/login");
                }}
                title="Sign out"
              >
                <span className="profile-avatar">
                  {user.full_name
                    .split(/\\s+/)
                    .map((part) => part[0])
                    .slice(0, 2)
                    .join("")
                    .toUpperCase()}
                </span>
                <span>
                  <b>{user.full_name}</b>
                  <small>Sign out · {role}</small>
                </span>
                <LogOut size={15} />
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
                displayName={user.full_name}
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
                institutionId={user?.institution_id ?? undefined}
                submittedCaseRef={submittedCaseRef}
                setSubmittedCaseRef={setSubmittedCaseRef}
              />
            )}
            {page === "Mentorship" && <MentorshipPage notify={notify} />}
            {page === "Community" && <CommunityPage notify={notify} />}
            {page === "Learning library" && <Learning notify={notify} />}
            {page === "Case workspace" && <CaseWorkspace />}
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
                displayName={user.full_name}
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
