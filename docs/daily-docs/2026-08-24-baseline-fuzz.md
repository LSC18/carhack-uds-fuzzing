# [2026-08-24] 기존 UDS Fuzz Harness 빌드 및 기준선 실행 - 이승찬

- 담당자: 이승찬
- 작업 구분: PoC 개발
- 상태: 완료
- 소요 시간: 실제 작업시간 입력 필요
- 대상: `driftregion/iso14229`
- 대상 Commit: `77063d27b0990fb7bd22aed06657e7f49dd96ea8`
- 환경: Ubuntu 24.04.4 LTS ARM64
- 빌드 도구: Bazel 9.2.0
- 컴파일러: GCC 13.3.0, Clang 18

## 1. 오늘 확인할 질문

`iso14229`의 기존 UDS Fuzz Harness를 Ubuntu ARM64 환경에서 빌드하고, 기존 Corpus를 이용해 동일한 테스트 결과를 재현할 수 있는가?

## 2. 진행 내용

- 작업 대상: `driftregion/iso14229`
- 사용 환경: VMware Fusion, Ubuntu 24.04.4 LTS ARM64
- 사용 도구:
  - Git 2.43.0
  - GCC/G++ 13.3.0
  - Clang 18
  - Bazelisk
  - Bazel 9.2.0
  - LLVM LibFuzzer
- 실행·분석한 내용:
  - 공개 UDS 구현체 저장소 확보 및 버전 고정
  - 기존 `fuzz/fuzz_server.cc` 구조 분석
  - LibFuzzer 입력이 Mock ISO-TP를 통해 UDS Server로 전달되는 경로 확인
  - Bazel 기반 기존 Fuzz Target 빌드
  - 저장소에 포함된 기존 Corpus 재생
  - 캐시를 사용하지 않는 재현 스크립트 작성 및 실행
  - 빌드·실행·실패 로그와 SHA-256 기록

### 기존 Harness 처리 흐름

```text
LLVMFuzzerTestOneInput(data, size)
→ FuzzedDataProvider로 입력 분리
→ UDS Server와 Mock Client 생성
→ 변형된 주소·메시지·시간 정보 생성
→ UDSTpSend()로 요청 전송
→ UDSServerPoll()로 요청 처리
→ UDSTpRecv()로 응답 수신
```

### 주요 코드 위치

- `fuzz/fuzz_server.cc:118`: Fuzzer 진입점
- `fuzz/fuzz_server.cc:119`: 입력 데이터 분할
- `fuzz/fuzz_server.cc:134`: UDS Server 초기화
- `fuzz/fuzz_server.cc:137~138`: Mock ISO-TP Server/Client 생성
- `fuzz/fuzz_server.cc:149~150`: 변형 메시지 생성
- `fuzz/fuzz_server.cc:161`: 요청 전송
- `fuzz/fuzz_server.cc:170`: 서버 요청 처리
- `fuzz/fuzz_server.cc:171`: 응답 수신

### 실행 명령 또는 입력값

대상 버전 및 파일 Hash 기록:

```bash
cd /home/lsc18/carhack-targets/iso14229

git rev-parse HEAD
git remote -v
sha256sum iso14229.c iso14229.h
```

Bazel 및 컴파일 환경 준비:

```bash
sudo apt install -y g++

sudo apt install -y \
  clang-18 \
  libclang-rt-18-dev \
  libfuzzer-18-dev
```

Fuzz Target 빌드:

```bash
CC=/usr/bin/clang-18 \
CXX=/usr/bin/clang++-18 \
bazel build //fuzz:fuzz_server \
  2>&1 | tee baseline-fuzz-build.log
```

기존 Corpus 테스트:

```bash
CC=/usr/bin/clang-18 \
CXX=/usr/bin/clang++-18 \
bazel test //fuzz:fuzz_server \
  --test_output=all \
  --test_timeout=120 \
  --nocache_test_results \
  2>&1 | tee baseline-fuzz-run.log
```

직접 작성한 재현 스크립트:

```text
/home/lsc18/carhack-uds-fuzzing/scripts/run-baseline.sh
```

스크립트 실행:

```bash
cd /home/lsc18/carhack-uds-fuzzing

bash -n scripts/run-baseline.sh
./scripts/run-baseline.sh
```

## 3. 결과

- 실제로 확인된 결과:
  - Bazel 9.2.0 ARM64 실행 환경을 구성했다.
  - `//fuzz:fuzz_server` Target 빌드에 성공했다.
  - 기존 Corpus 입력이 순차적으로 재생되는 것을 확인했다.
  - 각 Corpus 입력이 `OK`로 처리되는 것을 확인했다.
  - 캐시를 비활성화한 상태에서 테스트를 다시 실행했다.
  - 1개 테스트가 약 16.8초 만에 통과했다.
  - 해당 기준선 실행에서는 테스트를 중단시키는 Crash 또는 Timeout이 관찰되지 않았다.
  - 상세 출력은 약 3.9MB의 로그로 저장했다.

