import os
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models import Institution, User, MentorProfile
from app.security import hash_password

DEMO_USERS = [
    ("member@gtdhub.demo", "Tadiwa Member", "Member", "BUSE"),
    ("mentor@gtdhub.demo", "Tendai Mentor", "Mentor", "BUSE"),
    ("moderator@gtdhub.demo", "Munashe Moderator", "Moderator", "BUSE"),
    ("casehandler@gtdhub.demo", "Rudo Case Handler", "Case Handler", "BUSE"),
    ("orgadmin@gtdhub.demo", "Farai Organisation Admin", "Organisation Administrator", "BUSE"),
    ("programmeadmin@gtdhub.demo", "Kundai Programme Admin", "Programme Administrator", None),
    ("tncube@gtdhub.demo", "Mr. T. Ncube", "Mentor", "BUSE"),
    ("fdlamini@gtdhub.demo", "Ms. F. Dlamini", "Mentor", "BUSE"),
]

MENTOR_PROFILES = [
    ("mentor@gtdhub.demo", "Research Mentor", "Engineering", "Supports research confidence, career development and navigating technical spaces.", "Research, Career, Engineering"),
    ("tncube@gtdhub.demo", "Academic Mentor", "Computer Science", "Offers guidance on study pathways, technical learning and academic development.", "Academic, Computer Science, Learning"),
    ("fdlamini@gtdhub.demo", "STEM Professional", "Data", "Shares experience in data careers, leadership and professional growth.", "Leadership, Wellbeing, Data"),
]

def seed():
    Base.metadata.create_all(bind=engine)
    password = os.getenv("DEMO_DEFAULT_PASSWORD", "GtdHubDemo!2026")
    with SessionLocal() as db:
        institution = db.query(Institution).filter_by(code="BUSE").first()
        if institution is None:
            institution = Institution(name="Bindura University of Science Education (Demo)", code="BUSE")
            db.add(institution)
            db.flush()
        for email, full_name, role, institution_code in DEMO_USERS:
            user = db.query(User).filter_by(email=email).first()
            if user is None:
                db.add(User(
                    email=email, full_name=full_name, role=role,
                    institution_id=institution.id if institution_code else None,
                    password_hash=hash_password(password), is_active=True,
                ))
        db.flush()
        primary_mentor = db.query(User).filter_by(email="mentor@gtdhub.demo").first()
        for email, *_ in MENTOR_PROFILES:
            extra_mentor = db.query(User).filter_by(email=email).first()
            if extra_mentor is not None and primary_mentor is not None:
                extra_mentor.password_hash = primary_mentor.password_hash
        for email, title, discipline, bio, expertise in MENTOR_PROFILES:
            mentor_user = db.query(User).filter_by(email=email).first()
            if mentor_user is None:
                continue
            profile = db.query(MentorProfile).filter_by(user_id=mentor_user.id).first()
            if profile is None:
                db.add(MentorProfile(
                    user_id=mentor_user.id,
                    institution_id=institution.id,
                    title=title, discipline=discipline, bio=bio,
                    expertise=expertise, accepting_requests=True,
                ))
        db.commit()
    print("Seed complete. Six primary role accounts and three fictional mentor profiles are available.")
    for email, *_ in DEMO_USERS:
        print(" -", email)

if __name__ == "__main__":
    seed()
