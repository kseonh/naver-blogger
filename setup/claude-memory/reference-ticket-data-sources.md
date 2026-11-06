---
name: reference-ticket-data-sources
description: 티켓 정보 수집처별로 WebFetch로 읽을 수 있는지 여부와 유용한 URL (2026-10-24 시험)
metadata:
  node_type: memory
  type: reference
  originSessionId: 2f0292fe-ba9d-4342-9f37-3d0cca2906ee
  modified: 2026-10-23T18:28:29.167Z
---

**읽힘 (WebFetch)**
- NOL(인터파크 후신): 오픈 예정 `https://nol.yanolja.com/ticket/display/upcoming` (25건, 날짜·시간·제목), 장르 페이지 `/ticket/genre/{concert|musical|play|classic|exhibition|sports|family}`의 "일간 랭킹" 5개, 상세 `/ticket/products/{id}` (가격·회차·캐스팅·취소규정 등 풍부, 줄거리는 이미지라 없음). tickets.interpark.com은 NOL로 301 리다이렉트.
- YES24 티켓: `https://ticket.yes24.com/` 티켓오픈 공지 정적 HTML(단독·선예매 표기), 전체 공지 `/New/Notice/NoticeMain.aspx`. 랭킹 탭은 JS라 안 보임.
- 멜론티켓: `https://ticket.melon.com/csoon/index.htm` HOT 티켓오픈 소식 (날짜만, 시각 없음). 랭킹은 JS라 안 보임.
- JYP: jype.com은 앨범 소식 위주, 공연 공지는 JS.

**안 읽힘 (JS 렌더링, 제목만 나옴)**: 티켓링크, openingticket.com, 타임티켓. 크롬 도구로 렌더링해서 읽어야 할 수 있음(미시도).
**못 읽음**: 카카오톡 채널, 네이버 블로그(도구 차단), SM·YG는 미시험.

**Why:** 사용자가 NOL·YES24만으로는 정보가 적다며 더 많은 사이트의 인기 순위 Top 10을 매주 나열하길 원한다.
**How to apply:** 위 표대로 가능한 곳부터 읽고, 읽을 수 없는 곳은 크롬 렌더링을 시도하되 불가하면 솔직히 표기한다. 관련: [[project-naver-blog-ticket-info]]
