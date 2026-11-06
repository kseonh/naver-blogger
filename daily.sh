#!/bin/bash
# 매일 09:00 launchd 가 실행. 새 글감을 찾아 글을 만들고 텔레그램으로 알린다.
cd "$(dirname "$0")" || exit 1
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
/usr/local/bin/claude -p "$(cat daily_prompt.md)" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Write,Edit,Glob,Grep,WebFetch,WebSearch,Bash(grep:*),Bash(ls:*),Bash(python3 build_index.py:*),Bash(python3 notify.py:*)" \
  >> "logs/$(date +%F).log" 2>&1 || python3 notify.py "자동 작성 실행 실패. logs/$(date +%F).log 를 확인해 주세요"
# 새 글의 대표 이미지 배경을 Gemini로 만들고(키가 없으면 건너뜀) index.html 에 반영한다
python3 gen_image.py >> "logs/$(date +%F).log" 2>&1 && python3 build_index.py >> "logs/$(date +%F).log" 2>&1
# 다 끝나면 화면을 꺼서 잠근다(깨우기 설정 뒤 로그인 상태로 남지 않도록)
pmset displaysleepnow
