#!/usr/bin/env python3
"""
Reset all review data to the initial state.

This clears:
- SQLite raw_reviews table
- SQLite assignments table
- review_outputs/<run_id>/raw_reviews.jsonl
- review_outputs/<run_id>/gt_issue_list.jsonl
- review_outputs/<run_id>/accepted_pseudo_labels.jsonl
- review_outputs/<run_id>/pseudo_label_error_list.jsonl
- review_outputs/<run_id>/last_export.json
- review_outputs/<run_id>/accepted_pseudo_labels.coco.json
- review_outputs/<run_id>/summary.json
- review_outputs/<run_id>/assignments.json
"""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import backend.db as db


def reset_run_dir(run_dir: Path):
    for name in [
        'raw_reviews.jsonl',
        'gt_issue_list.jsonl',
        'accepted_pseudo_labels.jsonl',
        'pseudo_label_error_list.jsonl',
        'last_export.json',
    ]:
        file_path = run_dir / name
        if file_path.exists():
            file_path.unlink()

    (run_dir / 'accepted_pseudo_labels.coco.json').write_text(
        json.dumps({'images': [], 'annotations': [], 'categories': []}, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    (run_dir / 'summary.json').write_text(
        json.dumps({
            'run_id': run_dir.name,
            'total_reviewed': 0,
            'gt_error_count': 0,
            'accepted_pseudo_label_count': 0,
            'pseudo_label_error_count': 0,
            'error_type_count': {
                'category_error': 0,
                'box_size_error': 0,
                'false_positive': 0,
                'false_negative': 0,
            },
        }, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    assignments_file = run_dir / 'assignments.json'
    if assignments_file.exists():
        assignments_file.write_text(json.dumps({}, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    review_root = ROOT / 'review_outputs'
    db.init_db()

    conn = db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute('DELETE FROM raw_reviews')
        cur.execute('DELETE FROM assignments')
        conn.commit()
    finally:
        conn.close()

    if review_root.exists():
        for run_dir in review_root.iterdir():
            if run_dir.is_dir():
                reset_run_dir(run_dir)

    print('Reset complete: cleared all review records and assignments.')


if __name__ == '__main__':
    main()
