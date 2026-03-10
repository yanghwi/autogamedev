"""
Midnight Bestiary — 인간 플레이 모드 (터미널)

실행: python3 play_cli.py
"""

from game import Unit, make_random_unit, battle
import os


ARCHETYPE_ICON = {
    'beast': '🐺', 'imp': '👿', 'blob': '🫧', 'bot': '🤖', 'ghost': '👻',
}


def clear():
    os.system('clear' if os.name != 'nt' else 'cls')


def hp_bar(current: int, maximum: int, width: int = 16) -> str:
    ratio = max(0, current / maximum) if maximum > 0 else 0
    filled = round(ratio * width)
    return f"[{'█' * filled}{'░' * (width - filled)}] {current}/{maximum}"


def fmt_unit(u: Unit, max_hp: int, indent: str = "  ") -> str:
    icon = ARCHETYPE_ICON.get(u.name, '?')
    alive = "  " if u.is_alive() else "💀"
    return f"{indent}{alive} {icon} {u.name:6s} ATK {u.atk:2d}  {hp_bar(u.hp, max_hp)}"


def interactive_play():
    clear()
    print("=" * 50)
    print("  ☽ MIDNIGHT BESTIARY ☾")
    print("=" * 50)
    print()
    print("  5라운드를 생존하라.")
    print("  매 라운드, 3마리 중 1마리를 드래프트한다.")
    print()
    input("  [Enter] 시작...")

    team: list[Unit] = []
    team_max_hps: list[int] = []
    enemy_power = [0.9, 0.95, 1.0, 1.1, 1.2]

    for round_num in range(1, 6):
        clear()
        print(f"  ══ ROUND {round_num}/5 ══")
        print()

        if team:
            print("  현재 팀:")
            for u, mhp in zip(team, team_max_hps):
                print(fmt_unit(u, mhp, "    "))
            print()

        # 드래프트
        choices = [make_random_unit(tier=round_num) for _ in range(3)]
        print("  드래프트 — 하나를 선택하세요:")
        print()
        for i, c in enumerate(choices):
            icon = ARCHETYPE_ICON.get(c.name, '?')
            print(f"    [{i + 1}] {icon} {c.name:6s}  HP {c.hp:3d}  ATK {c.atk:2d}")
        print()

        while True:
            try:
                pick = int(input("  선택 (1-3): ")) - 1
                if 0 <= pick <= 2:
                    break
            except (ValueError, EOFError):
                pass
            print("  1, 2, 3 중 하나를 입력하세요.")

        chosen = choices[pick]
        team.append(chosen)
        team_max_hps.append(chosen.hp)
        icon = ARCHETYPE_ICON.get(chosen.name, '?')
        print(f"\n  → {icon} {chosen.name} 영입!")

        # 적 생성
        n_enemies = max(1, round(len(team) * 0.55))
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
        won = log.winner == 'a'

        # 전투 후 유닛 상태를 팀에 반영
        for i, post in enumerate(log.a_units):
            team[i].hp = post.hp
        for i, post in enumerate(log.b_units):
            enemies[i].hp = post.hp

        # 결과 표시
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
            print("  ✦ 승리!")
        else:
            print("  ✘ 패배...")

        if won and round_num < 5:
            for u in team:
                if u.is_alive():
                    max_hp = 25 + round_num * 5 + 5
                    u.hp = min(max_hp, u.hp + round(max_hp * 0.15))
            print("  (생존 유닛 HP 15% 회복)")

        if not won:
            print(f"\n  라운드 {round_num}에서 전멸. {round_num - 1}라운드 클리어.")
            input("\n  [Enter] 종료...")
            return

        if round_num < 5:
            input("\n  [Enter] 다음 라운드...")

    print()
    print("  ★★★ 전 라운드 클리어! ★★★")
    input("\n  [Enter] 종료...")


if __name__ == '__main__':
    interactive_play()
