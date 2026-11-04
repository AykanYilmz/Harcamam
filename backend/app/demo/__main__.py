import argparse
import os

from app.core.database import SessionLocal
from app.demo.seed import DEMO_EMAIL, DEMO_PASSWORD, reset_demo_account


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or reset the demo account.")
    parser.add_argument("--email", default=os.environ.get("DEMO_EMAIL", DEMO_EMAIL))
    parser.add_argument("--password", default=os.environ.get("DEMO_PASSWORD", DEMO_PASSWORD))
    args = parser.parse_args()

    with SessionLocal() as db:
        user, results = reset_demo_account(db, args.email, args.password)
        imported = sum(result.imported for result in results)
        print(f"{user.email}: {len(results)} statements, {imported} transactions")


if __name__ == "__main__":
    main()
