export type Role = 'Student' | 'Mentor' | 'Moderator' | 'Case handler' | 'HEI administrator' | 'Programme administrator'
export const roles: Role[] = ['Student','Mentor','Moderator','Case handler','HEI administrator','Programme administrator']
export const institutions = ['All institutions','Bindura University of Science Education','University of Zimbabwe','National University of Science and Technology','Midlands State University','Chinhoyi University of Technology','Harare Institute of Technology','Great Zimbabwe University','Lupane State University','Zimbabwe Open University','Manicaland State University','Marondera University of Agricultural Sciences']
export const mentors = [
  {name:'Dr. Tariro Moyo',field:'Computer Science',institution:'University of Zimbabwe',focus:'Research pathways · Career growth',initials:'TM',tone:'lavender'},
  {name:'Eng. Nyasha Dube',field:'Electrical Engineering',institution:'NUST',focus:'Leadership · Industry readiness',initials:'ND',tone:'peach'},
  {name:'Dr. Rudo Chikore',field:'Data Science',institution:'BUSE',focus:'Postgraduate study · Research',initials:'RC',tone:'mint'},
]
export const discussions = [
  {category:'STEM journeys',title:'Finding your voice in technical spaces',author:'Munashe · Student',replies:18,time:'2 hours ago',tag:'Featured'},
  {category:'Research & learning',title:'How did you choose your first research topic?',author:'Tendai · Student',replies:9,time:'Yesterday',tag:'Discussion'},
  {category:'Career development',title:'Preparing for your first industry placement',author:'Kundai · Mentor',replies:24,time:'2 days ago',tag:'Popular'},
]
export const cases = [
  {id:'DEMO-1042',institution:'Bindura University of Science Education',type:'Support request',received:'Today · 09:42',status:'Awaiting triage',priority:'Standard',consent:'Referral consent given'},
  {id:'DEMO-1038',institution:'University of Zimbabwe',type:'Information request',received:'Yesterday · 14:18',status:'In progress',priority:'Standard',consent:'Information only'},
  {id:'DEMO-1029',institution:'Midlands State University',type:'Referral request',received:'18 Nov · 11:06',status:'Referral initiated',priority:'Follow-up',consent:'Referral consent given'},
]
