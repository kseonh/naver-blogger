"""글마다 대표 이미지 '배경'을 Gemini로 만든다. 제목 글자는 index.html 에서 얹는다(AI가 한글을 자주 깨뜨려서).
실행: python3 gen_image.py [--force]   키: .env 의 GEMINI_API_KEY (모델은 GEMINI_IMAGE_MODEL, 기본 gemini-2.5-flash-image)
결과: posts/images/bg/<글파일명>.jpg (900px). 이미 있으면 건너뛴다."""
import base64, html, json, pathlib, re, subprocess, sys, tempfile, time
from notify import _env

root = pathlib.Path(__file__).parent
OUT = root / "posts/images/bg"
SCENE = {  # 실제 인물·로고·글자가 없는 분위기 사진으로만 만든다
    "콘서트": "a packed concert arena seen from behind the crowd, stage lights and light sticks glowing, no performers' faces",
    "공연": "an empty grand theater stage with red velvet curtains and a single warm spotlight",
    "스포츠": "a night stadium under bright floodlights, empty seats and a green field, no players",
    "축제": "a festival at dusk with glowing lanterns, string lights and soft bokeh crowd silhouettes",
    "전시": "a bright modern art gallery with blank framed canvases and soft museum lighting",
    "항공권": "an airplane wing above clouds at sunrise",
}


def gemini(prompt):
    env = _env()
    model = env.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["IMAGE"]}})
    r = subprocess.run(["curl", "-sS", "-m", "120", "-H", "Content-Type: application/json", "-H", "x-goog-api-key: " + env["GEMINI_API_KEY"],
                        "-d", body, f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr.replace(env["GEMINI_API_KEY"], "KEY"))
    d = json.loads(r.stdout)
    for p in d.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inlineData" in p:
            return base64.b64decode(p["inlineData"]["data"])
    raise RuntimeError("이미지 없음: " + r.stdout[:300].replace(env["GEMINI_API_KEY"], "KEY"))


OFF = root / "posts/images/official"
def official():
    # NOL 상품이면 판매처의 공식 포스터(og:image)를 받는다(출연자 얼굴이 나오는 대표 이미지). 없으면 AI 배경을 쓴다
    OFF.mkdir(parents=True, exist_ok=True)
    for f in sorted(root.glob("posts/*/20*.html")):
        dst = OFF / (f.stem + ".jpg")
        txt = f.read_text(encoding="utf-8")
        m = re.search(r"products/(\d{8})", txt); o = re.search(r'<meta name="official-image" content="(.*?)">', txt)
        if f.parent.name == "_archive" or dst.exists() or not (m or o): continue
        if o: u = o  # 글에 직접 적어 둔 공식 이미지 주소(NOL이 아닌 글)
        else:
            page = subprocess.run(["curl", "-s", "-m", "20", "-A", "Mozilla/5.0", f"https://nol.yanolja.com/ticket/products/{m.group(1)}"], capture_output=True, text=True).stdout
            u = re.search(r'og:image" content="([^"]*)', page)
        if not u: continue
        tmp = tempfile.mktemp()
        subprocess.run(["curl", "-s", "-m", "30", "-A", "Mozilla/5.0", "-e", "https://nol.yanolja.com/", "-o", tmp, u.group(1)])
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", "-Z", "900", tmp, "--out", str(dst)], capture_output=True)
        print("공식 포스터:", f.stem, "OK" if dst.exists() else "실패")
def main(force=False):
    official()
    if "GEMINI_API_KEY" not in _env():
        print("GEMINI_API_KEY 가 .env 에 없어서 이미지 생성을 건너뛰어요")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    made = failed = 0
    for f in sorted(root.glob("posts/*/20*.html")):
        if f.parent.name == "_archive" or (OUT / (f.stem + ".jpg")).exists() and not force:
            continue
        txt = f.read_text(encoding="utf-8")
        cat = re.search(r'<meta name="naver-category" content="(.*?)">', txt).group(1).split(">")[0].strip()
        title = html.unescape(re.search(r"<title>(.*?)</title>", txt, re.S).group(1)).split("(")[0].split("|")[0].strip()
        m = re.search(r'<meta name="image-scene" content="(.*?)">', txt)  # 글마다 공연·가수에 맞춘 장면(영문)
        scene = html.unescape(m.group(1)) if m else SCENE.get(cat, SCENE['공연'])
        prompt = (f"Square 1:1 cinematic concert/event key-art poster, rich color, dramatic lighting, strong single focal subject. Scene: {scene}. "
                  f"The image must clearly express this specific Korean event (do not write it): {title}. "
                  "If a performer, athlete or character fits, show them only as a backlit silhouette or from behind, face never visible, not any real person's likeness. "
                  "Strictly NO text, letters, numbers, logos, watermarks or brand marks. "
                  "Keep the lower-middle area calm and darker so a title can be overlaid.")
        try:
            for k in range(3):  # 503(일시 과부하)은 잠깐 뒤에 다시 시도한다
                try:
                    raw = gemini(prompt)
                    break
                except RuntimeError as e:
                    if "UNAVAILABLE" not in str(e) or k == 2:
                        raise
                    time.sleep(20)
            with tempfile.NamedTemporaryFile(suffix=".img") as t:
                t.write(raw); t.flush()  # 900px JPEG 로 줄여 index.html 에 넣어도 가볍게 한다(macOS sips)
                subprocess.run(["sips", "-Z", "900", "-s", "format", "jpeg", "-s", "formatOptions", "70", t.name, "--out", str(OUT / (f.stem + ".jpg"))], check=True, capture_output=True)
            made += 1
        except Exception as e:
            failed += 1
            print(f"실패 {f.name}: {e}")
            if "quota" in str(e).lower():  # 한도/결제 문제는 글마다 반복해도 소용없다
                print("한도 초과로 중단: 결제(빌링) 설정을 확인해 주세요")
                break
    print(f"이미지 생성 {made}개, 실패 {failed}개")


if __name__ == "__main__":
    main("--force" in sys.argv)
