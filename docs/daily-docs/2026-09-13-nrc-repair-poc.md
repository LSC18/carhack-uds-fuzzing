# [2026-09-13] NRC 0x13 피드백 기반 UDS 요청 자동 수정 최소 PoC - 이승찬

- 작업 구분: 개인 연구 / PoC 개발 / UDS 상태 인식형 퍼징
- 상태: 최소 PoC 완료
- 담당: 이승찬
- 실행 환경: macOS 로컬 Python 3, 외부 패키지 없음

## 1. 오늘 확인할 질문

UDS 서버가 반환한 NRC `0x13 Incorrect Message Length Or Invalid Format`을 자동으로 파싱하고, 실패한 요청의 길이를 수정해 재전송한 뒤 Positive Response까지 도달할 수 있는가?

## 2. 배경

이전 작업에서는 Cyclone DDS RTPS 하네스의 빌드, Corpus 실행과 Dictionary A/B 비교를 통해 퍼징 환경과 실험 기록 방법을 확인했다. 그러나 이는 공식 하네스 재현에 가까우며, 개인 연구 아이디어인 NRC 피드백 기반 UDS 요청 수정은 실제 코드로 구현되지 않은 상태였다.

오늘은 장시간 퍼징을 잠시 중단하고 개인 연구 아이디어의 최소 동작 단위를 구현했다.

```text
잘못된 UDS 요청
→ Negative Response 수신
→ NRC 의미 분석
→ Repair Rule 선택
→ 요청 자동 수정
→ 재전송
→ Positive Response 확인
```

## 3. PoC 범위

### 대상 서비스

- SID: `0x10 Diagnostic Session Control`
- 정상 요청 길이: 2바이트
- 기본 Session Sub-function: `0x01 Default Session`

### 입력과 기대 결과

| 단계 | 값 | 의미 |
|---|---|---|
| 최초 요청 | `10` | Sub-function이 빠진 잘못된 요청 |
| Negative Response | `7F 10 13` | SID 0x10 요청의 길이·형식 오류 |
| 자동 수정 | `10 → 10 01` | 기본 Session Sub-function 추가 |
| 재전송 응답 | `50 01` | Diagnostic Session Control Positive Response |

## 4. 구현 구조

```text
run_poc.py
  ├─ VirtualEcu
  │    └─ SID·길이·Sub-function 검증 및 UDS 응답 생성
  ├─ parse_response
  │    └─ Positive Response와 7F Negative Response 분류
  ├─ RepairEngine
  │    └─ NRC 0x13에 따라 요청 길이 보정
  ├─ NrcGuidedRunner
  │    └─ TX → RX → NRC → Repair → 재전송 루프
  └─ JsonlTrace
       └─ 전체 과정을 JSONL로 기록
```

### 구현 파일

- `ecu/virtual_ecu.py`: 격리된 최소 UDS Virtual ECU
- `fuzzer/nrc_guided.py`: NRC Parser, Repair Engine, 피드백 실행기
- `run_poc.py`: 한 번에 실행하는 PoC 진입점
- `tests/test_poc.py`: 단위·통합 테스트 5개
- `logs/sample/poc_trace.jsonl`: 실제 성공 실행의 비식별 샘플 로그

## 5. 실행 방법

```bash
cd carhack-uds-fuzzing
python3 run_poc.py
```

별도 Python 패키지는 필요하지 않다.

자동 테스트는 다음 명령으로 실행한다.

```bash
python3 -m unittest discover -s tests -v
```

## 6. 실제 실행 결과

```text
[TX] 10
[RX] 7F 10 13
[NRC] 0x13 Incorrect Message Length Or Invalid Format
[REPAIR] 10 -> 10 01
[TX] 10 01
[RX] 50 01
[RESULT] NRC-guided repair succeeded
[LOG] logs/poc_trace.jsonl
```

### 자동 테스트

