"""posts/*/*.html 을 훑어 발행 대기 목록 index.html 을 만든다. 실행: python3 build_index.py"""
import base64, html, json, pathlib, re

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

GAP = '<p style="margin:0;">&nbsp;</p>'  # 네이버에 붙여넣으면 h2 위 여백(margin)이 사라져서, 빈 줄을 직접 넣는다


HR = '<hr style="border:0;border-top:3px solid #222;margin:0 0 12px;">'  # 소제목 위 줄. h2 자체에 border 를 주면 네이버가 소제목 위·아래에 줄을 붙여서 hr 로 분리한다
H2 = '<h2 style="font-size:22px;margin:0;">'


def spaced(txt):  # 소제목을 [빈 줄 + 위 줄 + 소제목]으로 맞추고, 소제목 아래는 붙인다(여러 번 돌려도 같은 결과)
    txt = re.sub(r'<h2 style="[^"]*border-(?:top|bottom):3px solid #222[^"]*">', HR + H2, txt)
    txt = re.sub(r"(?<!%s)(<hr style=\"border:0;border-top:3px solid #222)" % re.escape(GAP), GAP + r"\1", txt)
    txt = re.sub(r"</table>(?!%s|\s*</div>)" % re.escape(GAP), "</table>" + GAP, txt)
    txt = re.sub(r'(</h2>)<p>', r'\1<p style="margin-top:0;">', txt)
    txt = re.sub(r'(</h2>)<p style="(?![^"]*margin-top)', r'\1<p style="margin-top:0;', txt)
    return re.sub(r'(</h2><table style="width:100%;border-collapse:collapse;font-size:16px;)margin:(?:20px 0|8px 0 20px);', r"\1margin:0 0 20px;", txt)


def kind(p):  # 상위 카테고리 글: TOP10 → 캘린더, 나머지는 하위 카테고리 글
    return 0 if "인기TOP10" in p.name else 1 if "티켓오픈캘린더" in p.name else 2


