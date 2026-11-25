# RD24001 BP-01~06 static query samples

Public synthetic data only. HTTP GET paths encode a single fixed example: ship ID 1234567, arrival year 2026, arrival sequence 001. The identifiers are simulated; arrival sequence is distinct from the operator-assigned voyageNumber RV-TEST-001. The JSON is a projection of the project's original BP event payloads, not a certified IMO or regulatory report. These are static files, not a dynamic query API: other paths return 404 and query strings do not filter. Source values are not independently verified. No authentication or IDS policy enforcement is implemented. GitHub raw may return text/plain even though the body is JSON; check compatibility with the target IDS connector. Do not publish operational data here.

OpenAPI: `openapi.json`. Sample path: `ships/1234567/arrivals/2026/001/bp-01.json` (through bp-06.json).
