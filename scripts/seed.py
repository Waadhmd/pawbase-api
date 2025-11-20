import os
import random
from datetime import timedelta
from faker import Faker
from sqlmodel import Session, create_engine
from datetime import  datetime, timezone
from app.schemas.models import (
    Organization,
    Shelter,
    User,
    Staff,
    Animal,
    MedicalRecord,
    Vaccination,
    AdoptionRequest,
)
from app.schemas.enums import UserRole, AdoptionStatus, RequestStatus
from app.core.security import get_password_hash

fake = Faker()

# --- DATABASE SETUP ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pawbase_api_user:xtvnfXWqOT7c3yvJ1uIMWzwQs6dPqqR4@dpg-d48qrammcj7s73e4erp0-a.frankfurt-postgres.render.com/pawbase_api")
engine = create_engine(DATABASE_URL, echo=True)

# --- ENVIRONMENT CHECK ---
ENV = os.getenv("ENV", "development")
if ENV == "production":
    print("🚫 Seeding is disabled in production!")
    exit(1)


# ------------------------------
# ----- SEED FUNCTIONS ----------
# ------------------------------
def create_organizations(session, n=3):
    orgs = []
    for _ in range(n):
        admin_user = User(
            email=fake.unique.email(),
            password=get_password_hash("password123"),
            role=UserRole.org_admin,
            created_at=datetime.now(timezone.utc)
        )
        session.add(admin_user)
        session.flush()  # assign admin_user.id

        org = Organization(
            name=fake.unique.company(),
            contact_email=fake.unique.company_email(),
            admin_id=admin_user.id
        )
        session.add(org)
        orgs.append((org, admin_user))
    session.commit()
    print(f"   -> Created {len(orgs)} organizations and {len(orgs)} admin users.")
    return orgs


def create_shelters(session, orgs, shelters_per_org=2):
    """Creates shelters and links them to organizations."""
    shelters = []
    for org, _ in orgs:
        for i in range(shelters_per_org):
            shelter = Shelter(
                city=fake.city() + " Shelter",
                name=f"{org.name[:10].strip()} - Branch {i + 1}",
                organization_id=org.id
            )
            session.add(shelter)
            session.flush()
            shelters.append(shelter)
    session.commit()
    print(f"   -> Created {len(shelters)} shelters.")
    return shelters


def create_staff(session, shelters, staff_per_shelter=3):
    staff_members = []
    for shelter in shelters:
        for _ in range(staff_per_shelter):
            user = User(
                email=fake.unique.email(),
                password=get_password_hash("password123"),
                role=UserRole.staff,
                created_at=datetime.now(timezone.utc)
            )
            session.add(user)
            session.flush() # Get user.id

            staff = Staff(
                user_id=user.id,
                shelter_id=shelter.id
            )
            session.add(staff)
            staff_members.append(staff)
    session.commit()
    print(f"   -> Created {len(staff_members)} staff users and links.")
    return staff_members


def create_animals(session, shelters, animals_per_shelter=5):
    """Creates animal records."""
    animals = []
    SPECIES = ["dog", "cat", "bird", "rabbit"]
    DOG_BREEDS = ["labrador", "terrier", "poodle", "shepherd"]
    CAT_BREEDS = ["siamese", "calico", "maine Coon", "bengal"]

    for shelter in shelters:
        for _ in range(animals_per_shelter):
            species = random.choice(SPECIES)
            breed = random.choice(DOG_BREEDS) if species == "Dog" else random.choice(CAT_BREEDS)

            animal = Animal(
                shelter_id=shelter.id,
                name=fake.first_name(),
                species_name=species,
                breed_name=breed,
                status=random.choice(list(AdoptionStatus)),
                date_of_birth=fake.date_of_birth(minimum_age=0, maximum_age=10),
                is_neutered=fake.boolean(chance_of_getting_true=70),
                weight=random.uniform(1.0, 50.0),
                public_description=fake.paragraph(nb_sentences=3)
            )
            session.add(animal)
            session.flush()
            animals.append(animal)
    session.commit()
    print(f"   -> Created {len(animals)} animal records.")
    return animals


def create_medical_records(session, animals, staff_members):
    """Creates medical records linked to animals and staff."""
    records_created = 0

    # SIMPLIFIED FILTERING LOGIC
    for animal in animals:
        # Filter the Staff link objects directly by shelter_id
        eligible_staff = [user for user in staff_members if user.shelter_id == animal.shelter_id]
        if not eligible_staff:
            continue

        for _ in range(random.randint(1, 3)):
            # Pick a random Staff object
            staff = random.choice(eligible_staff)

            record = MedicalRecord(
                animal_id=animal.id,
                staff_user_id=staff.user_id,
                exam_date=fake.date_this_year(),
                condition=fake.sentence(nb_words=5),
                vet_notes=fake.paragraph(nb_sentences=3)
            )
            session.add(record)
            records_created += 1

    session.commit()
    print(f"   -> Created {records_created} medical records.")


def create_vaccinations(session, animals, staff_members):
    """Creates vaccination records."""
    vaccinations_created = 0
    for animal in animals:
        shelter_staff = [user for user in staff_members if user.shelter_id == animal.shelter_id]
        if not shelter_staff:
            continue

        for _ in range(random.randint(1, 2)):
            staff = random.choice(shelter_staff)
            vaccination_date = fake.date_this_year()
            valid_until = vaccination_date + timedelta(days=365)
            vaccination = Vaccination(
                animal_id=animal.id,
                staff_user_id=staff.user_id,
                vaccine_type=random.choice(["Rabies", "Distemper", "Parvo", "Hepatitis"]),
                vaccination_date=vaccination_date,
                valid_until=valid_until,
                notes=fake.sentence()
            )
            session.add(vaccination)
            vaccinations_created += 1

    session.commit()
    print(f"   -> Created {vaccinations_created} vaccinations.")


def create_adopters(session, n=10):
    """Creates adopter users."""
    adopters = []
    for _ in range(n):
        user = User(
            email=fake.unique.email(),
            password=get_password_hash("password123"),
            role=UserRole.adopter,
            created_at=datetime.now(timezone.utc)
        )
        session.add(user)
        session.flush()
        adopters.append(user)
    session.commit()
    return adopters


def create_adoption_requests(session, animals, adopters, n_requests=20):
    """Creates adoption requests linking animals and adopters."""
    requests_created = 0
    for _ in range(n_requests):
        animal = random.choice(animals)
        adopter = random.choice(adopters)
        adoption_request = AdoptionRequest(
            animal_id=animal.id,
            adopter_user_id=adopter.id,
            status=random.choice(list(RequestStatus)),
            request_date=fake.date_time_this_year(tzinfo=timezone.utc)
        )
        session.add(adoption_request)
        requests_created += 1
    session.commit()


# ------------------------------
# ---------- MAIN --------------
# ------------------------------
def main():
    print("--- Starting PawBase Data Seeding ---")
    from app.schemas.models import SQLModel

    # Create tables if not exist
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables created/ensured.")

    with Session(engine) as session:
        orgs = create_organizations(session)
        shelters = create_shelters(session, orgs)
        staff_members = create_staff(session, shelters)
        animals = create_animals(session, shelters)
        adopters = create_adopters(session)
        # We must commit here to ensure the relationships (like staff_users.staff_users)
        # are correctly loaded and mapped before they are queried in subsequent functions.
        create_medical_records(session, animals, staff_members)
        create_vaccinations(session, animals, staff_members)

        create_adoption_requests(session, animals, adopters)

        print("✅ Seeding complete!")


if __name__ == "__main__":
    main()
