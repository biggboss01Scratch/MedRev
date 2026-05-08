import sys, importlib.util
sys.path.insert(0, r'D:\Projects\MedRev')
spec = importlib.util.spec_from_file_location("appmod", r"D:\Projects\MedRev\backend\app.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
app = getattr(mod, 'app')
client = app.test_client()
# login
r = client.post('/login', data={'username':'doctor_1','password':'password1'}, follow_redirects=True)
print('login status', r.status_code)
# get doctor page
r2 = client.get('/doctor')
print('doctor status', r2.status_code)
print('contains user', b'doctor_1' in r2.data)
# submit a dummy review (needs a task to exist)
payload = {
  'run_id': 'test_run_001',
  'task_id': 'test_task',
  'task_type': 'hard_sample_gt_review',
  'organ': '肾脏',
  'image_name': 'x.jpg',
  'image_path': 'fake',
  'review_result': 'gt_correct',
  'reviewer_id': 'should_be_overridden',
  'submitted_at': '2026-05-02T00:00:00Z'
}
import json
r3 = client.post('/review', json=payload)
print('post review', r3.status_code, r3.get_json())
