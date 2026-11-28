"""Synthetic read-only sample API. Python 3.10+; no external dependencies.
Run: python sample_service/server.py --host 127.0.0.1 --port 8000
Local development only: no TLS, authentication, IDS or MSW submission.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'docs/api/v2'
CATALOG = json.loads((SITE / 'catalog.json').read_text(encoding='utf-8'))
DATA, RAW, ROUTES = {}, {}, {}
for entry in CATALOG['items']:
    sid = entry['sampleId']
    RAW[sid] = (SITE / entry['file']).read_bytes()
    DATA[sid] = json.loads(RAW[sid])
    for route in (entry['resourcePath'], '/samples/' + sid, '/' + entry['file']):
        ROUTES[route] = sid


def encode(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def openapi() -> dict:
    response = {'200': {'description': 'Synthetic JSON object', 'content': {'application/json': {'schema': {'type': 'object'}}}}, '400': {'description': 'Invalid query'}, '404': {'description': 'Unknown fixture'}, '304': {'description': 'ETag matched'}}
    paths = {}
    for entry in CATALOG['items']:
        key = 'reportId' if entry['kind'] == 'report' else 'messageId'
        path = entry['resourcePath'].rsplit('/', 1)[0] + '/{' + key + '}'
        paths.setdefault(path, {'get': {'operationId': 'get' + ('Report' if entry['kind'] == 'report' else entry['schemaName']), 'parameters': [{'in': 'path', 'name': key, 'required': True, 'schema': {'type': 'string'}, 'example': entry['recordId']}], 'responses': response}})
    params = [{'in': 'query', 'name': key, 'schema': {'type': 'string'}} for key in ('sampleId', 'scenarioId', 'serviceId', 'shipImoNumber')]
    params += [{'in': 'query', 'name': 'limit', 'schema': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 100}}, {'in': 'query', 'name': 'offset', 'schema': {'type': 'integer', 'minimum': 0, 'default': 0}}]
    for path, name in (('/samples', 'listSamples'), ('/msw-reporting/v1/reports', 'listReports')):
        paths[path] = {'get': {'operationId': name, 'parameters': params, 'responses': response}}
    paths['/samples/{sampleId}'] = {'get': {'operationId': 'getSample', 'parameters': [{'in': 'path', 'name': 'sampleId', 'required': True, 'schema': {'type': 'string', 'enum': list(DATA)}}], 'responses': response}}
    for path, name in (('/catalog', 'getCatalog'), ('/healthz', 'getHealth')):
        paths[path] = {'get': {'operationId': name, 'responses': response}}
    return {'openapi': '3.1.0', 'info': {'title': 'RD24001 read-only sample server', 'version': '1.0.0', 'description': 'Synthetic fixtures only. No writes, IDS enforcement or regulatory submission. Schemas are descriptive, not full conformance schemas.'}, 'servers': [{'url': '/'}], 'security': [], 'paths': paths}


def query_samples(query: str, reports_only: bool = False) -> dict:
    values = parse_qs(query, keep_blank_values=True, max_num_fields=20)
    allowed = {'sampleId', 'scenarioId', 'serviceId', 'shipImoNumber', 'limit', 'offset'}
    if set(values) - allowed:
        raise ValueError('Unsupported query parameter')
    if any(len(v) != 1 or not v[0] for v in values.values()):
        raise ValueError('Parameters must be non-empty and occur once')
    args = {k: v[0] for k, v in values.items()}
    try:
        limit, offset = int(args.get('limit', '100')), int(args.get('offset', '0'))
    except ValueError as exc:
        raise ValueError('limit and offset must be integers') from exc
    if not 1 <= limit <= 100 or offset < 0:
        raise ValueError('limit must be 1..100; offset must be nonnegative')
    found = []
    for entry in CATALOG['items']:
        sid = entry['sampleId']
        if reports_only and entry['kind'] != 'report':
            continue
        fields = {'sampleId': sid, 'scenarioId': entry['scenarioId'], 'serviceId': sid if entry['kind'] == 'report' else '', 'shipImoNumber': DATA[sid]['ship']['imoShipNumberId']['content']}
        if any(fields[k] != args[k] for k in fields if k in args):
            continue
        found.append({'sampleId': sid, 'data': DATA[sid]})
    return {'synthetic': True, 'total': len(found), 'limit': limit, 'offset': offset, 'items': found[offset:offset + limit]}


class Handler(BaseHTTPRequestHandler):
    server_version = 'RD24001Sample/1.0'
    sys_version = ''

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(10)

    def send_body(self, status: int, body: bytes, content_type: str = 'application/json; charset=utf-8') -> None:
        etag = '"' + hashlib.sha256(body).hexdigest() + '"'
        matched = status == 200 and self.headers.get('If-None-Match') == etag
        self.send_response(304 if matched else status)
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Access-Control-Allow-Origin', '*')
        if status == 200:
            self.send_header('ETag', etag)
        if not matched:
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
        if status == 405:
            self.send_header('Allow', 'GET, HEAD, OPTIONS')
        self.end_headers()
        if not matched and self.command != 'HEAD':
            self.wfile.write(body)

    def error(self, status: int, code: str, message: str) -> None:
        self.send_body(status, encode({'error': {'code': code, 'message': message}}))

    def do_GET(self) -> None:
        try:
            target = urlsplit(self.path)
            path = unquote(target.path)
            if path in ('/samples', '/msw-reporting/v1/reports'):
                self.send_body(200, encode(query_samples(target.query, path != '/samples')))
                return
            if target.query:
                self.error(400, 'INVALID_QUERY', 'Filters are supported only on collection endpoints')
            elif path in ROUTES:
                self.send_body(200, RAW[ROUTES[path]])
            elif path in ('/catalog', '/catalog.json'):
                self.send_body(200, encode(CATALOG))
            elif path == '/openapi.json':
                self.send_body(200, encode(openapi()))
            elif path == '/healthz':
                self.send_body(200, encode({'status': 'ok', 'mode': 'synthetic-read-only', 'sampleCount': len(DATA)}))
            elif path in ('/', '/index.html'):
                self.send_body(200, (SITE / 'index.html').read_bytes(), 'text/html; charset=utf-8')
            else:
                self.error(404, 'NOT_FOUND', 'No fixture exists for this path')
        except ValueError as exc:
            self.error(400, 'INVALID_QUERY', str(exc))

    do_HEAD = do_GET

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header('Allow', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'If-None-Match')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def readonly(self) -> None:
        self.close_connection = True
        self.error(405, 'READ_ONLY', 'Only GET, HEAD and OPTIONS are supported')

    do_POST = do_PUT = do_PATCH = do_DELETE = do_TRACE = do_CONNECT = readonly


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error('port must be between 0 and 65535')
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f'RD24001 synthetic read-only demo: http://{args.host}:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
