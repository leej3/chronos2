from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.configs.database import DATABASE_URL
from src.core.models import Boiler

def init_boiler_data(db: Session):
    # Create initial boiler data
    boiler_data = [
        Boiler(
            id=1, 
            backup=0,
            # timestamp='2021-01-01 00:00:00',
            # switched_timestamp='2021-01-01 00:00:00',
            status=1,
            manual_override=1,
            system_supply_temp=82.4,
            outlet_temp=83.1,
            flue_temp=76.3,
            cascade_current_power=17,
            lead_firing_rate=0,
        ),
        Boiler(
            id=2, 
            backup=1,
            # timestamp='2021-01-01 00:00:00',
            # switched_timestamp='2021-01-01 00:00:00',
            status=1,
            manual_override=0,
            system_supply_temp=0,
            outlet_temp=0,
            flue_temp=0,
            cascade_current_power=0,
            lead_firing_rate=0,
        ),
    ]

    # Add data to the session
    db.add_all(boiler_data)
    # Commit the transaction
    db.commit()

    def main():
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Create a new session
        db = SessionLocal()

        try:
            init_boiler_data(db)
        finally:
            db.close()

    if __name__ == "__main__":
        main()