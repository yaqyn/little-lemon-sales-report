"""Initialize and report without touching the Django schema."""
import argparse
from .connection_pool import create_pool
from .database import initialize_database, seed_database, validate_data
from .procedures import create_procedures
from .reports import REPORT_QUERIES, print_table, run_report, write_report


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--report", action="store_true", help="Write the complete report after setup.")
    output.add_argument(
        "--show-report", choices=sorted(REPORT_QUERIES), metavar="NAME",
        help="Print one named report after setup without replacing report artifacts.",
    )
    return parser


def main():
    args = build_parser().parse_args()
    pool = create_pool()
    initialize_database(pool)
    seed_database(pool)
    validate_data(pool)
    create_procedures(pool)
    if args.report:
        reports = write_report(pool)
        print_table("Sales summary (demonstration data, USD)", reports["summary"])
    elif args.show_report:
        rows = run_report(pool, args.show_report)
        print_table(args.show_report.replace("_", " ").title(), rows)


if __name__ == "__main__":
    main()
