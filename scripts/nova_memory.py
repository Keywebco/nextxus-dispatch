"""Snapshot verified Nova observations into Catalyst session memory."""

import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import yaml

TARGET = 'Keywebco/sovereign-knowledge-os'
API = f'https://api.github.com/repos/{TARGET}/contents/'
FOUNDATION = 'https://github.com/Keywebco/sovereign-knowledge-os/blob/main/knowledge/echo-core.md'
NODE = re.compile(r'EC-(\d{3,})')


def latest_file(folder, pattern):
    files = sorted(Path(folder).glob(pattern))
    return files[-1] if files else None


def report(path, label):
    if not path or not path.exists():
        return f'{label}: unavailable; no report has been committed.'
    return f'Source: `{path.name}`\n\n{path.read_text(encoding="utf-8").strip()}'


def health_state(path):
    if not path:
        return ('unknown — no health report committed', 0, 0, 0, ['Unknown'])
    rows = re.findall(r'^\|\s*(https?://[^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$',
                      path.read_text(encoding='utf-8'), flags=re.M)
    checked = len(rows)
    passing = sum('✅' in status for _, status in rows)
    failing = [f'{url} ({status})' for url, status in rows if '✅' not in status]
    operational = 'yes' if checked and not failing else ('no' if checked else 'unknown — health report has no checks')
    return operational, checked, checked, passing, failing


def items(values, empty):
    if not values:
        return f'- {empty}'
    return '\n'.join('- ' + (json.dumps(value, ensure_ascii=False, sort_keys=True)
                             if isinstance(value, (dict, list)) else str(value)) for value in values)


def escape_cell(value):
    return str(value or 'Not recorded').replace('|', '\\|').replace('\n', ' ')


def build_snapshot(root, now):
    root = Path(root)
    lattice = yaml.safe_load((root / 'lattice/lattice_state.yaml').read_text(encoding='utf-8'))
    health = latest_file(root / 'health-reports', '????-??-??-??.md')
    operational, checked, total, passing, failing = health_state(health)
    directives = sorted((root / 'directives').glob(f'*{now:%Y-%m-%d}*')) if (root / 'directives').is_dir() else []
    workers = lattice.get('workers') or {}
    rows = '\n'.join(f'| {escape_cell(name)} | {escape_cell(data.get("last_run"))} | {escape_cell(data.get("last_result"))} |'
                     for name, data in workers.items())
    contents = [
        f'# Catalyst Session Memory — {now:%Y-%m-%d}', '',
        f'Last updated: {now:%H:%M} UTC', '',
        'Operational snapshot from committed reports. A missing or old check is not live verification.', '',
        '## System State (EC-S001)',
        f'- Federation operational: {operational} (latest committed health report only)',
        f'- Sites checked: {checked} of {total} in latest health report',
        f'- Sites passing: {passing}',
        f'- Sites failing: {", ".join(failing) if failing else "None recorded"}',
        f'- Health source: `{health.relative_to(root)}`' if health else '- Health source: unavailable', '',
        '## Open Issues (EC-S002)', items(lattice.get('open_issues'), 'None recorded in lattice.'), '',
        '## Active Work Orders (EC-S003)', items(lattice.get('work_orders'), 'None recorded in lattice.'), '',
        '## Workers Last Run (EC-S004)',
        '| Worker | Last Run | Result |', '|--------|----------|--------|',
        rows or '| No workers recorded | Not recorded | Not recorded |', '',
        '## Domains Status (EC-S005)',
        report(root / 'lattice/nova-domain-report.md', 'Domain report'), '',
        '## Commerce Status (EC-S006)',
        report(root / 'lattice/nova-commerce-report.md', 'Commerce report'), '',
        '## Today\'s Directives (EC-S007)',
        '\n\n'.join(report(path, 'Directive') for path in directives) if directives else 'No directives logged today.', '',
        '## Additional Worker Reports',
        '### Nova Dispatch',
        report(latest_file(root / 'lattice', 'nova-dispatch*.md') or latest_file(root / 'dispatch', '????-??-??-status.md'), 'Dispatch report'), '',
        '### Nova Health', report(root / 'lattice/nova-health-report.md' if (root / 'lattice/nova-health-report.md').exists() else health, 'Health report'), '',
        '### Nova Readability', report(root / 'lattice/nova-readability-report.md', 'Readability report'), '',
        '## Foundation Knowledge', f'See: {FOUNDATION}',
    ]
    return '\n'.join(contents).rstrip() + '\n'


def api(path, token, payload=None):
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28'}
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    if data is not None:
        headers['Content-Type'] = 'application/json'
    request = Request(API + path, data=data, headers=headers, method='PUT' if data is not None else 'GET')
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        if error.code == 404 and payload is None:
            return None
        raise


def existing(path, token):
    result = api(path, token)
    if result is None:
        return '', None
    if result.get('type') != 'file':
        raise ValueError(f'Not a file: {path}')
    return base64.b64decode(result['content']).decode('utf-8'), result['sha']


def put(path, text, token, message):
    for attempt in range(3):
        previous, sha = existing(path, token)
        if previous == text:
            return
        payload = {'message': message, 'content': base64.b64encode(text.encode()).decode(), 'branch': 'main'}
        if sha:
            payload['sha'] = sha
        try:
            api(path, token, payload)
            saved, _ = existing(path, token)
            if saved != text:
                raise RuntimeError(f'GET verification failed for {path}')
            print(f'GET verified: {TARGET}/{path}')
            return
        except HTTPError as error:
            if error.code not in (409, 422) or attempt == 2:
                raise
    raise RuntimeError(f'Could not write {path}')


def next_id(token):
    entries = api('memory', token) or []
    highest = 64
    for entry in entries:
        if entry['name'].startswith('catalyst-session-') and entry['name'].endswith('.md'):
            text, _ = existing('memory/' + entry['name'], token)
            highest = max(highest, *(int(match) for match in NODE.findall(text)), 64)
    return highest + 1


def publish(root, now, token):
    snapshot = build_snapshot(root, now)
    day_path = f'memory/catalyst-session-{now:%Y-%m-%d}.md'
    stamp = f'{now:%Y-%m-%d %H:%M} UTC'
    previous, _ = existing(day_path, token)
    if f'Run: {stamp}' not in previous:
        entry = f'## EC-{next_id(token):03d} — Catalyst session entry\nRun: {stamp}\n\n{snapshot}\n'
        daily = (previous.rstrip() + '\n\n' if previous else f'# Catalyst Session Log — {now:%Y-%m-%d}\n\n') + entry
        put(day_path, daily, token, f'memory: Catalyst session {stamp}')
    put('memory/catalyst-latest.md', snapshot, token, f'memory: refresh Catalyst latest {stamp}')


if __name__ == '__main__':
    token = os.environ.get('SOVEREIGN_KNOWLEDGE_TOKEN')
    if not token:
        sys.exit('SOVEREIGN_KNOWLEDGE_TOKEN is required (cross-repository contents:write)')
    publish(Path('.'), datetime.now(timezone.utc), token)
