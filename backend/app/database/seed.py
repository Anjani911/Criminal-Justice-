from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database.database import engine, Base, SessionLocal
from app.auth.security import get_password_hash
from app.models import CrimeHead, CrimeSubHead, Employee, CaseMaster, Accused, Victim, ArrestSurrender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")


def seed_db():
    logger.info("Initializing seeding sequence...")
    db = SessionLocal()

    try:
        # Clear existing data in reverse order of foreign keys
        logger.info("Cleaning up existing database records...")
        db.query(ArrestSurrender).delete()
        db.query(Victim).delete()
        db.query(Accused).delete()
        db.query(CaseMaster).delete()
        db.query(Employee).delete()
        db.query(CrimeSubHead).delete()
        db.query(CrimeHead).delete()
        db.commit()

        # 1. Seed default employees (with hashed passwords)
        logger.info("Seeding default employees...")
        default_pw_hash = get_password_hash("password123")
        
        admin = Employee(
            username="admin",
            hashed_password=default_pw_hash,
            name="Platform Administrator",
            rank="Superintendent of Police",
            role="Administrator",
            badge_number="SP-1001",
            unit_name="SCRB Headquarters"
        )
        
        officer = Employee(
            username="officer",
            hashed_password=default_pw_hash,
            name="Senior Officer Ramesh",
            rank="Deputy Commissioner of Police",
            role="Officer",
            badge_number="DCP-2002",
            unit_name="Central Division"
        )
        
        investigator = Employee(
            username="investigator",
            hashed_password=default_pw_hash,
            name="Investigator Karthik",
            rank="Police Sub-Inspector",
            role="Investigator",
            badge_number="PSI-3003",
            unit_name="Indiranagar PS"
        )
        
        db.add_all([admin, officer, investigator])
        db.flush()  # Populates IDs

        # 2. Seed Crime Classification Categories
        logger.info("Seeding crime heads and subheads...")
        
        cyber = CrimeHead(code="CYBER", name="Cyber Crimes")
        theft = CrimeHead(code="THEFT", name="Property Theft")
        homicide = CrimeHead(code="HOMICIDE", name="Homicide")
        db.add_all([cyber, theft, homicide])
        db.flush()

        phishing = CrimeSubHead(crime_head_id=cyber.id, code="PHISH", name="Online Phishing & Fraud")
        ransomware = CrimeSubHead(crime_head_id=cyber.id, code="RANSOM", name="Ransomware & Extortion")
        bike_theft = CrimeSubHead(crime_head_id=theft.id, code="BIKE_THEFT", name="Two-Wheeler Theft")
        housebreak = CrimeSubHead(crime_head_id=theft.id, code="HOUSEBREAK", name="Burglary / House Breaking")
        murder = CrimeSubHead(crime_head_id=homicide.id, code="MURDER", name="Murder (Section 302 IPC)")
        
        db.add_all([phishing, ransomware, bike_theft, housebreak, murder])
        db.flush()

        # 3. Seed Sample Cases
        logger.info("Seeding sample FIR cases...")
        
        case_1 = CaseMaster(
            fir_number="IND-2026-0001",
            incident_date=datetime.now() - timedelta(days=10),
            registered_date=datetime.now() - timedelta(days=9),
            status="Under Investigation",
            brief_facts="A citizen reported credit card credential theft and transfer of 75,000 INR to a dummy account.",
            district="Bengaluru City",
            unit_name="Indiranagar PS",
            crime_head_id=cyber.id,
            crime_subhead_id=phishing.id,
            investigating_officer_id=investigator.id
        )

        case_2 = CaseMaster(
            fir_number="IND-2026-0002",
            incident_date=datetime.now() - timedelta(days=5),
            registered_date=datetime.now() - timedelta(days=5),
            status="Chargesheeted",
            brief_facts="A motorcycle was stolen from outside the metro station parking area during evening hours.",
            district="Bengaluru City",
            unit_name="Indiranagar PS",
            crime_head_id=theft.id,
            crime_subhead_id=bike_theft.id,
            investigating_officer_id=investigator.id
        )
        
        db.add_all([case_1, case_2])
        db.flush()

        # 4. Seed Accused and Victims
        logger.info("Seeding accused and victims...")
        
        accused_1 = Accused(
            case_id=case_1.id,
            name="Vikram Sen",
            age=26,
            gender="Male",
            address="Koramangala, Bengaluru",
            phone="9876543210",
            status="Arrested"
        )
        
        accused_2 = Accused(
            case_id=case_2.id,
            name="Raju Bike Thief",
            age=22,
            gender="Male",
            address="Unknown Address",
            phone="None",
            status="Absconding"
        )
        
        db.add_all([accused_1, accused_2])
        db.flush()

        victim_1 = Victim(
            case_id=case_1.id,
            name="Suresh Hegde",
            age=51,
            gender="Male",
            address="Indiranagar, Bengaluru",
            phone="9000100020",
            injury_type="None"
        )
        
        victim_2 = Victim(
            case_id=case_2.id,
            name="Priya Sharma",
            age=29,
            gender="Female",
            address="Domlur, Bengaluru",
            phone="9845012345",
            injury_type="None"
        )
        
        db.add_all([victim_1, victim_2])
        db.flush()

        # 5. Seed Arrest Events
        logger.info("Seeding arrest history...")
        
        arrest = ArrestSurrender(
            case_id=case_1.id,
            accused_id=accused_1.id,
            arrest_date=datetime.now() - timedelta(days=4),
            arrest_type="Arrested",
            arrest_by_employee_id=investigator.id,
            remarks="Arrested from Kolkata transit hideout. Recovered electronic credentials."
        )
        db.add(arrest)

        db.commit()
        logger.info("Database seeding COMPLETED successfully!")

    except Exception as e:
        db.rollback()
        logger.error(f"Seeding failed: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
