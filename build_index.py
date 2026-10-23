"""posts/*/*.html 을 훑어 발행 대기 목록 index.html 을 만든다. 실행: python3 build_index.py"""
import html, pathlib, re

root = pathlib.Path(__file__).parent
WRITE = "https://blog.naver.com/ticket_info?Redirect=Write"  # 글쓰기 화면 링크(내 브라우저에서 직접 클릭)

ORDER = ["콘서트", "공연", "축제", "전시", "스포츠", "항공권"]  # 블로그 카테고리 순서
PID = re.compile(r"/products/(\w+)")

def kind(p):  # 카테고리 안 정렬: TOP10 → 캘린더 → 랭킹순 상세 → 나머지(최신순)
    return 0 if "인기TOP10" in p.name else 1 if "티켓오픈캘린더" in p.name else 2

groups = {}
for cat in sorted({p.parent.name for p in root.glob("posts/*/*.html") if not p.parent.name.startswith("_")}, key=lambda c: ORDER.index(c) if c in ORDER else 99):
    files = sorted(root.glob(f"posts/{cat}/*.html"))
    top = next((f for f in files if kind(f) == 0), None)
    rank = {}  # 상품 ID -> TOP10 글 안에서의 순위(카드 등장 순서)
    if top:
        for i, pid in enumerate(dict.fromkeys(PID.findall(top.read_text(encoding="utf-8"))), 1):
            rank[pid] = i
    def key(f):
        txt = f.read_text(encoding="utf-8")
        pid = next(iter(PID.findall(txt)), None)
        r = rank.get(pid, 99) if kind(f) == 2 else 0
        return (kind(f), r, tuple(-ord(c) for c in f.name[:10]))
    rows = []
    for f in sorted(files, key=key):
        txt = f.read_text(encoding="utf-8")
        m = re.search(r"<title>(.*?)</title>", txt, re.S)
        assert m, f"title 없음: {f}"
        pid = next(iter(PID.findall(txt)), None)
        badge = "TOP10" if kind(f) == 0 else "캘린더" if kind(f) == 1 else (f"{rank[pid]}위" if pid in rank else "")
        rows.append((f.name[:10], badge, html.unescape(m.group(1)).strip(), f.relative_to(root).as_posix()))
    groups[cat] = rows

# 발행 순서: 블로그는 최신 글이 위에 보이므로, 카테고리마다 아래 글(낮은 순위)부터 올리고 TOP10을 마지막에 올린다
seq, n = {}, 0
for r in groups.values():
    for x in reversed(r):
        n += 1
        seq[x[3]] = n

def li(d, badge, t, href):
    b = f'<b class="bd">{badge}</b> ' if badge else ""
    return (f'<li data-id="{html.escape(href)}"><label><input type="checkbox"> 발행 완료</label> '
            f'<b class="sq">발행 {seq[href]}번</b> <small>{d}</small><br>{b}<a href="{html.escape(href)}" target="_blank">{html.escape(t)}</a></li>')

items = "\n".join(f"<h2>{c} <small>({len(r)}개)</small></h2>\n<ul>\n" + "\n".join(li(*x) for x in r) + "\n</ul>" for c, r in groups.items())
rows = [x for r in groups.values() for x in r]
(root / "index.html").write_text(f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>발행 대기 목록</title>
<style>body{{max-width:680px;margin:24px auto;padding:0 16px;font:16px/1.7 -apple-system,'Apple SD Gothic Neo',sans-serif}}
li{{margin:14px 0;list-style:none;border-bottom:1px solid #eee;padding-bottom:10px}}li.done{{opacity:.4}}
.sq{{color:#03c75a;margin-left:8px}}.bd{{background:#222;color:#fff;border-radius:6px;padding:1px 8px;font-size:13px}}h2{{margin-top:36px;border-bottom:3px solid #222;padding-bottom:6px}}.go{{display:inline-block;background:#03c75a;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:bold}}</style></head>
<body><h1>발행 대기 목록</h1>
<p><a class="go" href="{WRITE}" target="_blank">네이버 글쓰기 열기</a></p>
<p>순서: ① 글 제목을 눌러 열기 → ② [제목 복사] [본문 복사] → ③ 글쓰기 창에 붙여넣고 발행 → ④ 아래 "발행 완료" 체크</p>
{items}
<script>
document.querySelectorAll('li').forEach(function(li){{
  var k='done:'+li.dataset.id, cb=li.querySelector('input');
  try{{cb.checked=localStorage.getItem(k)==='1'}}catch(e){{}}
  li.classList.toggle('done',cb.checked);
  cb.onchange=function(){{li.classList.toggle('done',cb.checked);try{{localStorage.setItem(k,cb.checked?'1':'0')}}catch(e){{}}}};
}});
</script></body></html>
""", encoding="utf-8")
print(f"index.html: {len(rows)}개 글")
