# CLAUDE.md — Midnight Bestiary

AI 에이전트 자율 게임 개발 프로젝트. EarthBound 톤의 싱글플레이어 몬스터 드래프트 오토배틀러.

## 프로젝트 철학

Karpathy의 autoresearch에서 영감. 에이전트가 자율적으로 게임을 개발하되, 게임은 정량 평가가 어려우므로 **인간 데모 검증 루프**를 따른다:

```
구현 → 빌드 검증 → 인간에게 데모 시연 → 피드백 수렴 → 다음 이터레이션
```

- 무한 루프를 돌지 말 것. 의미 있는 단위로 끊어서 인간의 재미 판단을 받을 것.
- 변경 후 반드시 빌드 통과 확인: `npm run build --workspace=@midnight-bestiary/client`
- 한 번에 너무 많이 바꾸지 말 것. 작은 변경 → 검증 → 다음 변경.

## 보존해야 할 자산

- **287개 EarthBound 스타일 픽셀 스프라이트**: `client/public/sprites/*.png`
- **Mother/EarthBound 분위기**: 다크 보라 팔레트, 사이키델릭 배경, 레트로 폰트
- **디자인 토큰**: `tailwind.config.js`의 midnight/arcane/tier 색상 체계
- **CSS 유틸리티**: `index.css`의 eb-window, psychedelic-bg, scanlines, lobby-title

## 기술 스택

- **클라이언트 전용** (서버 없음): React 18 + Vite + Tailwind 3 + Zustand
- **플랫폼**: 아이폰 사파리 세로, 한 손 엄지, 10분 세션
- **빌드**: `npm run build --workspace=@midnight-bestiary/client`
- **개발**: `npm run dev` → http://localhost:5173

## 핵심 파일 구조

```
client/
  public/sprites/           ← 287개 PNG 스프라이트 (절대 삭제 금지)
  src/
    prototype/
      monsters.ts           ← 134개 몬스터 데이터 + 시너지 시스템
      store.ts              ← Zustand 게임 엔진 (드래프트/배틀/웨이브)
      App.tsx               ← 전체 UI (타이틀/드래프트/배틀/결과)
    index.css               ← 글로벌 스타일 + EarthBound UI 컴포넌트
    main.tsx                ← 엔트리포인트
  tailwind.config.js        ← 디자인 토큰 (midnight, arcane, tier 색상)
```

## 게임 핵심 루프

```
타이틀 → 드래프트(3택1) → 오토배틀 관전 → 승리 → 다음 드래프트 → ... → 10웨이브 클리어/패배
```

- **드래프트**: 매 웨이브 전, 3마리 중 1마리를 팀에 추가 (최대 4마리)
- **시너지**: 같은 카테고리 2마리+ 시 보너스 (animal=ATK, humanoid=DEF, supernatural=HP 등)
- **오토배틀**: 턴제 자동 전투, 600ms 간격으로 이벤트 재생
- **10웨이브**: 티어 1 → 5까지 점진적 난이도 상승, 웨이브 5/10은 보스

## 몬스터 데이터

- 134마리, 8 카테고리 (animal, humanoid, machine, supernatural, insect, plant, blob, boss)
- 5 티어 (스탯 범위가 다름), ID 기반 결정론적 스탯 파생
- 시너지 보너스: min2(2마리 이상), min3(3마리 이상)

## 반드시 지킬 것

- **하드코딩 색상 금지**: Tailwind 클래스만 사용
- **스프라이트 경로**: `/sprites/{imageTag}.png` (spriteUrl 함수 사용)
- **빌드 깨지면 즉시 수정**: tsc + vite build 모두 통과해야 함
- **변경 후 데모 가능 상태 유지**: 항상 플레이 가능한 상태를 유지할 것

## 하지 말 것

- **`npm run build` (루트)** 실행 금지 → workspace 지정 필수
- **서버 코드 추가 금지** (현재 클라이언트 전용 아키텍처)
- **스프라이트 파일 삭제/이동 금지**
- **인간 검증 없이 핵심 게임 루프 변경 금지**

## 다음 이터레이션 후보 (인간 피드백 후 결정)

- 드래프트 선택의 깊이 (시너지 미리보기, 교체 UX 개선)
- 오토배틀 연출 강화 (이펙트, 사운드, 카메라 흔들림)
- 진행 영속성 (localStorage 최고 기록)
- 메타 진행 (런 간 해금 시스템)
- 밸런스 조정 (웨이브/티어/시너지 수치)
