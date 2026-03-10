"""
Midnight Bestiary — evaluate.py

게임의 "재미"를 정량적으로 측정하는 프레임워크.
에이전트는 이 지표들을 기반으로 game.py를 진화시킨다.
지표 자체도 에이전트가 추가/수정할 수 있다.
"""

import math
import statistics
from game import play, greedy_strategy, tank_strategy


def run_evaluation(n_games: int = 2000) -> dict:
    """n_games 판을 돌려서 지표를 수집한다."""
    random_results = [play() for _ in range(n_games)]
    greedy_results = [play(strategy=greedy_strategy) for _ in range(n_games)]
    tank_results = [play(strategy=tank_strategy) for _ in range(n_games)]

    # 1. 승률
    win_rate = sum(1 for r in random_results if r.won) / n_games
    greedy_wr = sum(1 for r in greedy_results if r.won) / n_games
    tank_wr = sum(1 for r in tank_results if r.won) / n_games

    # 2. 의사결정 의미성: 최선 전략 vs 랜덤의 차이
    best_strategy_wr = max(greedy_wr, tank_wr)
    decision_impact = best_strategy_wr - win_rate

    # 3. 다양성: 클리어한 라운드 수의 분포 엔트로피
    round_counts = {}
    for r in random_results:
        k = r.rounds_cleared
        round_counts[k] = round_counts.get(k, 0) + 1
    total = sum(round_counts.values())
    probs = [c / total for c in round_counts.values()]
    diversity = -sum(p * math.log2(p) for p in probs if p > 0)

    # 4. 긴장감: 배틀에서 우세 변화(lead_changes)가 있는 비율
    all_battles = [b for r in random_results for b in r.battles]
    if all_battles:
        tense_battles = sum(1 for b in all_battles if b.lead_changes > 0)
        tension = tense_battles / len(all_battles)
        avg_lead_changes = statistics.mean(b.lead_changes for b in all_battles)
    else:
        tension = 0.0
        avg_lead_changes = 0.0

    # 5. 진행감: 후반 라운드에 도달하는 비율 (라운드별 생존율)
    if random_results:
        total_rounds = random_results[0].total_rounds
        survival_by_round = []
        for r_num in range(1, total_rounds + 1):
            survived = sum(1 for r in random_results if r.rounds_cleared >= r_num)
            survival_by_round.append(survived / n_games)
        # 진행감 = 라운드 간 생존율 감소의 일관성 (단조감소면 좋음)
        if len(survival_by_round) > 1:
            diffs = [survival_by_round[i] - survival_by_round[i + 1]
                     for i in range(len(survival_by_round) - 1)]
            progression = statistics.mean(diffs) if diffs else 0.0
        else:
            progression = 0.0
    else:
        survival_by_round = []
        progression = 0.0

    metrics = {
        'n_games': n_games,
        'win_rate_random': round(win_rate, 4),
        'win_rate_greedy': round(greedy_wr, 4),
        'win_rate_tank': round(tank_wr, 4),
        'decision_impact': round(decision_impact, 4),
        'diversity_entropy': round(diversity, 4),
        'tension_ratio': round(tension, 4),
        'avg_lead_changes': round(avg_lead_changes, 4),
        'progression_gradient': round(progression, 4),
        'survival_curve': [round(s, 3) for s in survival_by_round],
    }
    return metrics


def print_report(metrics: dict):
    print("=" * 55)
    print("  EVALUATION REPORT")
    print("=" * 55)
    for k, v in metrics.items():
        if k == 'survival_curve':
            print(f"  {k:25s}: {v}")
        else:
            print(f"  {k:25s}: {v}")
    print("=" * 55)

    issues = []
    wr = metrics['win_rate_random']
    if wr > 0.7:
        issues.append(f"승률 {wr:.0%} — 너무 쉬움")
    if wr < 0.15:
        issues.append(f"승률 {wr:.0%} — 너무 어려움")
    if metrics['decision_impact'] < 0.03:
        issues.append(f"의사결정 영향 {metrics['decision_impact']:.1%} — 전략이 무의미")
    if metrics['tension_ratio'] < 0.1:
        issues.append(f"긴장감 {metrics['tension_ratio']:.1%} — 일방적 전투")
    if metrics['progression_gradient'] < 0.01:
        issues.append(f"진행감 {metrics['progression_gradient']:.3f} — 성장 곡선 없음")

    if issues:
        print("\n  개선 필요:")
        for issue in issues:
            print(f"    ! {issue}")
    else:
        print("\n  현재 상태 양호.")


if __name__ == '__main__':
    metrics = run_evaluation(3000)
    print_report(metrics)
