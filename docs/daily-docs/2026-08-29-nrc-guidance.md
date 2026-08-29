# [2026-08-29] NRC 기반 Guided Input 전략 생성

## 1. 오늘 확인할 질문

관측된 NRC 종류에 따라 다음 퍼징 입력의 변형 방향을 자동으로 추천할 수 있는가?

## 2. 진행 내용

- 작업 대상: 3일차 NRC 분류 결과
- 입력 파일: `results/day03-nrc-classification.csv`
- 사용 환경: Ubuntu 24.04 ARM64, VMware Fusion
- 작업 구분: PoC 개발
- 상태: 완료
- 소요 시간: 약 20분
- 사용 도구: Python 3, awk, grep, Git

NRC 분류 결과를 입력으로 받아 NRC별 다음 입력 전략을 생성하는 Python 스크립트를 직접 작성했다.

```text
scripts/generate_nrc_guidance.py
```

주요 대응 규칙은 다음과 같다.

| NRC | 의미 | 다음 입력 전략 |
|---|---|---|
| `0x11` | ServiceNotSupported | CHANGE_SERVICE |
| `0x12` | SubFunctionNotSupported | MUTATE_SUBFUNCTION |
| `0x13` | IncorrectMessageLengthOrInvalidFormat | REPAIR_LENGTH |
| `0x21` | BusyRepeatRequest | RETRY_WITH_DELAY |
| `0x22` | ConditionsNotCorrect | CHANGE_STATE |
| `0x24` | RequestSequenceError | BUILD_SEQUENCE |
| `0x31` | RequestOutOfRange | MUTATE_PARAMETER |
| `0x33` | SecurityAccessDenied | CHANGE_SESSION_PATH |
| `0x35` | InvalidKey | MUTATE_SECURITY_INPUT |
| `0x36` | ExceedNumberOfAttempts | RESET_SECURITY_SEQUENCE |
| `0x37` | RequiredTimeDelayNotExpired | WAIT_AND_RETRY |
| `0x70` | UploadDownloadNotAccepted | CHANGE_TRANSFER_PRECONDITION |

실행 명령은 다음과 같다.

```bash
python3 -m py_compile scripts/generate_nrc_guidance.py

python3 scripts/generate_nrc_guidance.py | \
  tee logs/day04-guidance-run.log
```

## 3. 결과

### 입력

- 관측된 NRC 유형: 63종
- 전체 Negative Response: 48,988건

### 출력

```text
observed_nrc_types=63
guided_types=19
output=results/day04-nrc-guidance.csv
```

별도 전략이 지정된 19종은 직접 정의한 핵심 NRC 12종과 UNKNOWN 7종으로 구성된다.

주요 결과는 다음과 같다.

| NRC 또는 분류 | 발생 건수 | 생성된 전략 |
|---|---:|---|
| `0x13` | 6,337 | REPAIR_LENGTH |
| `0x31` | 2,309 | MUTATE_PARAMETER |
| `0x70` | 1,623 | CHANGE_TRANSFER_PRECONDITION |
| `0x12` | 828 | MUTATE_SUBFUNCTION |
| `0x22` | 367 | CHANGE_STATE |
| `0x37` | 199 | WAIT_AND_RETRY |
| UNKNOWN | 8 | LOG_AND_EXPLORE |

다음 핵심 규칙의 자동 검증이 모두 통과했다.

```text
PASS: 0x13 -> REPAIR_LENGTH
PASS: 0x31 -> MUTATE_PARAMETER
PASS: 0x22 -> CHANGE_STATE
PASS: 0x37 -> WAIT_AND_RETRY
PASS: UNKNOWN -> LOG_AND_EXPLORE
```

### 성공·실패 판단

- NRC별 대응 규칙을 코드로 구현했다.
- 63종의 관측 NRC에 다음 입력 전략을 할당했다.
- 핵심 규칙 5개의 자동 검증이 모두 통과했다.
- 전략별 NRC 종류와 전체 발생 건수를 CSV로 저장했다.

### 한계

현재 스크립트는 NRC를 분석하여 다음 입력 전략을 추천하는 단계다. 추천된 전략이 실제 Fuzz Harness의 입력 생성 과정에 다시 적용되는 완전한 피드백 루프는 아직 구현되지 않았다.

또한 실제 ECU 펌웨어가 아닌 공개 UDS 구현체와 Mock ISO-TP 환경에서 생성된 데이터를 사용했다.

## 4. 증거

- `day04-01-guidance-result.png`: NRC별 Guided Input 전략 생성 결과
- `day04-02-guidance-validation.png`: 핵심 규칙 5개의 자동 검증 결과
- `day04-03-guidance-source.png`: 직접 작성한 전략 생성 스크립트

### 코드 및 결과 경로

- 전략 생성 코드: `scripts/generate_nrc_guidance.py`
- 실행 로그: `logs/day04-guidance-run.log`
- 전체 전략 결과: `results/day04-nrc-guidance.csv`
- 핵심 전략 결과: `results/day04-key-guidance.csv`
- 전략별 요약: `results/day04-action-summary.csv`
- GitHub Commit: 커밋 후 입력

## 문제 및 시행착오

3일차까지는 NRC를 수집하고 분류했지만, 해당 결과가 다음 입력 생성 과정으로 연결되지 않았다.

이를 보완하기 위해 NRC별로 길이 보정, 파라미터 변형, 상태 변경, 재시도 등의 대응 규칙을 정의하고 자동으로 CSV를 생성하는 스크립트를 작성했다.

## 5. 다음 작업

생성된 전략 중 `REPAIR_LENGTH`, `MUTATE_PARAMETER`, `CHANGE_STATE`를 실제 입력 생성기에 연결하고 기존 무작위 방식과 결과를 비교한다.

## 오늘의 한 줄 결론

관측된 NRC를 기반으로 다음 입력 변형 방향을 선택하는 Guided Input 전략 생성 스크립트를 구현하고 핵심 규칙을 자동 검증했다.
