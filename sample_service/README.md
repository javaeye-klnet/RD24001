# RD24001 read-only sample API

16 synthetic fixtures from integrated design v2: 12 BT messages across BP-01 to BP-06 and four reports S1-S4. Existing `docs/bp-query-samples/` files are unchanged. Model version: `2.0.0-draft.1`. Sample service version: `1.0.0`.

## Public GET endpoints

Base URL: `https://raw.githubusercontent.com/javaeye-klnet/RD24001/main/docs/api/v2`

| Path | Content |
| --- | --- |
| `/catalog.json` | All 16 samples and their scenario, schema and runtime resource paths |
| `/samples/BT-01-01.json` through `/samples/BT-06-02.json` | Two exchange messages for each BP |
| `/samples/S1.json` | AI decision audit report |
| `/samples/S2.json` | ROC operation report |
| `/samples/S3.json` | Cyber incident report |
| `/samples/S4.json` | Environmental emission report |
| `/openapi.json` | Static GET-only OpenAPI: 17 operations |

```bash
curl -fSL 'https://raw.githubusercontent.com/javaeye-klnet/RD24001/main/docs/api/v2/samples/S1.json'
```

These URLs return static JSON bodies, not a dynamic backend. GitHub raw can label them `text/plain`; an Accept header does not force the response type. Query strings do not filter. Unknown paths use the host's own errors. No authentication or IDS usage-policy enforcement is implemented. Do not publish operational or confidential data here.

## Executable query server

Python 3.10+; standard library only. This code is NOT automatically executed by GitHub or GitHub Pages.

```bash
git clone https://github.com/javaeye-klnet/RD24001.git
cd RD24001
python sample_service/server.py --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the sample browser. `/openapi.json` describes 18 implemented GET operations. HEAD and OPTIONS are also supported. Write methods return 405, invalid queries return 400, and unknown records return 404. Supported filters: `sampleId`, `scenarioId`, `serviceId`, `shipImoNumber`, `limit`, `offset`.

```bash
curl 'http://127.0.0.1:8000/samples?scenarioId=BP-05&limit=10'
curl 'http://127.0.0.1:8000/msw-reporting/v1/reports?serviceId=S1'
curl 'http://127.0.0.1:8000/msw-reporting/v1/reports/REPORT-S1-001'
curl 'http://127.0.0.1:8000/maritime-data/v1/sensorObservations/MSG-BT-01-01'
python -m unittest discover -s sample_service -v
```

This is a local development server, not production Internet hosting. There is no TLS, authentication, IDS negotiation or policy enforcement, persistence, real MSW submission or economic settlement. Deployment/security work is required for an externally hosted runtime.

## Browser and Pages

`docs/api/v2/index.html` provides client-side scenario/type filters and JSON previews. It works through the local server. This change does not enable or claim a GitHub Pages deployment. The public raw JSON URLs do not require Pages. Opening raw HTML does not launch the UI.

## Provenance and validation

Fixture JSON objects are preserved from `examples/` of `RD24001_Integrated_Design_Package_v2.zip`; only whitespace is compacted. `fixture_checksums.json` hashes the published bytes. Embedded evidence hashes and IDs remain illustrative, not independently verified audit evidence.

66 local HTTP unit tests passed. They cover fixture reads, business paths, filters, pagination, HEAD, OPTIONS, ETag, invalid queries, unknown records and write rejection. This is not GitHub-hosted runtime validation, a load test or an accredited test report. Original design validation separately passed 53 static cases. The original 37 design operations are NOT all implemented: creation, submission, validation and economy endpoints are outside this read-only sample service.

IMO numbers, names, reports, coefficients and codes are synthetic. The model is a project draft referencing IMO semantics and UN/CEFACT conventions, not an officially approved IMO/UN/CEFACT API. No complete standard-conformance, IDS-certification, environmental-verification or regulatory-acceptance claim is made.
