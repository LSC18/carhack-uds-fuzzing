# [2026-08-27] UDS 응답 분석 및 NRC Logger 구현

## 1. 오늘 확인할 질문

기존 UDS Fuzz Harness에서 Negative Response를 식별하고 Request SID와 NRC 값을 기록할 수 있는가?

## 2. 진행 내용

- 작업 대상: `driftregion/iso14229`
- 대상 Commit: `77063d27`
- 사용 환경: Ubuntu 24.04.4 LTS ARM64, VMware Fusion
- 사용 도구: Git, Bazel 9.2.0, Clang 18, LLVM LibFuzzer, clang-format
- 분석 파일: `fuzz/fuzz_server.cc`

기존 Fuzz Harness에서 UDS 응답을 수신하는 `UDSTpRecv()` 호출 위치를 확인했다.

응답이 최소 3바이트이고 첫 번째 바이트가 `0x7F`인 경우 Request SID와 NRC를 출력하도록 코드를 추가했다.

```cpp
ssize_t ret =
    UDSTpRecv(mock_client, client_recv_buf, sizeof(client_recv_buf), NULL);

if (ret >= 3 && client_recv_buf[0] == 0x7F) {
    fprintf(stderr, "[NRC] request_sid=0x%02X nrc=0x%02X len=%zd\n",
            client_recv_buf[1], client_recv_buf[2], ret);
}
```

코드 작성 후 `git diff --check`와 `clang-format`을 이용해 공백과 들여쓰기를 정리했다.

이후 Clang 18과 Bazel을 이용해 수정된 Fuzz Harness를 빌드하고 테스트했다.

```bash
CC=/usr/bin/clang-18 \
CXX=/usr/bin/clang++-18 \
bazel build //fuzz:fuzz_server
```

```bash
CC=/usr/bin/clang-18 \
CXX=/usr/bin/clang++-18 \
bazel test //fuzz:fuzz_server \
  --test_output=all \
  --test_timeout=120 \
  --nocache_test_results
```

NRC 로그에서 NRC 값을 추출하고 종류별 발생 횟수를 집계했다.

```bash
grep -oE 'nrc=0x[0-9A-Fa-f]{2}' logs/day02-nrc-detail.log |
sort |
uniq -c |
sort -nr
```

## 3. 결과

- 수정된 Fuzz Harness 빌드 성공
- Fuzz Test 실행 성공
- 테스트 결과: `PASSED in 22.2s`
- NRC Logger 실제 출력 확인
- 총 NRC 출력: 48,988건
- Request SID, NRC, 응답 길이 기록 성공

주요 집계 결과:

| NRC | 발생 횟수 |
|---|---:|
| `0x10` | 35,815 |
| `0x13` | 6,337 |
| `0x31` | 2,309 |
| `0x70` | 1,623 |
| `0x12` | 828 |

### 입력

LibFuzzer와 기존 Corpus가 생성한 변형 UDS 요청을 사용했다.

### 출력 예시

```text
[NRC] request_sid=0x34 nrc=0x11 len=3
[NRC] request_sid=0x85 nrc=0x10 len=3
[NRC] request_sid=0x34 nrc=0x31 len=3
[NRC] request_sid=0x2E nrc=0x13 len=3
```

### 판단

기존 Harness의 응답 수신 위치에 NRC Logger를 추가하고 실제 출력을 확인했다.

다만 현재 Mock Server에서는 Fuzz 입력에 의해 임의의 오류값이 생성될 수 있으므로, 수집된 모든 값을 실제 ECU의 유효 NRC라고 판단할 수는 없다. 다음 작업에서 표준 NRC와 비표준 값을 구분할 필요가 있다.

## 4. 증거

- 수정 코드: `harness/fuzz_server_nrc_logger.cc`
- 코드 Patch: `harness/day02-nrc-logger.patch`
- 빌드 로그: `logs/day02-nrc-build.log`
- 실행 로그: `logs/day02-nrc-run.log`
- 상세 NRC 로그: `logs/day02-nrc-detail.log`
- NRC 집계: `results/day02-nrc-counts.txt`
- GitHub 저장소: `https://github.com/LSC18/carhack-uds-fuzzing`
- GitHub Commit: 작업 완료 후 추가
- 스크린샷:
  - 대상 Commit 및 코드 상태
  - 기존 응답 처리 흐름
  - NRC Logger 코드와 Git Diff
  - 빌드 성공 결과
  - NRC 실제 출력
  - NRC별 발생 횟수

## 문제 및 시행착오

- 발생한 문제: Nano로 코드를 입력한 후 공백과 탭이 혼합됨
- 확인 방법: `git diff --check`
- 해결 방법: `clang-format-18`로 변경 구간의 형식 정리
- 결과: 공백 경고 제거 후 빌드 성공

`clang-format`은 C/C++의 문법이나 로직을 수정하는 도구가 아니라 들여쓰기, 공백, 탭, 줄바꿈 등의 코드 형식을 통일하는 도구임을 확인했다.

## 5. 다음 작업

수집된 NRC 중 표준 NRC와 비표준 값을 구분하고, NRC별 의미에 따라 입력을 분류하는 최소 로직을 작성한다.

## 오늘의 한 줄 결론

기존 UDS Fuzz Harness에 NRC Logger를 직접 추가하고, 48,988건의 Negative Response를 수집하여 NRC별 발생 횟수를 확인했다.
