---
name: feedback-image-policy
description: 대표 이미지는 인터넷의 공식 이미지를 우선, Gemini는 정말 없을 때만 (비용·품질)
metadata:
  type: feedback
---

Gemini로 만든 이미지는 품질이 보통이고 돈이 많이 든다. 인터넷에서 받은 공식 포스터·행사 이미지를 최대한 쓰고, 없을 때만 Gemini를 쓴다.

**Why:** 사용자가 품질과 비용에 불만. NOL 공식 포스터(성시경 등)는 품질이 좋았다.
**How to apply:** gen_image.py 가 official-image 메타 → NOL → 멜론 csoonId → 판매처·주최 링크 순으로 받고, 공식 이미지가 있으면 Gemini 를 건너뛴다. 종합·캘린더 글, 티켓링크(로고만 나옴), 뉴스 기사 링크(엉뚱한 사진)는 제외. 모델 교체(Nano Banana Pro `gemini-3-pro-image`, Nano Banana 2 `gemini-3.1-flash-image`)는 미정이며 .env 의 GEMINI_IMAGE_MODEL 로 바꾼다. 관련: [[feedback-blog-content-rules]]
