"""
Midnight Bestiary — game.py (Seed v1)

진화 이력:
  v0: 최소 원형 (Unit + battle + play)
  v1: 배틀 로그 추가 → 긴장감 측정 가능
      다중 라운드 + 드래프트 선택 추가 → 진행감/의사결정 측정 가능
"""

import random
from dataclasses import dataclass


@dataclass
class Unit:
    name: str
    hp: int
    atk: int

    def is_alive(self) -> bool:
        return self.hp > 0


@dataclass
class BattleLog:
    turns: int
    winner: str  # 'a' or 'b'
    a_hp_remaining: float  # 0~1 비율
    b_hp_remaining: float
    lead_changes: int  # 우세가 뒤바뀐 횟수


def battle(team_a: list[Unit], team_b: list[Unit]) -> BattleLog:
    """team_a vs team_b. 배틀 로그 반환."""
    a = [Unit(u.name, u.hp, u.atk) for u in team_a]
    b = [Unit(u.name, u.hp, u.atk) for u in team_b]
    a_max_hp = sum(u.hp for u in a)
    b_max_hp = sum(u.hp for u in b)

    lead_changes = 0
    prev_leader = None

    for turn in range(200):
        alive_a = [u for u in a if u.is_alive()]
        alive_b = [u for u in b if u.is_alive()]
        if not alive_a or not alive_b:
            break

        # 누가 우세한가
        a_ratio = sum(u.hp for u in alive_a) / a_max_hp
        b_ratio = sum(u.hp for u in alive_b) / b_max_hp
        leader = 'a' if a_ratio >= b_ratio else 'b'
        if prev_leader and leader != prev_leader:
            lead_changes += 1
        prev_leader = leader

        # a 공격
        attacker = alive_a[turn % len(alive_a)]
        target = alive_b[0]
        target.hp -= max(1, attacker.atk)

        alive_b = [u for u in b if u.is_alive()]
        if not alive_b:
            break

        # b 공격
        attacker = alive_b[turn % len(alive_b)]
        target = [u for u in a if u.is_alive()][0]
        target.hp -= max(1, attacker.atk)

    alive_a = [u for u in a if u.is_alive()]
    alive_b = [u for u in b if u.is_alive()]
    a_hp_ratio = sum(max(0, u.hp) for u in a) / a_max_hp if a_max_hp else 0
    b_hp_ratio = sum(max(0, u.hp) for u in b) / b_max_hp if b_max_hp else 0
    winner = 'a' if a_hp_ratio >= b_hp_ratio else 'b'

    return BattleLog(
        turns=turn + 1,
        winner=winner,
        a_hp_remaining=max(0, a_hp_ratio),
        b_hp_remaining=max(0, b_hp_ratio),
        lead_changes=lead_changes,
    )


# ===== 유닛 풀 (에이전트가 진화시킬 부분) =====

def make_random_unit(tier: int = 1) -> Unit:
    """티어에 따라 유닛 생성. 티어 체계는 에이전트가 발전시킨다."""
    names = ['beast', 'imp', 'blob', 'bot', 'ghost']
    base_hp = 25 + tier * 5
    base_atk = 3 + tier * 1
    return Unit(
        name=random.choice(names),
        hp=random.randint(base_hp, base_hp + 10),
        atk=random.randint(base_atk, base_atk + 2),
    )


# ===== 게임: 라운드 연속 + 드래프트 =====

@dataclass
class GameResult:
    won: bool
    rounds_cleared: int
    total_rounds: int
    battles: list[BattleLog]
    choices_made: int  # 의사결정 횟수
    choice_outcomes: list[bool]  # 각 선택 후 승리 여부


def play(strategy=None) -> GameResult:
    """
    한 판의 게임.

    strategy: (choices: list[Unit], round_num: int) -> int
        드래프트 선택 함수. None이면 랜덤.
    """
    team: list[Unit] = []
    battles: list[BattleLog] = []
    choice_outcomes: list[bool] = []
    n_rounds = 5  # 에이전트가 조정할 수 있음

    for round_num in range(1, n_rounds + 1):
        # 드래프트: 3개 중 1개 선택
        choices = [make_random_unit(tier=round_num) for _ in range(3)]
        if strategy:
            pick = strategy(choices, round_num)
        else:
            pick = random.randint(0, 2)
        team.append(choices[pick])

        # 적: 팀 수의 ~65%, 드래프트와 같은 티어
        n_enemies = max(1, round(len(team) * 0.65))
        enemies = [make_random_unit(tier=round_num) for _ in range(n_enemies)]

        # 전투
        log = battle(team, enemies)
        battles.append(log)
        won_round = log.winner == 'a'
        choice_outcomes.append(won_round)

        if not won_round:
            return GameResult(
                won=False,
                rounds_cleared=round_num - 1,
                total_rounds=n_rounds,
                battles=battles,
                choices_made=round_num,
                choice_outcomes=choice_outcomes,
            )

    return GameResult(
        won=True,
        rounds_cleared=n_rounds,
        total_rounds=n_rounds,
        battles=battles,
        choices_made=n_rounds,
        choice_outcomes=choice_outcomes,
    )


# ===== 전략 비교 (의사결정 의미성 측정용) =====

def greedy_strategy(choices: list[Unit], round_num: int) -> int:
    """가장 높은 ATK 선택."""
    return max(range(len(choices)), key=lambda i: choices[i].atk)

def tank_strategy(choices: list[Unit], round_num: int) -> int:
    """가장 높은 HP 선택."""
    return max(range(len(choices)), key=lambda i: choices[i].hp)


if __name__ == '__main__':
    N = 1000
    random_wins = sum(1 for _ in range(N) if play().won)
    greedy_wins = sum(1 for _ in range(N) if play(strategy=greedy_strategy).won)
    tank_wins = sum(1 for _ in range(N) if play(strategy=tank_strategy).won)
    print(f"1000판 승률:")
    print(f"  랜덤:   {random_wins / 10:.1f}%")
    print(f"  ATK욕심: {greedy_wins / 10:.1f}%")
    print(f"  HP탱크:  {tank_wins / 10:.1f}%")
