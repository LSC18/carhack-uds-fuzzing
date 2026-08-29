#!/usr/bin/env python3

import csv
import re
from collections import Counter
from pathlib import Path

TARGET_HEADER = Path("/home/lsc18/carhack-targets/iso14229/src/uds.h")
INPUT_LOG = Path("logs/day02-nrc-detail.log")
OUTPUT_CSV = Path("results/day03-nrc-classification.csv")

definition_pattern = re.compile(
    r"UDS_NRC_([A-Za-z0-9_]+)\s*=\s*(0x[0-9A-Fa-f]+)"
)
log_pattern = re.compile(r"nrc=(0x[0-9A-Fa-f]{2})")

definitions = {}

for line in TARGET_HEADER.read_text(errors="replace").splitlines():
    match = definition_pattern.search(line)
    if match:
        name = match.group(1)
        value = int(match.group(2), 16)
        definitions[value] = name

counts = Counter()

for line in INPUT_LOG.read_text(errors="replace").splitlines():
    match = log_pattern.search(line)
    if match:
        counts[int(match.group(1), 16)] += 1

OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_CSV.open("w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["nrc", "count", "classification", "name"])

    for value, count in counts.most_common():
        if value in definitions:
            classification = "DEFINED"
            name = definitions[value]
        else:
            classification = "UNKNOWN"
            name = ""

        writer.writerow([
            f"0x{value:02X}",
            count,
            classification,
            name,
        ])

print(f"definitions={len(definitions)}")
print(f"observed_values={len(counts)}")
print(f"total_nrc={sum(counts.values())}")
print(f"output={OUTPUT_CSV}")
