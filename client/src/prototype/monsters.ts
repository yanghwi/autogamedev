/**
 * Midnight Bestiary — 몬스터 데이터 (클라이언트 전용)
 * server/src/game/data/monsterRegistry.ts 에서 파생
 */

export type MonsterCategory = 'animal' | 'humanoid' | 'machine' | 'supernatural' | 'insect' | 'plant' | 'blob' | 'boss';

export interface MonsterDef {
  id: number;
  name: string;
  imageTag: string;
  desc: string;
  tier: 1 | 2 | 3 | 4 | 5;
  category: MonsterCategory;
  hp: number;
  atk: number;
  def: number;
}

// ===== 티어별 스탯 범위 (서버와 동일) =====
const TIER_RANGES: Record<number, { hp: [number, number]; atk: [number, number]; def: [number, number] }> = {
  1: { hp: [35, 50], atk: [6, 9], def: [2, 4] },
  2: { hp: [55, 75], atk: [10, 15], def: [4, 6] },
  3: { hp: [75, 105], atk: [15, 20], def: [6, 9] },
  4: { hp: [105, 120], atk: [20, 23], def: [9, 11] },
  5: { hp: [130, 160], atk: [23, 28], def: [10, 14] },
};

function deriveStats(id: number, tier: number) {
  const r = TIER_RANGES[tier];
  return {
    hp: r.hp[0] + ((id * 13 + 7) % (r.hp[1] - r.hp[0] + 1)),
    atk: r.atk[0] + ((id * 7 + 3) % (r.atk[1] - r.atk[0] + 1)),
    def: r.def[0] + ((id * 3 + 1) % (r.def[1] - r.def[0] + 1)),
  };
}

type Def = [string, string, string, 1 | 2 | 3 | 4 | 5, MonsterCategory];

