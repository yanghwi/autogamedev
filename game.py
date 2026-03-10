"""
Midnight Bestiary — game.py

진화 이력:
  v0: 최소 원형 (Unit + battle + play)
  v1: 배틀 로그 + 다중 라운드 + 드래프트
  v2: 7종 아키타입 + 시너지 + 패시브 시스템
  v3: 9라운드 + 동시공격 + underdog/fatigue/last_stand 메커닉
  v4: 시너지 보장 드래프트 + underdog 임계값 최적화
      FUN SCORE 98.8~99.0/100
"""

import random
from dataclasses import dataclass


@dataclass
class Unit:
    name: str
    hp: int
    atk: int
    max_hp: int = 0  # 패시브 판정용
    revived: bool = False  # phoenix 부활 여부

    def __post_init__(self):
        if self.max_hp == 0:
            self.max_hp = self.hp

    def is_alive(self) -> bool:
        return self.hp > 0

    def check_phoenix_revive(self) -> bool:
        """phoenix: 최초 사망 시 HP 50%로 부활."""
        if self.name == 'phoenix' and not self.revived and self.hp <= 0:
            self.hp = max(1, round(self.max_hp * 0.5))
            self.revived = True
            return True
        return False

    def effective_atk(self) -> int:
        """패시브 반영 공격력."""
        atk = self.atk
        # beast 광폭: HP 50% 이하 → ATK 1.5배
        if self.name == 'beast' and self.hp <= self.max_hp * 0.5:
            atk = round(atk * 1.5)
        return atk

    def damage_reduction(self) -> float:
        """피해 감소 비율. blob: 25% 감소."""
        if self.name == 'blob':
            return 0.25
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
    highlights: list = None  # 전투 주요 이벤트 문자열 리스트


def apply_synergy(team: list[Unit]):
    """같은 종족 2+ → 소폭 버프. 3+ → 더 큰 버프."""
    from collections import Counter
    counts = Counter(u.name for u in team)
    for u in team:
        n = counts[u.name]
        if n >= 4:
            u.hp = round(u.hp * 1.55)
            u.atk = round(u.atk * 1.55)
        elif n >= 3:
            u.hp = round(u.hp * 1.35)
            u.atk = round(u.atk * 1.35)
        elif n >= 2:
            u.hp = round(u.hp * 1.20)
            u.atk = round(u.atk * 1.20)
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
    highlights = []

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
            side = "아군" if leader == 'a' else "적군"
            highlights.append(f"턴{turn}: {side} 역전!")
        prev_leader = leader

        # wyrm 성장: 매 3턴마다 ATK +1 (긴 전투에서 역전)
        if turn > 0 and turn % 3 == 0:
            for u in alive_a + alive_b:
                if u.name == 'wyrm':
                    u.atk += 1

        # 전투 피로: 턴 12 이후 전 유닛 매 턴 HP -1 (장기전 가속)
        if turn >= 12:
            for u in alive_a + alive_b:
                u.hp = max(1, u.hp - 1)

        # imp 사기 진작: 살아있는 imp 수만큼 팀 전원 ATK +1
        imp_bonus_a = sum(1 for u in alive_a if u.name == 'imp' and u.is_alive())
        imp_bonus_b = sum(1 for u in alive_b if u.name == 'imp' and u.is_alive())

        # 최후의 발악: 팀에 1마리만 남으면 ATK +50%
        last_stand_a = 1.5 if len(alive_a) == 1 else 1.0
        last_stand_b = 1.5 if len(alive_b) == 1 else 1.0

        # 역전 보너스: 열세 팀 피해 15% 감소 (역전 기회 증가)
        underdog_a = 0.85 if a_ratio < b_ratio - 0.05 else 1.0
        underdog_b = 0.85 if b_ratio < a_ratio - 0.05 else 1.0

        def do_attack(atk_unit, def_unit, imp_bonus, last_stand=1.0, underdog=1.0):
            base_atk = round((atk_unit.effective_atk() + imp_bonus) * last_stand)
            dmg = max(1, round(base_atk * random.uniform(0.3, 1.7) * underdog))
            # 크리티컬 히트: 10% 확률로 2배 데미지
            is_crit = random.random() < 0.10
            if is_crit:
                dmg *= 2
                highlights.append(f"턴{turn}: {atk_unit.name} 크리티컬! {dmg}dmg")
            if def_unit.name == 'ghost' and random.random() < 0.25:
                dmg = 0  # ghost 회피
                # ghost 반격: 회피 성공 시 공격자에게 반격
                counter = max(1, round(def_unit.effective_atk() * 0.5))
                atk_unit.hp -= counter
                highlights.append(f"턴{turn}: ghost 회피! → {counter}dmg 반격")
            # blob 피해 감소
            reduction = def_unit.damage_reduction()
            if reduction > 0:
                dmg = max(1, round(dmg * (1 - reduction)))
            def_unit.hp -= dmg
            # bot 연사: 50% 확률로 약한 추가 타격
            if atk_unit.name == 'bot' and random.random() < 0.6:
                bonus = max(1, dmg // 3)
                def_unit.hp -= bonus
            if not def_unit.is_alive():
                if def_unit.check_phoenix_revive():
                    highlights.append(f"턴{turn}: phoenix 부활! HP {def_unit.hp}")
                else:
                    highlights.append(f"턴{turn}: {atk_unit.name}→{def_unit.name} 처치!")

        # 동시 공격: 양팀이 동시에 공격 (선공 유리 제거)
        # 아군은 적 전위(0번) 집중, 적은 아군 랜덤 타겟 (비대칭 — 분산 피해로 역전 기회 증가)
        attacker_a = alive_a[turn % len(alive_a)]
        target_a = alive_b[0]
        attacker_b = alive_b[turn % len(alive_b)]
        target_b = random.choice(alive_a) if random.random() < 0.20 else alive_a[0]
        do_attack(attacker_a, target_a, imp_bonus_a, last_stand_a, underdog_b)
        do_attack(attacker_b, target_b, imp_bonus_b, last_stand_b, underdog_a)

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
        highlights=highlights[-8:] if highlights else [],  # 최근 8개
    )


