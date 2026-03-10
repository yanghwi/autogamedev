"""
Midnight Bestiary — evaluate.py

게임의 "재미"를 정량적으로 측정하는 프레임워크.
에이전트는 이 지표들을 기반으로 game.py를 진화시킨다.
지표 자체도 에이전트가 추가/수정할 수 있다.
"""

import math
import statistics
from game import play, greedy_strategy, tank_strategy, synergy_strategy, hybrid_strategy


def run_evaluation(n_games: int = 2000) -> dict:
    """n_games 판을 돌려서 지표를 수집한다."""
    random_results = [play() for _ in range(n_games)]
    greedy_results = [play(strategy=greedy_strategy) for _ in range(n_games)]
    tank_results = [play(strategy=tank_strategy) for _ in range(n_games)]
    synergy_results = [play(strategy=synergy_strategy) for _ in range(n_games)]
    hybrid_results = [play(strategy=hybrid_strategy) for _ in range(n_games)]

    # 1. 승률
    win_rate = sum(1 for r in random_results if r.won) / n_games
    greedy_wr = sum(1 for r in greedy_results if r.won) / n_games
    tank_wr = sum(1 for r in tank_results if r.won) / n_games
    synergy_wr = sum(1 for r in synergy_results if r.won) / n_games
    hybrid_wr = sum(1 for r in hybrid_results if r.won) / n_games

    # 2. 의사결정 의미성: 최선 전략 vs 랜덤의 차이
    best_strategy_wr = max(greedy_wr, tank_wr, synergy_wr, hybrid_wr)
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
        # 박빙 비율: 승자 HP < 30%인 전투 비율 (추가 긴장감 지표)
        close_finishes = sum(1 for b in all_battles
                           if (b.winner == 'a' and b.a_hp_remaining < 0.3)
                           or (b.winner == 'b' and b.b_hp_remaining < 0.3))
        close_finish_rate = close_finishes / len(all_battles)
    else:
        tension = 0.0
        avg_lead_changes = 0.0
        close_finish_rate = 0.0

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

    # 6. 역전 드라마: 중반(R5)까지 1패 이상이었지만 최종 승리한 비율
    if random_results:
        comebacks = 0
        eligible = 0
        for r in random_results:
            # R5까지의 전투 결과 확인
            losses_by_r5 = sum(1 for b in r.battles[:5] if b.winner == 'b')
            if losses_by_r5 >= 1:
                eligible += 1
                if r.won:
                    comebacks += 1
        comeback_rate = comebacks / eligible if eligible > 0 else 0.0
    else:
        comeback_rate = 0.0

    # 7. 전략 다양성: 모든 전략이 랜덤 이상 + 전략 간 분포
    strategy_wrs = [greedy_wr, tank_wr, synergy_wr, hybrid_wr]
    above_random = sum(1 for s in strategy_wrs if s > win_rate) / len(strategy_wrs)
    strategy_spread = statistics.stdev(strategy_wrs) if len(strategy_wrs) > 1 else 0

    metrics = {
        'n_games': n_games,
        'win_rate_random': round(win_rate, 4),
        'win_rate_greedy': round(greedy_wr, 4),
        'win_rate_tank': round(tank_wr, 4),
        'win_rate_synergy': round(synergy_wr, 4),
        'win_rate_hybrid': round(hybrid_wr, 4),
        'decision_impact': round(decision_impact, 4),
        'diversity_entropy': round(diversity, 4),
        'tension_ratio': round(tension, 4),
        'avg_lead_changes': round(avg_lead_changes, 4),
        'progression_gradient': round(progression, 4),
        'strategies_above_random': round(above_random, 2),
        'strategy_spread': round(strategy_spread, 4),
        'close_finish_rate': round(close_finish_rate, 4),
        'comeback_rate': round(comeback_rate, 4),
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

    # 복합 재미 점수 (0~100, 7개 차원)
    m = metrics
    wr = m['win_rate_random']
    # 승률: 25~45%가 이상적 (15점)
    wr_score = max(0, 1 - ((wr - 0.35) / 0.25) ** 2) * 15
    # 의사결정: 높을수록 좋음 (최대 0.5 → 15점)
    di_score = min(m['decision_impact'] / 0.5, 1.0) * 15
    # 긴장감: 역전 비율 (최대 0.8 → 14점)
    tn_score = min(m['tension_ratio'] / 0.8, 1.0) * 14
    # 박빙: 승자 HP<30% 비율 (최대 0.5 → 14점)
    cf_score = min(m['close_finish_rate'] / 0.5, 1.0) * 14
    # 다양성: 높을수록 좋음 (최대 3.0 → 14점)
    dv_score = min(m['diversity_entropy'] / 3.0, 1.0) * 14
    # 전략 다양성: 모든 전략이 랜덤 이상이면 만점 (14점)
    st_score = m['strategies_above_random'] * 14
    # 역전 드라마: comeback_rate (최대 0.15 → 14점)
    cb_score = min(m['comeback_rate'] / 0.15, 1.0) * 14
    fun_score = round(wr_score + di_score + tn_score + cf_score + dv_score + st_score + cb_score, 1)
    print(f"\n  ★ FUN SCORE: {fun_score}/100")
    print(f"    난이도 {wr_score:.1f}/15  의사결정 {di_score:.1f}/15  긴장감 {tn_score:.1f}/14  박빙 {cf_score:.1f}/14  다양성 {dv_score:.1f}/14  전략폭 {st_score:.1f}/14  역전 {cb_score:.1f}/14")


if __name__ == '__main__':
    metrics = run_evaluation(3000)
    print_report(metrics)
