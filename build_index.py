"""posts/*/*.html 을 훑어 발행 대기 목록 index.html 을 만든다. 실행: python3 build_index.py"""
import html, pathlib, re

root = pathlib.Path(__file__).parent
WRITE = "https://blog.naver.com/ticket_info?Redirect=Write"  # 글쓰기 화면 링크(내 브라우저에서 직접 클릭)

# 실제 블로그 카테고리(상위 → 하위 순서). 글의 <meta name="naver-category">에 "상위 > 하위" 또는 "상위"를 적는다.
TREE = {
    "콘서트": ["K-POP", "힙합", "내한공연", "밴드/인디", "페스티벌"],
    "공연": ["뮤지컬", "연극", "코미디", "클래식/무용"],
    "축제": ["지역축제", "문화축제", "불꽃축제"],
    "전시": ["미술관", "박물관", "체험전"],
    "스포츠": ["야구", "축구", "농구/배구", "격투기", "E스포츠"],
    "항공권": ["국제선 특가", "국내선 특가"],
}
PID = re.compile(r"/products/(\w+)")


def kind(p):  # 상위 카테고리 글: TOP10 → 캘린더, 나머지는 하위 카테고리 글
    return 0 if "인기TOP10" in p.name else 1 if "티켓오픈캘린더" in p.name else 2


posts = []  # (상위, 하위 또는 "", 정렬키, 날짜, 배지, 제목, href)
for cat in TREE:
    files = sorted(root.glob(f"posts/{cat}/*.html"))
    top = next((f for f in files if kind(f) == 0), None)
    rank = {}  # 상품 ID -> TOP10 글 안에서의 순위(카드 등장 순서)
    if top:
        for i, pid in enumerate(dict.fromkeys(PID.findall(top.read_text(encoding="utf-8"))), 1):
            rank[pid] = i
    for f in files:
        txt = f.read_text(encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", txt, re.S)
        meta = re.search(r'<meta name="naver-category" content="(.*?)">', txt)
        assert title and meta, f"title/naver-category 없음: {f}"
        parent, _, sub = (x.strip() for x in html.unescape(meta.group(1)).partition(">"))
        assert parent == cat and (not sub or sub in TREE[cat]), f"카테고리 불일치: {f} -> {meta.group(1)}"
        pid = next(iter(PID.findall(txt)), None)
        badge = "TOP10" if kind(f) == 0 else "캘린더" if kind(f) == 1 else (f"{rank[pid]}위" if pid in rank else "")
        order = (0, kind(f)) if not sub else (1 + TREE[cat].index(sub), rank.get(pid, 99))
        posts.append((cat, sub, order, f.name[:10], badge, html.unescape(title.group(1)).strip(), f.relative_to(root).as_posix()))

# 발행 순서: 블로그는 최신 글이 위에 보이므로 하위 카테고리 글(낮은 순위)부터 올리고 상위 카테고리 TOP10을 마지막에 올린다
seq = {p[6]: i for i, p in enumerate(
    [p for cat in TREE for p in sorted((q for q in posts if q[0] == cat), key=lambda q: q[2], reverse=True)], 1)}


def li(p):
    cat, sub, _, d, badge, t, href = p
    b = f'<b class="bd">{badge}</b> ' if badge else ""
    path = f"{cat} &gt; {sub}" if sub else f"{cat} <small>(상위 카테고리)</small>"
    return (f'<li data-id="{html.escape(href)}"><label><input type="checkbox"> 발행 완료</label> '
            f'<b class="sq">발행 {seq[href]}번</b> <small>{d}</small><br>'
            f'<span class="cat">📂 {path}</span><br>{b}<a href="{html.escape(href)}" target="_blank">{html.escape(t)}</a></li>')


sections = []
for cat in TREE:
    mine = sorted((q for q in posts if q[0] == cat), key=lambda q: q[2])
    if not mine:
        continue
    block = [f"<h2>{cat} <small>({len(mine)}개)</small></h2>"]
    shown = None
    for p in mine:
        head = "상위 카테고리 (맨 위에 올릴 글)" if not p[1] else p[1]
        if head != shown:
            if shown is not None:
                block.append("</ul>")
            block.append(f"<h3>{html.escape(head)}</h3>\n<ul>")
            shown = head
        block.append(li(p))
    block.append("</ul>")
    sections.append("\n".join(block))
items = "\n".join(sections)
rows = posts
(root / "index.html").write_text(f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>발행 대기 목록</title>
<style>body{{max-width:680px;margin:24px auto;padding:0 16px;font:16px/1.7 -apple-system,'Apple SD Gothic Neo',sans-serif}}
li{{margin:14px 0;list-style:none;border-bottom:1px solid #eee;padding-bottom:10px}}li.done{{opacity:.4}}
ul{{padding:0}}.sq{{color:#03c75a;margin-left:8px}}.cat{{color:#2e6bff;font-weight:bold;font-size:14px}}
.bd{{background:#222;color:#fff;border-radius:6px;padding:1px 8px;font-size:13px}}
h2{{margin-top:36px;border-bottom:3px solid #222;padding-bottom:6px}}h3{{margin:18px 0 0;color:#555;font-size:16px}}
.go{{display:inline-block;background:#03c75a;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:bold}}</style></head>
<body><h1>발행 대기 목록</h1>
<p><a class="go" href="{WRITE}" target="_blank">네이버 글쓰기 열기</a></p>
<p>순서: ① 글 제목을 눌러 열기 → ② [제목 복사] [본문 복사] → ③ 글쓰기 창에 붙여넣고 📂 표시된 카테고리를 골라 발행 → ④ "발행 완료" 체크.<br>
<small>발행 번호 순서대로 올리면 각 카테고리 맨 위에 TOP10(상위 카테고리 글)이 보여요.</small></p>
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
