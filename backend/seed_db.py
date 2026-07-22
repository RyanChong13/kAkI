"""Seed script to populate the grants table from seed/grants.json."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import Base
from app.models import *  # noqa - ensure all models are registered

engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)


def seed_grants():
    db = Session()
    from app.models.grant import Grant

    # Clear existing
    db.query(Grant).delete()
    db.commit()

    seed_path = os.path.join(os.path.dirname(__file__), "seed", "grants.json")
    with open(seed_path) as f:
        grants_data = json.load(f)

    for g in grants_data:
        grant = Grant(
            name=g["name"],
            amount=g["amount"],
            cap_remaining=g["cap_remaining"],
            eligibility_criteria=g["eligibility_criteria"],
        )
        db.add(grant)

    db.commit()
    print(f"Seeded {len(grants_data)} grants.")
    db.close()


if __name__ == "__main__":
    seed_grants()
