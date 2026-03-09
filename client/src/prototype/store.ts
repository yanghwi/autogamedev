/**
 * Midnight Bestiary — 게임 상태 관리 (Zustand)
 */
import { create } from 'zustand';
import {
  MonsterDef, MONSTERS_BY_TIER, pickRandom, calcSynergies, applySynergies,
  type MonsterCategory,
} from './monsters';

// ===== 배틀 유닛 =====

export interface BattleUnit {
  uid: string;
  base: MonsterDef;
  maxHp: number;
  hp: number;
  atk: number;
  def: number;
  alive: boolean;
}

// ===== 배틀 이벤트 (재생용) =====

export interface BattleEvent {
  type: 'attack' | 'kill' | 'battle_end';
  attackerUid?: string;
  defenderUid?: string;
  damage?: number;
  winner?: 'player' | 'enemy';
}

// ===== 웨이브 설정 =====

interface WaveConfig {
  tiers: number[];
  count: number;
  isBoss: boolean;
}

const WAVE_CONFIGS: WaveConfig[] = [
  { tiers: [1],    count: 1, isBoss: false },  // wave 1
  { tiers: [1],    count: 2, isBoss: false },  // wave 2
  { tiers: [1, 2], count: 2, isBoss: false },  // wave 3
  { tiers: [2],    count: 2, isBoss: false },  // wave 4
  { tiers: [3],    count: 1, isBoss: true  },  // wave 5 (mini-boss)
  { tiers: [2, 3], count: 3, isBoss: false },  // wave 6
  { tiers: [3],    count: 3, isBoss: false },  // wave 7
  { tiers: [3, 4], count: 3, isBoss: false },  // wave 8
  { tiers: [4],    count: 3, isBoss: false },  // wave 9
  { tiers: [5],    count: 1, isBoss: true  },  // wave 10 (final boss)
];

// ===== 드래프트 티어 매핑 =====

function getDraftTiers(wave: number): number[] {
  if (wave <= 2) return [1];
  if (wave <= 4) return [1, 2];
  if (wave <= 6) return [2, 3];
  if (wave <= 8) return [3, 4];
  return [4];
}

// ===== 게임 상태 =====

export type GamePhase = 'title' | 'draft' | 'battle_intro' | 'battling' | 'battle_result' | 'game_over' | 'victory';

interface GameState {
  phase: GamePhase;
  wave: number;           // 1-based
  team: MonsterDef[];     // 최대 4
  draftChoices: MonsterDef[];
  swapTarget: number | null; // 팀이 풀일 때 교체할 인덱스

  // 배틀
  playerUnits: BattleUnit[];
  enemyUnits: BattleUnit[];
  battleLog: BattleEvent[];
  currentEventIndex: number;
  battleWon: boolean;

  // 스코어
  totalKills: number;
  wavesCleared: number;

  // 액션
  startGame: () => void;
  selectDraft: (monsterId: number) => void;
  setSwapTarget: (index: number | null) => void;
  startBattle: () => void;
  advanceEvent: () => void;
  nextWave: () => void;
  restart: () => void;
}

let uidCounter = 0;
function makeUid() { return `u${++uidCounter}`; }

function createUnit(def: MonsterDef, synergies: ReturnType<typeof calcSynergies>['active'] = []): BattleUnit {
  const boosted = applySynergies({ atk: def.atk, def: def.def, hp: def.hp }, synergies);
  return {
    uid: makeUid(),
    base: def,
    maxHp: boosted.hp,
    hp: boosted.hp,
    atk: boosted.atk,
    def: boosted.def,
    alive: true,
  };
}

// ===== 배틀 시뮬레이션 =====

function simulateBattle(playerUnits: BattleUnit[], enemyUnits: BattleUnit[]): BattleEvent[] {
  const log: BattleEvent[] = [];
  const pUnits = playerUnits.map(u => ({ ...u }));
  const eUnits = enemyUnits.map(u => ({ ...u }));

  let turn = 0;
  const MAX_TURNS = 100;

  while (turn < MAX_TURNS) {
    const pAlive = pUnits.filter(u => u.alive);
    const eAlive = eUnits.filter(u => u.alive);
    if (pAlive.length === 0 || eAlive.length === 0) break;

    // 플레이어 턴
    const attacker = pAlive[turn % pAlive.length];
    const target = eAlive[0];
    const dmg = Math.max(1, attacker.atk - target.def);
    target.hp -= dmg;
    log.push({ type: 'attack', attackerUid: attacker.uid, defenderUid: target.uid, damage: dmg });
    if (target.hp <= 0) {
      target.alive = false;
      log.push({ type: 'kill', attackerUid: attacker.uid, defenderUid: target.uid });
    }

    // 적 생존 체크
    if (eUnits.filter(u => u.alive).length === 0) {
      log.push({ type: 'battle_end', winner: 'player' });
      return log;
    }

    // 적 턴
    const eAlive2 = eUnits.filter(u => u.alive);
    const eAttacker = eAlive2[turn % eAlive2.length];
    const pAlive2 = pUnits.filter(u => u.alive);
    const pTarget = pAlive2[0];
    const eDmg = Math.max(1, eAttacker.atk - pTarget.def);
    pTarget.hp -= eDmg;
    log.push({ type: 'attack', attackerUid: eAttacker.uid, defenderUid: pTarget.uid, damage: eDmg });
    if (pTarget.hp <= 0) {
      pTarget.alive = false;
      log.push({ type: 'kill', attackerUid: eAttacker.uid, defenderUid: pTarget.uid });
    }

    if (pUnits.filter(u => u.alive).length === 0) {
      log.push({ type: 'battle_end', winner: 'enemy' });
      return log;
    }

    turn++;
  }

  // 타임아웃 — 남은 HP 비율로 판정
  const pHpRatio = pUnits.filter(u => u.alive).reduce((s, u) => s + u.hp / u.maxHp, 0);
  const eHpRatio = eUnits.filter(u => u.alive).reduce((s, u) => s + u.hp / u.maxHp, 0);
  log.push({ type: 'battle_end', winner: pHpRatio >= eHpRatio ? 'player' : 'enemy' });
  return log;
}

