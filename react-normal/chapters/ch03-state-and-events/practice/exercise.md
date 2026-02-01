# 챕터 03 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.jsx` 참조

---

## 문제 1: 좋아요 버튼 (난이도: ⭐)

### 설명
SNS 게시글의 좋아요 버튼을 구현하세요. 버튼을 클릭하면 좋아요 수가 증가하고, 다시 클릭하면 취소(감소)됩니다.

### 요구 사항
- `LikeButton` 컴포넌트를 만드세요
- 두 가지 상태를 관리하세요:
  - `isLiked` (불리언): 좋아요 여부
  - `likeCount` (숫자): 좋아요 수 (초기값: 42)
- 버튼 클릭 시:
  - `isLiked`가 `false`이면 -> `true`로 변경, `likeCount` +1
  - `isLiked`가 `true`이면 -> `false`로 변경, `likeCount` -1
- 좋아요 상태에 따라 버튼 스타일(색상)을 다르게 표시하세요
- 좋아요 수를 버튼 옆에 표시하세요

### 힌트
<details><summary>힌트 보기</summary>

- 두 상태를 동시에 업데이트: 하나의 핸들러에서 `setIsLiked`과 `setLikeCount`를 모두 호출
- 토글 패턴: `setIsLiked(prev => !prev)`
- 조건부 스타일: `backgroundColor: isLiked ? '#dc2626' : '#e5e7eb'`

</details>

---

## 문제 2: 색상 선택기 (난이도: ⭐⭐)

### 설명
사용자가 색상을 선택하면 배경색이 변경되는 색상 선택기를 만드세요.

### 요구 사항
- `ColorPicker` 컴포넌트를 만드세요
- 상태:
  - `selectedColor` (문자열): 현재 선택된 색상 (초기값: `"#ffffff"`)
  - `recentColors` (배열): 최근 선택한 색상 목록 (최대 5개)
- 색상 팔레트를 표시하세요 (최소 8가지 색상)
- 색상을 클릭하면:
  - `selectedColor`가 해당 색상으로 변경
  - `recentColors` 배열 앞에 추가 (이미 있으면 중복 제거 후 앞에 추가)
  - 배열 최대 길이가 5를 초과하면 가장 오래된 것 제거
- 미리보기 영역의 배경색을 `selectedColor`로 표시하세요
- 최근 사용한 색상 목록을 표시하세요
- "초기화" 버튼으로 흰색으로 되돌리세요

### 힌트
<details><summary>힌트 보기</summary>

- 중복 제거 후 앞에 추가: `[newColor, ...prev.filter(c => c !== newColor)]`
- 최대 길이 제한: `.slice(0, 5)`
- 배열 불변 업데이트를 사용하세요 (push 대신 spread)
- 색상 팔레트: `["#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6", "#8b5cf6", "#ec4899", "#6b7280"]`

</details>

---

## 문제 3: 텍스트 편집기 (난이도: ⭐⭐)

### 설명
실시간 미리보기가 가능한 간단한 텍스트 편집기를 만드세요.

### 요구 사항
- `TextEditor` 컴포넌트를 만드세요
- 상태:
  - `text` (문자열): 편집 중인 텍스트
  - `fontSize` (숫자): 글자 크기 (초기값: 16, 범위: 12~32)
  - `isBold` (불리언): 굵게 여부
  - `isItalic` (불리언): 기울임 여부
  - `textColor` (문자열): 글자 색상
- `<textarea>`로 텍스트를 입력받으세요
- 글자 크기 조절: +/- 버튼으로 2px씩 증감 (최소 12, 최대 32)
- 굵게/기울임 토글 버튼을 만드세요
- 미리보기 영역에 현재 설정이 적용된 텍스트를 표시하세요
- 글자 수와 단어 수를 실시간으로 표시하세요

### 힌트
<details><summary>힌트 보기</summary>

- 글자 크기 제한: `setFontSize(prev => Math.min(32, prev + 2))`
- 단어 수 계산: `text.trim().split(/\s+/).filter(Boolean).length`
- 스타일 적용: `fontWeight: isBold ? 'bold' : 'normal'`
- 여러 상태를 하나의 객체로 관리해도 되고, 각각 별도의 useState로 관리해도 됩니다

</details>

---

## 문제 4: 장바구니 (난이도: ⭐⭐⭐)

### 설명
상품을 추가/제거하고 수량을 조절할 수 있는 간단한 장바구니를 구현하세요.

### 요구 사항
- `ShoppingCart` 컴포넌트를 만드세요
- 상품 목록 (하드코딩):
  ```jsx
  const products = [
    { id: 1, name: "노트북", price: 1200000 },
    { id: 2, name: "마우스", price: 35000 },
    { id: 3, name: "키보드", price: 89000 },
    { id: 4, name: "모니터", price: 450000 },
  ];
  ```
- 상태: `cartItems` (배열): 장바구니 항목 `[{ id, name, price, quantity }]`
- 기능:
  - "담기" 버튼: 장바구니에 추가 (이미 있으면 수량 +1)
  - "+" / "-" 버튼: 수량 증감 (최소 1)
  - "삭제" 버튼: 장바구니에서 제거
- 장바구니 총 금액을 계산하여 표시하세요
- 가격은 `toLocaleString()`으로 포맷팅하세요
- 장바구니가 비었을 때 "장바구니가 비어있습니다" 메시지를 표시하세요

### 힌트
<details><summary>힌트 보기</summary>

- 이미 담긴 상품 확인: `cartItems.find(item => item.id === product.id)`
- 수량 업데이트: `map`으로 해당 항목만 수정
- 총 금액: `cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0)`
- 수량이 1일 때 -를 누르면 삭제할지, 1 미만으로 안 내려가게 할지 선택하세요

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요.
> 상태 업데이트 시 불변성을 꼭 지키세요. 배열의 push/splice 대신 spread, map, filter를 사용합니다.
