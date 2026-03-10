"""
Midnight Bestiary — 인간 플레이 모드 (터미널)

실행: python3 play_cli.py
"""

from game import Unit, make_random_unit, battle
import os


# ANSI 색상
class C:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BG_RED = '\033[41m'


ARCHETYPE_ICON = {
    'beast': '🐺', 'imp': '👿', 'blob': '🫧', 'bot': '🤖', 'ghost': '👻', 'wyrm': '🐉', 'phoenix': '🔥',
}

ARCHETYPE_COLOR = {
    'beast': C.RED, 'imp': C.MAGENTA, 'blob': C.CYAN, 'bot': C.WHITE,
    'ghost': C.DIM, 'wyrm': C.GREEN, 'phoenix': C.YELLOW,
}

PASSIVE_DESC = {
    'beast': '광폭: HP 50%↓ → ATK 1.5x',
    'imp':   '사기진작: imp 수만큼 팀 ATK+1',
    'blob':  '경화: 받는 피해 -30%',
    'bot':   '연사: 50% 추가 타격',
    'ghost': '회피: 25% 회피+반격',
    'wyrm':  '성장: 매 4턴 ATK+1',
    'phoenix': '부활: 최초 사망 시 HP 50%로 부활',
}

SYNERGY_NOTE = "  ※ 같은 종족 2마리→스탯+15%, 3마리→스탯+30%"


def clear():
    os.system('clear' if os.name != 'nt' else 'cls')


def hp_bar(current: int, maximum: int, width: int = 16) -> str:
    ratio = max(0, current / maximum) if maximum > 0 else 0
    filled = round(ratio * width)
    # 색상: 초록(>50%) → 노랑(>25%) → 빨강(≤25%)
    if ratio > 0.5:
        color = C.GREEN
    elif ratio > 0.25:
        color = C.YELLOW
    else:
        color = C.RED
    bar = f"{color}{'█' * filled}{C.DIM}{'░' * (width - filled)}{C.RESET}"
    return f"[{bar}] {current}/{maximum}"


def fmt_unit(u: Unit, max_hp: int, indent: str = "  ") -> str:
    icon = ARCHETYPE_ICON.get(u.name, '?')
    color = ARCHETYPE_COLOR.get(u.name, '')
    alive = "  " if u.is_alive() else "💀"
    name_str = f"{color}{u.name:6s}{C.RESET}" if u.is_alive() else f"{C.DIM}{u.name:6s}{C.RESET}"
    return f"{indent}{alive} {icon} {name_str} ATK {u.atk:2d}  {hp_bar(u.hp, max_hp)}"


