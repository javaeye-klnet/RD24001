# RD24001 샘플 조회 API

스마트·자율운항선박 밸류체인 데이터 통합 설계 v2의 **합성 샘플 16종**을 조회하는 공개 GET 인터페이스와 로컬 실행용 API 서버입니다. 기존 `docs/bp-query-samples/`는 변경하지 않았습니다.

## 바로 조회

| 구분 | 링크 |
| --- | --- |
| 전체 샘플 목록 | [catalog.json](https://raw.githubusercontent.com/javaeye-klnet/RD24001/main/docs/api/v2/catalog.json) |
| BP-01 센서 관측 | [BT-01-01.json](https://raw.githubusercontent.com/javaeye-klnet/RD24001/main/docs/api/v2/samples/BT-01-01.json) |
| S1 AI 의사결정 감사 로그 | [S1.json](https://raw.githubusercontent.com/javaeye-klnet/RD24001/main/docs/api/v2/samples/S1.json) |
| S2 ROC 운항상황 | [S2.json](https://raw.githubusercontent.com/javaeye-klnet/RD24001/main/docs/api/v2/samples/S2.json) |
| S3 사이버보안 이상탐지 | [S3.json](https://raw.githubusercontent.com/javaeye-klnet/RD24001/main/docs/api/v2/samples/S3.json) |
| S4 환경 배출량 | [S4.json](https://raw.githubusercontent.com/javaeye-klnet/RD24001/main/docs/api/v2/samples/S4.json) |
| 공개 조회용 OpenAPI | [openapi.json](docs/api/v2/openapi.json) |

위 주소는 고정 JSON을 반환하는 **정적 샘플 조회 경로**입니다. 검색조건에 따라 결과를 생성하는 외부 API 서버가 배포된 것은 아닙니다. 인증이나 IDS 계약·정책 집행 기능은 없으며 실제 운항·개인·기밀 데이터를 게시하면 안 됩니다. GitHub raw의 응답 Content-Type은 text/plain일 수 있으므로 IDS 커넥터 연계 시 확인해야 합니다.

## 동적 조건 조회: 로컬 API 서버

Python 3.10 이상에서 별도 패키지 설치 없이 실행합니다.

```bash
git clone https://github.com/javaeye-klnet/RD24001.git
cd RD24001
python sample_service/server.py --host 127.0.0.1 --port 8000
```

샘플 조회 화면: `http://127.0.0.1:8000/`

```bash
curl 'http://127.0.0.1:8000/samples?scenarioId=BP-05'
curl 'http://127.0.0.1:8000/msw-reporting/v1/reports?serviceId=S1'
curl 'http://127.0.0.1:8000/msw-reporting/v1/reports/REPORT-S1-001'
```

[구현·실행 안내](sample_service/README.md) / [서버 코드](sample_service/server.py) / [시험 코드](sample_service/test_server.py) / [로컬 검증 결과](sample_service/validation_results.json)

## 범위

BP 6종의 교환 메시지 12개와 S1~S4 보고 샘플 4개를 제공합니다. 공개 정적 GET 명세는 목록을 포함해 17개 작업, 로컬 서버 명세는 조건 조회 등을 포함해 18개 GET 작업입니다. 원래 설계서의 37개 작업 전체를 구현한 것은 아닙니다. 생성·수정·MSW 제출·경제모델 정산과 실제 IDS 등록·인증·계약협상·이용정책 집행은 포함하지 않습니다.

로컬 HTTP 시험 66건과 원 설계 패키지의 정적 검사 53건을 수행했습니다. 공인시험·국가 MSW 연계시험·IDS 상호운용 시험 결과가 아닙니다. 메시지 내부의 선박번호·명칭·코드·계수·증빙은 합성 예시이며, IMO/UN/CEFACT 공식 발행·승인 모델로 표시하지 않습니다.

`docs/api/v2/index.html`은 조회 화면 소스입니다. GitHub Pages 활성화나 외부 실행 서버 배포는 이 변경에 포함하지 않았습니다.
