#!/usr/bin/env python3

import csv
from pathlib import Path

INPUT_CSV = Path("results/day03-nrc-classification.csv")
OUTPUT_CSV = Path("results/day04-nrc-guidance.csv")

GUIDANCE = {
    "0x11": (
        "CHANGE_SERVICE",
        "지원되지 않는 Service이므로 다른 SID를 선택한다.",
    ),
    "0x12": (
        "MUTATE_SUBFUNCTION",
        "현재 Service의 SubFunction 값을 변경한다.",
    ),
    "0x13": (
        "REPAIR_LENGTH",
        "메시지 길이와 형식을 우선 보정한다.",
    ),
    "0x21": (
        "RETRY_WITH_DELAY",
        "서버가 처리 중일 수 있으므로 지연 후 재시도한다.",
    ),
    "0x22": (
        "CHANGE_STATE",
        "현재 상태에서 조건이 충족되지 않아 세션 또는 선행 상태를 변경한다.",
    ),
    "0x24": (
        "BUILD_SEQUENCE",
        "요청 순서가 맞지 않아 선행 요청을 포함한 시퀀스를 구성한다.",
    ),
    "0x31": (
        "MUTATE_PARAMETER",
        "요청 데이터의 식별자 또는 파라미터 범위를 변경한다.",
    ),
    "0x33": (
        "CHANGE_SESSION_PATH",
        "Security Access가 거부되어 진단 세션과 선행 절차를 확인한다.",
    ),
    "0x35": (
        "MUTATE_SECURITY_INPUT",
        "현재 Security Access 입력을 변형하되 허가된 Mock 환경에서만 검증한다.",
    ),
    "0x36": (
        "RESET_SECURITY_SEQUENCE",
        "시도 횟수 초과 상태이므로 테스트 상태를 초기화한다.",
    ),
    "0x37": (
        "WAIT_AND_RETRY",
        "필요한 지연 시간이 지나지 않았으므로 대기 후 재시도한다.",
    ),
    "0x70": (
        "CHANGE_TRANSFER_PRECONDITION",
        "Upload 또는 Download 요청의 세션과 선행 조건을 변경한다.",
    ),
}

rows = []

with INPUT_CSV.open(newline="") as input_file:
    reader = csv.DictReader(input_file)

    for row in reader:
        nrc = row["nrc"]
        count = int(row["count"])
        classification = row["classification"]
        name = row["name"]

        if classification == "UNKNOWN":
            action = "LOG_AND_EXPLORE"
            reason = "구현체에 정의되지 않은 값이므로 별도 기록 후 재현 여부를 확인한다."
        else:
            action, reason = GUIDANCE.get(
                nrc,
                (
                    "KEEP_MUTATING",
                    "정의된 NRC이지만 별도 규칙이 없어 기존 변형을 계속한다.",
                ),
            )

        rows.append({
            "nrc": nrc,
            "count": count,
            "classification": classification,
            "name": name,
            "action": action,
            "reason": reason,
        })

rows.sort(key=lambda item: item["count"], reverse=True)

OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_CSV.open("w", newline="") as output_file:
    fieldnames = [
        "nrc",
        "count",
        "classification",
        "name",
        "action",
        "reason",
    ]

    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"input={INPUT_CSV}")
print(f"output={OUTPUT_CSV}")
print(f"observed_nrc_types={len(rows)}")
print(f"guided_types={sum(row['action'] != 'KEEP_MUTATING' for row in rows)}")
