import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app import app


def run():
    client = app.test_client()
    r1 = client.get('/tasks/hard')
    print('GET /tasks/hard ->', r1.status_code, len(r1.get_json()))
    r2 = client.get('/tasks/pseudo')
    print('GET /tasks/pseudo ->', r2.status_code, len(r2.get_json()))
    # pick a task_id from hard if exists
    hard = r1.get_json()
    if hard:
        tid = hard[0]['task_id']
        r3 = client.get(f'/task/{tid}')
        print(f'GET /task/{tid} ->', r3.status_code)
    # post a fake review
    with client.session_transaction() as sess:
        sess['user'] = 'doctor_1'
        sess['role'] = 'doctor'
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
        'submitted_at': '2026-05-02T12:00:00Z'
    }
    r4 = client.post('/review', json=payload)
    print('POST /review ->', r4.status_code, r4.get_json())
    # render image for the hard task
    resp = client.get('/render', query_string={'task_id': payload['task_id'], 'show': 'both'})
    print('GET /render ->', resp.status_code, 'content-type:', resp.content_type)
    if resp.status_code == 200:
        out = Path(__file__).resolve().parents[1] / 'backend_render.jpg'
        out.write_bytes(resp.data)
        print('Wrote render to', out)


if __name__ == '__main__':
    run()