CARD = {}  # href -> [이모지, 제목, 부제, 하단문구] (naver-card 메타가 있는 글만 맞춤 대표 카드)
OFF = {}  # href -> 공식 포스터 data URI(있으면 대표 이미지로 그대로 쓴다)
BG = {}  # href -> data URI (gen_image.py 가 만든 배경. file:// 에서 캔버스가 막히지 않게 data URI 로 넣는다)
DATA = {}  # href -> [제목, 본문HTML] (index.html 안에서 바로 복사하려고 넣어 둔다)
posts = []  # (상위, 하위 또는 "", 정렬키, 날짜, 배지, 제목, href)
for cat in TREE:
    files = sorted(root.glob(f"posts/{cat}/*.html"))
    top = next((f for f in files if kind(f) == 0), None)
    rank = {}  # 상품 ID -> TOP10 글 안에서의 순위(카드 등장 순서)
    if top:
        for i, pid in enumerate(dict.fromkeys(PID.findall(top.read_text(encoding="utf-8"))), 1):
            rank[pid] = i
    for f in files:
        txt = spaced(f.read_text(encoding="utf-8"))
        f.write_text(txt, encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", txt, re.S)
        meta = re.search(r'<meta name="naver-category" content="(.*?)">', txt)
        assert title and meta, f"title/naver-category 없음: {f}"
        parent, _, sub = (x.strip() for x in html.unescape(meta.group(1)).partition(">"))
        assert parent == cat and (not sub or sub in TREE[cat]), f"카테고리 불일치: {f} -> {meta.group(1)}"
        pid = next(iter(PID.findall(txt)), None)
        cd = re.search(r'<meta name="naver-card" content="(.*?)">', txt)
        if cd:
            CARD[f.relative_to(root).as_posix()] = html.unescape(cd.group(1)).split("|")
        h1 = re.search(r'<h1 id="post-title"[^>]*>(.*?)</h1>', txt, re.S)
        bd = re.search(r'<div id="post-body">(.*?)</div>\s*<script>', txt, re.S)
        assert h1 and bd, f"post-title/post-body 없음: {f}"
        bg = root / "posts/images/bg" / (f.stem + ".jpg")
        if bg.exists():
            BG[f.relative_to(root).as_posix()] = "data:image/jpeg;base64," + base64.b64encode(bg.read_bytes()).decode()
        of = root / "posts/images/official" / (f.stem + ".jpg")
        if of.exists():
            OFF[f.relative_to(root).as_posix()] = "data:image/jpeg;base64," + base64.b64encode(of.read_bytes()).decode()
        DATA[f.relative_to(root).as_posix()] = [html.unescape(h1.group(1)).strip(), bd.group(1)]
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
            f'<button type="button" class="cp" data-k="t">① 제목 복사</button><button type="button" class="cp" data-k="b">② 본문 복사</button> '
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
body>h2{{margin-top:36px;border-bottom:3px solid #222;padding-bottom:6px}}body>h3{{margin:18px 0 0;color:#555;font-size:16px}}
.cp{{margin:0 4px;padding:6px 12px;border:0;border-radius:6px;background:#222;color:#fff;font-weight:bold;cursor:pointer}}.cp[data-k=b]{{background:#03c75a}}
.ov{{position:fixed;inset:0;background:#fff;z-index:99;display:none;overflow:auto;padding:24px 16px}}.ov .in{{max-width:680px;margin:0 auto}}
.ov .big{{display:block;width:100%;margin:10px 0;padding:18px;border:0;border-radius:12px;font-size:20px;font-weight:bold;color:#fff;cursor:pointer;background:#222}}
.ov .cat2{{font-size:26px;font-weight:bold;color:#2e6bff;margin:8px 0}}.ov .ttl{{font-size:19px;line-height:1.5;margin:8px 0 18px}}.ov .sm{{background:#eee;color:#333;font-size:15px;padding:10px}}
.go{{display:inline-block;background:#03c75a;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:bold}}</style></head>
<body><h1>발행 대기 목록</h1>
<p><a class="go" href="{WRITE}" target="_blank">네이버 글쓰기 열기</a> <button type="button" id="pm" class="go" style="border:0;cursor:pointer;background:#2e6bff;font-size:16px">▶ 발행 모드</button></p>
<p>순서(발행 모드): 제목 복사 → 대표 이미지 복사(본문 첫 줄에 붙여넣기, 이게 썸네일이 돼요) → 본문 복사. 순서: ① 글쓰기 창을 열어 둔다 → ② 여기서 [① 제목 복사] 후 제목칸에, [② 본문 복사] 후 본문에 붙여넣기(⌘V) → ③ 글쓰기 창에 붙여넣고 📂 표시된 카테고리를 골라 발행 → ④ "발행 완료" 체크.<br>
<small>발행 번호 순서대로 올리면 각 카테고리 맨 위에 TOP10(상위 카테고리 글)이 보여요.</small></p>
{items}
<script>
var CARD={json.dumps(CARD, ensure_ascii=False)};
var OFF={json.dumps(OFF)};var OI={{}};for(var k in OFF){{OI[k]=new Image();OI[k].src=OFF[k]}}
var BG={json.dumps(BG)};var IMG={{}};for(var k in BG){{IMG[k]=new Image();IMG[k].src=BG[k]}}
var DATA={json.dumps(DATA, ensure_ascii=False).replace('</','<\\/')};
function copyTo(k,id,b){{
  var d=DATA[id],o=b.textContent,n=document.createElement('div');
  if(k==='t')n.textContent=d[0];else n.innerHTML=d[1];  // 본문은 서식(표·사진·링크)째로 복사
  n.style.cssText='position:fixed;left:-9999px;top:0;width:680px';document.body.appendChild(n);
  var s=getSelection(),r=document.createRange();r.selectNodeContents(n);s.removeAllRanges();s.addRange(r);
  var ok=document.execCommand('copy');s.removeAllRanges();n.remove();
  b.textContent=ok?'복사됨 ✓':'복사 실패';setTimeout(function(){{b.textContent=o}},1500);
}}
function fit(x,t,w,px,f){{do{{x.font='bold '+px+'px '+f;px-=4}}while(x.measureText(t).width>w&&px>30);return px}}
// 배경 사진이 있으면 사진 위에 어두운 막을 깔고, 없으면 기존 그라데이션을 쓴다
function bgfill(x,id,fb){{var i=IMG[id];if(i&&i.complete&&i.naturalWidth){{x.drawImage(i,0,0,900,900);var s=x.createLinearGradient(0,0,0,900);s.addColorStop(0,'rgba(0,0,0,.25)');s.addColorStop(1,'rgba(0,0,0,.7)');x.fillStyle=s;x.fillRect(0,0,900,900);return true}}fb();return false}}
function card(d,id){{
  var c=document.createElement('canvas');c.width=c.height=900;var x=c.getContext('2d'),f="'Apple SD Gothic Neo','Malgun Gothic',sans-serif";
  var g=x.createLinearGradient(0,0,900,900);g.addColorStop(0,'#0b2a5b');g.addColorStop(1,'#1c6fd1');if(!bgfill(x,id,function(){{x.fillStyle=g;x.fillRect(0,0,900,900);
  x.fillStyle='rgba(255,255,255,.07)';x.beginPath();x.arc(780,140,330,0,7);x.fill();x.beginPath();x.arc(80,860,250,0,7);x.fill()}}));
  x.textBaseline='alphabetic';x.font='200px sans-serif';x.fillText(d[0],60,300);
  x.fillStyle='#ffd23f';x.fillRect(60,350,120,10);
  x.fillStyle='#fff';fit(x,d[1],780,100,f);x.fillText(d[1],60,490);
  x.fillStyle='#ffd23f';fit(x,d[2],780,64,f);x.fillText(d[2],60,590);
  x.fillStyle='rgba(255,255,255,.85)';fit(x,d[3],780,38,f);x.fillText(d[3],60,820);
  return c;
}}
function cover(id,cat){{
  var p=OI[id];
  if(p&&p.complete&&p.naturalWidth){{  // 공식 포스터: 흐린 배경 위에 비율 그대로 가운데 배치
    var c0=document.createElement('canvas');c0.width=c0.height=900;var x0=c0.getContext('2d');
    x0.filter='blur(30px) brightness(.6)';x0.drawImage(p,-60,-60,1020,1020*p.naturalHeight/p.naturalWidth);x0.filter='none';
    var h=900,w=900*p.naturalWidth/p.naturalHeight;x0.drawImage(p,(900-w)/2,0,w,h);return c0}}
  if(CARD[id])return card(CARD[id],id);
  var c=document.createElement('canvas');c.width=c.height=900;var x=c.getContext('2d');
  var g=x.createLinearGradient(0,0,900,900);g.addColorStop(0,'#03c75a');g.addColorStop(1,'#0a7d3b');bgfill(x,id,function(){{x.fillStyle=g;x.fillRect(0,0,900,900)}});
  var f="'Apple SD Gothic Neo','Malgun Gothic',sans-serif";
  x.fillStyle='rgba(255,255,255,.18)';x.fillRect(60,70,300,70);x.fillStyle='#fff';x.font='bold 38px '+f;x.textBaseline='middle';
  x.fillText(cat.replace(/^📂\\s*/,'').split('>').pop().trim().slice(0,10),84,106);
  var t=DATA[id][0].split(/ \\(| \\| /)[0].replace(/\\s*티켓 예매 정보$/,' 예매 정보'),lines=[],cur='';
  for(var i=0;i<t.length;i++){{cur+=t[i];if(cur.length>=11||(cur.length>=8&&t[i]===' ')){{lines.push(cur.trim());cur=''}}}}
  if(cur.trim())lines.push(cur.trim());lines=lines.slice(0,5);
  x.font='bold 84px '+f;x.textBaseline='alphabetic';var y=450-(lines.length-1)*55;
  lines.forEach(function(l,k){{x.fillText(l,60,y+k*110)}});
  x.font='bold 36px '+f;x.fillStyle='rgba(255,255,255,.85)';x.fillText('ticket_info · 티켓 예매 정보',60,830);
  return c;
}}
function copyCover(id,cat,b,prev){{
  var o=b.textContent;
  var c=cover(id,cat);if(prev){{prev.innerHTML='';c.style.cssText='width:160px;border-radius:8px';prev.appendChild(c)}}
  c.toBlob(function(bl){{
    var done=function(m){{b.textContent=m;setTimeout(function(){{b.textContent=o}},1800)}};
    try{{navigator.clipboard.write([new ClipboardItem({{'image/png':bl}})]).then(function(){{done('복사됨 ✓')}},function(){{done('복사 실패: 아래 이미지를 우클릭해 복사')}})}}catch(e){{done('복사 실패: 아래 이미지를 우클릭해 복사')}}
  }});
}}
function copyAll(id,cat,b,prev){{
  var o=b.textContent,c=cover(id,cat),done=function(m){{b.textContent=m;setTimeout(function(){{b.textContent=o}},1800)}};
  if(prev){{prev.innerHTML='';c.style.cssText='width:160px;border-radius:8px';prev.appendChild(c)}}
  var h='<img src="'+c.toDataURL('image/jpeg',.9)+'" width="680"><p style="margin:0;">&nbsp;</p>'+DATA[id][1];
  try{{navigator.clipboard.write([new ClipboardItem({{'text/html':new Blob([h],{{type:'text/html'}}),'text/plain':new Blob([DATA[id][1].replace(/<[^>]+>/g,' ')],{{type:'text/plain'}})}})]).then(function(){{done('복사됨 ✓')}},function(){{done('복사 실패')}})}}catch(e){{done('복사 실패')}}
}}
// 발행 모드: 발행 번호 순서로 안 올린 글을 하나씩 보여 준다
var Q=[].slice.call(document.querySelectorAll('li')).sort(function(a,b){{return parseInt(a.querySelector('.sq').textContent.replace(/[^0-9]/g,''))-parseInt(b.querySelector('.sq').textContent.replace(/[^0-9]/g,''))}});
var ov=document.createElement('div');ov.className='ov';document.body.appendChild(ov);
function show(){{
  var li=Q.filter(function(l){{return !l.querySelector('input').checked}})[0];
  if(!li){{ov.innerHTML='<div class="in"><h1>🎉 모두 발행했어요</h1><button class="big sm" id="x">닫기</button></div>';ov.querySelector('#x').onclick=function(){{ov.style.display='none'}};return}}
  var left=Q.filter(function(l){{return !l.querySelector('input').checked}}).length,id=li.dataset.id;
  ov.innerHTML='<div class="in"><small>남은 글 '+left+'개 · '+li.querySelector('.sq').textContent+'</small>'
   +'<div class="cat2">'+li.querySelector('.cat').innerHTML+'</div><div class="ttl"></div>'
   +'<button class="big" data-k="t">① 제목 복사</button><button class="big" id="cv" style="background:#ff7a1a">② 대표 이미지 복사 (본문 맨 위에 먼저 붙여넣기)</button><div id="pv" style="text-align:center"></div><button class="big" data-k="b" style="background:#03c75a">③ 본문 복사 (이미지 아래에 붙여넣기)</button>'
   +'<button class="big" id="ok" style="background:#2e6bff">발행 완료 → 다음 글</button>'
   +'<button class="big sm" id="sk">건너뛰기</button><button class="big sm" id="x">닫기</button></div>';
  ov.querySelector('.ttl').textContent=DATA[id][0];
  ov.querySelectorAll('[data-k]').forEach(function(b){{b.onclick=function(){{copyTo(b.dataset.k,id,b)}}}});
  ov.querySelector('#cv').onclick=function(){{copyCover(id,li.querySelector('.cat').textContent,this,ov.querySelector('#pv'))}};
  ov.querySelector('#ok').onclick=function(){{var c=li.querySelector('input');c.checked=true;c.onchange();show()}};
  ov.querySelector('#sk').onclick=function(){{Q.push(Q.splice(Q.indexOf(li),1)[0]);show()}};
  ov.querySelector('#x').onclick=function(){{ov.style.display='none'}};
}}
document.getElementById('pm').onclick=function(){{ov.style.display='block';show()}};
document.querySelectorAll('li').forEach(function(li){{
  var k='done:'+li.dataset.id, cb=li.querySelector('input');
  try{{cb.checked=localStorage.getItem(k)==='1'}}catch(e){{}}
  li.classList.toggle('done',cb.checked);
  li.querySelectorAll('.cp').forEach(function(b){{b.onclick=function(){{copyTo(b.dataset.k,li.dataset.id,b)}}}});
  cb.onchange=function(){{li.classList.toggle('done',cb.checked);try{{localStorage.setItem(k,cb.checked?'1':'0')}}catch(e){{}}}};
}});
</script></body></html>
""", encoding="utf-8")
print(f"index.html: {len(rows)}개 글")
if "--notify" in __import__("sys").argv:
    import notify
    notify.send(f"📝 발행 대기 글 {len(rows)}개가 준비됐어요. index.html 을 열어 [발행 모드]로 올려 주세요.")
