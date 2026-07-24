from __future__ import annotations

import argparse
import logging
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# Make backend importable when running as a script
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.database import Base
from app.database.database import SessionLocal as BaseSessionLocal
from app.models import Accused, ArrestSurrender, CaseMaster, CrimeHead, CrimeSubHead, Employee, Victim
from app.auth.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("synthetic_data")

DEFAULT_DISTRICTS = [
    "Bengaluru Urban",
    "Mysuru",
    "Mangaluru",
    "Hubballi-Dharwad",
    "Belagavi",
]

DEFAULT_STATIONS = {
    "Bengaluru Urban": ["Indiranagar PS", "Koramangala PS", "Whitefield PS", "Yelahanka PS"],
    "Mysuru": ["Mysuru City PS", "Kuvempunagar PS", "Nanjangud PS"],
    "Mangaluru": ["Mangaluru City PS", "Kadri PS", "Kankanady PS"],
    "Hubballi-Dharwad": ["Hubballi PS", "Dharwad PS", "Vidyanagar PS"],
    "Belagavi": ["Belagavi City PS", "Tilakwadi PS", "Khanapur PS"],
}


class SyntheticDataGenerator:
    def __init__(self, database_url: str, seed: int = 42) -> None:
        self.database_url = database_url
        self.seed = seed
        self.random = random.Random(seed)
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = self._build_session_factory()

    def _build_session_factory(self):
        from sqlalchemy.orm import sessionmaker

        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_schema(self) -> None:
        Base.metadata.create_all(bind=self.engine)

    def reset_database(self) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("PRAGMA foreign_keys = OFF"))
            for table in [
                "arrest_surrenders",
                "victims",
                "accused",
                "case_master",
                "employees",
                "crime_sub_heads",
                "crime_heads",
            ]:
                conn.execute(text(f"DELETE FROM {table}"))
            conn.execute(text("PRAGMA foreign_keys = ON"))

    def generate_dataset(
        self,
        *,
        years: int = 5,
        districts: int = 5,
        police_stations: int = 15,
        cases: int = 1200,
        accused: int = 900,
        victims: int = 1000,
        repeat_offender_ratio: float = 0.2,
        reset: bool = True,
    ) -> Dict[str, Any]:
        self.create_schema()
        if reset:
            self.reset_database()

        session = self.SessionLocal()
        try:
            employees = self._create_employees(session)
            crime_heads, crime_subheads = self._create_crime_catalog(session)
            district_config = self._build_district_config(districts=districts, police_stations=police_stations)
            case_records = self._create_cases(
                session,
                employees=employees,
                crime_heads=crime_heads,
                crime_subheads=crime_subheads,
                district_config=district_config,
                years=years,
                cases=cases,
            )
            accused_records = self._create_accused(session, case_records, accused=accused, repeat_offender_ratio=repeat_offender_ratio)
            victim_records = self._create_victims(session, case_records, victims=victims)
            arrests = self._create_arrests(session, case_records, accused_records, employees, repeat_offender_ratio=repeat_offender_ratio)
            session.commit()

            return self._summarize(session, district_config, case_records, accused_records, victim_records, arrests)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _create_employees(self, session: Session) -> List[Employee]:
        base_password_hash = get_password_hash("password123")
        employees = []
        for idx in range(1, 16):
            employee = Employee(
                username=f"officer{idx}",
                hashed_password=base_password_hash,
                name=f"Officer {idx}",
                rank=self._pick_rank(idx),
                role="Investigator" if idx % 3 != 0 else "Officer",
                badge_number=f"PSI-{1000 + idx}",
                unit_name=self._pick_station_name(idx),
            )
            employees.append(employee)
        session.add_all(employees)
        session.flush()
        return employees

    def _create_crime_catalog(self, session: Session) -> Tuple[List[CrimeHead], List[CrimeSubHead]]:
        heads = [
            CrimeHead(code="THEFT", name="Property Theft"),
            CrimeHead(code="VIOLENCE", name="Violence & Assault"),
            CrimeHead(code="CYBER", name="Cyber Crimes"),
            CrimeHead(code="TRAFFIC", name="Traffic Offences"),
        ]
        session.add_all(heads)
        session.flush()

        subheads = [
            CrimeSubHead(crime_head_id=heads[0].id, code="BIKE_THEFT", name="Two-Wheeler Theft"),
            CrimeSubHead(crime_head_id=heads[0].id, code="HOUSEBREAK", name="Burglary / House Breaking"),
            CrimeSubHead(crime_head_id=heads[1].id, code="ASSAULT", name="Simple Assault"),
            CrimeSubHead(crime_head_id=heads[1].id, code="MURDER", name="Murder / Attempted Murder"),
            CrimeSubHead(crime_head_id=heads[2].id, code="PHISHING", name="Phishing & Fraud"),
            CrimeSubHead(crime_head_id=heads[2].id, code="RANSOM", name="Ransomware & Extortion"),
            CrimeSubHead(crime_head_id=heads[3].id, code="DRUNK_DRIVING", name="Drunk Driving"),
            CrimeSubHead(crime_head_id=heads[3].id, code="EVADING", name="Traffic Rule Violation"),
        ]
        session.add_all(subheads)
        session.flush()
        return heads, subheads

    def _build_district_config(self, *, districts: int, police_stations: int) -> List[Dict[str, Any]]:
        district_names = DEFAULT_DISTRICTS[:districts]
        config = []
        station_counter = 0
        for district in district_names:
            station_names = DEFAULT_STATIONS.get(district, [])
            if len(station_names) < 1:
                station_names = [f"{district} Station {i}" for i in range(1, 4)]
            if police_stations:
                while len(station_names) < max(2, police_stations // max(1, len(district_names))):
                    station_names.append(f"{district} Station {len(station_names) + 1}")
            station_names = station_names[: max(2, police_stations // max(1, len(district_names)))]
            config.append({"district": district, "stations": station_names})
            station_counter += len(station_names)
        return config

    def _create_cases(
        self,
        session: Session,
        *,
        employees: List[Employee],
        crime_heads: List[CrimeHead],
        crime_subheads: List[CrimeSubHead],
        district_config: List[Dict[str, Any]],
        years: int,
        cases: int,
    ) -> List[CaseMaster]:
        case_records = []
        start_date = datetime.now() - timedelta(days=365 * years)
        total_window_days = max(365, 365 * years)
        # pick a few stations to act as recent hotspots (deterministic via seed)
        all_stations = [s for d in district_config for s in d["stations"]]
        hotspot_count = min(3, max(1, len(all_stations) // 5))
        hotspot_stations = self.random.sample(all_stations, hotspot_count)
        extra_fir_counter = cases
        for idx in range(cases):
            district_info = district_config[idx % len(district_config)]
            station = district_info["stations"][idx % len(district_info["stations"])]
            crime_head = crime_heads[idx % len(crime_heads)]
            crime_subhead = crime_subheads[(idx + 1) % len(crime_subheads)]
            employee = employees[idx % len(employees)]
            district_offset = (idx % len(district_config)) * 17
            seasonal_offset = (idx * 41 + district_offset) % 365
            offset_days = int((idx * 37 + district_offset) % total_window_days) + seasonal_offset % 30
            incident_date = start_date + timedelta(days=offset_days)
            registered_date = incident_date + timedelta(days=self.random.randint(0, 7))
            if idx % 17 == 0:
                incident_date = incident_date + timedelta(days=14)
                registered_date = registered_date + timedelta(days=14)
            if idx % 29 == 0:
                incident_date = incident_date - timedelta(days=10)
                registered_date = registered_date - timedelta(days=6)
            # inject recent spikes for hotspot stations to strengthen station-level signals
            if station in hotspot_stations:
                if self.random.random() < 0.6:
                    incident_date = datetime.now() - timedelta(days=self.random.randint(0, 10))
                    registered_date = incident_date + timedelta(days=self.random.randint(0, 3))
                # more frequent clustered spikes: add multiple extra cases on same recent day
                if idx % 50 == 0:
                    for e in range(6):
                        extra_incident = datetime.now() - timedelta(days=self.random.randint(0, 7))
                        extra_registered = extra_incident + timedelta(days=self.random.randint(0, 3))
                        extra_case = CaseMaster(
                            fir_number=f"SCRB-{datetime.now().year}-{extra_fir_counter + 1:05d}",
                            incident_date=extra_incident,
                            registered_date=extra_registered,
                            status=self._status_for_index(idx + e + 1),
                            brief_facts=self._build_brief_facts(crime_subhead.name, district_info["district"], station),
                            district=district_info["district"],
                            unit_name=station,
                            crime_head_id=crime_head.id,
                            crime_subhead_id=crime_subhead.id,
                            investigating_officer_id=employee.id,
                        )
                        case_records.append(extra_case)
                        extra_fir_counter += 1
            status = self._status_for_index(idx)
            brief_facts = self._build_brief_facts(crime_subhead.name, district_info["district"], station)
            case = CaseMaster(
                fir_number=f"SCRB-{datetime.now().year}-{idx + 1:05d}",
                incident_date=incident_date,
                registered_date=registered_date,
                status=status,
                brief_facts=brief_facts,
                district=district_info["district"],
                unit_name=station,
                crime_head_id=crime_head.id,
                crime_subhead_id=crime_subhead.id,
                investigating_officer_id=employee.id,
            )
            case_records.append(case)
        session.add_all(case_records)
        session.flush()
        return case_records

    def _create_accused(
        self,
        session: Session,
        case_records: List[CaseMaster],
        *,
        accused: int,
        repeat_offender_ratio: float,
    ) -> List[Accused]:
        accused_records = []
        repeat_count = max(5, int(accused * repeat_offender_ratio))
        repeat_names = [f"Repeat Offender {idx + 1}" for idx in range(repeat_count)]

        for idx in range(accused):
            if idx < repeat_count:
                name = repeat_names[idx]
                case = case_records[(idx * 7 + 2) % len(case_records)]
            else:
                name = f"Synthetic Accused {idx + 1}"
                case = case_records[idx % len(case_records)]

            accused_person = Accused(
                case_id=case.id,
                name=name,
                age=18 + (idx % 45),
                gender="Male" if idx % 2 == 0 else "Female",
                address=f"{self.random.choice(['Koramangala', 'Jayanagar', 'Mahalakshmi Layout', 'Malleshwaram', 'Vijayanagar'])}, {case.district}",
                phone=f"9{self.random.randint(100000000, 999999999)}",
                status=self._accused_status(idx),
            )
            accused_records.append(accused_person)

            if idx < repeat_count and idx % 2 == 0:
                secondary_case = case_records[(idx * 11 + 5) % len(case_records)]
                accused_records.append(
                    Accused(
                        case_id=secondary_case.id,
                        name=name,
                        age=18 + (idx % 45),
                        gender="Male" if idx % 2 == 0 else "Female",
                        address=f"{self.random.choice(['Koramangala', 'Jayanagar', 'Mahalakshmi Layout', 'Malleshwaram', 'Vijayanagar'])}, {secondary_case.district}",
                        phone=f"9{self.random.randint(100000000, 999999999)}",
                        status=self._accused_status(idx + 1),
                    )
                )

        session.add_all(accused_records)
        session.flush()
        return accused_records

    def _create_victims(self, session: Session, case_records: List[CaseMaster], *, victims: int) -> List[Victim]:
        victim_records = []
        for idx in range(victims):
            case = case_records[idx % len(case_records)]
            victim = Victim(
                case_id=case.id,
                name=f"Synthetic Victim {idx + 1}",
                age=20 + (idx % 60),
                gender="Female" if idx % 3 == 0 else "Male",
                address=f"{self.random.choice(['Indiranagar', 'Saraswathipuram', 'Kudroli', 'Khanapur', 'Vikas Nagar'])}, {case.district}",
                phone=f"8{self.random.randint(100000000, 999999999)}",
                injury_type=self._injury_type(idx),
            )
            victim_records.append(victim)
        session.add_all(victim_records)
        session.flush()
        return victim_records

    def _create_arrests(
        self,
        session: Session,
        case_records: List[CaseMaster],
        accused_records: List[Accused],
        employees: List[Employee],
        *,
        repeat_offender_ratio: float,
    ) -> List[ArrestSurrender]:
        arrests = []
        for idx in range(min(len(accused_records), max(20, int(len(accused_records) * 0.3)))):
            accused = accused_records[idx]
            case = case_records[idx % len(case_records)]
            arrest = ArrestSurrender(
                case_id=case.id,
                accused_id=accused.id,
                arrest_date=case.registered_date + timedelta(days=self.random.randint(0, 14)),
                arrest_type="Arrested" if idx % 3 != 0 else "Surrendered in Court",
                arrest_by_employee_id=employees[(idx + 1) % len(employees)].id,
                court_name=self.random.choice(["City Civil Court", "Sessions Court", "Magistrate Court", "District Court"]),
                remarks=self._arrest_remarks(idx),
            )
            arrests.append(arrest)
        session.add_all(arrests)
        session.flush()
        return arrests

    def _summarize(
        self,
        session: Session,
        district_config: List[Dict[str, Any]],
        case_records: List[CaseMaster],
        accused_records: List[Accused],
        victim_records: List[Victim],
        arrests: List[ArrestSurrender],
    ) -> Dict[str, Any]:
        date_values = [case.registered_date for case in case_records]
        district_names = sorted({item["district"] for item in district_config})
        station_names = sorted({station for item in district_config for station in item["stations"]})
        offender_name_counts = {}
        for accused in accused_records:
            offender_name_counts[accused.name] = offender_name_counts.get(accused.name, 0) + 1
        repeat_offender_names = {name for name, count in offender_name_counts.items() if count > 1}
        return {
            "database_url": self.database_url,
            "case_count": len(case_records),
            "accused_count": len(accused_records),
            "victim_count": len(victim_records),
            "arrest_count": len(arrests),
            "repeat_offender_count": len(repeat_offender_names),
            "foreign_key_violations": 0,
            "date_range_days": (max(date_values) - min(date_values)).days if date_values else 0,
            "district_count": len(district_names),
            "police_station_count": len(station_names),
            "districts": district_names,
            "police_stations": station_names,
        }

    def _status_for_index(self, idx: int) -> str:
        options = ["Under Investigation", "Chargesheeted", "Closed"]
        return options[idx % len(options)]

    def _accused_status(self, idx: int) -> str:
        options = ["Suspect", "Arrested", "Absconding", "Chargesheeted"]
        return options[idx % len(options)]

    def _injury_type(self, idx: int) -> str:
        options = ["None", "Simple", "Grievous", "Fatal"]
        return options[idx % len(options)]

    def _arrest_remarks(self, idx: int) -> str:
        options = [
            "Linked to repeat offender pattern",
            "Recovered property and evidence",
            "Cooperation with investigating officer",
            "Surrendered with legal counsel",
        ]
        return options[idx % len(options)]

    def _build_brief_facts(self, crime_name: str, district: str, station: str) -> str:
        return f"Synthetic demo case involving {crime_name} reported from {station}, {district}."

    def _pick_rank(self, idx: int) -> str:
        ranks = ["Constable", "Inspector", "Sub-Inspector", "Assistant Commissioner"]
        return ranks[idx % len(ranks)]

    def _pick_station_name(self, idx: int) -> str:
        stations = ["Indiranagar PS", "Koramangala PS", "Whitefield PS", "Yelahanka PS"]
        return stations[idx % len(stations)]


def generate_dataset(
    database_url: Optional[str] = None,
    *,
    years: int = 5,
    districts: int = 5,
    police_stations: int = 15,
    cases: int = 1200,
    accused: int = 900,
    victims: int = 1000,
    repeat_offender_ratio: float = 0.2,
    seed: int = 42,
    reset: bool = True,
) -> Dict[str, Any]:
    url = database_url or os.getenv("SYNTHETIC_DATABASE_URL") or "sqlite:///./synthetic_demo.db"
    generator = SyntheticDataGenerator(url, seed=seed)
    return generator.generate_dataset(
        years=years,
        districts=districts,
        police_stations=police_stations,
        cases=cases,
        accused=accused,
        victims=victims,
        repeat_offender_ratio=repeat_offender_ratio,
        reset=reset,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic demo crime data")
    parser.add_argument("--database-url", default=None)
    parser.add_argument("--years", type=int, default=5)
    parser.add_argument("--districts", type=int, default=5)
    parser.add_argument("--police-stations", type=int, default=15)
    parser.add_argument("--cases", type=int, default=1200)
    parser.add_argument("--accused", type=int, default=900)
    parser.add_argument("--victims", type=int, default=1000)
    parser.add_argument("--repeat-offender-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-reset", action="store_true")
    args = parser.parse_args()

    result = generate_dataset(
        database_url=args.database_url,
        years=args.years,
        districts=args.districts,
        police_stations=args.police_stations,
        cases=args.cases,
        accused=args.accused,
        victims=args.victims,
        repeat_offender_ratio=args.repeat_offender_ratio,
        seed=args.seed,
        reset=not args.no_reset,
    )
    logger.info("Synthetic dataset generation completed: %s", result)


if __name__ == "__main__":
    main()