const DEFS: Def[] = [
  ['scruffy-dog', '누더기 떠돌이 개', '배고파 눈이 사나운 떠돌이 개.', 1, 'animal'],
  ['dark-crow', '불길한 까마귀', '노란 부리가 위협적으로 빛나는 검은 까마귀.', 1, 'animal'],
  ['jade-cobra', '비취 코브라', '똬리를 틀고 혀를 날름거리는 비취색 코브라.', 2, 'animal'],
  ['forest-mage', '숲의 마법사', '초록 로브의 수상한 마법사.', 2, 'humanoid'],
  ['horned-demon', '뿔 달린 악마', '보라색 뿔 달린 악마. 으르렁거린다.', 3, 'supernatural'],
  ['rocket-gremlin', '로켓 그렘린', '로켓에 탄 그렘린. 제어 불능.', 3, 'machine'],
  ['wild-donkey', '야생 당나귀', '뒷발질이 무시무시한 야생 당나귀.', 1, 'animal'],
  ['shadow-wisp', '그림자 정령', '어둠 속의 그림자 정령. 빨간 눈.', 1, 'supernatural'],
  ['sewer-mouse', '하수구 쥐', '하수구에서 기어 나온 초록 쥐.', 1, 'animal'],
  ['suited-gorilla', '정장 고릴라', '정장 입은 고릴라. 주먹을 불끈.', 3, 'humanoid'],
  ['poison-shroom', '독버섯', '빨간 점박이 독버섯. 포자를 뿜는다.', 1, 'plant'],
  ['angry-imp', '성난 임프', '작지만 엄청나게 화난 임프.', 1, 'humanoid'],
  ['violet-priest', '보라 사제', '보라 법복의 수상한 사제.', 2, 'humanoid'],
  ['crimson-showman', '진홍 쇼맨', '빨간 턱시도의 위험한 마술사.', 3, 'humanoid'],
  ['alley-punk', '골목 불량배', '시비를 걸고 싶어 안달인 불량배.', 1, 'humanoid'],
  ['tiny-sprout', '꼬마 새싹', '아주 작은 새싹. 뿌리가 날카롭다.', 1, 'plant'],
  ['silver-saucer', '은색 비행접시', '수상한 빛줄기를 쏘는 비행접시.', 2, 'machine'],
  ['great-treant', '거대 나무 정령', '살아 움직이는 거대한 나무.', 3, 'plant'],
  ['rabbit-archdemon', '토끼 대악마', '토끼 귀의 대악마. 강대한 마력.', 4, 'supernatural'],
  ['rabbit-sorcerer', '토끼 주술사', '보라색 토끼 주술사.', 3, 'supernatural'],
  ['cave-bear', '동굴곰', '동굴에서 나온 거대한 곰.', 3, 'animal'],
  ['tunnel-mole', '땅굴 두더지', '삽처럼 날카로운 앞발의 두더지.', 1, 'animal'],
  ['green-bat', '초록 박쥐', '초음파 공격의 초록빛 박쥐.', 1, 'animal'],
  ['birdcage-witch', '새장 마녀', '새장 모자의 마녀.', 3, 'humanoid'],
  ['neon-firefly', '네온 반딧불이', '눈부신 거대 반딧불이.', 1, 'insect'],
  ['trash-critter', '쓰레기통 괴물', '쓰레기통의 정체불명 생물.', 1, 'animal'],
  ['scarlet-naga', '진홍 나가', '인간의 얼굴에 뱀의 몸.', 3, 'supernatural'],
  ['horned-raider', '뿔투구 약탈자', '방패를 들고 돌진하는 약탈자.', 3, 'humanoid'],
  ['pumpkin-head', '호박 머리', '입에서 불빛이 새어 나오는 호박.', 2, 'supernatural'],
  ['shambling-zombie', '비틀 좀비', '느리지만 멈추지 않는 좀비.', 2, 'supernatural'],
  ['midnight-panther', '자정의 표범', '어둠과 하나가 된 검은 표범.', 2, 'animal'],
  ['pale-ghost', '창백한 유령', '둥둥 떠다니며 한기를 뿜는 유령.', 1, 'supernatural'],
  ['club-caveman', '곤봉 원시인', '뇌보다 근육이 먼저 움직이는 원시인.', 2, 'humanoid'],
  ['mountain-ram', '산양', '단단한 뿔로 돌진하는 산양.', 2, 'animal'],
  ['mad-duck', '성난 오리', '결코 만만하지 않은 성난 오리.', 1, 'animal'],
  ['violet-slime', '보라 슬라임', '닿으면 녹는 보라색 슬라임.', 1, 'blob'],
  ['swamp-frog', '늪지 개구리', '혀 공격이 번개처럼 빠른 개구리.', 1, 'animal'],
  ['tribal-warrior', '부족 전사', '근육과 경험이 남다른 전사.', 3, 'humanoid'],
  ['scale-fighter', '도마뱀 전사', '꼬리 공격의 직립 도마뱀.', 2, 'animal'],
  ['red-hopper', '빨간 토끼', '발차기가 무서운 빨간 토끼.', 1, 'animal'],
  ['iron-stag-beetle', '쇠갑충', '철갑 등껍질의 거대한 쇠갑충.', 4, 'insect'],
  ['cherry-pudding', '체리 푸딩', '달콤한 냄새에 속으면 안 되는 푸딩.', 1, 'blob'],
  ['flutter-moth', '나풀 나방', '비늘 가루가 독인 나방.', 1, 'insect'],
  ['hover-disc', '호버 디스크', '레이저 빔을 발사하는 원반.', 2, 'machine'],
  ['bloated-goblin', '배불뚝이 고블린', '의외로 민첩한 배불뚝이.', 2, 'supernatural'],
  ['toddling-mushroom', '아장 버섯', '포자 구름이 위험한 아장 버섯.', 2, 'plant'],
  ['pebble-fungus', '조약돌 균', '밟으면 터지는 돌 모양 균류.', 1, 'plant'],
  ['stampede-bison', '돌진 들소', '한번 달리면 멈출 수 없는 들소.', 3, 'animal'],
  ['gentle-bronto', '순한 공룡', '순해 보이지만 꼬리는 가차 없다.', 2, 'animal'],
  ['plump-caterpillar', '통통 애벌레', '독침이 숨겨진 통통 애벌레.', 1, 'insect'],
  ['dish-critter', '접시 괴물', '접시 위의 정체불명 생물.', 1, 'blob'],
  ['gray-wolf', '회색 늑대', '날카로운 이빨의 회색 늑대.', 2, 'animal'],
  ['tin-knight', '양철 기사', '작지만 검술이 수준급인 기사.', 2, 'humanoid'],
  ['bone-mask', '해골 가면', '눈구멍에서 빛이 나는 해골 가면.', 1, 'supernatural'],
  ['armored-hornet', '갑옷 말벌', '마비독 침의 갑옷 말벌.', 2, 'insect'],
  ['spindly-bot', '가느다란 로봇', '관절이 삐걱거리는 로봇.', 2, 'machine'],
  ['wriggling-worm', '꿈틀 벌레', '소름 돋는 꿈틀거리는 벌레.', 2, 'blob'],
  ['raging-fatty', '분노한 뚱보', '몸통 박치기가 위험한 뚱보.', 2, 'humanoid'],
  ['cursed-sign', '저주받은 표지판', '글씨가 스스로 바뀌는 표지판.', 1, 'machine'],
  ['trench-coat-man', '트렌치코트 남자', '주머니에 뭐가 들었을까.', 2, 'humanoid'],
  ['runaway-taxi', '폭주 택시', '손님 없이 미친 듯이 달리는 택시.', 2, 'machine'],
  ['guitar-lizard', '기타 도마뱀', '음파 공격이 주특기인 도마뱀.', 2, 'animal'],
  ['dark-eyeball', '어둠의 눈알', '모든 것을 꿰뚫어 보는 눈알.', 1, 'blob'],
  ['mad-rooster', '미친 수탉', '부리와 발톱이 흉기인 수탉.', 2, 'animal'],
  ['haunted-canvas', '빙의된 그림', '액자 속에서 뭔가 기어 나온다.', 2, 'supernatural'],
  ['melting-clock', '녹는 시계', '주변의 시간이 뒤틀리는 시계.', 3, 'supernatural'],
  ['rogue-hydrant', '폭주 소화전', '물을 뿜어대는 소화전.', 1, 'machine'],
  ['possessed-pump', '빙의된 주유기', '기름을 무기로 쓰는 주유기.', 2, 'machine'],
  ['retro-robot', '레트로 로봇', '구식이지만 힘은 건재한 로봇.', 2, 'machine'],
  ['ribbon-mouse', '리본 쥐', '귀여운 외모에 속으면 큰일.', 1, 'animal'],
  ['titan-beetle', '타이탄 딱정벌레', '강철보다 단단한 등껍질.', 4, 'insect'],
  ['venus-trap', '거대 파리지옥', '벌린 입이 위협적인 파리지옥.', 3, 'plant'],
  ['frost-bear', '얼음 곰', '입김이 모든 것을 얼리는 곰.', 3, 'animal'],
  ['dustball', '먼지 뭉치', '재채기를 유발하는 먼지 생물.', 1, 'blob'],
  ['dusk-bat', '황혼 박쥐', '주황빛 날개의 스산한 박쥐.', 1, 'animal'],
  ['sea-stallion', '해마 기사', '물줄기를 뿜는 해마 기사.', 2, 'animal'],
  ['psychic-snail', '사이키 달팽이', '환각 줄무늬의 달팽이.', 2, 'supernatural'],
  ['sinister-puppet', '섬뜩한 인형', '누가 줄을 당기는 걸까.', 3, 'supernatural'],
  ['ooze-phantom', '흘러내리는 유령', '잡으려 하면 빠져나가는 슬라임.', 2, 'blob'],
  ['patrol-drone', '순찰 드론', '레이더로 추적하는 드론.', 2, 'machine'],
  ['spider-mech', '거미 로봇', '여섯 다리의 위협적 거미 로봇.', 3, 'machine'],
  ['magma-snail', '용암 달팽이', '뜨겁게 달아오른 달팽이.', 2, 'supernatural'],
  ['gilded-automaton', '황금 자동인형', '화려하지만 치명적인 인형.', 4, 'machine'],
  ['corrupt-officer', '타락한 경관', '법을 악용하는 경관.', 3, 'humanoid'],
  ['shades-brawler', '선글라스 싸움꾼', '주먹에 자신 있는 싸움꾼.', 3, 'humanoid'],
  ['elder-mummy', '고대 미라', '붕대 사이로 저주가 스며든다.', 4, 'supernatural'],
  ['thorned-fiend', '가시 악마', '가까이 가면 찔리는 악마.', 3, 'supernatural'],
  ['floating-lips', '떠다니는 입술', '키스 공격의 거대한 입술.', 2, 'supernatural'],
  ['face-serpent', '인면사', '인간의 얼굴로 웃으며 다가온다.', 3, 'supernatural'],
  ['storm-cloud', '분노한 뇌운', '번개를 마구 내리치는 뇌운.', 3, 'supernatural'],
  ['plate-imp', '접시 임프', '접시를 무기로 던지는 임프.', 1, 'blob'],
  ['one-eyed-stalker', '외눈 추적자', '긴 다리로 끈질기게 쫓는 외눈.', 2, 'supernatural'],
  ['armored-orb', '장갑 구체', '구르면서 돌진하는 구체.', 3, 'machine'],
  ['crown-serpent', '왕관 뱀', '위엄 서린 줄무늬 왕관 뱀.', 3, 'animal'],
  ['kiss-blob', '키스 블롭', '납작하게 달라붙는 입술 블롭.', 1, 'blob'],
  ['giant-larva', '거대 유충', '화난 표정으로 돌진하는 유충.', 3, 'insect'],
  ['dusk-spider', '황혼 거미', '보라 독의 황혼 거미.', 3, 'insect'],
  ['crimson-ogre', '진홍 오우거', '압도적 근력의 진홍 거인.', 4, 'humanoid'],
  ['singing-cat', '노래하는 고양이', '음파로 정신을 혼란시키는 고양이.', 1, 'animal'],
  ['wisp-serpent', '유령 뱀', '반투명한 몸의 유령 뱀.', 2, 'supernatural'],
  ['golden-titan', '황금 거인', '압도적인 금빛 골렘.', 5, 'boss'],
  ['mud-toad', '진흙 두꺼비', '갑자기 솟아오르는 진흙 두꺼비.', 2, 'blob'],
  ['pincer-crab', '집게 게', '집게와 촉수를 휘두르는 게.', 3, 'animal'],
  ['mini-saucer', '소형 비행접시', '윙윙거리며 빔을 쏘는 소형.', 1, 'machine'],
  ['coral-pony', '산호 조랑말', '갈기가 해초 같은 조랑말.', 2, 'animal'],
  ['elder-oak', '고대 참나무', '뿌리로 대지를 뒤흔드는 참나무.', 4, 'plant'],
  ['emerald-knight', '에메랄드 기사', '창과 방패의 에메랄드 기사.', 4, 'humanoid'],
  ['arcane-wizard', '마도사', '지팡이에서 마력이 쏟아진다.', 3, 'humanoid'],
  ['pastel-unicorn', '파스텔 유니콘', '뿔에서 무지개빛 빔.', 2, 'animal'],
  ['coiled-wyrm', '또아리 와이번', '거대한 몸으로 길을 막는다.', 3, 'animal'],
  ['pumpkin-blob', '호박 블롭', '데굴데굴 굴러오는 주황 공.', 1, 'blob'],
  ['solar-face', '태양의 얼굴', '눈부신 빛으로 시야를 빼앗는다.', 3, 'supernatural'],
  ['bell-robot', '종 로봇', '종소리에 맞춰 공격하는 로봇.', 2, 'machine'],
  ['evil-eye', '사악한 눈', '응시만으로 저주를 거는 눈.', 1, 'supernatural'],
  ['jovial-dragon', '느긋한 드래곤', '웃고 있지만 브레스는 무자비.', 5, 'boss'],
  ['stone-face', '돌 얼굴', '표정 없는 눈의 소름 끼치는 돌.', 3, 'blob'],
  ['baby-rex', '아기 공룡', '이빨이 아직 날카로운 아기 공룡.', 2, 'animal'],
  ['phantom-skull', '유령 해골', '이를 딱딱 부딪치는 유령 해골.', 2, 'supernatural'],
  ['mad-professor', '미친 교수', '수상한 실험 도구의 교수.', 2, 'humanoid'],
  ['sinister-professor', '불길한 교수', '안경 뒤 위험한 눈빛.', 3, 'humanoid'],
  ['flame-wraith', '불꽃 원령', '닿으면 모든 것이 타오른다.', 3, 'supernatural'],
  ['wandering-sage', '방랑 현자', '지팡이가 심상치 않은 현자.', 2, 'humanoid'],
  ['twin-watchers', '쌍둥이 감시자', '동시에 두 방향을 본다.', 2, 'supernatural'],
  ['molecular-drone', '분자 드론', '불안정한 에너지의 드론.', 3, 'machine'],
  ['chomping-lips', '깨무는 입술', '이빨을 덜컥이는 공중 입술.', 2, 'blob'],
  ['volt-toad', '전기 두꺼비', '온몸에서 스파크가 튄다.', 3, 'animal'],
  ['dread-guardian', '공포의 수호자', '거대한 갑옷의 수호자.', 5, 'boss'],
  ['cyclops-lurker', '외눈 잠복자', '기묘한 프로포션의 외눈.', 3, 'supernatural'],
  ['wyrm-dragon', '긴 용', '동양풍 용의 위엄.', 4, 'animal'],
  ['blade-sphere', '칼날 구체', '회전하며 모든 것을 베는 구체.', 3, 'machine'],
  ['kraken-spawn', '크라켄의 자식', '촉수가 사방으로 뻗는다.', 4, 'animal'],
  ['shadow-wings', '그림자 날개', 'V자로 날카롭게 날아드는 날개.', 3, 'supernatural'],
  ['staff-phantom', '지팡이 유령', '지팡이를 쥔 채 떠다니는 유령.', 2, 'supernatural'],
  ['infernal-knight', '지옥 기사', '붉은 갑옷에서 열기가 뿜어진다.', 4, 'humanoid'],
];

