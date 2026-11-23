import { useEffect, useMemo, useState } from "react";
import {
  Activity, ArrowLeft, ArrowRight, Bell, BookOpen, BriefcaseBusiness, Building2, CalendarDays,
  Check, ChevronDown, ChevronRight, CircleHelp, ClipboardList, FileText, Filter, GraduationCap,
  Handshake, Heart, HeartHandshake, Home, Info, LifeBuoy, LockKeyhole, LogOut, Menu, MessageCircle,
  Search, ShieldCheck, Users, X, Zap, ChartNoAxesColumnIncreasing, Scale, Stethoscope, BookMarked,
  Settings, Landmark, UserRound, Sparkles
} from "lucide-react";
import { activities, cases, discussions, mentors, metrics, navByRole, organisations, roles, supportOptions, type DemoRole } from "./data/demo";
import { api, apiConfigured } from "./lib/api";

type Page = string;
const iconMap: Record<string, any> = {
  Overview: Home, "Find support": Search, "Safe reporting": ShieldCheck, Mentorship: HeartHandshake,
  Community: MessageCircle, "Learning library": BookOpen, "Case workspace": BriefcaseBusiness,
  "Organisation overview": Building2, "Programme insights": ChartNoAxesColumnIncreasing, Administration: Settings
};
const navIcon = (name: string) => {
  const Icon = iconMap[name] || Home;
  return <Icon size={19} strokeWidth={2.1} />;
};