// ===== 스토어 =====

export const useGameStore = create<GameState>((set, get) => ({
  phase: 'title',
  wave: 0,
  team: [],
  draftChoices: [],
  swapTarget: null,

  playerUnits: [],
  enemyUnits: [],
  battleLog: [],
  currentEventIndex: -1,
  battleWon: false,

  totalKills: 0,
  wavesCleared: 0,

  startGame: () => {
    uidCounter = 0;
    const tiers = getDraftTiers(1);
    const pool = tiers.flatMap(t => MONSTERS_BY_TIER[t] || []);
    const choices = pickRandom(pool, 3);
    set({
      phase: 'draft',
      wave: 1,
      team: [],
      draftChoices: choices,
      swapTarget: null,
      totalKills: 0,
      wavesCleared: 0,
    });
  },

  selectDraft: (monsterId: number) => {
    const { team, draftChoices, swapTarget } = get();
    const picked = draftChoices.find(m => m.id === monsterId);
    if (!picked) return;

    let newTeam: MonsterDef[];
    if (team.length < 4) {
      newTeam = [...team, picked];
    } else if (swapTarget !== null) {
      newTeam = [...team];
      newTeam[swapTarget] = picked;
    } else {
      return; // 팀 풀인데 교체 대상 미선택
    }

    set({ team: newTeam, phase: 'battle_intro', swapTarget: null });
  },

  setSwapTarget: (index: number | null) => {
    set({ swapTarget: index });
  },

  startBattle: () => {
    const { wave, team } = get();
    const config = WAVE_CONFIGS[wave - 1];
    if (!config) return;

    // 적 생성
    const pool = config.tiers.flatMap(t => MONSTERS_BY_TIER[t] || []);
    const enemies = config.isBoss
      ? pickRandom(pool, 1)
      : pickRandom(pool, config.count);

    // 시너지 적용
    const { active } = calcSynergies(team);
    const playerUnits = team.map(def => createUnit(def, active));
    const enemyUnits = enemies.map(def => createUnit(def));

    // 배틀 시뮬레이션
    const log = simulateBattle(playerUnits, enemyUnits);
    const lastEvent = log[log.length - 1];
    const battleWon = lastEvent?.winner === 'player';
    const kills = log.filter(e => e.type === 'kill' && playerUnits.some(u => u.uid === e.attackerUid)).length;

    // 유닛 HP 초기화 (리플레이용)
    playerUnits.forEach(u => { u.hp = u.maxHp; u.alive = true; });
    enemyUnits.forEach(u => { u.hp = u.maxHp; u.alive = true; });

    set({
      phase: 'battling',
      playerUnits,
      enemyUnits,
      battleLog: log,
      currentEventIndex: -1,
      battleWon,
      totalKills: get().totalKills + kills,
    });
  },

  advanceEvent: () => {
    const { battleLog, currentEventIndex, playerUnits, enemyUnits, battleWon, wave, wavesCleared } = get();
    const nextIdx = currentEventIndex + 1;
    if (nextIdx >= battleLog.length) {
      // 배틀 종료
      if (battleWon) {
        const isLastWave = wave >= WAVE_CONFIGS.length;
        set({
          phase: isLastWave ? 'victory' : 'battle_result',
          wavesCleared: wavesCleared + 1,
        });
      } else {
        set({ phase: 'game_over' });
      }
      return;
    }

    // 이벤트 적용
    const event = battleLog[nextIdx];
    const allUnits = [...playerUnits, ...enemyUnits];

    if (event.type === 'attack' && event.defenderUid && event.damage) {
      const defender = allUnits.find(u => u.uid === event.defenderUid);
      if (defender) {
        defender.hp = Math.max(0, defender.hp - event.damage);
      }
    }
    if (event.type === 'kill' && event.defenderUid) {
      const defender = allUnits.find(u => u.uid === event.defenderUid);
      if (defender) {
        defender.alive = false;
        defender.hp = 0;
      }
    }

    set({
      currentEventIndex: nextIdx,
      playerUnits: [...playerUnits],
      enemyUnits: [...enemyUnits],
    });
  },

  nextWave: () => {
    const { wave, team } = get();
    const nextWave = wave + 1;

    // 식물 시너지: 배틀 후 힐
    const { active } = calcSynergies(team);
    const healRatio = active.reduce((sum, s) => sum + s.healAfterBattle, 0);
    // (프로토타입에서는 HP가 매 배틀 리셋되므로 힐은 향후 구현)

    const tiers = getDraftTiers(nextWave);
    const pool = tiers.flatMap(t => MONSTERS_BY_TIER[t] || []);
    const choices = pickRandom(pool, 3);

    set({
      phase: 'draft',
      wave: nextWave,
      draftChoices: choices,
      swapTarget: null,
    });
  },

  restart: () => {
    get().startGame();
  },
}));
