export type DemoRole = "Member" | "Mentor" | "Moderator" | "Case Handler" | "Organisation Administrator" | "Programme Administrator";
export const roles: DemoRole[] = ["Member", "Mentor", "Moderator", "Case Handler", "Organisation Administrator", "Programme Administrator"];
export const navByRole: Record<DemoRole, string[]> = {
  Member: ["Overview", "Find support", "Safe reporting", "Mentorship", "Community", "Learning library"],
  Mentor: ["Overview", "Mentorship", "Community", "Learning library"],
  Moderator: ["Overview", "Community", "Learning library"],
  "Case Handler": ["Overview", "Case workspace", "Find support"],
  "Organisation Administrator": ["Overview", "Organisation overview", "Administration"],
  "Programme Administrator": ["Overview", "Case workspace", "Programme insights", "Organisation overview", "Administration"]
};
export const metrics = [
  { label: "Registered users", value: "1,248", icon: "users", tone: "mint" },
  { label: "Mentorship connections", value: "362", icon: "handshake", tone: "lilac" },
  { label: "Resources available", value: "74", icon: "book", tone: "cream" },
  { label: "Member engagement", value: "86%", icon: "chart", tone: "rose" }
];
export const mentors = [
  { id: "M-01", name: "Dr. R. Moyo", role: "Researcher · Engineering", tags: ["Research", "Career"], bio: "Supports research confidence, career development and navigating technical spaces.", initials: "RM" },
  { id: "M-02", name: "Mr. T. Ncube", role: "Lecturer · Computer Science", tags: ["Academic", "Mentorship"], bio: "Offers guidance on study pathways, technical learning and academic development.", initials: "TN" },
  { id: "M-03", name: "Ms. F. Dlamini", role: "STEM Professional · Data", tags: ["Leadership", "Wellbeing"], bio: "Shares experience in data careers, leadership and professional growth.", initials: "FD" }
];
export const supportOptions = [
  { title: "Psychosocial Support", description: "Counselling, wellbeing and mental health services.", icon: "heart", tone: "lilac" },
  { title: "Health Services", description: "Reproductive, sexual and general health support.", icon: "health", tone: "mint" },
  { title: "Legal Information", description: "Your rights, reporting options and available legal support.", icon: "scale", tone: "cream" },
  { title: "Institutional Support", description: "Campus services, designated focal points and student support.", icon: "building", tone: "blue" }
];
export const activities = [
  { date: "26", month: "NOV", title: "Mentorship Circle: Women in STEM", meta: "Thu, 26 Nov · 15:00–16:00 · Online", type: "Mentorship" },
  { date: "28", month: "NOV", title: "Campus Dialogue: Safe & Inclusive STEM Spaces", meta: "Sat, 28 Nov · 10:00–12:00 · Main Hall", type: "Learning" }
];
export const discussions = [
  { title: "Finding your voice in technical spaces", author: "Munashe · Member", replies: 18, category: "STEM journeys" },
  { title: "How did you choose your first research topic?", author: "Tendai · Member", replies: 9, category: "Research & learning" },
  { title: "Preparing for your first industry placement", author: "Kundai · Mentor", replies: 24, category: "Career development" }
];
export const cases = [
  { id: "DEMO-1042", organisation: "Bindura University of Science Education", type: "Support request", received: "Today · 09:42", status: "Awaiting triage", consent: "Referral consent given" },
  { id: "DEMO-1038", organisation: "University of Zimbabwe", type: "Information request", received: "Yesterday · 14:18", status: "In progress", consent: "Information only" },
  { id: "DEMO-1029", organisation: "Midlands State University", type: "Referral request", received: "18 Nov · 11:06", status: "Referral initiated", consent: "Referral consent given" }
];
export const organisations = ["All organisations", "Bindura University of Science Education", "University of Zimbabwe", "National University of Science and Technology", "Midlands State University", "Chinhoyi University of Technology", "Harare Institute of Technology", "Great Zimbabwe University", "Lupane State University", "Zimbabwe Open University", "Manicaland State University", "Marondera University of Agricultural Sciences"];