// ===== 빌드 =====

export const ALL_MONSTERS: MonsterDef[] = DEFS.map((def, i) => {
  const id = i + 1;
  const [imageTag, name, desc, tier, category] = def;
  const stats = deriveStats(id, tier);
  return { id, imageTag, name, desc, tier, category, ...stats };
});

// ===== 인덱스 =====

export const MONSTERS_BY_TIER: Record<number, MonsterDef[]> = { 1: [], 2: [], 3: [], 4: [], 5: [] };
for (const m of ALL_MONSTERS) {
  MONSTERS_BY_TIER[m.tier].push(m);
}

// ===== 유틸 =====

export function pickRandom<T>(arr: T[], count: number): T[] {
  const shuffled = [...arr].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}

export function spriteUrl(imageTag: string): string {
  return `/sprites/${imageTag}.png`;
}

// ===== 카테고리 표시 =====

export const CATEGORY_INFO: Record<MonsterCategory, { label: string; color: string; emoji: string }> = {
  animal:       { label: '야수',   color: 'text-green-400',  emoji: '🐾' },
  humanoid:     { label: '인간형', color: 'text-blue-400',   emoji: '⚔️' },
  machine:      { label: '기계',   color: 'text-slate-300',  emoji: '⚙️' },
  supernatural: { label: '초자연', color: 'text-purple-400', emoji: '👁️' },
  insect:       { label: '곤충',   color: 'text-yellow-400', emoji: '🦗' },
  plant:        { label: '식물',   color: 'text-emerald-400',emoji: '🌿' },
  blob:         { label: '블롭',   color: 'text-pink-400',   emoji: '🫧' },
  boss:         { label: '보스',   color: 'text-gold',       emoji: '👑' },
};