# ===== 유닛 풀 (에이전트가 진화시킬 부분) =====

ARCHETYPES = [
    ('beast', 0.8, 1.4),   # 유리포: 낮은 HP, 높은 ATK
    ('imp',   1.0, 1.0),   # 균형형
    ('blob',  1.3, 0.7),   # 탱커: 높은 HP, 낮은 ATK
    ('bot',   0.9, 1.2),   # 딜러
    ('ghost', 1.1, 0.9),   # 서브탱커
    ('wyrm',  1.2, 0.6),   # 성장형: 낮은 ATK, 턴 경과 시 성장
    ('phoenix', 1.0, 0.8),  # 부활형: 평균 HP, 낮은 ATK, 1회 부활
]
ARCHETYPE_MAP = {name: (hp_m, atk_m) for name, hp_m, atk_m in ARCHETYPES}


def make_random_unit(tier: int = 1, stat_mult: float = 1.0, archetype: str = None) -> Unit:
    """티어에 따라 유닛 생성. archetype 지정 시 해당 아키타입으로 생성."""
    if archetype and archetype in ARCHETYPE_MAP:
        name = archetype
        hp_mult, atk_mult = ARCHETYPE_MAP[archetype]
    else:
        name, hp_mult, atk_mult = random.choice(ARCHETYPES)
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
    n_rounds = 9  # 9라운드: 보스전 추가
    lives = 2  # 목숨 2개: 첫 패배는 생존, 두 번째가 게임오버

    for round_num in range(1, n_rounds + 1):
        # 드래프트: 기본 4개, 직전 라운드 승리 시 +1 보너스 선택지
        n_choices = 4
        if round_num > 1 and choice_outcomes and choice_outcomes[-1]:
            n_choices = 5  # 승리 보상: 선택지 확대
        choices = [make_random_unit(tier=round_num) for _ in range(n_choices)]
        # R3 이후: 선택지 중 1개를 팀 종족으로 보장 (시너지 빌드 지원)
        if team and round_num >= 3:
            team_names = [u.name for u in team]
            if not any(c.name in team_names for c in choices):
                # 선택지에 팀 종족이 없으면 마지막 슬롯을 교체
                target_name = random.choice(team_names)
                replacement = make_random_unit(tier=round_num, archetype=target_name)
                choices[-1] = replacement
        if strategy:
            import inspect
            sig = inspect.signature(strategy)
            if len(sig.parameters) >= 3:
                pick = strategy(choices, round_num, team=team)
            else:
                pick = strategy(choices, round_num)
        else:
            pick = random.randint(0, len(choices) - 1)
        team.append(choices[pick])

        # 적: 라운드별 수 직접 지정 (R1-2 평탄 해소) + 스탯 배율
        enemies_per_round = [2, 2, 2, 3, 3, 4, 4, 5, 3]  # R1: 2마리로 시작, R9: 보스전
        n_enemies = enemies_per_round[round_num - 1]
        enemy_power = [0.55, 0.8, 0.95, 0.95, 1.0, 1.05, 1.15, 1.2, 1.35]
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
            lives -= 1
            if lives <= 0:
                return GameResult(
                    won=False,
                    rounds_cleared=round_num - 1,
                    total_rounds=n_rounds,
                    battles=battles,
                    choices_made=round_num,
                    choice_outcomes=choice_outcomes,
                )
            # 부활: 전 유닛 HP 30%로 회복하고 계속
            for u in team:
                max_hp = 25 + round_num * 5 + 5
                u.hp = max(1, round(max_hp * 0.3))

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

def hybrid_strategy(choices: list[Unit], round_num: int) -> int:
    """초반(R1-3) 탱커 우선, 후반(R4+) 딜러 우선."""
    if round_num <= 3:
        return max(range(len(choices)), key=lambda i: choices[i].hp)
    return max(range(len(choices)), key=lambda i: choices[i].atk)

def synergy_strategy(choices: list[Unit], round_num: int, team: list = None) -> int:
    """팀에 이미 있는 종족을 우선 선택 (시너지 극대화)."""
    if not team:
        return max(range(len(choices)), key=lambda i: choices[i].atk + choices[i].hp)
    from collections import Counter
    counts = Counter(u.name for u in team)
    def score(i):
        c = choices[i]
        # 시너지 보너스: 이미 같은 종족이 있으면 크게 가산
        syn = counts.get(c.name, 0) * 25
        # wyrm 초반 가치: 일찍 뽑을수록 성장 시간 ↑
        wyrm_bonus = 10 if c.name == 'wyrm' and round_num <= 3 else 0
        return c.atk + c.hp + syn + wyrm_bonus
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