```text
test_full_feedback_loop_succeeds_and_logs ... ok
test_parser_extracts_nrc ... ok
test_repair_engine_adds_default_subfunction ... ok
test_short_session_request_returns_nrc_13 ... ok
test_valid_default_session_request_is_positive ... ok

Ran 5 tests in 0.005s
OK
```

## 7. 성공·실패 판단

**최소 PoC 성공.** 다음 항목을 실제 실행으로 확인했다.

1. 잘못된 `10` 요청 생성
2. Virtual ECU의 `7F 10 13` 응답
3. Parser의 NRC `0x13` 분류
4. Repair Engine의 `10 01` 자동 생성
5. 수정 요청 재전송
6. `50 01` Positive Response 도달
7. 수정 전후 입력과 응답 JSONL 저장
8. 자동 테스트 5개 통과

## 8. 증거

### 저장소

- 저장소: `LSC18/carhack-uds-fuzzing`
- Git branch: `codex/nrc-repair-poc`
- Git commit: 본 문서와 PoC 코드를 함께 기록

### 실제 로그

- 로컬 실행 로그: `logs/poc_trace.jsonl`
- 공유용 샘플: `logs/sample/poc_trace.jsonl`

### 재현 명령

```bash
python3 run_poc.py
python3 -m unittest discover -s tests -v
```

## 9. 현재 한계

- 현재 PoC는 NRC 기반 피드백 루프 자체를 검증하는 transport-independent 구현이다.
- Virtual ECU는 SID `0x10`과 NRC `0x11`, `0x12`, `0x13`만 지원한다.
- 현재 전송은 프로세스 내부 함수 호출이며 실제 SocketCAN, vCAN 또는 ISO-TP를 사용하지 않는다.
- ECU 상태는 Diagnostic Session만 최소 모델링하며 Security Level과 요청 Sequence Scheduling은 포함하지 않는다.
- 비교군 Random·Grammar·Stateful Fuzzer와 정량 실험은 아직 구현하지 않았다.
- 실제 차량, 외부 ECU 및 공용 네트워크에는 접근하지 않았다.

## 10. PoC 준비도

| 항목 | 상태 | 근거 |
|---|---|---|
| 실행 가능한 코드 | 완료 | `python3 run_poc.py` |
| 정확한 입력 | 완료 | `10` |
| Negative Response | 완료 | `7F 10 13` |
| NRC Parser | 완료 | NRC 0x13 분류 |
| Repair Rule | 완료 | `10 → 10 01` |
| Positive Response | 완료 | `50 01` |
| 실행 로그 | 완료 | JSONL Trace |
| 자동 테스트 | 완료 | 5개 통과 |
| README 재현 절차 | 완료 | 실행·예상 출력·한계 기록 |
| vCAN/ISO-TP 연결 | 확인 필요 | 다음 구현 단계 |
| 실제 Virtual ECU 프로세스 연동 | 확인 필요 | Transport Adapter 필요 |

## 11. 다음 작업

현재 Parser와 Repair Engine은 유지하고 전송 계층을 분리해 Linux `vcan`과 ISO-TP 기반 Virtual ECU에 연결한다.

우선순위:

1. `Transport` 인터페이스 분리
2. 현재 함수 호출 방식을 `InMemoryTransport`로 이동
3. Linux용 SocketCAN/ISO-TP Adapter 추가
4. 실제 Virtual ECU 요청 `10 → 7F 10 13` 확보
5. 자동 수정된 `10 01 → 50 01` 확인
6. NRC `0x12` 또는 `0x31` Repair Rule 추가

완료 조건은 동일한 `run_poc.py` 피드백 루프가 in-memory ECU와 vCAN/ISO-TP ECU에서 모두 작동하고, 각 실행의 요청·응답 로그를 남기는 것이다.

## 오늘의 한 줄 결론

UDS NRC `0x13`을 자동으로 파싱해 잘못된 Diagnostic Session Control 요청 `10`을 `10 01`로 수정하고 재전송하여 Positive Response `50 01`까지 도달하는 개인 연구용 최소 PoC를 구현했다.
