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
    'blob':  '경화: 받는 피해 -25%',
    'bot':   '연사: 50% 추가 타격',
    'ghost': '회피: 25% 회피+반격',
    'wyrm':  '성장: 매 4턴 ATK+1',
    'phoenix': '부활: 최초 사망 시 HP 50%로 부활',
}

SYNERGY_NOTE = "  ※ 같은 종족 2마리→스탯+20%, 3마리→스탯+35%"


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


def _show_game_summary(team, team_max_hps, all_battles, cleared, total, lives):
    """게임 종료 후 상세 요약."""
    from collections import Counter
    print(f"\n  {C.BOLD}── 게임 요약 ──{C.RESET}")
    print(f"  라운드: {cleared}/{total}  |  남은 목숨: {'♥' * lives if lives else '없음'}")

    # 팀 구성
    print(f"\n  {C.BOLD}팀 구성:{C.RESET}")
    for u, mhp in zip(team, team_max_hps):
        print(fmt_unit(u, mhp, "    "))

    # 전투 통계
    total_turns = sum(b.turns for b in all_battles)
    total_reversals = sum(b.lead_changes for b in all_battles)
    total_highlights = sum(len(b.highlights) for b in all_battles)

    print(f"\n  {C.BOLD}전투 통계:{C.RESET}")
    wins = sum(1 for b in all_battles if b.winner == 'a')
    losses = sum(1 for b in all_battles if b.winner == 'b')
    print(f"    총 {len(all_battles)}전 {wins}승 {losses}패")
    # 라운드별 승패 타임라인
    timeline = "    "
    for i, b in enumerate(all_battles):
        if b.winner == 'a':
            timeline += f"{C.GREEN}W{C.RESET}"
        else:
            timeline += f"{C.RED}L{C.RESET}"
        if i < len(all_battles) - 1:
            timeline += "→"
    print(timeline)
    print(f"    총 턴 수: {total_turns}  |  역전: {total_reversals}회")

    # 가장 극적인 전투
    if all_battles:
        most_dramatic = max(all_battles, key=lambda b: b.lead_changes)
        drama_round = all_battles.index(most_dramatic) + 1
        if most_dramatic.lead_changes > 0:
            print(f"    최고 명장면: R{drama_round} ({most_dramatic.lead_changes}회 역전!)")

    # 시너지 현황
    counts = Counter(u.name for u in team)
    synergies = [(n, c) for n, c in counts.items() if c >= 2]
    if synergies:
        syn_str = ", ".join(f"{ARCHETYPE_ICON.get(n,'?')}{n}x{c}" for n, c in synergies)
        print(f"    시너지: {syn_str}")

    # 플레이 등급
    total_reversals = sum(b.lead_changes for b in all_battles)
    wins = sum(1 for b in all_battles if b.winner == 'a')
    score = cleared * 10 + wins * 5 + total_reversals * 2 + lives * 15
    if score >= 100:
        grade, grade_color = "S", C.YELLOW
    elif score >= 80:
        grade, grade_color = "A", C.GREEN
    elif score >= 60:
        grade, grade_color = "B", C.CYAN
    elif score >= 40:
        grade, grade_color = "C", C.WHITE
    else:
        grade, grade_color = "D", C.DIM
    print(f"\n  {C.BOLD}플레이 등급: {grade_color}{grade}{C.RESET}  ({score}점)")

    # 전략 팁
    print(f"\n  {C.DIM}팁: 같은 종족을 모으면 시너지 보너스! (2+→스탯 UP){C.RESET}")


def _show_bestiary():
    """종족 도감 표시."""
    print(f"\n  {C.BOLD}── 종족 도감 ──{C.RESET}")
    for name, desc in PASSIVE_DESC.items():
        icon = ARCHETYPE_ICON.get(name, '?')
        color = ARCHETYPE_COLOR.get(name, '')
        print(f"    {icon} {color}{name:8s}{C.RESET} {desc}")
    print(f"\n  {SYNERGY_NOTE}")
    print()


