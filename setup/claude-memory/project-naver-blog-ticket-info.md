---
name: project-naver-blog-ticket-info
description: "네이버 블로그 ticket_info 운영 프로젝트의 구조, 실제 카테고리, 글 제작 워크플로"
metadata:
  node_type: memory
  type: project
  originSessionId: 2f0292fe-ba9d-4342-9f37-3d0cca2906ee
  modified: 2026-10-23T18:28:17.466Z
---

사용자는 네이버 블로그 `ticket_info`(blog.naver.com/ticket_info)를 운영한다. 캐릭터 티코(TICO, 헤드셋 쓴 독수리), 메인 블루 #2E6BFF, 포인트 옐로 #FFD54F. 이미지 자산은 ~/Downloads/티켓인포_블로그/ 와 ~/Downloads/티켓인포_배너_*.png.

**작업 저장소**: ~/projects/naver-blog (git, main). GitHub 연결은 미완료(gh 로그인 필요, SSH 키는 kseonh/naver-blogger 전용). 옛 저장소 project1은 그대로 둠(2026-10-08 글 이미지 링크가 kseonh/naver-blogger raw 주소).

**실제 블로그 카테고리** (사용자가 붙여준 목록, 2026-10-24 기준):
- 콘서트: K-POP, 힙합, 내한공연, 밴드/인디, 페스티벌
- 공연: 뮤지컬, 연극, 코미디, 클래식/무용
- 스포츠: 야구, 축구, 농구/배구, 격투기, E스포츠
- 축제: 지역축제, 문화축제, 불꽃축제
- 전시: 미술관, 박물관, 체험전
- 항공권: 국제선 특가, 국내선 특가
- "티켓팅 정보" 카테고리는 없음.

**폴더 구조**: posts/<카테고리>/날짜_이름.html. 각 분류 폴더 상단에 `날짜_티켓오픈캘린더.html`을 올리는 방식. 스포츠·항공권은 확인된 정보가 없어 비어 있음. posts/_archive는 옛 종합 글.

**글 형식**: 상단 고정 "제목 복사/본문 복사" 버튼, `#post-title`, `#post-body`, 서식 유지 복사 스크립트, 말미 해시태그, 3줄 요약 박스. 구어체("언니") 말투, 본문 1000자 이상, 핵심 키워드 3회 이상. 모든 스타일은 인라인(네이버가 style 태그를 지움).

**Why:** 매일 티켓 정보를 정확히 올리는 블로그라 구조를 바꾸지 않고 이어가야 한다.
**How to apply:** 새 글은 위 폴더·형식·카테고리 이름 그대로 만든다. 카테고리 이름이 바뀌면 사용자가 붙여준 최신 목록을 따른다. 관련: [[feedback-blog-content-rules]], [[reference-ticket-data-sources]]
