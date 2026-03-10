"""
Midnight Bestiary — 인간 플레이 모드 (터미널)

실행: python3 play_cli.py
"""

from game import Unit, make_random_unit, battle, ARCHETYPE_MAP
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
    'bot':   '연사: 60% 추가 타격',
    'ghost': '회피: 25% 회피+반격',
    'wyrm':  '성장: 매 3턴 ATK+1',
    'phoenix': '부활: 최초 사망 시 HP 50%로 부활',
}

SYNERGY_NOTE = "  ※ 같은 종족 2마리→+20%, 3마리→+35%, 4마리→+55%"


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
    enemies_per_round = [2, 2, 2, 2, 3, 4, 4, 5, 3]
    enemy_power = [round(p * power_mult, 2) for p in [0.70, 0.85, 0.95, 1.20, 1.0, 1.10, 1.15, 1.2, 1.40]]
    prev_won = False  # 직전 라운드 승리 여부 (보너스 선택지용)
    just_revived = False  # 부활 직후 플래그
    all_battles = []  # 전투 기록 누적

    for round_num in range(1, n_rounds + 1):
        clear()
        lives_str = "♥" * lives + "♡" * (max_lives - lives)
        # 라운드별 분위기 내러티브
        flavor = {
            1: "달이 떠오른다...",
            2: "숲에서 울음소리가 들린다.",
            3: "안개가 짙어진다.",
            4: "강력한 기운이 느껴진다...",
            5: "하늘이 붉게 물든다.",
            6: "그림자가 길어진다.",
            7: "바람이 비명을 지른다.",
            8: "어둠이 모든 것을 삼킨다.",
            9: "최후의 전투가 시작된다...",
        }
        if round_num == n_rounds:
            print(f"  {C.RED}{C.BOLD}══ FINAL ROUND  {lives_str} ══{C.RESET}")
            print(f"  {C.DIM}{flavor.get(round_num, '')}{C.RESET}")
        else:
            print(f"  ══ ROUND {round_num}/{n_rounds}  {lives_str} ══")
            if round_num in flavor:
                print(f"  {C.DIM}{flavor[round_num]}{C.RESET}")
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
                syn_str = ", ".join(f"{ARCHETYPE_ICON.get(n,'?')}{n}x{c}(+{20 if c==2 else 35 if c==3 else 55}%)"
                                     for n, c in synergies)
                print(f"    시너지: {syn_str}")
            print()

        # 드래프트 — 승리 보상: 선택지 +1
        n_choices = 5 if (round_num > 1 and prev_won) else 4
        choices = [make_random_unit(tier=round_num) for _ in range(n_choices)]
        # R3 이후: 선택지 중 1개를 팀 종족으로 보장 (시너지 빌드 지원)
        if team and round_num >= 3:
            import random
            team_names_set = [u.name for u in team]
            if not any(c.name in team_names_set for c in choices):
                target_name = random.choice(team_names_set)
                replacement = make_random_unit(tier=round_num, archetype=target_name)
                choices[-1] = replacement
        bonus_tag = " (+1 보너스!)" if n_choices == 5 else ""
        print(f"  드래프트{bonus_tag} — 하나를 선택하세요:")
        if round_num == 1:
            print(f"  {C.DIM}(첫 유닛! 높은 ATK=공격력, 높은 HP=생존력. 패시브도 확인!){C.RESET}")
        print()
        from collections import Counter
        team_counts = Counter(u.name for u in team)
        for i, c in enumerate(choices):
            icon = ARCHETYPE_ICON.get(c.name, '?')
            passive = PASSIVE_DESC.get(c.name, '')
            existing = team_counts.get(c.name, 0)
            if existing >= 2:
                syn_tag = f" {C.YELLOW}★★ {existing}마리→강화!{C.RESET}"
            elif existing >= 1:
                syn_tag = f" {C.GREEN}★ 시너지!{C.RESET}"
            else:
                syn_tag = ""
            # 스탯 평가 (ATK*2 + HP 기준 상위면 강조)
            power = c.atk * 2 + c.hp
            best_power = max(ch.atk * 2 + ch.hp for ch in choices)
            stat_tag = f" {C.CYAN}◆최강{C.RESET}" if power == best_power and not syn_tag else ""
            print(f"    [{i + 1}] {icon} {c.name:6s}  HP {c.hp:3d}  ATK {c.atk:2d}  ({passive}){syn_tag}{stat_tag}")
        # 교체 옵션: R4+, 팀 3마리 이상일 때 기존 유닛과 교체 가능
        can_swap = round_num >= 4 and len(team) >= 3
        if can_swap:
            print(f"    {C.DIM}[S] 교체 — 기존 유닛 1마리를 방출하고 새 유닛 영입{C.RESET}")
        print()

        while True:
            try:
                raw = input(f"  선택 (1-{n_choices}{', S=교체' if can_swap else ''}): ").strip()
                if can_swap and raw.lower() == 's':
                    # 교체 모드: 먼저 뽑을 유닛 선택
                    print(f"\n  {C.BOLD}영입할 유닛 선택:{C.RESET}")
                    for i, c in enumerate(choices):
                        icon = ARCHETYPE_ICON.get(c.name, '?')
                        print(f"    [{i + 1}] {icon} {c.name:6s}  HP {c.hp:3d}  ATK {c.atk:2d}")
                    while True:
                        try:
                            recruit = int(input(f"  영입 (1-{n_choices}): ")) - 1
                            if 0 <= recruit < n_choices:
                                break
                        except (ValueError, EOFError):
                            pass
                    # 방출할 유닛 선택
                    print(f"\n  {C.BOLD}방출할 유닛 선택:{C.RESET}")
                    for i, u in enumerate(team):
                        uicon = ARCHETYPE_ICON.get(u.name, '?')
                        status = f"HP {u.hp}" if u.is_alive() else "💀"
                        print(f"    [{i + 1}] {uicon} {u.name:6s}  {status}  ATK {u.atk}")
                    while True:
                        try:
                            release = int(input(f"  방출 (1-{len(team)}): ")) - 1
                            if 0 <= release < len(team):
                                break
                        except (ValueError, EOFError):
                            pass
                    released = team[release]
                    ricon = ARCHETYPE_ICON.get(released.name, '?')
                    team.pop(release)
                    team_max_hps.pop(release)
                    chosen = choices[recruit]
                    team.append(chosen)
                    team_max_hps.append(chosen.hp)
                    nicon = ARCHETYPE_ICON.get(chosen.name, '?')
                    print(f"\n  {ricon} {released.name} 방출 → {nicon} {chosen.name} 영입!")
                    break
                pick = int(raw) - 1
                if 0 <= pick < n_choices:
                    chosen = choices[pick]
                    team.append(chosen)
                    team_max_hps.append(chosen.hp)
                    break
            except (ValueError, EOFError):
                pass
            print(f"  1~{n_choices} 중 하나를 입력하세요.")
        if not (can_swap and raw.lower() == 's'):
            icon = ARCHETYPE_ICON.get(chosen.name, '?')
            print(f"\n  → {icon} {chosen.name} 영입!")

        # 적 생성 — game.py와 동일한 공식
        n_enemies = enemies_per_round[round_num - 1]
        ep = enemy_power[round_num - 1]
        if just_revived:
            ep *= 0.85  # 부활 직후: 적 15% 약화
            just_revived = False
            print(f"  {C.CYAN}부활 효과: 적이 약해졌다!{C.RESET}")
        enemies = [make_random_unit(tier=round_num, stat_mult=ep)
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

        # 전투 전망
        my_power = my_total_atk * 2 + my_total_hp
        en_power = en_total_atk * 2 + en_total_hp
        ratio = my_power / en_power if en_power > 0 else 1
        if ratio > 1.3:
            outlook = f"{C.GREEN}압도적 우세 — 편하게 이길 수 있다{C.RESET}"
        elif ratio > 1.1:
            outlook = f"{C.GREEN}약간 유리 — 무난한 승리 예상{C.RESET}"
        elif ratio > 0.9:
            outlook = f"{C.YELLOW}호각 — 승패를 알 수 없다!{C.RESET}"
        elif ratio > 0.7:
            outlook = f"{C.RED}열세 — 행운이 필요하다{C.RESET}"
        else:
            outlook = f"{C.RED}큰 위기 — 기적을 바라자...{C.RESET}"
        print(f"  {C.DIM}전망:{C.RESET} {outlook}")

        # 시너지 버프 미리보기
        from collections import Counter
        my_counts = Counter(u.name for u in team if u.is_alive())
        active_syn = [(n, c) for n, c in my_counts.items() if c >= 2]
        if active_syn:
            syn_parts = []
            for n, c in active_syn:
                pct = 20 if c == 2 else 35 if c == 3 else 55
                icon = ARCHETYPE_ICON.get(n, '?')
                syn_parts.append(f"{icon}{n}x{c}(+{pct}%)")
            print(f"  {C.YELLOW}⚡ 시너지 발동: {', '.join(syn_parts)}{C.RESET}")

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

        # 전투 실황 중계 — HP 타임라인 + 하이라이트
        import time
        print()
        a_hp_pct = f"{log.a_hp_remaining:.0%}"
        b_hp_pct = f"{log.b_hp_remaining:.0%}"

        # HP 타임라인 미니 그래프 (5턴 간격 샘플링)
        if log.hp_timeline and len(log.hp_timeline) > 2:
            print(f"  {C.BOLD}── 전투 실황 ──{C.RESET}")
            step = max(1, len(log.hp_timeline) // 6)
            samples = log.hp_timeline[::step][:6]
            for i, (ar, br) in enumerate(samples):
                turn_num = i * step + 1
                a_bar = "█" * round(ar * 10) + "░" * (10 - round(ar * 10))
                b_bar = "█" * round(br * 10) + "░" * (10 - round(br * 10))
                a_c = C.GREEN if ar >= br else C.RED
                b_c = C.RED if ar >= br else C.GREEN
                leader = "◀" if ar > br else "▶" if br > ar else "="
                print(f"    T{turn_num:2d}  {a_c}{a_bar}{C.RESET} {leader} {b_c}{b_bar}{C.RESET}")
                time.sleep(0.15)
            print()

        if log.highlights:
            for h in log.highlights:
                icon = "💥" if "크리티컬" in h else "👻" if "회피" in h else "🔥" if "부활" in h else "💀" if "처치" in h else "⚔️" if "역전" in h else "⚡"
                print(f"    {icon} {h}")
                time.sleep(0.2)
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
            # 패배 분석 — 다중 원인 진단
            from collections import Counter
            loss_reasons = []
            alive_enemies = [e for e in enemies if e.hp > 0]
            if alive_enemies:
                strongest = max(alive_enemies, key=lambda e: e.atk)
                eicon = ARCHETYPE_ICON.get(strongest.name, '?')
                loss_reasons.append(f"{eicon}{strongest.name}(ATK {strongest.atk})이 너무 강했다")
            if len(team) < n_enemies:
                loss_reasons.append(f"수적 열세 ({len(team)} vs {n_enemies})")
            loss_counts = Counter(u.name for u in team)
            if all(c < 2 for c in loss_counts.values()):
                loss_reasons.append("시너지 없음 — 같은 종족을 모아보세요")
            my_atk = sum(u.atk for u in team)
            en_hp = sum(e.hp for e in enemies)
            if my_atk * 3 < en_hp:
                loss_reasons.append("화력 부족 — ATK 높은 유닛이 필요")
            if log.turns <= 5:
                loss_reasons.append("너무 빨리 전멸 — 탱커(blob)가 필요할 수도")
            if loss_reasons:
                print(f"  {C.DIM}패인 분석:{C.RESET}")
                for reason in loss_reasons[:3]:
                    print(f"    {C.DIM}• {reason}{C.RESET}")
            lives -= 1
            if lives > 0:
                just_revived = True
                print(f"  {C.YELLOW}✘ 패배... 하지만 아직 목숨 {lives}개 남음!{C.RESET}")
                print("  (전원 HP 50%로 부활 + 다음 라운드 적 -15% 약화)")
                for i, u in enumerate(team):
                    max_hp = 25 + round_num * 5 + 5
                    u.hp = max(1, round(max_hp * 0.5))
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
            import time
            print()
            for ch in f"  ─── GAME OVER ───":
                print(f"{C.RED}{C.BOLD}{ch}{C.RESET}", end='', flush=True)
                time.sleep(0.04)
            print()
            if round_num >= 7:
                print(f"  {C.YELLOW}R{round_num}까지 도달 — 거의 다 왔었다!{C.RESET}")
            elif round_num >= 4:
                print(f"  {C.CYAN}중반까지 도달. 시너지를 노려보세요!{C.RESET}")
            else:
                print(f"  {C.DIM}초반 탈락. HP 높은 유닛으로 버텨보세요!{C.RESET}")
            _show_game_summary(team, team_max_hps, all_battles, round_num - 1, n_rounds, 0)
            retry = input("\n  다시 도전? (y/n): ").strip().lower()
            if retry == 'y':
                interactive_play()
            return

        if round_num < n_rounds:
            input("\n  [Enter] 다음 라운드...")

    print()
    import time
    for ch in "  ★★★ 전 라운드 클리어! ★★★":
        print(f"{C.YELLOW}{C.BOLD}{ch}{C.RESET}", end='', flush=True)
        time.sleep(0.05)
    print()
    if lives == max_lives:
        print(f"  {C.GREEN}무패 클리어! 완벽합니다!{C.RESET}")
    elif lives == max_lives - 1:
        print(f"  {C.CYAN}아슬아슬한 클리어!{C.RESET}")
    _show_game_summary(team, team_max_hps, all_battles, n_rounds, n_rounds, lives)
    retry = input("\n  다시 도전? (y/n): ").strip().lower()
    if retry == 'y':
        interactive_play()


if __name__ == '__main__':
    interactive_play()
