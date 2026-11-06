"""텔레그램 알림. 토큰은 .env 에만 둔다. 실행: python3 notify.py "메시지"  /  python3 notify.py --find-chat (채팅 ID를 .env에 저장)"""
import json, pathlib, subprocess, sys

ENV = pathlib.Path(__file__).parent / ".env"

def _env():
    d = {}
    for line in ENV.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip("'\"")
    return d

def _api(method, **data):  # curl 은 macOS 시스템 인증서를 써서 파이썬 SSL 오류를 피한다
    cmd = ["curl", "-sS", "-m", "20", f"https://api.telegram.org/bot{_env()['TELEGRAM_BOT_TOKEN']}/{method}"]
    for k, v in data.items():
        cmd += ["--data-urlencode", f"{k}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("텔레그램 연결 실패: " + r.stderr.replace(_env()["TELEGRAM_BOT_TOKEN"], "TOKEN"))
    return json.loads(r.stdout)

def send(text):
    return _api("sendMessage", chat_id=_env()["TELEGRAM_CHAT_ID"], text=text)["ok"]

def find_chat():
    msgs = [u["message"]["chat"] for u in _api("getUpdates")["result"] if "message" in u]
    if not msgs:
        raise SystemExit("받은 메시지가 없어요. 텔레그램에서 봇에게 아무 메시지나 보낸 뒤 다시 실행해 주세요.")
    cid = msgs[-1]["id"]
    ENV.write_text("".join(l + "\n" for l in ENV.read_text().splitlines() if not l.startswith("TELEGRAM_CHAT_ID")) + f"TELEGRAM_CHAT_ID={cid}\n")
    print("채팅 ID 저장 완료:", cid)

if __name__ == "__main__":
    if sys.argv[1:] == ["--find-chat"]:
        find_chat()
    else:
        print(send(" ".join(sys.argv[1:]) or "테스트 알림"))