export default function App() {
  const [role, setRole] = useState<DemoRole>("Member");
  const [page, setPage] = useState<Page>("Welcome");
  const [menuOpen, setMenuOpen] = useState(false);
  const [roleOpen, setRoleOpen] = useState(false);
  const [toast, setToast] = useState("");
  const [search, setSearch] = useState("");
  const [reportStep, setReportStep] = useState(0);
  const [anonymous, setAnonymous] = useState(true);
  const [consent, setConsent] = useState(false);
  const [mentorQuery, setMentorQuery] = useState("");
  const [requested, setRequested] = useState<string[]>([]);
  const [caseStatus, setCaseStatus] = useState<Record<string,string>>({});
  const [selectedCase, setSelectedCase] = useState(cases[0].id);
  const [organisation, setOrganisation] = useState(organisations[1]);
  const [activeTab, setActiveTab] = useState("All");
  const [installPrompt, setInstallPrompt] = useState<any>(null);
  const [apiState, setApiState] = useState<"local" | "connected" | "unavailable">("local");
  const [apiOverview, setApiOverview] = useState<any>(null);

  useEffect(() => {
    if (!apiConfigured) return;
    Promise.all([api.health(), api.demoOverview()]).then(([, overview]) => {
      setApiOverview(overview);
      setApiState("connected");
    }).catch(() => setApiState("unavailable"));
  }, []);

  const notify = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 2800); };
  const open = (next: string) => { setPage(next); setMenuOpen(false); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const switchRole = (next: DemoRole) => { setRole(next); setPage("Overview"); setRoleOpen(false); setMenuOpen(false); };
  const visibleMentors = useMemo(() => mentors.filter(m => `${m.name} ${m.role} ${m.tags.join(" ")}`.toLowerCase().includes(mentorQuery.toLowerCase()) && (activeTab === "All" || m.tags.includes(activeTab))), [mentorQuery, activeTab]);

  (window as any).onbeforeinstallprompt = (event: any) => { event.preventDefault(); setInstallPrompt(event); };
  const install = async () => {
    if (!installPrompt) { notify("Use your browser menu to install or add GTD Hub to your home screen."); return; }
    await installPrompt.prompt(); setInstallPrompt(null);
  };

  const quickExit = () => { open("Overview"); setRoleOpen(false); notify("Quick Exit demonstration activated. This concept does not contact an external service."); };

  if (page === "Welcome") return <Welcome onStart={() => open("Role selection")} />;
  if (page === "Role selection") return <RoleSelection onBack={() => open("Welcome")} onSelect={(r) => switchRole(r)} />;

  const nav = navByRole[role];
  return <div className="min-h-screen bg-[#f7f8fc] text-brand-ink">
    <div className="demo-ribbon">PROPOSAL DEMONSTRATOR <span>·</span> FICTIONAL DATA ONLY <span className="hidden sm:inline ml-auto">Concept experience — not a live support service</span></div>
    <div className="app-frame">
      <aside className={`sidebar ${menuOpen ? "sidebar-open" : ""}`}>
        <div className="brand-lockup">
          <Brand compact={false}/>
          <button className="icon-button mobile-only" onClick={() => setMenuOpen(false)} aria-label="Close navigation"><X/></button>
        </div>
        <div className="role-label">MY ROLE (DEMO)</div>
        <button className="role-picker" onClick={() => setRoleOpen(!roleOpen)} aria-expanded={roleOpen}>
          <UserRound size={18}/><span><b>{role}</b><small>{role === "Member" ? "Help seeker · Primary user" : "Explore demo workspace"}</small></span><ChevronDown size={16}/>
        </button>
        {roleOpen && <div className="role-popover">{roles.map(r => <button key={r} onClick={() => switchRole(r)} className={r===role?"selected":""}>{r}{r===role&&<Check size={15}/>}</button>)}</div>}
        <div className="nav-label">WORKSPACE</div>
        <nav className="side-nav" aria-label="Main navigation">
          {nav.map(item => <button key={item} onClick={() => open(item)} className={`side-link ${page===item?"active":""}`}>{navIcon(item)}<span>{item}</span></button>)}
        </nav>
        <div className="sidebar-bottom">
          <button className="quick-exit" onClick={quickExit}><LogOut size={17}/> Quick Exit</button>
          <button className="help-link" onClick={() => open("Help & guidance")}><CircleHelp size={17}/> Help & guidance</button>
          <div className="sidebar-wave"/>
        </div>
      </aside>
      {menuOpen && <button className="mobile-scrim" aria-label="Close navigation overlay" onClick={() => setMenuOpen(false)}/>}
      <main className="main-column">
        <header className="topbar">
          <button className="icon-button mobile-only" onClick={() => setMenuOpen(true)} aria-label="Open navigation"><Menu/></button>
          <div className="breadcrumbs"><Home size={16}/><ChevronRight size={14}/><b>{page}</b></div>
          <div className="top-tools">
            <label className="search-box"><Search size={17}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search support, resources, events..."/><kbd>Ctrl K</kbd></label>
            <button className="icon-button" aria-label="Notifications" onClick={() => notify("You are all caught up in this fictional demo.")}><Bell/><i/></button>
            <button className="profile-chip" onClick={() => setRoleOpen(!roleOpen)}><span className="profile-avatar">TM</span><span><b>Tadiwa M.</b><small>{role}</small></span><ChevronDown size={15}/></button>
            <button className="install-button" onClick={install} title="Install GTD Hub"><span>Install</span><DownloadIcon/></button>
          </div>
        </header>
        <div className="page-content">
          {page==="Overview" && <Dashboard role={role} go={open} notify={notify} overview={apiOverview} apiState={apiState}/>}
          {page==="Find support" && <Support notify={notify}/>}
          {page==="Safe reporting" && <Reporting step={reportStep} setStep={setReportStep} anonymous={anonymous} setAnonymous={setAnonymous} consent={consent} setConsent={setConsent} notify={notify}/>}
          {page==="Mentorship" && <Mentorship query={mentorQuery} setQuery={setMentorQuery} activeTab={activeTab} setActiveTab={setActiveTab} list={visibleMentors} requested={requested} setRequested={setRequested} notify={notify}/>}
          {page==="Community" && <Community notify={notify}/>}
          {page==="Learning library" && <Learning notify={notify}/>}
          {page==="Case workspace" && <CaseWorkspace selected={selectedCase} setSelected={setSelectedCase} statuses={caseStatus} setStatuses={setCaseStatus}/>}
          {page==="Organisation overview" && <Organisation selected={organisation} setSelected={setOrganisation}/>}
          {page==="Programme insights" && <Programme selected={organisation} setSelected={setOrganisation}/>}
          {page==="Administration" && <Administration notify={notify}/>}
          {page==="Help & guidance" && <Help/>}
          {!["Overview","Find support","Safe reporting","Mentorship","Community","Learning library","Case workspace","Organisation overview","Programme insights","Administration","Help & guidance"].includes(page) && <Dashboard role={role} go={open} notify={notify} overview={apiOverview} apiState={apiState}/>}
        </div>
        <footer className="app-footer"><span>GTD Hub · PROGEN-Hub for STEM</span><span>Responsive · Mobile-first · WCAG 2.1 AA design target</span><button onClick={quickExit}><Zap size={14}/> Quick Exit</button></footer>
      </main>
    </div>
    <div className="prototype-note"><ShieldCheck size={14}/> Demonstration environment · Fictional users and records · No real reports are submitted</div>
    {toast && <div className="toast" role="status"><Check size={17}/>{toast}</div>}
  </div>;
}
function DownloadIcon(){return <ArrowRight size={15}/>}

