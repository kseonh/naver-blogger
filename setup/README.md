# 다른 PC에서 이어서 쓰기

1. 저장소를 clone 한다: `git clone <원격 주소> ~/projects/naver-blog` (원격 주소는 원래 PC에서 `git remote -v`로 확인).
2. 비밀값: `cp .env.example .env` 후 텔레그램 토큰·chat id, Gemini 키를 채운다. `.env`는 git에 올리지 않는다.
3. Claude 메모리 복원(이전 결정을 기억하게): 저장소 폴더에서 `claude`를 한 번 실행해 `~/.claude/projects/<경로를 -로 바꾼 이름>/` 이 생기게 한 뒤, 그 아래 `memory/` 폴더에 `setup/claude-memory/*.md` 를 복사한다.
4. 매일 09시 자동 실행(맥): `sed "s#__REPO__#$PWD#" setup/com.seankim.naverblog.daily.plist > ~/Library/LaunchAgents/com.seankim.naverblog.daily.plist` 후 `launchctl load ~/Library/LaunchAgents/com.seankim.naverblog.daily.plist`.
5. 확인할 것: `daily.sh`는 `/usr/local/bin/claude` 경로를 쓴다(`which claude`가 다르면 고친다). `gen_image.py`는 macOS `sips`를 쓴다.
6. 프로젝트 규칙은 `CLAUDE.md`/`AGENTS.md`에 이미 있다. 메모리가 바뀌면 `setup/claude-memory/`에 다시 복사해 커밋한다.
