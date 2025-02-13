"""Database inspection utilities for development and debugging."""

from typing import List, Optional

from sqlalchemy import create_engine, inspect, text
from src.core.configs.database import DATABASE_URL


def inspect_table(
    table_name: str, limit: int = 1, where_clause: Optional[str] = None
) -> None:
    """
    Inspect a database table's schema and sample data.

    Args:
        table_name: Name of the table to inspect
        limit: Number of sample rows to show (default: 1)
        where_clause: Optional WHERE clause for filtering sample data
    """
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)

    if table_name not in inspector.get_table_names():
        print(f"Table '{table_name}' not found. Available tables:")
        print("\n".join(f"- {t}" for t in inspector.get_table_names()))
        return

    print(f"\n=== {table_name} Table Schema ===")
    columns = inspector.get_columns(table_name)
    for column in columns:
        print(f"Column: {column['name']}")
        print(f"  Type: {column['type']}")
        print(f"  Nullable: {column['nullable']}")
        print("---")

    # Check sample data
    with engine.connect() as connection:
        query = f"SELECT * FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        query += f" LIMIT {limit}"

        results = connection.execute(text(query)).fetchall()
        if results:
            print(f"\n=== Sample Data ({len(results)} rows) ===")
            for row in results:
                print("\nRow:")
                for column, value in zip(columns, row):
                    print(f"  {column['name']}: {value}")


def list_tables() -> List[str]:
    """List all tables in the database."""
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    return inspector.get_table_names()


if __name__ == "__main__":
    # Example usage
    print("Available tables:", list_tables())
    inspect_table("boiler", limit=2)  # Show 2 rows from boiler table
