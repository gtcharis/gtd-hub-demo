# GTD Hub Proposal Demonstrator — Screen Inventory v0.2

**Boundary:** this is a selection-stage interactive concept demonstrator, not the full contracted GTD Hub product. It uses fictional identities, organisations, activities, metrics and cases. It is not a live reporting or safeguarding channel.

## Principal screens and derived views

| ID | Principal screen | Derived views / states |
|---|---|---|
| DEM-01 | Welcome / Demo Entry | Product purpose, fictional-data notice, start demo |
| DEM-02 | Role Selection | Member, Mentor, Moderator, Case Handler, Organisation Administrator, Programme Administrator |
| DEM-03 | Member Dashboard | Welcome, demo metrics, support prompt, activities, exploration shortcuts |
| DEM-04 | Find Support | Psychosocial, health, legal and institutional information; emergency guidance |
| DEM-05 | Safe Reporting | Anonymous/identified choice, pathway explanation, consent choice, review, completion |
| DEM-06 | Mentorship | Search, category filters, mentor cards, request-noted state |
| DEM-07 | Community | Discussion list, community guidelines, disabled post action |
| DEM-08 | Learning & Advocacy | Resource cards and preview state |
| DEM-09 | Case Workspace | Fictional inbox, case selection, status simulation, referral pathway explanation |
| DEM-10 | Organisation Overview | Organisation selector, sample indicators, management entry points |
| DEM-11 | Programme Insights | Scope selector, aggregate sample metrics, illustrative trend |
| DEM-12 | Administration | Members, roles, organisation settings, support directory, notifications, audit concepts |
| DEM-13 | Help & Guidance | Privacy, accessibility, support and demo boundary |

## Shared application shell

- Proposal demonstrator banner and persistent fictional-data notice
- Responsive sidebar / mobile navigation drawer
- Role switcher
- Search affordance
- Notification demonstration
- Profile identity
- Quick Exit demonstration
- Install PWA affordance
- Toast/status feedback

## Role-to-screen visibility

| Role | Primary navigation |
|---|---|
| Member | Overview, Find support, Safe reporting, Mentorship, Community, Learning library |
| Mentor | Overview, Mentorship, Community, Learning library |
| Moderator | Overview, Community, Learning library |
| Case Handler | Overview, Case workspace, Find support |
| Organisation Administrator | Overview, Organisation overview, Administration |
| Programme Administrator | Overview, Programme insights, Organisation overview, Administration |

## Design rules

- Mobile-first; desktop is an expanded responsive layout.
- Parent screens own their detail states, dialogs, tabs and workflow steps.
- Do not create a separate route for every small interaction.
- Product terminology is organisation-neutral; Student/Staff appears only as contextual programme-specific copy.
- No live GBV report submission or real support contact is simulated.
