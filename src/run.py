"""Initialize and report without touching the Django schema."""
import argparse
from .connection_pool import create_pool
from .database import initialize_database, seed_database, validate_data
from .procedures import create_procedures
from .reports import print_table, write_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true", help="Write the complete report after setup.")
    args = parser.parse_args()
    pool = create_pool()
    initialize_database(pool)
    seed_database(pool)
    validate_data(pool)
    create_procedures(pool)
    if args.report:
        reports = write_report(pool)
        print_table("Sales summary (demonstration data, USD)", reports["summary"])


if __name__ == "__main__":
    main()