- 성공·실패 판단: 성공
- 새롭게 알게 된 내용:
  - 기존 Harness는 실제 CAN 장치 대신 Mock ISO-TP를 사용한다.
  - `FuzzedDataProvider`는 하나의 Fuzzer 입력을 메시지, 주소, 시간 등의 값으로 분리한다.
  - 기존 Harness는 Crash 탐색 및 안정성 검사에는 사용할 수 있다.
  - NRC를 분류하고 다음 입력을 수정하는 상태 인식 로직은 기존 Harness에서 확인되지 않았다.
  - Bazel은 테스트 결과를 캐시하므로 재현 검증에는 `--nocache_test_results`가 필요하다.
- 예상과 달랐던 점:
  - GCC 설치만으로는 C++ Harness를 빌드할 수 없었다.
  - `FuzzedDataProvider.h`가 별도의 LLVM 개발 패키지에 포함되어 있었다.
  - 상세 stdout이 Bazel의 화면 출력 제한인 1MB를 초과했다.

### 입력

```text
iso14229 저장소에 포함된 기존 Fuzz Corpus
```

### 출력

```text
//fuzz:fuzz_server PASSED in 16.8s
Executed 1 out of 1 test: 1 test passes
```

### 판단

```text
Ubuntu 24.04.4 ARM64 환경에서 기존 UDS Fuzz Harness의 빌드와
Corpus 재생을 재현했다. Custom NRC 로직 구현 전 비교 기준선으로 사용할 수 있다.
```

## 4. 증거

- 코드 경로:
  - `/home/lsc18/carhack-uds-fuzzing/scripts/run-baseline.sh`
  - `/home/lsc18/carhack-targets/iso14229/fuzz/fuzz_server.cc`
- GitHub Commit: 로컬 Commit 후 입력
- 실행 로그:
  - `logs/target-version.log`
  - `logs/bazel-version.log`
  - `logs/baseline-fuzz-build.log`
  - `logs/baseline-fuzz-run.log`
  - `logs/baseline-fuzz-detail.log`
  - `logs/baseline-fuzz-detail-hash.log`
  - `logs/baseline-fuzz-build-failed-missing-gpp.log`
  - `logs/baseline-fuzz-build-failed-missing-fuzzer-header.log`
- 스크린샷:
  - Bazel 9.2.0 설치 결과
  - `cc1plus` 오류 화면
  - `FuzzedDataProvider.h` 오류 화면
  - 원본 Fuzz Target 빌드 성공 화면
  - 캐시 없는 Corpus 테스트 통과 화면
- 실행 영상: 미촬영
- 참고 자료:
  - https://github.com/driftregion/iso14229
  - https://driftregion.github.io/iso14229/
  - https://bazel.build/install/bazelisk
  - https://llvm.org/docs/LibFuzzer.html

## 문제 및 시행착오

### 발생한 오류 1

```text
gcc: fatal error: cannot execute 'cc1plus': execvp: No such file or directory
```

- 확인한 원인: GCC는 설치되어 있었지만 C++ 컴파일러인 `g++`가 설치되지 않았다.
- 시도한 해결 방법: Ubuntu 패키지 관리자를 통해 `g++`를 설치했다.
- 각 시도의 결과: C++ 컴파일 단계까지 진행됐다.

### 발생한 오류 2

```text
fatal error: fuzzer/FuzzedDataProvider.h: No such file or directory
```

- 확인한 원인: LLVM LibFuzzer 개발 헤더가 설치되지 않았다.
- 시도한 해결 방법:
  - `clang-18` 설치
  - `libclang-rt-18-dev` 설치
  - `libfuzzer-18-dev` 설치
  - Bazel 빌드 시 Clang 18 명시
- 각 시도의 결과: `//fuzz:fuzz_server` Target 빌드에 성공했다.

### 발생한 문제 3

```text
Executed 0 out of 1 test: 1 test passes
```

- 확인한 원인: Bazel이 이전 테스트 결과를 캐시하여 실제 Corpus 테스트를 다시 실행하지 않았다.
- 시도한 해결 방법: 재현 스크립트에 `--nocache_test_results` 옵션을 추가했다.
- 각 시도의 결과:

```text
Executed 1 out of 1 test: 1 test passes
```

- 아직 해결되지 않은 부분: 없음

## 5. 다음 작업

- `UDSTpRecv()`로 수신한 UDS 응답에서 `0x7F, 요청 SID, NRC`를 추출하고 종류별 발생 횟수를 저장하는 NRC Logger를 설계한다.

## 오늘의 한 줄 결론

공개 UDS 구현체의 기존 Fuzz Harness를 Ubuntu ARM64 환경에서 빌드하고, 직접 작성한 스크립트로 기존 Corpus 테스트를 캐시 없이 재현했다.
