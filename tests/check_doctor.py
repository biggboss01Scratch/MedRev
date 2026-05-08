import sys
import importlib.util

sys.path.insert(0, r'D:\Projects\MedRev')
spec = importlib.util.spec_from_file_location("appmod", r"D:\Projects\MedRev\backend\app.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
app = getattr(mod, 'app')
resp = app.test_client().get('/doctor')
print('status', resp.status_code)
print('content-type', resp.headers.get('Content-Type'))
print('len', len(resp.data))