function Brand({compact=true}:{compact?:boolean}) {
  return <div className="brand">
    <div className="brand-symbol" aria-hidden="true"><i/><i/><i/><i/><i/></div>
    <div><div className="brand-word">gtd<span>hub</span></div>{!compact&&<small>GENDER-TRANSFORMATIVE DIGITAL HUB</small>}</div>
  </div>;
}
function Welcome({onStart}:{onStart:()=>void}) {
  return <div className="entry-screen">
    <div className="entry-top"><Brand/><span className="demo-pill">DEMO</span></div>
    <div className="entry-hero">
      <div className="entry-copy"><p className="eyebrow">CONNECT · SUPPORT · TRANSFORM</p><h1>A safer, more connected space for everyone.</h1><p>Explore a concept for support, reporting, mentorship, learning and action on gender equality.</p><button className="primary-button" onClick={onStart}>Explore the demo <ArrowRight size={19}/></button><div className="demo-warning"><Info size={17}/> Proposal demonstrator only. Fictional data. No real reporting or live services.</div></div>
      <div className="entry-people" aria-label="Illustration of a diverse group of STEM community members"><div className="people-orb orb-a"/><div className="people-orb orb-b"/><div className="people-caption">Belonging. Opportunity. Change.</div></div>
    </div>
  </div>;
}
function RoleSelection({onBack,onSelect}:{onBack:()=>void,onSelect:(r:DemoRole)=>void}) {
  const descriptions:Record<DemoRole,string> = {
    Member:"Access support, reporting, mentorship and learning.",
    Mentor:"Guide, support and connect with members.",
    Moderator:"Support safe and respectful community spaces.",
    "Case Handler":"Manage and refer fictional support cases.",
    "Organisation Administrator":"Oversee an organisation's GTD Hub workspace.",
    "Programme Administrator":"View programme insights across organisations."
  };
  const icons=[Users,GraduationCap,ShieldCheck,BriefcaseBusiness,Landmark,ChartNoAxesColumnIncreasing];
  return <div className="role-screen">
    <button className="back-link" onClick={onBack}><ArrowLeft size={17}/> Back</button><Brand/>
    <p className="eyebrow mt-10">INTERACTIVE ROLE EXPLORATION</p><h1>Explore GTD Hub as a different user</h1><p className="lead">Choose a role to experience the key features and workflows in the demo.</p>
    <div className="role-grid">{roles.map((r,i)=>{const Icon=icons[i];return <button key={r} onClick={()=>onSelect(r)} className={`role-card role-${i}`}><Icon size={30}/><span><b>{r}</b><small>{descriptions[r]}</small></span><ArrowRight className="role-arrow"/></button>})}</div>
    <div className="demo-warning"><Info size={17}/> All accounts, identities and records are fictional. This demonstration does not receive real reports.</div>
  </div>;
}
function PageTitle({eyebrow,title,description,action}:{eyebrow:string,title:string,description:string,action?:React.ReactNode}) {
  return <div className="page-title"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="lead">{description}</p></div>{action}</div>;
}
function Dashboard({role,go,notify,overview,apiState}:{role:DemoRole,go:(p:string)=>void,notify:(s:string)=>void,overview:any,apiState:"local"|"connected"|"unavailable"}) {
  const member=role==="Member";
  return <div className="space-y-6">
    <section className="welcome-card">
      <div className="welcome-text"><p className="eyebrow">MONDAY, 23 NOVEMBER 2026</p><h1>Good morning, <em>Tadiwa</em> 👋</h1><p>Welcome to GTD Hub — a safe, inclusive space for support, mentorship, learning and action on gender equality in STEM.</p><span className="gold-rule"/></div>
      <div className="welcome-image"><div className="image-placeholder"><Users size={76}/><span>A connected STEM community</span></div></div>
    </section>
    <section className="metric-grid">{metrics.map((m,i)=>{const Icon=[Users,Handshake,BookOpen,ChartNoAxesColumnIncreasing][i];const values=overview?[overview.members,overview.mentorship_connections,overview.resources,`${overview.engagement_percent}%`]:null;return <div className={`metric-card ${m.tone}`} key={m.label}><Icon size={31}/><div><b>{values?values[i]:m.value}</b><span>{m.label}</span></div></div>})}</section>
    <div className="metric-disclaimer"><Info size={15}/> Metrics are illustrative demonstration data only. {apiState==="connected"?"Read from demo API.":apiState==="unavailable"?"API unavailable; local demo data shown.":"Local demo data."}</div>
    <section className="dashboard-middle">
      <div className="support-hero"><ShieldCheck size={48}/><div><h2>Need support?</h2><p>Access trusted, confidential and inclusive support services.</p><button className="white-button" onClick={()=>go("Find support")}>Find support <ArrowRight size={17}/></button></div></div>
      <div className="activity-panel"><div className="panel-heading"><CalendarDays/><h2>Upcoming activities</h2></div>{activities.map(a=><div className="activity-row" key={a.title}><div className="date-box"><b>{a.month}</b><strong>{a.date}</strong></div><div><b>{a.title}</b><small>{a.meta}</small></div><span className="tag">{a.type}</span></div>)}</div>
    </section>
    <section><div className="section-heading"><h2>Explore your hub</h2><p>Choose where you would like to begin.</p></div><div className="explore-grid">
      <ExploreCard icon={<Users/>} title="Find a mentor" description="Connect with mentors and role models." tone="lilac" onClick={()=>go("Mentorship")}/>
      <ExploreCard icon={<MessageCircle/>} title="Join the community" description="Share, learn and get support from peers." tone="cream" onClick={()=>go("Community")}/>
      <ExploreCard icon={<BookOpen/>} title="Explore resources" description="Guides, toolkits and learning materials." tone="mint" onClick={()=>go("Learning library")}/>
    </div></section>
    {!member&&<div className="notice"><Info size={17}/> You are viewing a role-specific demonstration workspace for {role}. All metrics and records are fictional.</div>}
  </div>;
}
function ExploreCard({icon,title,description,tone,onClick}:{icon:React.ReactNode,title:string,description:string,tone:string,onClick:()=>void}) {
  return <button className={`explore-card ${tone}`} onClick={onClick}><span>{icon}</span><div><b>{title}</b><small>{description}</small></div><ArrowRight size={18}/></button>;
}
function Support({notify}:{notify:(s:string)=>void}) {
  return <><PageTitle eyebrow="SUPPORT DIRECTORY" title="Find support" description="Explore support information and options. You can review information before deciding what, if anything, to do next."/>
    <div className="notice"><ShieldCheck/><div><b>You are in control.</b><p>This is illustrative directory content. Live contacts and referral pathways would be validated with each participating organisation.</p></div></div>
    <div className="support-grid">{supportOptions.map((s,i)=>{const Icon=[Heart,Stethoscope,Scale,Building2][i];return <article className={`support-tile ${s.tone}`} key={s.title}><Icon size={34}/><div><h3>{s.title}</h3><p>{s.description}</p><button className="text-action" onClick={()=>notify(`${s.title}: illustrative service information. Live details would be organisation-verified.`)}>View information <ArrowRight size={15}/></button></div></article>})}</div>
    <div className="emergency-card"><div className="emergency-symbol"><LifeBuoy size={29}/></div><div><b>Emergency support</b><p>If you are in immediate danger, contact local emergency services or a trusted person. This demo does not provide emergency response.</p></div><button onClick={()=>notify("Emergency contacts must be confirmed and configured by the participating organisation.")}>Read guidance <ArrowRight size={16}/></button></div>
  </>;
}
function Reporting({step,setStep,anonymous,setAnonymous,consent,setConsent,notify}:{step:number,setStep:(n:number)=>void,anonymous:boolean,setAnonymous:(v:boolean)=>void,consent:boolean,setConsent:(v:boolean)=>void,notify:(s:string)=>void}) {
  const steps=["Your choice","Your options","Review","Confirmation"];
  return <><PageTitle eyebrow="SAFE REPORTING · CONCEPT JOURNEY" title="Make a report" description="Explore how a person could understand reporting options and make informed choices." action={<button className="outline-button" onClick={()=>{setStep(0);setAnonymous(true);setConsent(false);}}>Reset journey</button>}/>
    <div className="notice warning"><LockKeyhole/><div><b>Fictional demonstration only</b><p>Do not enter real names, contact details, incidents or personal experiences. No information is sent or stored.</p></div></div>
    <div className="report-layout"><section className="report-card"><div className="stepper">{steps.map((s,i)=><div className={step===i?"current":step>i?"done":""} key={s}><span>{step>i?<Check size={14}/>:i+1}</span><small>{s}</small></div>)}</div>
      {step===0&&<div className="report-step"><div className="report-art"><ShieldCheck size={62}/><FileText size={48}/></div><h2>Choose how you would like to proceed</h2><p>You can explore anonymous or identified reporting options. This demonstration does not submit a report.</p>
        <button className={`choice-row ${anonymous?"chosen":""}`} onClick={()=>setAnonymous(true)}><span className="radio-dot"/><span><b>Anonymous report</b><small>Explore a route without providing an identity.</small></span><UserRound/></button>
        <button className={`choice-row ${!anonymous?"chosen":""}`} onClick={()=>setAnonymous(false)}><span className="radio-dot"/><span><b>Identified report</b><small>Explore a route where a case handler could follow up, subject to consent and approved protocols.</small></span><UserRound/></button>
      </div>}
      {step===1&&<div className="report-step"><h2>{anonymous?"Understand the anonymous pathway":"Understand the identified pathway"}</h2><p>This is a conceptual explanation, not a live intake form.</p><div className="pathway-box"><b>1. Share only what you choose</b><p>A future service would explain what information is requested and why.</p></div><div className="pathway-box"><b>2. Review available support options</b><p>Support information and referral choices would be shown before any sharing.</p></div><label className="consent-row"><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/><span><b>Demonstration consent choice</b><small>Simulate choosing whether information may be shared for referral. This setting has no real effect.</small></span></label></div>}
      {step===2&&<div className="report-step"><h2>Review your demonstration choices</h2><p>No incident details or personal information are collected in this prototype.</p><div className="review-row"><span>Reporting route</span><b>{anonymous?"Anonymous":"Identified"}</b></div><div className="review-row"><span>Referral sharing choice</span><b>{consent?"Consent indicated":"No consent indicated"}</b></div><div className="notice"><Info/><p>In the proposed production system, human safeguarding personnel would make triage and referral decisions under approved protocols. The software would not make those decisions.</p></div></div>}
      {step===3&&<div className="report-step success"><div className="success-icon"><Check size={35}/></div><h2>Demonstration journey complete</h2><p>You have explored the reporting options. No report was submitted, no information was transmitted and no case was created.</p><button className="primary-button" onClick={()=>{setStep(0);setConsent(false);setAnonymous(true);}}>Explore again <ArrowRight size={17}/></button></div>}
      <div className="step-actions">{step>0&&step<3&&<button className="outline-button" onClick={()=>setStep(step-1)}>Back</button>}{step<3&&<button className="primary-button" onClick={()=>setStep(step+1)}>{step===2?"Complete demo":"Continue"} <ArrowRight size={17}/></button>}</div>
    </section>
    <aside className="report-aside"><div className="aside-card"><ShieldCheck size={30}/><h3>Your safety and choices matter</h3><p>The proposed platform would support informed consent, confidentiality and human-led safeguarding workflows.</p></div><div className="aside-card"><HeartHandshake size={29}/><h3>Support is available</h3><p>You can explore the support directory without starting a reporting journey.</p><button className="text-action" onClick={()=>notify("Choose Find support from the navigation to explore the sample directory.")}>Explore support <ArrowRight size={15}/></button></div></aside></div>
  </>;
}
function Mentorship({query,setQuery,activeTab,setActiveTab,list,requested,setRequested,notify}:{query:string,setQuery:(v:string)=>void,activeTab:string,setActiveTab:(v:string)=>void,list:typeof mentors,requested:string[],setRequested:(v:string[])=>void,notify:(s:string)=>void}) {
  const filters=["All","Research","Career","Academic","Leadership","Wellbeing"];
  return <><PageTitle eyebrow="MENTORSHIP NETWORK" title="Find a mentor" description="Discover people who can share experience, encouragement and guidance."/>
    <div className="mentor-tools"><label className="search-input"><Search/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search mentors, disciplines or interests"/></label><button className="outline-button" onClick={()=>setActiveTab("All")}><Filter size={16}/> Clear filters</button></div>
    <div className="filter-pills">{filters.map(f=><button key={f} className={activeTab===f?"active":""} onClick={()=>setActiveTab(f)}>{f}</button>)}</div>
    <div className="mentor-grid">{list.map((m,i)=><article className="mentor-card" key={m.id}><div className={`mentor-avatar avatar-${i}`}>{m.initials}</div><span className="verified"><Check size={13}/> Demo profile</span><h3>{m.name}</h3><p className="mentor-role">{m.role}</p><p>{m.bio}</p><div className="tag-row">{m.tags.map(t=><span key={t}>{t}</span>)}</div><button className={requested.includes(m.id)?"outline-button":"primary-button"} onClick={()=>{setRequested(requested.includes(m.id)?requested.filter(x=>x!==m.id):[...requested,m.id]);notify("Demo connection preference updated locally only.");}}>{requested.includes(m.id)?"Request noted":"Explore connection"} <ArrowRight size={15}/></button></article>)}</div>
  </>;
}
function Community({notify}:{notify:(s:string)=>void}) {
  return <><PageTitle eyebrow="PEER COMMUNITY" title="Join the conversation" description="Explore supportive spaces for sharing ideas, learning and connection." action={<button className="primary-button" onClick={()=>notify("Posting is disabled in this proposal demonstrator.")}>Start a discussion <ArrowRight size={16}/></button>}/>
    <div className="community-layout"><div className="discussion-list">{discussions.map(d=><article className="discussion-card" key={d.title}><div className="discussion-avatar">{d.author.slice(0,1)}</div><div><small>{d.category} · {d.author}</small><h3>{d.title}</h3><p>Explore perspectives and learn from the experiences of the community.</p><span>{d.replies} replies · Fictional discussion</span></div><ChevronRight/></article>)}</div><aside className="aside-card"><ShieldCheck size={28}/><h3>Community guidelines</h3><ul><li>Respect different experiences and identities.</li><li>Do not share another person's private information.</li><li>Keep discussions constructive and supportive.</li><li>Use moderation and reporting tools responsibly.</li></ul></aside></div>
  </>;
}
function Learning({notify}:{notify:(s:string)=>void}) {
  const items=[["Gender-Responsive Mentorship Toolkit","Toolkit","Practical guidance for mentors and champions."],["Understanding consent and support pathways","Learning module","Explore key concepts and support options."],["Creating inclusive STEM spaces","Guide","Ideas for building safer, more inclusive communities."],["Advocacy and change-making","Resource pack","Tools for constructive institutional engagement."]];
  return <><PageTitle eyebrow="LEARNING & ADVOCACY" title="Explore resources" description="Discover practical resources, learning materials and advocacy content."/><div className="resource-grid">{items.map((x,i)=><article className={`resource-card resource-${i}`} key={x[0]}><div className="resource-cover"><span>{x[1]}</span><BookOpen size={38}/><small>GTD HUB · DEMO</small></div><div className="resource-body"><span className="eyebrow">FEATURED RESOURCE</span><h3>{x[0]}</h3><p>{x[2]}</p><button className="text-action" onClick={()=>notify("Resource preview is illustrative; no external document is opened.")}>Preview resource <ArrowRight size={15}/></button></div></article>)}</div></>;
}
function CaseWorkspace({selected,setSelected,statuses,setStatuses}:{selected:string,setSelected:(v:string)=>void,statuses:Record<string,string>,setStatuses:(v:Record<string,string>)=>void}) {
  const item=cases.find(c=>c.id===selected)||cases[0];
  return <><PageTitle eyebrow="RESTRICTED DEMONSTRATION WORKSPACE" title="Case handling" description="Explore fictional case records and human-led workflow concepts. This is not a live case-management system."/>
    <div className="notice warning"><LockKeyhole/><div><b>Fictional cases only</b><p>No real disclosures, identities or case records are present. Production access would be tightly controlled, logged and governed by approved safeguarding procedures.</p></div></div>
    <div className="case-layout"><div className="case-list">{cases.map(c=><button key={c.id} className={selected===c.id?"selected":""} onClick={()=>setSelected(c.id)}><b>{c.id}</b><span>{c.type}</span><small>{c.organisation}</small><em>{statuses[c.id]||c.status}</em></button>)}</div><div className="case-detail"><div className="case-head"><div><span className="eyebrow">FICTIONAL RECORD</span><h2>{item.id}</h2></div><span className="status-pill">{statuses[item.id]||item.status}</span></div><div className="case-fields"><div><small>Organisation</small><b>{item.organisation}</b></div><div><small>Record type</small><b>{item.type}</b></div><div><small>Received</small><b>{item.received}</b></div><div><small>Consent status</small><b>{item.consent}</b></div></div><div className="notice"><Info/><p>The demonstrator illustrates workflow controls only. It does not determine risk, make safeguarding decisions or contact anyone.</p></div><div className="case-actions"><button onClick={()=>setStatuses({...statuses,[item.id]:"Acknowledged"})}>Acknowledge</button><button onClick={()=>setStatuses({...statuses,[item.id]:"Under review"})}>Mark under review</button><button onClick={()=>setStatuses({...statuses,[item.id]:"Referral pathway illustrated"})}>View referral pathway</button></div></div></div>
  </>;
}
function Organisation({selected,setSelected}:{selected:string,setSelected:(v:string)=>void}) {
  return <><PageTitle eyebrow="ORGANISATION WORKSPACE" title="Organisation overview" description="A proposed organisation-scoped view for local administrators."/><label className="select-label">DEMO ORGANISATION<select value={selected} onChange={e=>setSelected(e.target.value)}>{organisations.map(o=><option key={o}>{o}</option>)}</select></label><div className="metric-grid">{[{v:"284",l:"Members"},{v:"62",l:"Mentorship connections"},{v:"18",l:"Learning activities"},{v:"76%",l:"Illustrative engagement"}].map(x=><div className="admin-metric" key={x.l}><b>{x.v}</b><span>{x.l}</span></div>)}</div><div className="panel-box"><h2>Organisation workspace</h2><p>Illustrative overview of member engagement, programme activities and support information configuration.</p><div className="admin-actions"><button>Member directory · Preview</button><button>Role assignments · Preview</button><button>Support directory · Preview</button><button>Organisation reports · Preview</button></div></div></>;
}
function Programme({selected,setSelected}:{selected:string,setSelected:(v:string)=>void}) {
  return <><PageTitle eyebrow="PROGRAMME MONITORING & LEARNING" title="Programme insights" description="Illustrative aggregated indicators across participating organisations."/><label className="select-label">SCOPE<select value={selected} onChange={e=>setSelected(e.target.value)}>{organisations.map(o=><option key={o}>{o}</option>)}</select></label><div className="metric-grid">{[{v:"1,248",l:"Registered members"},{v:"486",l:"Weekly active users"},{v:"71%",l:"Monthly active users"},{v:"362",l:"Mentorship connections"}].map(x=><div className="admin-metric" key={x.l}><b>{x.v}</b><span>{x.l}</span></div>)}</div><div className="panel-box"><h2>Engagement trend</h2><div className="bar-chart">{[42,55,49,68,61,82,75,91,72,86,94,80].map((v,i)=><div key={i} style={{height:`${v}%`}} title={`Illustrative period ${i+1}: ${v}%`}/>)}</div><div className="chart-legend"><span>Illustrative monthly activity index</span><span>Sample data only</span></div></div><div className="notice"><Info/><p>Metrics are fictional and do not represent project monitoring results. Production indicators and definitions would be agreed with project partners and researchers.</p></div></>;
}
function Administration({notify}:{notify:(s:string)=>void}) {
  const items=[["Members & invitations","Illustrative member administration",Users],["Roles & permissions","Role and organisation access concepts",ShieldCheck],["Organisation settings","Workspace configuration",Building2],["Support directory","Service information and referral configuration",LifeBuoy],["Notifications","Communication preferences and templates",Bell],["Audit & governance","Access history and oversight concepts",ClipboardList]];
  return <><PageTitle eyebrow="PLATFORM GOVERNANCE" title="Administration" description="Explore the proposed administration areas. Controls are illustrative and do not change a live platform."/><div className="admin-grid">{items.map(([t,d,I]:any)=><button className="admin-tile" key={t} onClick={()=>notify(`${t}: configuration preview only.`)}><I size={27}/><b>{t}</b><span>{d}</span><ArrowRight size={16}/></button>)}</div></>;
}
function Help(){return <><PageTitle eyebrow="HELP & GUIDANCE" title="Using GTD Hub safely" description="Information about the demonstrator and the principles guiding the proposed product."/><div className="help-grid"><div className="panel-box"><ShieldCheck/><h2>Privacy and confidentiality</h2><p>The demonstrator uses fictional identities, organisations and records. It is not connected to a live safeguarding service.</p></div><div className="panel-box"><AccessibilityIcon/><h2>Accessibility</h2><p>The proposed interface targets WCAG 2.1 AA and will be validated through accessibility testing.</p></div><div className="panel-box"><LifeBuoy/><h2>Support options</h2><p>Use the Find Support area to explore illustrative service categories. Live details require partner verification.</p></div></div></>}
function AccessibilityIcon(){return <Users/>}
