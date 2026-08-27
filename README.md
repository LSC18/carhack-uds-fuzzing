# CARHACK UDS Fuzzing Study

자동차 진단 프로토콜인 UDS와 Fuzzing을 학습하고, 최종적으로 NRC 피드백 기반 상태 인식형 UDS Fuzzing PoC를 구현하기 위한 개인 학습·실습 저장소다.

현재는 완성된 Fuzzing 도구를 개발한 단계가 아니다. `1 Day 1 Doc` 방식으로 공개 UDS 구현체를 분석하고, 기존 Fuzz Harness를 직접 실행·수정하면서 PoC에 필요한 기술을 단계적으로 확보하고 있다.

## 최종 목표

UDS Fuzzing 과정에서 발생하는 NRC(Negative Response Code)를 단순 실패 응답으로 처리하지 않고, 다음 입력을 결정하기 위한 피드백으로 활용하는 것이 목표다.

```text
UDS 입력 생성
→ 요청 전송
→ 응답 및 NRC 수집
→ NRC 의미와 ECU 상태 분석
→ 다음 입력 수정
→ 기존 Fuzzing 방식과 비교
```

9월 5일 PoC에서는 다음 내용을 보여주는 것을 목표로 한다.

- 공개·허가된 UDS 환경에서 Fuzzing 실행
- 기존 Fuzz Harness의 동작 과정 설명
- 직접 작성하거나 수정한 스크립트 실행
- 입력과 UDS 응답 로그 수집
- NRC 종류별 결과 분류
- NRC를 이용한 입력 변경 방식 제안 또는 최소 구현
- 다른 환경에서도 따라 할 수 있는 실행 방법 정리

## 진행 방법

매일 하나의 기술 질문과 하나의 결과물을 중심으로 학습한다.

각 차시는 다음 과정으로 진행한다.

```text
오늘 확인할 질문 선정
→ 개념 학습
→ 코드 분석 또는 실습
→ 성공·실패 결과 확인
→ 로그와 스크린샷 보존
→ Daily Doc 작성
→ Git Commit
```

단순히 기존 도구를 실행하는 데서 끝내지 않고, 실행 과정에서 확인한 문제를 코드와 스크립트 수정으로 연결하는 것을 기준으로 한다.

## 전체 학습 일정

| 단계 | 학습·실습 내용 | 결과물 |
|---|---|---|
| 1 | 공개 UDS 구현체 선정 및 구조 확인 | 대상과 버전 기록 |
| 2 | 기존 Fuzz Harness 입력 흐름 분석 | 코드 흐름 정리 |
| 3 | 빌드 환경 구성 및 기존 Harness 실행 | 성공·실패 로그 |
| 4 | 반복 실행용 스크립트 작성 | 재현 스크립트 |
| 5 | UDS 응답과 NRC 처리 코드 분석 | NRC 수집 위치 정리 |
| 6 | NRC Logger 또는 분류 로직 작성 | 직접 수정한 코드 |
| 7 | NRC 기반 입력 변경 규칙 구현 | Custom Harness |
| 8 | 기존 방식과 NRC 기반 방식 비교 | 비교 실험 결과 |
| 9 | 재현 검증 및 발표 정리 | PoC 실행 자료 |

일정은 실습 결과에 따라 변경될 수 있으며, 실패한 결과도 원인과 시도 내용을 기록해 다음 작업으로 연결한다.

## 현재까지 진행한 내용

현재 공개 UDS 구현체인 [`driftregion/iso14229`](https://github.com/driftregion/iso14229)을 첫 번째 학습 대상으로 사용하고 있다.

완료한 내용:

- 공개 UDS 구현체와 기존 Fuzz Harness 구조 확인
- Ubuntu ARM64 환경에서 빌드 환경 구성
- 기존 `fuzz_server` 빌드 및 기준선 실행 성공
- 빌드 과정에서 발생한 오류와 해결 과정 기록
- 반복 실행을 위한 `run-baseline.sh` 작성
- 실행 결과와 상세 로그 보존
- Daily Doc 작성

현재 결과는 NRC 기반 Fuzzing의 완성이 아니라, 이후 코드를 수정하고 비교 실험을 진행하기 위한 기준선이다.

## 다음 작업

다음 단계에서는 기존 Harness의 응답 수신 부분을 기준으로 다음 내용을 진행한다.

1. UDS Positive Response와 Negative Response 구분
2. `0x7F | Request SID | NRC` 구조 확인
3. NRC별 발생 횟수 기록
4. NRC와 입력값을 함께 저장하는 Logger 작성
5. NRC에 따라 다음 입력을 변경하는 규칙 설계
6. 기존 Fuzzing 결과와 비교

## 저장소 구성

```text
carhack-uds-fuzzing/
├── README.md
├── docs/
│   └── daily-docs/       # 1 Day 1 Doc 학습·실습 기록
├── logs/                 # 성공·실패 및 실행 로그
├── scripts/              # 반복 실행과 재현을 위한 스크립트
├── harness/              # 향후 Custom Harness 코드
└── results/              # 향후 비교 실험 결과
```

## 1 Day 1 Doc 작성 기준

각 Daily Doc에는 다음 내용을 남긴다.

- 오늘 확인할 기술 질문
- 작업 대상과 환경
- 사용한 도구와 명령
- 분석하거나 직접 수정한 코드
- 실제 입력과 출력
- 성공·실패 판단
- 오류와 해결 시도
- 로그·스크린샷·영상
- 다음 작업

문서는 `docs/daily-docs/`에 저장하고, 코드·로그와 함께 Git Commit으로 남긴다.

## 실험 범위

모든 실습은 공개·허가된 소프트웨어, Virtual ECU, Emulator 또는 격리된 테스트베드에서만 진행한다.

실제 차량이나 허가받지 않은 ECU는 실험 대상으로 사용하지 않는다.

## 참고

- [driftregion/iso14229](https://github.com/driftregion/iso14229)
- [LLVM LibFuzzer](https://llvm.org/docs/LibFuzzer.html)
- [Bazel Documentation](https://bazel.build/docs)
