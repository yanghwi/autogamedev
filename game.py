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
    max_hp: int = 0  # 패시브 판정용

    def __post_init__(self):
        if self.max_hp == 0:
            self.max_hp = self.hp

    def is_alive(self) -> bool:
        return self.hp > 0

    def effective_atk(self) -> int:
        """패시브 반영 공격력."""
        atk = self.atk
        # beast 광폭: HP 50% 이하 → ATK 1.5배
        if self.name == 'beast' and self.hp <= self.max_hp * 0.5:
            atk = round(atk * 1.5)
        return atk

    def damage_reduction(self) -> float:
        """피해 감소 비율. blob: 20% 감소."""
        if self.name == 'blob':
            return 0.2
        return 0.0


@dataclass
class BattleLog:
    turns: int
    winner: str  # 'a' or 'b'
    a_hp_remaining: float  # 0~1 비율
    b_hp_remaining: float
    lead_changes: int  # 우세가 뒤바뀐 횟수
    a_units: list = None  # 전투 후 a팀 유닛 상태
    b_units: list = None  # 전투 후 b팀 유닛 상태


def apply_synergy(team: list[Unit]):
    """같은 종족 2+ → 소폭 버프. 3+ → 더 큰 버프."""
    from collections import Counter
    counts = Counter(u.name for u in team)
    for u in team:
        n = counts[u.name]
        if n >= 3:
            u.hp = round(u.hp * 1.30)
            u.atk = round(u.atk * 1.30)
        elif n >= 2:
            u.hp = round(u.hp * 1.15)
            u.atk = round(u.atk * 1.15)
        u.max_hp = u.hp


def battle(team_a: list[Unit], team_b: list[Unit]) -> BattleLog:
    """team_a vs team_b. 배틀 로그 반환."""
    a = [Unit(u.name, u.hp, u.atk) for u in team_a]
    b = [Unit(u.name, u.hp, u.atk) for u in team_b]
    apply_synergy(a)
    apply_synergy(b)
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

        # imp 사기 진작: 살아있는 imp 수만큼 팀 전원 ATK +1
        imp_bonus_a = sum(1 for u in alive_a if u.name == 'imp' and u.is_alive())
        imp_bonus_b = sum(1 for u in alive_b if u.name == 'imp' and u.is_alive())

        def do_attack(atk_unit, def_unit, imp_bonus):
            base_atk = atk_unit.effective_atk() + imp_bonus
            dmg = max(1, round(base_atk * random.uniform(0.5, 1.5)))
            if def_unit.name == 'ghost' and random.random() < 0.25:
                dmg = 0  # ghost 회피
                # ghost 반격: 회피 성공 시 공격자에게 반격
                counter = max(1, round(def_unit.effective_atk() * 0.5))
                atk_unit.hp -= counter
            # blob 피해 감소
            reduction = def_unit.damage_reduction()
            if reduction > 0:
                dmg = max(1, round(dmg * (1 - reduction)))
            def_unit.hp -= dmg
            # bot 연사: 50% 확률로 약한 추가 타격
            if atk_unit.name == 'bot' and random.random() < 0.5:
                bonus = max(1, dmg // 3)
                def_unit.hp -= bonus

        # a 공격
        attacker = alive_a[turn % len(alive_a)]
        target = alive_b[0]
        do_attack(attacker, target, imp_bonus_a)

        alive_a = [u for u in a if u.is_alive()]
        alive_b = [u for u in b if u.is_alive()]
        if not alive_a or not alive_b:
            break

        # b 공격
        attacker = alive_b[turn % len(alive_b)]
        target = alive_a[0]
        do_attack(attacker, target, imp_bonus_b)

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
        a_units=a,
        b_units=b,
    )


# ===== 유닛 풀 (에이전트가 진화시킬 부분) =====

def make_random_unit(tier: int = 1, stat_mult: float = 1.0) -> Unit:
    """티어에 따라 유닛 생성. 아키타입별 스탯 분화로 전투 긴장감 증가."""
    # 아키타입: (이름, HP배율, ATK배율) — 총 파워 유사하되 배분이 다름
    archetypes = [
        ('beast', 0.8, 1.4),   # 유리포: 낮은 HP, 높은 ATK
        ('imp',   1.0, 1.0),   # 균형형
        ('blob',  1.3, 0.7),   # 탱커: 높은 HP, 낮은 ATK
        ('bot',   0.9, 1.2),   # 딜러
        ('ghost', 1.1, 0.9),   # 서브탱커
    ]
    name, hp_mult, atk_mult = random.choice(archetypes)
    base_hp = 25 + tier * 5
    base_atk = 3 + tier * 1
    return Unit(
        name=name,
        hp=round(random.randint(base_hp, base_hp + 10) * stat_mult * hp_mult),
        atk=max(1, round(random.randint(base_atk, base_atk + 2) * stat_mult * atk_mult)),
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
    n_rounds = 7  # 7라운드: 더 긴 진행감 곡선

    for round_num in range(1, n_rounds + 1):
        # 드래프트: 3개 중 1개 선택
        choices = [make_random_unit(tier=round_num) for _ in range(3)]
        if strategy:
            import inspect
            sig = inspect.signature(strategy)
            if len(sig.parameters) >= 3:
                pick = strategy(choices, round_num, team=team)
            else:
                pick = strategy(choices, round_num)
        else:
            pick = random.randint(0, 2)
        team.append(choices[pick])

        # 적: 라운드별 수 직접 지정 (R1-2 평탄 해소) + 스탯 배율
        enemies_per_round = [1, 2, 2, 3, 3, 4, 4]  # 7라운드 확장
        n_enemies = enemies_per_round[round_num - 1]
        enemy_power = [0.7, 0.8, 0.95, 0.95, 1.0, 1.1, 1.2]
        enemies = [make_random_unit(tier=round_num, stat_mult=enemy_power[round_num - 1])
                   for _ in range(n_enemies)]

        # 전투
        log = battle(team, enemies)
        battles.append(log)
        won_round = log.winner == 'a'
        choice_outcomes.append(won_round)

        # 라운드 승리 시 생존 유닛 HP 15% 회복 (누적 피해 완화)
        if won_round:
            for u in team:
                if u.is_alive():
                    max_hp = 25 + round_num * 5 + 5
                    u.hp = min(max_hp, u.hp + round(max_hp * 0.15))

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

def synergy_strategy(choices: list[Unit], round_num: int, team: list = None) -> int:
    """팀에 이미 있는 종족을 우선 선택 (시너지 극대화)."""
    if not team:
        return max(range(len(choices)), key=lambda i: choices[i].atk + choices[i].hp)
    from collections import Counter
    counts = Counter(u.name for u in team)
    def score(i):
        c = choices[i]
        # 시너지 보너스: 이미 같은 종족이 있으면 크게 가산
        syn = counts.get(c.name, 0) * 20
        return c.atk + c.hp + syn
    return max(range(len(choices)), key=score)


if __name__ == '__main__':
    N = 1000
    random_wins = sum(1 for _ in range(N) if play().won)
    greedy_wins = sum(1 for _ in range(N) if play(strategy=greedy_strategy).won)
    tank_wins = sum(1 for _ in range(N) if play(strategy=tank_strategy).won)
    print(f"1000판 승률:")
    print(f"  랜덤:   {random_wins / 10:.1f}%")
    print(f"  ATK욕심: {greedy_wins / 10:.1f}%")
    print(f"  HP탱크:  {tank_wins / 10:.1f}%")
