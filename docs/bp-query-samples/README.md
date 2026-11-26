# RD24001 BP-01~06 static query samples

Public synthetic data only. HTTP GET paths encode a single fixed example: IMO ship number 1234567, arrival year 2026, arrival sequence 001. The voyage number 001W is a synthetic example distinct from the port arrival sequence. The IMO ship number and voyage number map semantically to IMO0140 and IMO0191 respectively; their JSON names are project names, not an official IMO schema. Other fields, including arrivalYear, arrivalSequence and the BP payload, remain RD24001 project data and are not asserted to be IMO elements. The output preserves BP source payloads, but the synthetic voyage number is changed from the original RV-TEST-001. See imo-mapping.json for exact sources and limits.

Version 3: the JSON key `imoShipNumber` is renamed to `shipImoNumber` to follow the displayed IMO data element name, Ship IMO number. IMO0140's Reference Model name is `FAL_ Transport Means. IMO Ship Number. Identifier`; the camel-case JSON key is a project convention, not an IMO-published JSON property. Existing consumers must update their field mapping.

These are static files, not a dynamic query API: other paths return 404 and query strings do not filter. The content is not a certified IMO model or regulatory report. Source values are not independently verified. No authentication or IDS policy enforcement is implemented. GitHub raw may return text/plain even though the body is JSON; check compatibility with the target IDS connector. Do not publish operational data here.

OpenAPI: `openapi.json`. Sample path: `ships/1234567/arrivals/2026/001/bp-01.json` (through bp-06.json).
