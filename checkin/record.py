"""交互式录入一条记录。"""

from __future__ import annotations

from datetime import date

from . import storage


def _ask_int(prompt: str, low: int, high: int, default: int) -> int:
    while True:
        raw = input(f"{prompt} [{low}~{high}]（默认 {default}）：").strip()
        if raw == "":
            return default
        try:
            value = int(raw)
            if low <= value <= high:
                return value
        except ValueError:
            pass
        print(f"  请输入 {low} ~ {high} 的整数。")


def _ask_choice(prompt: str, options: list[str], default: str) -> str:
    while True:
        raw = input(f"{prompt}（{'/'.join(options)}，默认 {default}）：").strip()
        if raw == "":
            return default
        if raw in options:
            return raw
        print(f"  可选值：{options}")


def add_interactive() -> dict:
    today = date.today().isoformat()
    print("录入一条关系复盘记录（情绪 -2~2，投入/热度 0~3，压力 0~2）")
    event = {
        "date": input(f"日期（默认 {today}）：").strip() or today,
        "mood_self": _ask_int("你自己的情绪", -2, 2, 0),
        "mood_other": _ask_int(
            "对方情绪基调（2开心/1积极/0平静/-1低落/-2很差，主观观察）", -2, 2, 0
        ),
        "other_engagement": _ask_int(
            "对方回应热度（0冷淡简短/1偏少/2正常/3热情主动）", 0, 3, 2
        ),
        "other_stress": _ask_int(
            "对方压力状态（0放松/1有点累/2压力明显）", 0, 2, 0
        ),
        "interaction": _ask_choice(
            "互动类型", storage.INTERACTIONS, "chat"
        ),
        "initiative": _ask_choice(
            "谁主动", storage.INITIATIVES, "mutual"
        ),
        "effort_self": _ask_int("你的投入程度", 0, 3, 1),
        "note": input("备注（可空）：").strip(),
    }
    storage.append_event(event)
    print("已记录。")
    return event
