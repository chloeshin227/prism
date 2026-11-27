"""
결과 공유 — 서버나 로그인 없이, 결과를 링크 주소(쿼리 파라미터)에 담아 친구에게 보냅니다.

  내가 링크를 만든다  : make_link()  → https://…/?sc=crash&gr=B&rt=30&ch=compass
  친구가 링크를 연다   : parse_shared() 가 값을 검사해서 안전할 때만 '친구의 결과' 카드를 보여 줌

[예외 처리] 링크의 값이 잘못되었거나 조작되었으면(없는 시나리오, 이상한 등급, 숫자가 아닌 수익률 등)
            카드를 보여 주지 않고 조용히 무시합니다.
"""
import json
from urllib.parse import urlencode

import streamlit.components.v1 as components

from core.character import CHARACTERS
from data.scenarios import SCENARIOS

APP_URL = "https://prism72.streamlit.app"
GRADES = ("S", "A", "B", "C")


def make_link(sid: str, grade: str, ret: float, char_key: str) -> str:
    """결과를 담은 공유 링크. 수익률은 0.1% 단위 정수(rt=30 → +3.0%)로 담는다."""
    q = {"sc": sid, "gr": grade, "rt": round(ret * 1000), "ch": char_key}
    return f"{APP_URL}/?{urlencode(q)}"


def parse_shared(params) -> dict | None:
    """주소창의 값을 검사해서 안전하면 dict로, 아니면 None을 돌려준다."""
    try:
        sid, grade, ch = params.get("sc"), params.get("gr"), params.get("ch")
        if sid not in SCENARIOS or grade not in GRADES or ch not in CHARACTERS:
            return None
        rt = int(params.get("rt"))
        if not -1000 <= rt <= 5000:          # -100% ~ +500% 밖이면 조작된 값
            return None
        return {"sid": sid, "grade": grade, "ret": rt / 1000, "ch": CHARACTERS[ch]}
    except (TypeError, ValueError):
        return None


def share_buttons(link: str, text: str) -> None:
    """[링크 복사] [결과 공유하기] 버튼. 공유하기는 휴대폰의 공유창(카카오톡 등)을 연다."""
    link_js, text_js = json.dumps(link), json.dumps(text)
    components.html(
        """
<style>
  body{margin:0;font-family:inherit}
  .row{display:flex;gap:12px;flex-wrap:wrap}
  button{font:800 15px/1 'Helvetica Neue','Pretendard',sans-serif;padding:14px 22px;border-radius:14px;cursor:pointer;
         border:2px solid var(--t);background:var(--bg);color:var(--t);box-shadow:4px 4px 0 var(--s);transition:.15s}
  button.p{background:var(--a);color:var(--o)}
  button:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 var(--s)}
  button:active{transform:translate(3px,3px);box-shadow:1px 1px 0 var(--s)}
  #msg{margin-top:12px;font:700 13px 'Helvetica Neue','Pretendard',sans-serif;color:var(--t);min-height:18px}
</style>
<div class="row"><button class="p" id="copy">링크 복사</button><button id="share">결과 공유하기</button></div>
<div id="msg"></div>
<script>
(function(){
  var LINK=__LINK__, TEXT=__TEXT__;
  // 앱의 현재 색(라이트/다크)을 읽어와 버튼에 적용
  try{var cs=window.parent.getComputedStyle(window.parent.document.querySelector('.stApp'));
    var g=function(n,d){var v=cs.getPropertyValue(n).trim();return v||d};
    var r=document.documentElement.style;
    r.setProperty('--a',g('--accent','#ff5a6a'));r.setProperty('--o',g('--on-accent','#fff'));
    r.setProperty('--t',g('--text','#111'));r.setProperty('--s',g('--brut-shadow','#111'));r.setProperty('--bg','transparent');
  }catch(e){var r=document.documentElement.style;r.setProperty('--a','#ff5a6a');r.setProperty('--o','#fff');r.setProperty('--t','#111');r.setProperty('--s','#111');r.setProperty('--bg','transparent');}
  var msg=document.getElementById('msg');
  function say(t){msg.textContent=t;setTimeout(function(){msg.textContent='';},2600);}
  function fallbackCopy(s){var a=document.createElement('textarea');a.value=s;a.style.position='fixed';a.style.opacity='0';
    document.body.appendChild(a);a.select();var ok=false;try{ok=document.execCommand('copy');}catch(e){}document.body.removeChild(a);return ok;}
  function copy(s,done){
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(s).then(function(){done(true)},function(){done(fallbackCopy(s))});}
    else{done(fallbackCopy(s));}
  }
  document.getElementById('copy').onclick=function(){copy(LINK,function(ok){say(ok?'링크를 복사했어요!':'복사하지 못했어요. 아래 주소를 직접 복사해 주세요.');});};
  document.getElementById('share').onclick=function(){
    if(navigator.share){navigator.share({title:'PRISM',text:TEXT,url:LINK}).catch(function(){});}
    else{copy(TEXT+' '+LINK,function(ok){say(ok?'공유 문구를 복사했어요. 메신저에 붙여 넣으세요!':'복사하지 못했어요. 아래 주소를 직접 복사해 주세요.');});}
  };
})();
</script>
""".replace("__LINK__", link_js).replace("__TEXT__", text_js),
        height=96,
    )