def interactive_play():
    clear()
    print(f"{C.MAGENTA}{C.BOLD}{'=' * 50}")
    print("  ☽ MIDNIGHT BESTIARY ☾")
    print(f"{'=' * 50}{C.RESET}")
    print()
    print("  9라운드를 생존하라.")
    print("  매 라운드, 후보 중 1마리를 드래프트한다.")
    print()

    # 난이도 선택
    print(f"  {C.BOLD}난이도 선택:{C.RESET}")
    print(f"    [1] {C.GREEN}쉬움{C.RESET}  — 목숨 3개, 적 약화")
    print(f"    [2] {C.YELLOW}보통{C.RESET}  — 목숨 2개 (기본)")
    print(f"    [3] {C.RED}어려움{C.RESET} — 목숨 1개, 적 강화")
    print()

    while True:
        try:
            diff = int(input("  선택 (1-3): "))
            if 1 <= diff <= 3:
                break
        except (ValueError, EOFError):
            pass
        print("  1~3 중 하나를 입력하세요.")

    if diff == 1:  # 쉬움
        lives = 3
        power_mult = 0.85
        diff_name = "쉬움"
    elif diff == 3:  # 어려움
        lives = 1
        power_mult = 1.15
        diff_name = "어려움"
    else:  # 보통
        lives = 2
        power_mult = 1.0
        diff_name = "보통"
    max_lives = lives

    _show_bestiary()
    input("  [Enter] 시작...")

    team: list[Unit] = []
    team_max_hps: list[int] = []
    n_rounds = 9
    enemies_per_round = [1, 2, 2, 3, 3, 4, 4, 5, 3]
    enemy_power = [round(p * power_mult, 2) for p in [0.7, 0.8, 0.95, 0.95, 1.0, 1.05, 1.15, 1.2, 1.35]]
    prev_won = False  # 직전 라운드 승리 여부 (보너스 선택지용)
    all_battles = []  # 전투 기록 누적

    for round_num in range(1, n_rounds + 1):
        clear()
        lives_str = "♥" * lives + "♡" * (max_lives - lives)
        if round_num == n_rounds:
            print(f"  {C.RED}{C.BOLD}══ FINAL ROUND  {lives_str} ══{C.RESET}")
            print(f"  {C.DIM}최후의 전투가 시작된다...{C.RESET}")
        else:
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

        # 전력 비교 미리보기
        my_total_hp = sum(u.hp for u in team if u.is_alive())
        my_total_atk = sum(u.atk for u in team if u.is_alive())
        en_total_hp = sum(e.hp for e in enemies)
        en_total_atk = sum(e.atk for e in enemies)
        hp_adv = "유리" if my_total_hp > en_total_hp else "불리" if my_total_hp < en_total_hp else "동등"
        atk_adv = "유리" if my_total_atk > en_total_atk else "불리" if my_total_atk < en_total_atk else "동등"
        hp_color = C.GREEN if hp_adv == "유리" else C.RED if hp_adv == "불리" else C.YELLOW
        atk_color = C.GREEN if atk_adv == "유리" else C.RED if atk_adv == "불리" else C.YELLOW
        print(f"\n  {C.DIM}전력 비교: HP {hp_color}{my_total_hp}{C.RESET}{C.DIM} vs {en_total_hp} ({hp_color}{hp_adv}{C.RESET}{C.DIM})  ATK {atk_color}{my_total_atk}{C.RESET}{C.DIM} vs {en_total_atk} ({atk_color}{atk_adv}{C.RESET}{C.DIM}){C.RESET}")

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
        a_hp_pct = f"{log.a_hp_remaining:.0%}"
        b_hp_pct = f"{log.b_hp_remaining:.0%}"
        if log.highlights:
            print(f"  {C.BOLD}── 전투 진행 ──{C.RESET}")
            for h in log.highlights:
                icon = "💥" if "크리티컬" in h else "👻" if "회피" in h else "🔥" if "부활" in h else "💀" if "처치" in h else "⚔️" if "역전" in h else "⚡"
                print(f"    {icon} {h}")
                time.sleep(0.3)
            # 전투 후 HP 요약
            a_color = C.GREEN if won else C.RED
            b_color = C.RED if won else C.GREEN
            print(f"\n    {a_color}아군 HP {a_hp_pct}{C.RESET}  vs  {b_color}적군 HP {b_hp_pct}{C.RESET}")
            print()
        print("  ── 전투 결과 ──")
        # 전투 극적 정도에 따라 코멘트
        if log.lead_changes >= 3:
            print(f"  {C.YELLOW}⚡ 숨막히는 접전!{C.RESET}  턴 수: {log.turns}  |  역전: {log.lead_changes}회")
        elif log.turns >= 15:
            print(f"  {C.CYAN}⏳ 장기전...{C.RESET}  턴 수: {log.turns}  |  역전: {log.lead_changes}회")
        elif log.turns <= 5:
            print(f"  {C.RED}💨 순삭!{C.RESET}  턴 수: {log.turns}  |  역전: {log.lead_changes}회")
        else:
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

        # MVP 표시: 생존 유닛 중 가장 높은 ATK
        alive_team = [u for u in team if u.is_alive()]
        if alive_team and won:
            mvp = max(alive_team, key=lambda u: u.effective_atk())
            mvp_icon = ARCHETYPE_ICON.get(mvp.name, '?')
            print(f"  {C.YELLOW}★ MVP: {mvp_icon} {mvp.name} (ATK {mvp.atk}){C.RESET}")
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

        # 상황 맞춤 전략 팁 (첫 플레이어 학습 지원)
        if round_num < n_rounds:
            from collections import Counter
            tip_counts = Counter(u.name for u in team)
            tip_pairs = [n for n, c in tip_counts.items() if c == 1]
            tip_synergies = [n for n, c in tip_counts.items() if c >= 2]
            if round_num <= 2 and not tip_synergies:
                print(f"  {C.DIM}💡 팁: 같은 종족을 2마리 이상 모으면 시너지 보너스!{C.RESET}")
            elif round_num == 3 and tip_pairs:
                pair_name = tip_pairs[0]
                icon = ARCHETYPE_ICON.get(pair_name, '?')
                print(f"  {C.DIM}💡 팁: {icon}{pair_name}을 하나 더 뽑으면 시너지 발동!{C.RESET}")
            elif round_num >= 5 and not won:
                print(f"  {C.DIM}💡 팁: 어려운 후반! 높은 ATK 유닛이 생존에 도움됩니다.{C.RESET}")

        if not won and lives <= 0:
            print(f"\n  {C.RED}{C.BOLD}─── GAME OVER ───{C.RESET}")
            _show_game_summary(team, team_max_hps, all_battles, round_num - 1, n_rounds, 0)
            retry = input("\n  다시 도전? (y/n): ").strip().lower()
            if retry == 'y':
                interactive_play()
            return

        if round_num < n_rounds:
            input("\n  [Enter] 다음 라운드...")

    print()
    print(f"  {C.YELLOW}{C.BOLD}★★★ 전 라운드 클리어! ★★★{C.RESET}")
    _show_game_summary(team, team_max_hps, all_battles, n_rounds, n_rounds, lives)
    retry = input("\n  다시 도전? (y/n): ").strip().lower()
    if retry == 'y':
        interactive_play()


if __name__ == '__main__':
    interactive_play()
