from pathlib import Path

from scripts.generate_synthetic_data import generate_dataset


def test_generate_dataset_creates_consistent_demo_data(tmp_path):
    db_path = tmp_path / "synthetic_test.db"

    result = generate_dataset(
        database_url=f"sqlite:///{db_path}",
        years=2,
        districts=2,
        police_stations=4,
        cases=120,
        accused=110,
        victims=115,
        repeat_offender_ratio=0.2,
        seed=1234,
        reset=True,
    )

    assert result["case_count"] >= 120
    assert result["accused_count"] >= 90
    assert result["victim_count"] >= 100
    assert result["arrest_count"] >= 20
    assert result["repeat_offender_count"] >= 5
    assert result["foreign_key_violations"] == 0
    assert result["date_range_days"] >= 300
    assert result["district_count"] >= 2
    assert result["police_station_count"] >= 4