// ===== 시너지 정의 =====

export interface SynergyBonus {
  label: string;
  atkMul: number;
  defMul: number;
  hpMul: number;
  healAfterBattle: number; // 0~1 비율
}

export const SYNERGY_THRESHOLDS: Record<MonsterCategory, { min2: SynergyBonus; min3: SynergyBonus }> = {
  animal:       {
    min2: { label: '야수의 이빨',  atkMul: 1.2, defMul: 1.0, hpMul: 1.0, healAfterBattle: 0 },
    min3: { label: '야수의 군단',  atkMul: 1.4, defMul: 1.0, hpMul: 1.0, healAfterBattle: 0 },
  },
  humanoid:     {
    min2: { label: '전열 방어',    atkMul: 1.0, defMul: 1.2, hpMul: 1.0, healAfterBattle: 0 },
    min3: { label: '철벽 진형',    atkMul: 1.0, defMul: 1.4, hpMul: 1.0, healAfterBattle: 0 },
  },
  supernatural: {
    min2: { label: '어둠의 축복',  atkMul: 1.0, defMul: 1.0, hpMul: 1.2, healAfterBattle: 0 },
    min3: { label: '심연의 가호',  atkMul: 1.0, defMul: 1.0, hpMul: 1.4, healAfterBattle: 0 },
  },
  machine:      {
    min2: { label: '기계 연동',    atkMul: 1.15, defMul: 1.15, hpMul: 1.0, healAfterBattle: 0 },
    min3: { label: '풀 어셈블리',  atkMul: 1.3, defMul: 1.3, hpMul: 1.0, healAfterBattle: 0 },
  },
  insect:       {
    min2: { label: '벌레떼 습격',  atkMul: 1.3, defMul: 1.0, hpMul: 0.9, healAfterBattle: 0 },
    min3: { label: '대군세 침공',  atkMul: 1.5, defMul: 1.0, hpMul: 0.8, healAfterBattle: 0 },
  },
  plant:        {
    min2: { label: '광합성',       atkMul: 1.0, defMul: 1.0, hpMul: 1.0, healAfterBattle: 0.15 },
    min3: { label: '숲의 은총',    atkMul: 1.0, defMul: 1.0, hpMul: 1.0, healAfterBattle: 0.3 },
  },
  blob:         {
    min2: { label: '점액 공명',    atkMul: 1.1, defMul: 1.1, hpMul: 1.1, healAfterBattle: 0 },
    min3: { label: '슬라임 융합',  atkMul: 1.25, defMul: 1.25, hpMul: 1.25, healAfterBattle: 0 },
  },
  boss:         {
    min2: { label: '지배자의 위엄',atkMul: 1.3, defMul: 1.3, hpMul: 1.3, healAfterBattle: 0 },
    min3: { label: '절대자의 군림',atkMul: 1.5, defMul: 1.5, hpMul: 1.5, healAfterBattle: 0 },
  },
};

export function calcSynergies(team: MonsterDef[]): { active: SynergyBonus[]; counts: Record<string, number> } {
  const counts: Record<string, number> = {};
  for (const m of team) {
    counts[m.category] = (counts[m.category] || 0) + 1;
  }
  const active: SynergyBonus[] = [];
  for (const [cat, count] of Object.entries(counts)) {
    const thresholds = SYNERGY_THRESHOLDS[cat as MonsterCategory];
    if (count >= 3) active.push(thresholds.min3);
    else if (count >= 2) active.push(thresholds.min2);
  }
  return { active, counts };
}

export function applySynergies(base: { atk: number; def: number; hp: number }, synergies: SynergyBonus[]) {
  let { atk, def, hp } = base;
  for (const s of synergies) {
    atk = Math.round(atk * s.atkMul);
    def = Math.round(def * s.defMul);
    hp = Math.round(hp * s.hpMul);
  }
  return { atk, def, hp };
}
