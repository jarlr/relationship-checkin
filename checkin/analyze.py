"""统计指标、健康度评分与中性沟通建议。

所有指标只描述记录本身，用于自我复盘；mood_other 是主观观察值，
不用于推断对方真实想法，更不生成针对对方的策略。
"""

from __future__ import annotations

from collections import Counter
from statistics import mean, stdev

from . import storage


def summarize(events: list[dict]) -> dict:
    if not events:
        return {"total": 0}

    mood_self = [e["mood_self"] for e in events]
    mood_other = [e["mood_other"] for e in events]
    engagement = [e["other_engagement"] for e in events]
    stress = [e["other_stress"] for e in events]
    interactions = Counter(e["interaction"] for e in events)
    initiatives = Counter(e["initiative"] for e in events)
    efforts = [e["effort_self"] for e in events]

    active = [e for e in events if e["initiative"] in ("self", "other", "mutual")]
    self_share = 0.0
    if active:
        self_share = initiatives["self"] / len(active)

    summary = {
        "total": len(events),
        "mood_self_mean": mean(mood_self),
        "mood_other_mean": mean(mood_other),
        "other_engagement_mean": mean(engagement),
        "other_stress_mean": mean(stress),
        "mood_self_std": stdev(mood_self) if len(mood_self) > 1 else 0.0,
        "interaction_counts": dict(interactions),
        "initiative_counts": dict(initiatives),
        "effort_self_mean": mean(efforts),
        "self_initiative_share": self_share,
        "conflict_ratio": interactions["conflict"] / len(events),
    }
    summary["health_score"] = _score(summary)
    summary["suggestions"] = _suggest(events, summary)
    return summary


def _score(s: dict) -> int:
    """透明可解释的健康度评分，0 ~ 100。"""
    score = 60

    mood_avg = (s["mood_self_mean"] + s["mood_other_mean"]) / 2
    score += max(-15, min(20, mood_avg * 10))

    score -= s["conflict_ratio"] * 30

    # 主动越失衡扣分越多：理想是 self / other 接近对半
    imbalance = abs(s["self_initiative_share"] - 0.5)
    score -= imbalance * 20

    score -= s["mood_self_std"] * 5
    score -= s["other_stress_mean"] * 4

    return int(max(0, min(100, round(score))))


def _suggest(events: list[dict], s: dict) -> list[str]:
    tips: list[str] = []

    if s["self_initiative_share"] >= 0.7:
        tips.append("最近多由你主动推进互动，可以适当留白，给对方表达和回应的空间。")
    elif s["self_initiative_share"] <= 0.3 and s["initiative_counts"].get("other", 0):
        tips.append("对方主动较多，记得回应和反馈，别把对方的付出当成理所当然。")

    if s["conflict_ratio"] >= 0.25:
        tips.append("近期摩擦偏多，先把情绪平复下来再沟通，避免翻旧账或逼对方当场给结论。")

    if s["mood_self_mean"] <= -0.5:
        tips.append("你自己的情绪持续偏低，先照顾好状态；状态差时少做关系里的重大决定。")

    if s["mood_self_std"] >= 1.2:
        tips.append("情绪起伏较大，减少试探和猜测，直接、平和地说出自己的感受会更稳。")

    if s["other_stress_mean"] >= 1.3:
        tips.append("观察到对方压力偏明显，先少追问、少施压，留意照顾对方状态。")

    if s["other_engagement_mean"] <= 1.0:
        tips.append("近期对方回应偏少，先反思沟通节奏，避免连续发消息逼对方给回应。")

    last = events[-1]
    if last["interaction"] == "none":
        tips.append("最近一段缺少互动，可以找个轻松的由头聊一聊，而不是追问态度。")

    if not tips:
        tips.append("记录平稳，继续保持坦诚沟通，遇到分歧及时说开。")
    return tips


def print_summary(summary: dict) -> None:
    if summary["total"] == 0:
        print("还没有记录。先运行 `python main.py add` 写一条。")
        return

    print("=" * 42)
    print(f"记录条数：{summary['total']}")
    print(f"自己情绪均值：{summary['mood_self_mean']:.2f}  "
          f"观察到的对方情绪均值：{summary['mood_other_mean']:.2f}")
    print(f"对方回应热度均值：{summary['other_engagement_mean']:.2f} / 3  "
          f"对方压力状态均值：{summary['other_stress_mean']:.2f} / 2")
    print(f"自己投入程度均值：{summary['effort_self_mean']:.2f} / 3")
    print(f"你主动的占比：{summary['self_initiative_share'] * 100:.0f}%")
    print(f"冲突占比：{summary['conflict_ratio'] * 100:.0f}%")
    print(f"健康度自评：{summary['health_score']} / 100")
    print("-" * 42)
    print("复盘提醒：")
    for tip in summary["suggestions"]:
        print(f"  · {tip}")
    print("=" * 42)
