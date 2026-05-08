import json
import subprocess
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    run_dir = ROOT / 'review_outputs' / 'test_run_001'
    raw_reviews = run_dir / 'raw_reviews.jsonl'
    summary_file = run_dir / 'summary.json'
    coco_file = run_dir / 'accepted_pseudo_labels.coco.json'

    run_dir.mkdir(parents=True, exist_ok=True)
    raw_reviews.write_text('stale\n', encoding='utf-8')
    summary_file.write_text(json.dumps({'run_id': 'stale', 'total_reviewed': 99}, ensure_ascii=False), encoding='utf-8')

    spec = importlib.util.spec_from_file_location('medrev_app', ROOT / 'backend' / 'app.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app = module.app
    raw_reviews = module.RAW_REVIEWS
    summary_file = module.SUMMARY_FILE
    coco_file = module.ACCEPTED_PSEUDO_LABELS_COCO

    assert raw_reviews.read_text(encoding='utf-8') == ''
    summary = json.loads(summary_file.read_text(encoding='utf-8'))
    assert summary['total_reviewed'] == 0

    # write one review and export derived outputs
    payload = {
        'run_id': 'test_run_001',
        'task_id': 'test_run_001_hard_肾脏_001_1.jpg',
        'task_type': 'hard_sample_gt_review',
        'organ': 'kidney',
        'image_name': '001_1.jpg',
        'image_path': 'd:/Projects/MedRev/test_data/肾脏/普通/成人/case_001/001_1.jpg',
        'review_result': 'gt_error',
        'error_type': None,
        'reviewer_id': 'doctor_1',
        'submitted_at': '2026-05-03T00:00:00Z',
    }
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user'] = 'doctor_1'
        sess['role'] = 'doctor'
    resp = client.post('/review', json=payload)
    assert resp.status_code == 200

    proc = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'export_review_results.py')], capture_output=True, text=True)
    print(proc.stdout)
    assert proc.returncode == 0
    assert coco_file.exists()
    print('init/export checks passed')


if __name__ == '__main__':
    main()
