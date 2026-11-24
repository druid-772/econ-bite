import datetime as dt,json,pathlib,urllib.request,urllib.parse,xml.etree.ElementTree as ET,html,re,email.utils
P=pathlib.Path(__file__).parent
FEEDS=[('미국 연준','https://www.federalreserve.gov/feeds/press_all.xml', ['federalreserve.gov']),('미국 노동통계국','https://www.bls.gov/feed/bls_latest.rss',['bls.gov']),('연합뉴스 경제','https://www.yna.co.kr/rss/economy.xml',['yna.co.kr']),('한국은행','https://www.bok.or.kr/portal/bbs/B0000217/news.rss',['bok.or.kr']),('미국 경제분석국','https://www.bea.gov/news/rss.xml',['bea.gov'])]
def clean(s): return ' '.join(html.unescape(re.sub('<[^>]+>',' ',s or '')).split())
def allowed(url,domains):
    p=urllib.parse.urlparse(url); h=p.hostname or ''; return p.scheme=='https' and any(h==d or h.endswith('.'+d) for d in domains)
def main():
    now=dt.datetime.now(dt.timezone.utc); items=[]; seen=set()
    for name,url,domains in FEEDS:
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'EconomyBite RSS reader'})
            with urllib.request.urlopen(req,timeout=15) as r:
                if not allowed(r.geturl(),domains): continue
                root=ET.fromstring(r.read(2000000))
            for e in root.findall('.//item')[:25]:
                link=(e.findtext('link') or '').strip(); title=clean(e.findtext('title'))
                if not title or not allowed(link,domains) or link in seen: continue
                stamp=email.utils.parsedate_to_datetime(e.findtext('pubDate') or '')
                if stamp.tzinfo is None: continue
                age=(now-stamp).total_seconds()
                if not 0<=age<=7*86400: continue
                seen.add(link); items.append(dict(title=title,url=link,source=name,published=stamp.isoformat(),description=clean(e.findtext('description'))[:1200],verified_feed=True))
        except Exception as e: print(name,type(e).__name__)
    if items:
        items.sort(key=lambda x:dt.datetime.fromisoformat(x['published']),reverse=True)
        (P/'news.json').write_text(json.dumps(dict(updated_at=now.isoformat(),items=items[:30]),ensure_ascii=False,indent=2))
    else: print('No recent news; preserving old data')
if __name__=='__main__': main()
