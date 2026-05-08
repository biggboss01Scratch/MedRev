#!/usr/bin/env python3
"""
Migration script: Import existing assignments.json and raw_reviews.jsonl into SQLite database.
Run this once after updating to the database-based version.

Usage:
    python scripts/migrate_to_db.py
    python scripts/migrate_to_db.py --run-id test_run_001
"""

import argparse
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import backend.db as db

CONFIG_FILE = ROOT / 'config.json'

def load_config():
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open('r', encoding='utf-8') as f:
            return json.load(f)
    return {'run_id': 'test_run_001'}

def migrate_run(run_id: str):
    """Migrate a specific run_id's data to database."""
    print(f"\n=== Migrating run_id: {run_id} ===")
    
    review_dir = ROOT / 'review_outputs' / run_id
    if not review_dir.exists():
        print(f"Review directory {review_dir} does not exist, skipping.")
        return
    
    # Migrate assignments
    assignments_file = review_dir / 'assignments.json'
    if assignments_file.exists():
        print(f"Migrating assignments from {assignments_file}...")
        try:
            with assignments_file.open('r', encoding='utf-8') as f:
                assignments = json.load(f) or {}
            db.save_assignments_dict(run_id, assignments)
            print(f"  ✓ Migrated {len(assignments)} assignments")
        except Exception as e:
            print(f"  ✗ Error migrating assignments: {e}")
    else:
        print(f"  No assignments file found")
    
    # Migrate raw reviews
    raw_reviews_file = review_dir / 'raw_reviews.jsonl'
    if raw_reviews_file.exists():
        print(f"Migrating reviews from {raw_reviews_file}...")
        try:
            count = 0
            with raw_reviews_file.open('r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            record = json.loads(line)
                            db.append_review(record)
                            count += 1
                        except json.JSONDecodeError:
                            pass
            print(f"  ✓ Migrated {count} reviews")
        except Exception as e:
            print(f"  ✗ Error migrating reviews: {e}")
    else:
        print(f"  No raw_reviews file found")

def main():
    parser = argparse.ArgumentParser(description='Migrate JSON files to SQLite database')
    parser.add_argument('--run-id', help='Specific run_id to migrate (if not specified, migrate current run_id from config)')
    parser.add_argument('--all', action='store_true', help='Migrate all existing run_ids')
    args = parser.parse_args()
    
    # Initialize database
    print("Initializing database schema...")
    db.init_db()
    print("✓ Database initialized")
    
    if args.all:
        # Find all review_outputs directories
        review_outputs_dir = ROOT / 'review_outputs'
        if review_outputs_dir.exists():
            for run_dir in sorted(review_outputs_dir.iterdir()):
                if run_dir.is_dir():
                    migrate_run(run_dir.name)
        else:
            print("No review_outputs directory found")
    else:
        # Migrate single run_id
        run_id = args.run_id
        if not run_id:
            config = load_config()
            run_id = config.get('run_id', 'test_run_001')
        migrate_run(run_id)
    
    print("\n=== Migration complete ===")
    print("You can now use the database-backed system.")
    print("\nNote: The old JSON files are still present. You can keep them as backup or delete them:")
    print("  - review_outputs/<run_id>/assignments.json")
    print("  - review_outputs/<run_id>/raw_reviews.jsonl")

if __name__ == '__main__':
    main()
