"""数据读写与字段校验。

事件以 CSV 存储，字段含义：
- date            : 记录日期 YYYY-MM-DD
- mood_self       : 自己当天情绪，-2(很差) ~ 2(很好)
- mood_other      : 观察到的对方情绪基调，-2 ~ 2（主观观察，不代表对方真实心理）
- other_engagement : 观察到的对方回应热度，0(冷淡简短) ~ 3(热情主动)
- other_stress    : 观察到的对方压力状态，0(无) ~ 2(明显)
- interaction     : 当天互动类型
- initiative      : 当天谁主动
- effort_self     : 自己在这段互动里的投入程度 0 ~ 3
- note            : 备注（自由文本）
"""

from __future__ import annotations

import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "events.csv"

INTERACTIONS = ["chat", "companion", "conflict", "apology", "space", "none"]
INITIATIVES = ["self", "other", "mutual", "none"]

FIELDNAMES = [
    "date",
    "mood_self",
    "mood_other",
    "other_engagement",
    "other_stress",
    "interaction",
    "initiative",
    "effort_self",
    "note",
]


def _ensure_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def load_events() -> list[dict]:
    """读取全部事件；空表返回空列表。"""
    _ensure_file()
    with CSV_PATH.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key in ("mood_self", "mood_other", "other_engagement", "other_stress", "effort_self"):
            row[key] = int(row[key]) if row[key] != "" else 0
    return rows


def append_event(event: dict) -> None:
    """追加一条事件，并做基础校验。"""
    _validate(event)
    _ensure_file()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow({k: event.get(k, "") for k in FIELDNAMES})


def _validate(event: dict) -> None:
    if not event.get("date"):
        raise ValueError("date 不能为空")
    for key in ("mood_self", "mood_other"):
        value = int(event[key])
        if not -2 <= value <= 2:
            raise ValueError(f"{key} 需在 -2 ~ 2 之间，收到 {value}")
    engagement = int(event["other_engagement"])
    if not 0 <= engagement <= 3:
        raise ValueError(f"other_engagement 需在 0 ~ 3 之间，收到 {engagement}")
    stress = int(event["other_stress"])
    if not 0 <= stress <= 2:
        raise ValueError(f"other_stress 需在 0 ~ 2 之间，收到 {stress}")
    effort = int(event["effort_self"])
    if not 0 <= effort <= 3:
        raise ValueError(f"effort_self 需在 0 ~ 3 之间，收到 {effort}")
    if event["interaction"] not in INTERACTIONS:
        raise ValueError(f"interaction 须为 {INTERACTIONS} 之一")
    if event["initiative"] not in INITIATIVES:
        raise ValueError(f"initiative 须为 {INITIATIVES} 之一")
