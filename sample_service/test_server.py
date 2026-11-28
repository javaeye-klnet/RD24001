"""Run: python -m unittest discover -s sample_service -v"""
import hashlib
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
import server


class QuietHandler(server.Handler):
    def log_message(self, *_args):
        pass


class SampleApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=5)

    def request(self, path, method='GET', headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.httpd.server_port, timeout=5)
        try:
            conn.request(method, path, headers=headers or {})
            r = conn.getresponse()
            return r.status, dict(r.getheaders()), r.read()
        finally:
            conn.close()

    def test_catalog(self):
        status, _, body = self.request('/catalog')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['count'], 16)

    def test_fixture_checksums(self):
        manifest = json.loads((server.ROOT / 'sample_service/fixture_checksums.json').read_text())
        self.assertEqual(len(manifest), 16)
        for filename, digest in manifest.items():
            self.assertEqual(hashlib.sha256((server.ROOT / filename).read_bytes()).hexdigest(), digest)

    def test_query_all(self):
        self.assertEqual(json.loads(self.request('/samples')[2])['total'], 16)

    def test_query_scenario(self):
        self.assertEqual(json.loads(self.request('/samples?scenarioId=BP-05')[2])['total'], 5)

    def test_query_service(self):
        result = json.loads(self.request('/samples?serviceId=S1')[2])
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['items'][0]['data'], server.DATA['S1'])

    def test_query_ship(self):
        self.assertEqual(json.loads(self.request('/samples?shipImoNumber=1234567')[2])['total'], 16)

    def test_query_empty_result(self):
        self.assertEqual(json.loads(self.request('/samples?shipImoNumber=9999999')[2])['total'], 0)

    def test_query_pagination(self):
        result = json.loads(self.request('/samples?limit=2&offset=2')[2])
        self.assertEqual(result['total'], 16)
        self.assertEqual([i['sampleId'] for i in result['items']], ['BT-02-01', 'BT-02-02'])

    def test_report_collection(self):
        self.assertEqual(json.loads(self.request('/msw-reporting/v1/reports')[2])['total'], 4)

    def test_runtime_openapi(self):
        status, _, body = self.request('/openapi.json')
        api = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(len(api['paths']), 18)
        self.assertTrue(all(set(item) == {'get'} for item in api['paths'].values()))
        self.assertEqual(len({v['get']['operationId'] for v in api['paths'].values()}), 18)

    def test_static_openapi(self):
        api = json.loads((server.SITE / 'openapi.json').read_text())
        self.assertEqual(len(api['paths']), 17)
        self.assertTrue(all(set(item) == {'get'} for item in api['paths'].values()))

    def test_not_found(self):
        for path in ('/samples/NOPE', '/samples/../../README.md', '/msw-reporting/v1/reports/NOPE'):
            self.assertEqual(self.request(path)[0], 404)

    def test_invalid_query(self):
        for query in ('limit=0', 'limit=101', 'offset=-1', 'limit=nope', 'scenarioId=', 'x=1', 'limit=1&limit=2'):
            self.assertEqual(self.request('/samples?' + query)[0], 400)
        self.assertEqual(self.request('/samples/S1?x=1')[0], 400)

    def test_write_rejected(self):
        for method in ('POST', 'PUT', 'PATCH', 'DELETE', 'TRACE', 'CONNECT'):
            status, headers, body = self.request('/samples/S1', method)
            self.assertEqual(status, 405)
            self.assertEqual(headers['Allow'], 'GET, HEAD, OPTIONS')
            self.assertEqual(json.loads(body)['error']['code'], 'READ_ONLY')

    def test_etag(self):
        _, headers, _ = self.request('/samples/S1')
        status, _, body = self.request('/samples/S1', headers={'If-None-Match': headers['ETag']})
        self.assertEqual((status, body), (304, b''))

    def test_options(self):
        status, _, body = self.request('/samples/S1', 'OPTIONS')
        self.assertEqual((status, body), (204, b''))

    def test_ui(self):
        status, headers, body = self.request('/')
        self.assertEqual(status, 200)
        self.assertIn('text/html', headers['Content-Type'])
        self.assertIn(b'RD24001', body)

    def test_health(self):
        self.assertEqual(json.loads(self.request('/healthz')[2])['sampleCount'], 16)


def add_fixture_tests(sid):
    def get_test(self):
        for path in ('/samples/' + sid, '/samples/' + sid + '.json'):
            status, headers, body = self.request(path)
            self.assertEqual(status, 200)
            self.assertIn('application/json', headers['Content-Type'])
            self.assertEqual(json.loads(body), server.DATA[sid])
    def head_test(self):
        status, headers, body = self.request('/samples/' + sid, 'HEAD')
        self.assertEqual((status, body), (200, b''))
        self.assertEqual(int(headers['Content-Length']), len(server.RAW[sid]))
    def resource_test(self):
        path = next(e['resourcePath'] for e in server.CATALOG['items'] if e['sampleId'] == sid)
        status, _, body = self.request(path)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), server.DATA[sid])
    key = sid.replace('-', '_')
    setattr(SampleApiTests, 'test_fixture_' + key, get_test)
    setattr(SampleApiTests, 'test_head_' + key, head_test)
    setattr(SampleApiTests, 'test_resource_' + key, resource_test)


for sample_id in server.DATA:
    add_fixture_tests(sample_id)

if __name__ == '__main__':
    unittest.main()