def interactive_play():
    clear()
    print(f"{C.MAGENTA}{C.BOLD}{'=' * 50}")
    print("  ☽ MIDNIGHT BESTIARY ☾")
    print(f"{'=' * 50}{C.RESET}")
    print()
    print("  8라운드를 생존하라. (목숨 2개)")
    print("  매 라운드, 4마리 중 1마리를 드래프트한다.")
    print()
    print(SYNERGY_NOTE)
    print()
    input("  [Enter] 시작...")

    team: list[Unit] = []
    team_max_hps: list[int] = []
    n_rounds = 8
    lives = 2
    enemies_per_round = [1, 2, 2, 3, 3, 4, 4, 5]
    enemy_power = [0.7, 0.8, 0.95, 0.95, 1.0, 1.1, 1.2, 1.3]
    prev_won = False  # 직전 라운드 승리 여부 (보너스 선택지용)
    all_battles = []  # 전투 기록 누적

    for round_num in range(1, n_rounds + 1):
        clear()
        lives_str = "♥" * lives + "♡" * (2 - lives)
        print(f"  ══ ROUND {round_num}/{n_rounds}  {lives_str} ══")
        print()

        if team:
            print("  현재 팀:")
            for u, mhp in zip(team, team_max_hps):
                print(fmt_unit(u, mhp, "    "))
            # 시너지 현황
            from collections import Counter
            counts = Counter(u.name for u in team if u.is_alive())
            synergies = [(name, cnt) for name, cnt in counts.items() if cnt >= 2]
            if synergies:
                syn_str = ", ".join(f"{ARCHETYPE_ICON.get(n,'?')}{n}x{c}({'+'}{15 if c==2 else 30}%)"
                                     for n, c in synergies)
                print(f"    시너지: {syn_str}")
            print()

        # 드래프트 — 승리 보상: 선택지 +1
        n_choices = 5 if (round_num > 1 and prev_won) else 4
        choices = [make_random_unit(tier=round_num) for _ in range(n_choices)]
        bonus_tag = " (+1 보너스!)" if n_choices == 5 else ""
        print(f"  드래프트{bonus_tag} — 하나를 선택하세요:")
        print()
        from collections import Counter
        team_counts = Counter(u.name for u in team)
        for i, c in enumerate(choices):
            icon = ARCHETYPE_ICON.get(c.name, '?')
            passive = PASSIVE_DESC.get(c.name, '')
            existing = team_counts.get(c.name, 0)
            syn_tag = f" [팀 {existing}마리→시너지!]" if existing >= 1 else ""
            print(f"    [{i + 1}] {icon} {c.name:6s}  HP {c.hp:3d}  ATK {c.atk:2d}  ({passive}){syn_tag}")
        print()

        while True:
            try:
                pick = int(input(f"  선택 (1-{n_choices}): ")) - 1
                if 0 <= pick < n_choices:
                    break
            except (ValueError, EOFError):
                pass
            print(f"  1~{n_choices} 중 하나를 입력하세요.")

        chosen = choices[pick]
        team.append(chosen)
        team_max_hps.append(chosen.hp)
        icon = ARCHETYPE_ICON.get(chosen.name, '?')
        print(f"\n  → {icon} {chosen.name} 영입!")

        # 적 생성 — game.py와 동일한 공식
        n_enemies = enemies_per_round[round_num - 1]
        enemies = [make_random_unit(tier=round_num, stat_mult=enemy_power[round_num - 1])
                   for _ in range(n_enemies)]
        enemy_max_hps = [e.hp for e in enemies]

        print(f"\n  적 {n_enemies}마리 출현!")
        for e in enemies:
            eicon = ARCHETYPE_ICON.get(e.name, '?')
            print(f"    {eicon} {e.name:6s}  HP {e.hp:3d}  ATK {e.atk:2d}")

        input("\n  [Enter] 전투 시작...")

        # game.py의 battle() 사용 — 로직 항상 동기화
        log = battle(team, enemies)
        all_battles.append(log)
        won = log.winner == 'a'

        # 전투 후 유닛 상태를 팀에 반영
        for i, post in enumerate(log.a_units):
            team[i].hp = post.hp
        for i, post in enumerate(log.b_units):
            enemies[i].hp = post.hp

        # 전투 연출 — 하이라이트를 극적으로 표시
        import time
        print()
        if log.highlights:
            print("  ── 전투 진행 ──")
            for h in log.highlights:
                icon = "💥" if "크리티컬" in h else "👻" if "회피" in h else "🔥" if "부활" in h else "💀" if "처치" in h else "⚔️" if "역전" in h else "⚡"
                print(f"    {icon} {h}")
                time.sleep(0.3)
            print()
        print("  ── 전투 결과 ──")
        print(f"  턴 수: {log.turns}  |  역전: {log.lead_changes}회")
        print()
        print("  내 팀:")
        for u, mhp in zip(team, team_max_hps):
            print(fmt_unit(u, mhp, "    "))
        print()
        print("  적:")
        for e, emhp in zip(enemies, enemy_max_hps):
            print(fmt_unit(e, emhp, "    "))
        print()

        if won:
            print(f"  {C.GREEN}{C.BOLD}✦ 승리!{C.RESET}")
        else:
            lives -= 1
            if lives > 0:
                print(f"  {C.YELLOW}✘ 패배... 하지만 아직 목숨 {lives}개 남음!{C.RESET}")
                print("  (전원 HP 30%로 부활)")
                for i, u in enumerate(team):
                    max_hp = 25 + round_num * 5 + 5
                    u.hp = max(1, round(max_hp * 0.3))
                    team_max_hps[i] = max(team_max_hps[i], u.hp)
            else:
                print(f"  {C.RED}{C.BOLD}✘ 패배...{C.RESET}")

        prev_won = won

        if won and round_num < n_rounds:
            for u in team:
                if u.is_alive():
                    max_hp = 25 + round_num * 5 + 5
                    u.hp = min(max_hp, u.hp + round(max_hp * 0.15))
            print("  (생존 유닛 HP 15% 회복 + 다음 드래프트 선택지 +1)")

        if not won and lives <= 0:
            print(f"\n  {C.RED}{C.BOLD}─── GAME OVER ───{C.RESET}")
            print(f"  {round_num - 1}/{n_rounds} 라운드 클리어")
            print(f"  팀원: {', '.join(ARCHETYPE_ICON.get(u.name,'?') + u.name for u in team)}")
            total_lead_changes = sum(b.lead_changes for b in all_battles)
            print(f"  총 역전: {total_lead_changes}회")
            retry = input("\n  다시 도전? (y/n): ").strip().lower()
            if retry == 'y':
                interactive_play()
            return

        if round_num < n_rounds:
            input("\n  [Enter] 다음 라운드...")

    print()
    print(f"  {C.YELLOW}{C.BOLD}★★★ 전 라운드 클리어! ★★★{C.RESET}")
    print(f"  팀원: {', '.join(ARCHETYPE_ICON.get(u.name,'?') + u.name for u in team)}")
    total_lead_changes = sum(b.lead_changes for b in all_battles)
    print(f"  총 역전: {total_lead_changes}회  |  남은 목숨: {'♥' * lives}")
    retry = input("\n  다시 도전? (y/n): ").strip().lower()
    if retry == 'y':
        interactive_play()


if __name__ == '__main__':
    interactive_play()
