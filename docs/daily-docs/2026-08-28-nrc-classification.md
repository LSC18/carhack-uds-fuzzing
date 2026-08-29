# [2026-08-28] UDS NRC 정의 분석 및 표준·비표준 응답 분류

## 1. 오늘 확인할 질문

기존 UDS Fuzz Harness에서 수집한 NRC 값을 공개 구현체의 NRC 정의와 비교하여, 정의된 값과 정의되지 않은 값을 자동으로 분류할 수 있는가?

## 2. 진행 내용

- 작업 대상: 공개 UDS 구현체 `driftregion/iso14229`
- 대상 커밋: `77063d27`
- 사용 환경: Ubuntu 24.04 ARM64, VMware Fusion
- 작업 구분: 공개 구현 분석 / PoC 개발
- 상태: 완료
- 소요 시간: 실제 소요 시간 입력
- 사용 도구: Python 3, grep, awk, Git
- 분석 파일: `/home/lsc18/carhack-targets/iso14229/src/uds.h`
- 입력 로그: `logs/day02-nrc-detail.log`

`src/uds.h`에서 NRC 이름과 16진수 값을 확인하고, 이전 차시에서 수집한 NRC 로그를 자동 분류하는 Python 스크립트를 작성했다.

```bash
grep -RInE 'UDS_NRC_[A-Za-z0-9_]+[[:space:]]*=' \
  src iso14229.h 2>/dev/null
```

```bash
python3 scripts/classify_nrc.py
```

분류 기준은 다음과 같다.

- `DEFINED`: 대상 구현체의 `src/uds.h`에 이름과 값이 정의된 NRC
- `UNKNOWN`: 퍼징 로그에서 관측됐지만 해당 헤더에 정의되지 않은 값

## 3. 직접 작성·수정한 부분

다음 스크립트를 직접 작성했다.

- `scripts/classify_nrc.py`

스크립트는 다음 순서로 동작한다.

1. `src/uds.h`에서 NRC 이름과 값을 정규표현식으로 추출한다.
2. `day02-nrc-detail.log`에서 `nrc=0xXX` 값을 추출한다.
3. NRC별 발생 횟수를 계산한다.
4. 구현체 정의 여부에 따라 `DEFINED` 또는 `UNKNOWN`으로 분류한다.
5. 결과를 CSV 파일로 저장한다.

## 4. 결과

### 입력

- NRC 상세 로그: `logs/day02-nrc-detail.log`
- 구현체 NRC 정의: `/home/lsc18/carhack-targets/iso14229/src/uds.h`

### 출력

- 구현체에 정의된 NRC: 59종
- 로그에서 관측된 NRC: 63종
- 전체 Negative Response: 48,988건
- `DEFINED`: 56종, 48,980건
- `UNKNOWN`: 7종, 8건

상위 관측 결과는 다음과 같다.

| NRC | 발생 횟수 | 분류 | 이름 |
|---|---:|---|---|
| `0x10` | 35,815 | DEFINED | GeneralReject |
| `0x13` | 6,337 | DEFINED | IncorrectMessageLengthOrInvalidFormat |
| `0x31` | 2,309 | DEFINED | RequestOutOfRange |
| `0x70` | 1,623 | DEFINED | UploadDownloadNotAccepted |
| `0x12` | 828 | DEFINED | SubFunctionNotSupported |

UNKNOWN으로 분류된 값은 다음과 같다.

```text
0xFF, 0x29, 0x19, 0x04, 0xD0, 0x01, 0x30
```

### 판단

기존 Harness에서 생성된 NRC를 구현체 정의와 자동으로 비교하고 분류하는 데 성공했다.

다만 현재 결과는 실제 ECU나 실제 펌웨어의 응답이 아니다. Mock ISO-TP 기반 공개 UDS 구현체의 Harness에서 생성된 결과이며, callback 반환값 자체도 퍼징되므로 일부 UNKNOWN 값이 발생할 수 있다.

## 5. 증거

- `day03-01-nrc-definitions.png`: 공개 구현체의 NRC 이름 확인
- `day03-02-nrc-value-mapping.png`: NRC 이름과 16진수 값 매핑 확인
- `day03-03-nrc-classification.png`: 분류 스크립트 실행 및 CSV 출력
- `day03-04-classification-summary.png`: DEFINED·UNKNOWN 통계와 UNKNOWN 값 확인
- `day03-05-classifier-source.png`: 직접 작성한 Python 분류 스크립트

### 코드 및 결과 경로

- 분류 코드: `scripts/classify_nrc.py`
- NRC 정의 검색 로그: `logs/day03-nrc-definitions.log`
- 스크립트 실행 로그: `logs/day03-classifier-run.log`
- 전체 분류 결과: `results/day03-nrc-classification.csv`
- 분류 요약: `results/day03-classification-summary.csv`
- UNKNOWN 목록: `results/day03-unknown-nrc.csv`
- GitHub Commit: 커밋 후 입력

## 6. 문제 및 시행착오

- 처음에는 관측된 NRC 값을 숫자로만 집계하여 각 값의 의미를 바로 확인하기 어려웠다.
- 대상 구현체의 `src/uds.h`를 직접 분석해 NRC 이름과 값을 추출하도록 분류 스크립트를 작성했다.
- UNKNOWN 값은 곧바로 취약점이나 비정상 ECU 동작을 의미하지 않는다. Mock Harness에서 callback 반환값까지 변형되기 때문에 생성될 수 있다.

## 7. 다음 작업

NRC 유형에 따라 다음 입력 생성 전략을 달리하는 NRC 기반 입력 선택 로직을 설계하고, 기존 무작위 입력 방식과 비교한다.

## 오늘의 한 줄 결론

공개 UDS 구현체의 NRC 정의를 자동 추출하고, 48,988건의 응답을 DEFINED 48,980건과 UNKNOWN 8건으로 분류하는 스크립트를 구현했다.
