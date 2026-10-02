from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import nova_memory as memory

NOW = datetime(2026, 10, 2, 4, 0, tzinfo=timezone.utc)


def fixture(root):
    (root / 'lattice').mkdir()
    (root / 'health-reports').mkdir()
    (root / 'lattice/lattice_state.yaml').write_text('''workers:
  nova-domain: {last_run: '2026-10-02T02:30:00Z', last_result: 1 bad}
open_issues: [broken SSL]
work_orders: [repair certificate]
''')
    (root / 'health-reports/2026-10-02-01.md').write_text('''| URL | Status |
| --- | --- |
| https://ok.example | ✅ 200 |
| https://bad.example | ❌ 403 |
''')
    (root / 'lattice/nova-domain-report.md').write_text('One bad domain')
    (root / 'lattice/nova-commerce-report.md').write_text('All passing')
    (root / 'lattice/nova-readability-report.md').write_text('8 checked')
    (root / 'dispatch').mkdir()
    (root / 'dispatch/2026-10-02-status.md').write_text('Daily dispatch')


def test_build_snapshot_happy_path(tmp_path):
    fixture(tmp_path)
    (tmp_path / 'directives').mkdir()
    (tmp_path / 'directives/2026-10-02-directive.md').write_text('Stay grounded')
    snapshot = memory.build_snapshot(tmp_path, NOW)
    for value in ['EC-S001', 'EC-S007', 'Sites checked: 2 of 2', 'Sites passing: 1',
                  'https://bad.example', 'broken SSL', 'repair certificate', 'One bad domain',
                  'All passing', 'Daily dispatch', '8 checked', 'Stay grounded']:
        assert value in snapshot
    assert 'Federation operational: no' in snapshot


def test_missing_reports_not_misrepresented_as_healthy(tmp_path):
    (tmp_path / 'lattice').mkdir()
    (tmp_path / 'lattice/lattice_state.yaml').write_text('workers: {}\nopen_issues: []\nwork_orders: []\n')
    snapshot = memory.build_snapshot(tmp_path, NOW)
    assert 'Federation operational: unknown' in snapshot
    assert 'No directives logged today.' in snapshot
    assert 'Domain report: unavailable' in snapshot
    assert 'Sites checked: 0 of 0' in snapshot


def test_publish_appends_daily_and_refreshes_latest(tmp_path, monkeypatch):
    fixture(tmp_path)
    saved = {}
    monkeypatch.setattr(memory, 'existing', lambda path, token: (saved.get(path, ''), None))
    monkeypatch.setattr(memory, 'next_id', lambda token: 65 if not saved else 66)
    monkeypatch.setattr(memory, 'put', lambda path, text, token, message: saved.__setitem__(path, text))
    memory.publish(tmp_path, NOW, 'test')
    assert '## EC-065' in saved['memory/catalyst-session-2026-10-02.md']
    memory.publish(tmp_path, NOW, 'test')
    assert saved['memory/catalyst-session-2026-10-02.md'].count('Run: 2026-10-02 04:00 UTC') == 1
    memory.publish(tmp_path, NOW.replace(hour=8), 'test')
    assert '## EC-066' in saved['memory/catalyst-session-2026-10-02.md']
    assert 'Last updated: 08:00 UTC' in saved['memory/catalyst-latest.md']
