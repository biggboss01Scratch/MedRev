import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import backend.db as db

CONFIG_FILE = ROOT / 'config.json'
DEFAULT_CONFIG = {
    'run_id': 'test_run_001',
}


def load_config():
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    try:
        with CONFIG_FILE.open('r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return DEFAULT_CONFIG.copy()
    merged = DEFAULT_CONFIG.copy()
    merged.update(data if isinstance(data, dict) else {})
    return merged


CONFIG = load_config()
RUN_ID = CONFIG['run_id']
TASKS_DIR = ROOT / 'tasks'
REVIEW_DIR = ROOT / 'review_outputs' / RUN_ID
RAW_REVIEWS = REVIEW_DIR / 'raw_reviews.jsonl'
GT_ISSUE_LIST = REVIEW_DIR / 'gt_issue_list.jsonl'
ACCEPTED_PSEUDO_LABELS = REVIEW_DIR / 'accepted_pseudo_labels.jsonl'
ACCEPTED_PSEUDO_LABELS_COCO = REVIEW_DIR / 'accepted_pseudo_labels.coco.json'
PSEUDO_LABEL_ERROR_LIST = REVIEW_DIR / 'pseudo_label_error_list.jsonl'
SUMMARY_FILE = REVIEW_DIR / 'summary.json'


TASK_FILES = [TASKS_DIR / 'hard_sample_gt_review.jsonl', TASKS_DIR / 'pseudo_label_review.jsonl']


def read_jsonl(path: Path):
    if not path.exists():
        return []
    records = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                continue
    return records


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def build_coco_from_accepted(accepted_rows, task_map):
    categories = {}
    images = {}
    annotations = []
    next_image_id = 1
    next_annotation_id = 1

    def get_category_id(name):
        if name not in categories:
            categories[name] = len(categories) + 1
        return categories[name]

    for row in accepted_rows:
        task = task_map.get(row['task_id'], {})
        image_key = task.get('image_path') or row.get('image_path') or row['task_id']
        if image_key not in images:
            images[image_key] = {
                'id': next_image_id,
                'file_name': task.get('image_name', row.get('image_name', '')),
                'width': task.get('image_width', 0),
                'height': task.get('image_height', 0),
            }
            next_image_id += 1
        image_id = images[image_key]['id']
        preds = task.get('pseudo_label_prediction', []) or []
        for pred in preds:
            bbox = pred.get('bbox') or []
            if len(bbox) < 4:
                continue
            x1, y1, x2, y2 = bbox[:4]
            annotations.append({
                'id': next_annotation_id,
                'image_id': image_id,
                'category_id': get_category_id(pred.get('category', 'unknown')),
                'bbox': [x1, y1, x2 - x1, y2 - y1],
                'area': max(0, (x2 - x1)) * max(0, (y2 - y1)),
                'iscrowd': 0,
            })
            next_annotation_id += 1

    coco = {
        'images': list(images.values()),
        'annotations': annotations,
        'categories': [{'id': cid, 'name': name} for name, cid in sorted(categories.items(), key=lambda item: item[1])],
    }
    return coco


def export_results(run_id: str):
    task_rows = []
    for task_file in TASK_FILES:
        task_rows.extend(read_jsonl(task_file))
    task_map = {row['task_id']: row for row in task_rows if row.get('task_id')}

    # Read reviews from database instead of JSONL file
    raw_reviews = db.get_reviews_for_run(run_id)
    # Convert sqlite3.Row objects to dicts
    raw_reviews = [dict(r) if hasattr(r, 'keys') else r for r in raw_reviews]

    gt_issue_rows = []
    accepted_rows = []
    pseudo_error_rows = []
    error_counter = Counter()

    for row in raw_reviews:
        task = task_map.get(row.get('task_id'), {})
        review_result = row.get('review_result')
        if review_result == 'gt_error':
            gt_issue_rows.append({
                'run_id': row.get('run_id'),
                'task_id': row.get('task_id'),
                'organ': row.get('organ'),
                'image_name': row.get('image_name'),
                'image_path': row.get('image_path'),
            })
        elif review_result == 'pseudo_label_correct':
            accepted_rows.append({
                'run_id': row.get('run_id'),
                'task_id': row.get('task_id'),
                'organ': row.get('organ'),
                'image_name': row.get('image_name'),
                'image_path': row.get('image_path'),
                'pseudo_label_prediction': task.get('pseudo_label_prediction', []),
            })
        elif review_result == 'pseudo_label_error':
            error_type = row.get('error_type')
            pseudo_error_rows.append({
                'run_id': row.get('run_id'),
                'task_id': row.get('task_id'),
                'organ': row.get('organ'),
                'image_name': row.get('image_name'),
                'image_path': row.get('image_path'),
                'error_type': error_type,
            })
            if error_type:
                error_counter[error_type] += 1

    summary = {
        'run_id': run_id,
        'total_reviewed': len(raw_reviews),
        'gt_error_count': len(gt_issue_rows),
        'accepted_pseudo_label_count': len(accepted_rows),
        'pseudo_label_error_count': len(pseudo_error_rows),
        'error_type_count': {
            'category_error': error_counter.get('category_error', 0),
            'box_size_error': error_counter.get('box_size_error', 0),
            'false_positive': error_counter.get('false_positive', 0),
            'false_negative': error_counter.get('false_negative', 0),
        },
    }

    write_jsonl(GT_ISSUE_LIST, gt_issue_rows)
    write_jsonl(ACCEPTED_PSEUDO_LABELS, accepted_rows)
    write_jsonl(PSEUDO_LABEL_ERROR_LIST, pseudo_error_rows)
    ACCEPTED_PSEUDO_LABELS_COCO.write_text(json.dumps(build_coco_from_accepted(accepted_rows, task_map), ensure_ascii=False, indent=2), encoding='utf-8')
    SUMMARY_FILE.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    return summary


def main():
    parser = argparse.ArgumentParser(description='Export MedRev review outputs')
    parser.add_argument('--run-id', default=CONFIG['run_id'])
    args = parser.parse_args()
    summary = export_results(args.run_id)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
