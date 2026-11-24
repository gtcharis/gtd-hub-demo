import os
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models import Institution, User
from app.security import hash_password

DEMO_USERS = [
    ("member@gtdhub.demo", "Tadiwa Member", "Member", "BUSE"),
    ("mentor@gtdhub.demo", "Tendai Mentor", "Mentor", "BUSE"),
    ("moderator@gtdhub.demo", "Munashe Moderator", "Moderator", "BUSE"),
    ("casehandler@gtdhub.demo", "Rudo Case Handler", "Case Handler", "BUSE"),
    ("orgadmin@gtdhub.demo", "Farai Organisation Admin", "Organisation Administrator", "BUSE"),
    ("programmeadmin@gtdhub.demo", "Kundai Programme Admin", "Programme Administrator", None),
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
        db.commit()
    print("Seed complete. Six fictional role accounts are available.")
    print("Default password:", password)
    for email, *_ in DEMO_USERS:
        print(" -", email)

if __name__ == "__main__":
    seed()
