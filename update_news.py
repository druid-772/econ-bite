"""Collect public RSS headlines for a static GitHub Pages PWA. No AI summaries or full article reproduction."""
import datetime, json, pathlib, urllib.request, xml.etree.ElementTree as ET, html, re
BASE=pathlib.Path(__file__).resolve().parent
FEEDS=[('한국은행','https://www.bok.or.kr/portal/bbs/B0000217/news.rss'),('연합뉴스 경제','https://www.yna.co.kr/rss/economy.xml'),('연합뉴스 국제','https://www.yna.co.kr/rss/international.xml')]
items=[];seen=set()
for source,url in FEEDS:
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'EconomyBite/1.0 (RSS reader)'})
        with urllib.request.urlopen(req,timeout=15) as response: root=ET.fromstring(response.read(2_000_000))
        for entry in root.findall('.//item')[:12]:
            title=html.unescape(' '.join((entry.findtext('title') or '').split()))
            link=(entry.findtext('link') or '').strip()
            if not title or not link.startswith('https://') or link in seen: continue
            seen.add(link)
            desc=re.sub('<[^>]+>',' ',entry.findtext('description') or '')
            desc=html.unescape(' '.join(desc.split()))[:220]
            items.append({'title':title,'source':source,'url':link,'published':(entry.findtext('pubDate') or ''),'description':desc})
    except Exception as exc: print('Feed unavailable:',source,str(exc))
if not items:
    print('No valid feeds; retaining prior news.json instead of replacing with empty news')
else:
    data={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'items':items[:24]}
    (BASE/'news.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Saved',len(data['items']),'headlines')
