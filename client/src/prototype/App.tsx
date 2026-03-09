/**
 * Midnight Bestiary — 프로토타입 UI
 * 드래프트 → 오토배틀 → 드래프트 루프
 */
import { useEffect, useRef, useState } from 'react';
import { useGameStore, type BattleUnit, type BattleEvent } from './store';
import {
  type MonsterDef, spriteUrl, CATEGORY_INFO, calcSynergies,
  type MonsterCategory,
} from './monsters';

// ===== 티어 색상 =====
const TIER_BORDER: Record<number, string> = {
  1: 'border-slate-500',
  2: 'border-green-500',
  3: 'border-blue-500',
  4: 'border-purple-500',
  5: 'border-gold',
};
const TIER_GLOW: Record<number, string> = {
  1: '',
  2: 'shadow-[0_0_8px_rgba(34,197,94,0.3)]',
  3: 'shadow-[0_0_8px_rgba(59,130,246,0.4)]',
  4: 'shadow-[0_0_12px_rgba(168,85,247,0.5)]',
  5: 'shadow-[0_0_16px_rgba(251,191,36,0.6)]',
};
const TIER_LABEL: Record<number, string> = { 1: '★', 2: '★★', 3: '★★★', 4: '★★★★', 5: '★★★★★' };

// ===== 타이틀 화면 =====
function TitleScreen() {
  const startGame = useGameStore(s => s.startGame);

  return (
    <div className="flex-1 flex flex-col items-center justify-center relative overflow-hidden">
      {/* 사이키델릭 배경 */}
      <div className="psychedelic-bg" />
      <div className="checker-overlay" />

      {/* 별 */}
      {Array.from({ length: 20 }).map((_, i) => (
        <div
          key={i}
          className="lobby-star"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 2}s`,
          }}
        />
      ))}

      <div className="relative z-10 text-center px-6">
        <h1 className="font-title text-2xl xs:text-3xl lobby-title mb-4 leading-relaxed">
          MIDNIGHT<br />BESTIARY
        </h1>
        <p className="lobby-subtitle text-arcane-light font-body text-sm mb-2">
          자정의 도감
        </p>
        <p className="text-slate-400 text-xs mb-12 font-body">
          몬스터를 모아 전투하라
        </p>

        <button
          onClick={startGame}
          className="eb-window px-8 py-4 text-gold font-body text-base
                     active:scale-95 transition-transform"
        >
          ▶ 게임 시작
        </button>
      </div>

      <div className="scanlines" />
    </div>
  );
}

// ===== 몬스터 카드 =====
function MonsterCard({
  monster, onClick, selected, compact, showSwap, onSwap,
}: {
  monster: MonsterDef;
  onClick?: () => void;
  selected?: boolean;
  compact?: boolean;
  showSwap?: boolean;
  onSwap?: () => void;
}) {
  const cat = CATEGORY_INFO[monster.category];

  if (compact) {
    return (
      <div
        className={`relative flex flex-col items-center p-1.5 rounded border-2 ${TIER_BORDER[monster.tier]}
                     ${selected ? 'bg-arcane/30 ring-2 ring-gold' : 'bg-midnight-700'}
                     ${showSwap ? 'cursor-pointer' : ''}`}
        onClick={onSwap}
      >
        <img
          src={spriteUrl(monster.imageTag)}
          alt={monster.name}
          className="w-10 h-10 object-contain image-rendering-pixelated"
          style={{ imageRendering: 'pixelated' }}
        />
        <span className="text-[10px] text-slate-300 mt-0.5 truncate w-full text-center">{monster.name}</span>
        {showSwap && selected && (
          <div className="absolute inset-0 bg-red-500/30 rounded flex items-center justify-center">
            <span className="text-[10px] text-white font-bold">교체</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <button
      onClick={onClick}
      className={`flex flex-col items-center p-3 rounded-lg border-2
                   ${TIER_BORDER[monster.tier]} ${TIER_GLOW[monster.tier]}
                   bg-midnight-700 hover:bg-midnight-600 active:scale-95
                   transition-all w-full`}
    >
      {/* 티어 */}
      <div className="text-[10px] text-gold mb-1">{TIER_LABEL[monster.tier]}</div>

      {/* 스프라이트 */}
      <img
        src={spriteUrl(monster.imageTag)}
        alt={monster.name}
        className="w-16 h-16 object-contain mb-2"
        style={{ imageRendering: 'pixelated' }}
      />

      {/* 이름 */}
      <div className="text-sm font-bold text-white mb-1">{monster.name}</div>

      {/* 카테고리 */}
      <div className={`text-[10px] ${cat.color} mb-2`}>
        {cat.emoji} {cat.label}
      </div>

      {/* 스탯 */}
      <div className="flex gap-2 text-[11px]">
        <span className="text-red-400">⚔{monster.atk}</span>
        <span className="text-blue-400">🛡{monster.def}</span>
        <span className="text-green-400">♥{monster.hp}</span>
      </div>

      {/* 설명 */}
      <p className="text-[10px] text-slate-400 mt-2 line-clamp-2">{monster.desc}</p>
    </button>
  );
}

// ===== 시너지 표시 =====
function SynergyDisplay({ team }: { team: MonsterDef[] }) {
  const { active, counts } = calcSynergies(team);

  if (active.length === 0 && Object.keys(counts).length === 0) {
    return <div className="text-xs text-slate-500 text-center">팀을 구성하면 시너지가 활성화됩니다</div>;
  }

  return (
    <div className="flex flex-wrap gap-1.5 justify-center">
      {Object.entries(counts).map(([cat, count]) => {
        const info = CATEGORY_INFO[cat as MonsterCategory];
        const isActive = count >= 2;
        return (
          <div
            key={cat}
            className={`flex items-center gap-1 px-2 py-0.5 rounded text-[11px]
                         ${isActive ? 'bg-arcane/30 border border-arcane-light/50' : 'bg-midnight-700 border border-midnight-600'}`}
          >
            <span>{info.emoji}</span>
            <span className={isActive ? info.color : 'text-slate-500'}>{info.label}</span>
            <span className={isActive ? 'text-gold font-bold' : 'text-slate-500'}>{count}</span>
          </div>
        );
      })}
      {active.map((s, i) => (
        <div key={i} className="text-[10px] text-gold px-2 py-0.5 bg-gold/10 rounded border border-gold/30">
          {s.label}
        </div>
      ))}
    </div>
  );
}

// ===== 드래프트 화면 =====
function DraftScreen() {
  const { wave, team, draftChoices, swapTarget, selectDraft, setSwapTarget } = useGameStore();
  const teamFull = team.length >= 4;

  return (
    <div className="flex-1 flex flex-col p-4 pb-safe">
      {/* 웨이브 표시 */}
      <div className="text-center mb-3">
        <span className="text-gold font-body text-sm">WAVE {wave}/10</span>
        <h2 className="text-white font-bold text-lg mt-1">몬스터를 선택하세요</h2>
        {teamFull && (
          <p className="text-xs text-arcane-light mt-1">팀이 가득 찼습니다. 교체할 몬스터를 먼저 선택하세요.</p>
        )}
      </div>

      {/* 팀 현황 */}
      <div className="mb-3">
        <div className="flex gap-2 justify-center mb-2">
          {team.map((m, i) => (
            <MonsterCard
              key={m.id}
              monster={m}
              compact
              showSwap={teamFull}
              selected={swapTarget === i}
              onSwap={() => setSwapTarget(swapTarget === i ? null : i)}
            />
          ))}
          {Array.from({ length: 4 - team.length }).map((_, i) => (
            <div key={`empty-${i}`} className="w-14 h-16 rounded border-2 border-dashed border-midnight-600 flex items-center justify-center">
              <span className="text-midnight-600 text-lg">?</span>
            </div>
          ))}
        </div>
        <SynergyDisplay team={team} />
      </div>

      {/* 드래프트 선택지 */}
      <div className="flex-1 flex gap-2 items-start">
        {draftChoices.map(m => (
          <div key={m.id} className="flex-1">
            <MonsterCard
              monster={m}
              onClick={() => {
                if (!teamFull || swapTarget !== null) selectDraft(m.id);
              }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

// ===== 배틀 인트로 =====
function BattleIntro() {
  const { wave, startBattle } = useGameStore();
  const isBonus = wave === 5 || wave === 10;

  useEffect(() => {
    const timer = setTimeout(startBattle, 1500);
    return () => clearTimeout(timer);
  }, [startBattle]);

  return (
    <div className="flex-1 flex flex-col items-center justify-center">
      <div className={`font-title text-xl ${isBonus ? 'text-gold animate-pulse-glow' : 'text-white'} animate-fade-in`}>
        {isBonus ? '⚠ BOSS WAVE ⚠' : `WAVE ${wave}`}
      </div>
      <div className="text-arcane-light font-body text-sm mt-2 animate-fade-in">
        전투 준비...
      </div>
    </div>
  );
}

// ===== 배틀 유닛 표시 =====
function UnitSprite({
  unit, isAttacking, isDefending, damage, isPlayer,
}: {
  unit: BattleUnit;
  isAttacking: boolean;
  isDefending: boolean;
  damage: number | null;
  isPlayer: boolean;
}) {
  const hpPercent = Math.max(0, (unit.hp / unit.maxHp) * 100);
  const hpColor = hpPercent > 50 ? 'bg-green-500' : hpPercent > 25 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div
      className={`flex flex-col items-center transition-all duration-200 relative
                   ${!unit.alive ? 'opacity-20 scale-75' : ''}
                   ${isAttacking ? (isPlayer ? 'translate-x-3' : '-translate-x-3') : ''}
                   ${isDefending ? 'animate-shake' : ''}`}
    >
      {/* 데미지 숫자 */}
      {damage !== null && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2 text-red-400 font-bold text-sm animate-slide-up z-10">
          -{damage}
        </div>
      )}

      {/* 스프라이트 */}
      <img
        src={spriteUrl(unit.base.imageTag)}
        alt={unit.base.name}
        className={`w-12 h-12 object-contain ${!isPlayer ? '-scale-x-100' : ''}`}
        style={{ imageRendering: 'pixelated' }}
      />

      {/* 이름 */}
      <div className="text-[9px] text-slate-300 mt-0.5 truncate max-w-[56px] text-center">
        {unit.base.name}
      </div>

      {/* HP바 */}
      <div className="w-12 h-1.5 bg-midnight-900 rounded-full mt-0.5 overflow-hidden">
        <div
          className={`h-full ${hpColor} transition-all duration-300`}
          style={{ width: `${hpPercent}%` }}
        />
      </div>
      <div className="text-[8px] text-slate-500">{Math.max(0, unit.hp)}/{unit.maxHp}</div>
    </div>
  );
}

// ===== 배틀 화면 =====
function BattleScreen() {
  const {
    wave, playerUnits, enemyUnits, battleLog, currentEventIndex,
    advanceEvent, battleWon,
  } = useGameStore();

  const [attackingUid, setAttackingUid] = useState<string | null>(null);
  const [defendingUid, setDefendingUid] = useState<string | null>(null);
  const [damageMap, setDamageMap] = useState<Record<string, number>>({});
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // 자동 재생
  useEffect(() => {
    timerRef.current = setInterval(() => {
      const state = useGameStore.getState();
      const nextIdx = state.currentEventIndex + 1;

      if (nextIdx >= state.battleLog.length) {
        if (timerRef.current) clearInterval(timerRef.current);
        // 약간의 딜레이 후 결과 화면으로
        setTimeout(() => advanceEvent(), 500);
        return;
      }

      const event = state.battleLog[nextIdx];

      // 애니메이션 표시
      if (event.type === 'attack') {
        setAttackingUid(event.attackerUid || null);
        setDefendingUid(event.defenderUid || null);
        if (event.defenderUid && event.damage) {
          setDamageMap(prev => ({ ...prev, [event.defenderUid!]: event.damage! }));
          setTimeout(() => {
            setDamageMap(prev => {
              const next = { ...prev };
              delete next[event.defenderUid!];
              return next;
            });
          }, 400);
        }
        setTimeout(() => {
          setAttackingUid(null);
          setDefendingUid(null);
        }, 300);
      }

      advanceEvent();
    }, 600);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [advanceEvent]);

  return (
    <div className="flex-1 flex flex-col p-4">
      {/* 웨이브 표시 */}
      <div className="text-center mb-4">
        <span className="text-gold font-body text-sm">WAVE {wave}/10</span>
      </div>

      {/* 배틀필드 */}
      <div className="flex-1 flex items-center justify-center gap-6">
        {/* 아군 */}
        <div className="flex flex-col gap-3 items-center">
          <div className="text-[10px] text-arcane-light font-bold mb-1">아군</div>
          {playerUnits.map(u => (
            <UnitSprite
              key={u.uid}
              unit={u}
              isPlayer
              isAttacking={attackingUid === u.uid}
              isDefending={defendingUid === u.uid}
              damage={damageMap[u.uid] ?? null}
            />
          ))}
        </div>

        {/* VS */}
        <div className="text-gold font-title text-lg">VS</div>

        {/* 적군 */}
        <div className="flex flex-col gap-3 items-center">
          <div className="text-[10px] text-red-400 font-bold mb-1">적군</div>
          {enemyUnits.map(u => (
            <UnitSprite
              key={u.uid}
              unit={u}
              isPlayer={false}
              isAttacking={attackingUid === u.uid}
              isDefending={defendingUid === u.uid}
              damage={damageMap[u.uid] ?? null}
            />
          ))}
        </div>
      </div>

      {/* 배틀 로그 (최근 이벤트) */}
      <div className="h-12 flex items-center justify-center">
        {currentEventIndex >= 0 && currentEventIndex < battleLog.length && (
          <BattleLogLine
            event={battleLog[currentEventIndex]}
            allUnits={[...playerUnits, ...enemyUnits]}
          />
        )}
      </div>
    </div>
  );
}

function BattleLogLine({ event, allUnits }: { event: BattleEvent; allUnits: BattleUnit[] }) {
  const getName = (uid?: string) => allUnits.find(u => u.uid === uid)?.base.name || '???';

  if (event.type === 'attack') {
    return (
      <div className="text-xs text-slate-300 animate-fade-in">
        <span className="text-white">{getName(event.attackerUid)}</span>
        {' → '}
        <span className="text-red-400">-{event.damage}</span>
        {' → '}
        <span className="text-white">{getName(event.defenderUid)}</span>
      </div>
    );
  }
  if (event.type === 'kill') {
    return (
      <div className="text-xs text-red-500 animate-fade-in font-bold">
        {getName(event.defenderUid)} 쓰러졌다!
      </div>
    );
  }
  return null;
}

// ===== 배틀 결과 =====
function BattleResult() {
  const { wave, wavesCleared, nextWave } = useGameStore();

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6">
      <div className="text-green-400 font-title text-xl mb-2 animate-fade-in">VICTORY!</div>
      <div className="text-slate-300 font-body text-sm mb-6">Wave {wave} 클리어</div>

      <button
        onClick={nextWave}
        className="eb-window px-8 py-4 text-gold font-body text-base active:scale-95 transition-transform"
      >
        ▶ 다음 웨이브
      </button>
    </div>
  );
}

// ===== 게임 오버 =====
function GameOverScreen() {
  const { wavesCleared, totalKills, restart } = useGameStore();

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6">
      <div className="text-red-500 font-title text-xl mb-2 animate-fade-in">DEFEATED</div>
      <div className="eb-window mb-6 text-center">
        <div className="text-sm text-slate-300 mb-2">클리어한 웨이브: <span className="text-gold font-bold">{wavesCleared}</span></div>
        <div className="text-sm text-slate-300">처치한 적: <span className="text-gold font-bold">{totalKills}</span></div>
      </div>

      <button
        onClick={restart}
        className="eb-window px-8 py-4 text-gold font-body text-base active:scale-95 transition-transform"
      >
        ▶ 다시 도전
      </button>
    </div>
  );
}

// ===== 승리 화면 =====
function VictoryScreen() {
  const { totalKills, restart } = useGameStore();

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 relative overflow-hidden">
      <div className="psychedelic-bg" />
      <div className="relative z-10 text-center">
        <div className="text-gold font-title text-2xl mb-4 lobby-title animate-fade-in">COMPLETE!</div>
        <div className="eb-window mb-6">
          <div className="text-sm text-slate-300 mb-1">10 웨이브 클리어!</div>
          <div className="text-sm text-slate-300">총 처치: <span className="text-gold font-bold">{totalKills}</span></div>
        </div>

        <button
          onClick={restart}
          className="eb-window px-8 py-4 text-gold font-body text-base active:scale-95 transition-transform"
        >
          ▶ 다시 플레이
        </button>
      </div>
      <div className="scanlines" />
    </div>
  );
}

// ===== 메인 앱 =====
export default function MidnightBestiary() {
  const phase = useGameStore(s => s.phase);

  return (
    <div className="min-h-dvh bg-midnight-900 flex flex-col">
      {phase === 'title' && <TitleScreen />}
      {phase === 'draft' && <DraftScreen />}
      {phase === 'battle_intro' && <BattleIntro />}
      {phase === 'battling' && <BattleScreen />}
      {phase === 'battle_result' && <BattleResult />}
      {phase === 'game_over' && <GameOverScreen />}
      {phase === 'victory' && <VictoryScreen />}
    </div>
  );
}
