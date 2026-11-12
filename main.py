"""命令行入口。

用法：
    python main.py add      # 交互式录入一条记录
    python main.py report   # 输出复盘摘要并生成趋势图
    python main.py seed     # 写入示例数据（仅用于演示）
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta

from checkin import analyze, record, report, storage


def _seed() -> None:
    base = date.today() - timedelta(days=6)
    samples = [
        (0, 1, 2, 0, "chat", "mutual", 1, "晚上聊了会儿日常"),
        (1, 1, 3, 0, "companion", "self", 2, "一起吃饭散步"),
        (0, -1, 1, 1, "conflict", "mutual", 1, "因为小事拌嘴，没说开"),
        (-1, 0, 0, 1, "space", "none", 0, "各自冷静一天"),
        (0, 1, 2, 0, "apology", "self", 1, "主动沟通，缓和下来"),
        (1, 1, 2, 0, "chat", "mutual", 1, "轻松聊天"),
    ]
    for i, (ms, mo, eng, stress, inter, init, effort, note) in enumerate(samples):
        storage.append_event(
            {
                "date": (base + timedelta(days=i)).isoformat(),
                "mood_self": ms,
                "mood_other": mo,
                "other_engagement": eng,
                "other_stress": stress,
                "interaction": inter,
                "initiative": init,
                "effort_self": effort,
                "note": note,
            }
        )
    print("示例数据已写入。")


def main() -> None:
    parser = argparse.ArgumentParser(description="关系健康度自我复盘工具")
    parser.add_argument("command", choices=["add", "report", "seed"])
    args = parser.parse_args()

    if args.command == "add":
        record.add_interactive()
    elif args.command == "report":
        events = storage.load_events()
        summary = analyze.summarize(events)
        analyze.print_summary(summary)
        path = report.render(events)
        if path:
            print(f"趋势图已生成：{path}")
    elif args.command == "seed":
        _seed()


if __name__ == "__main__":
    main()
