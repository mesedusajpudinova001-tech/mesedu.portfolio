from pathlib import Path
from html import escape
import json,re

root=Path(__file__).resolve().parents[1]
p=root/'interior/menu'
data=json.loads((p/'menu-data.json').read_text())
s=(p/'index.html').read_text()
prefix=s[:s.index('  <main')]
prefix=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="Меню ZÁDU: завтраки, горячие блюда, боулы, кофе, чай, коктейли, фреши и лимонады.">',prefix)
asset_version='20261013-address'
prefix=re.sub(r'href="\.\./interior\.css(?:\?[^\"]*)?"','href="../interior.css?v='+asset_version+'"',prefix)
footer=re.search(r'  <footer class="page-footer menu-footer">.*?</footer>',s,re.S).group(0)
details={}
photo_placeholder='<div class="item-photo menu-photo-placeholder" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><rect x="7" y="10" width="34" height="28" rx="4"/><circle cx="17" cy="19" r="3"/><path d="m8 33 10-10 8 8 6-6 9 9"/></svg><span>Здесь будет фото</span></div>'

def render_card(entry,category_id,index):
    entry_id=entry.get('id',category_id+'-'+str(index))
    hit='<span class="menu-hit">Хит</span>' if entry.get('hit') else ''
    variants=entry.get('variants',[])
    single=len(variants)==1
    has_description=bool(entry.get('description'))
    price='<p class="item-price">'+str(variants[0]['price'])+' ₽</p>' if single else ''
    arrow='<span class="description-arrow" aria-hidden="true">↗</span>' if has_description else ''
    copy='<div class="item-title"><h3>'+escape(entry['name'])+hit+'</h3>'+price+arrow+'</div>'
    if single and variants[0].get('volume'):
        copy+='<p class="item-portion">'+escape(variants[0]['volume'])+'</p>'
    if len(variants)>1:
        rows=[]
        for v in variants:
            label=' · '.join(x for x in [v.get('volume'),v.get('label')] if x)
            rows.append('<div class="variant-row"><span>'+escape(label)+'</span><strong>'+str(v['price'])+' ₽</strong></div>')
        copy+='<div class="variant-list">'+''.join(rows)+'</div>'
    if not variants:
        copy+='<p class="item-price-pending">Цена не указана</p>'
    if has_description:
        details[entry_id]={'name':entry['name'],'description':entry['description'],'priceLabel':' / '.join(str(v['price'])+' ₽' for v in variants) if variants else 'Цена не указана'}
        inside='<button class="description-trigger" type="button" data-description="'+escape(entry_id)+'" aria-haspopup="dialog" aria-controls="food-description" aria-label="'+escape('Подробнее: '+entry['name'])+'">'+photo_placeholder+'<div class="item-copy">'+copy+'</div></button>'
    else:
        inside=photo_placeholder+'<div class="item-copy">'+copy+'</div>'
    return '<article class="menu-item item-text-card dessert-card">'+inside+'</article>'

categories=data['categories']
groups=data['groups']
bar=next(g for g in groups if g['id']=='bar')
group_nav='\n'.join('      <a class="menu-group-card" href="#'+('bar' if g['id']=='bar' else g['categories'][0])+'" data-menu-group="'+g['id']+'"><span>'+escape(g['title'])+'</span></a>' for g in groups)
nav='\n'.join('        <a class="category-link" href="#'+c['id']+'" data-category="'+c['id']+'">'+escape(c['title'])+'</a>' for c in categories if c['id'] in bar['categories'])
sections=[]
for c in categories:
    note='<p class="category-note">'+escape(c['note'])+'</p>' if c.get('note') else ''
    back_id,back_label=('bar','Все напитки') if c['id'] in bar['categories'] else ('menu-groups','Все разделы')
    sections.append('      <section class="menu-category" id="'+c['id']+'" aria-labelledby="heading-'+c['id']+'"><div class="section-header"><h2 id="heading-'+c['id']+'" tabindex="-1">'+escape(c['title'])+'</h2><a class="all-sections" href="#'+back_id+'" data-menu-back>'+back_label+'</a></div>'+note+'<div class="item-grid">'+''.join(render_card(entry,c['id'],i) for i,entry in enumerate(c['items']))+'</div></section>')
payload=json.dumps(details,ensure_ascii=False).replace('<','\\u003c')
page=prefix+'  <main class="menu-layout" data-menu-view="home">\n    <div class="menu-groups" id="menu-groups"><h1 id="heading-menu" tabindex="-1">Меню</h1><nav class="menu-group-list" aria-label="Основные разделы меню">\n'+group_nav+'\n    </nav></div>\n    <section class="bar-choices" id="bar" aria-labelledby="heading-bar" hidden><h2 id="heading-bar" tabindex="-1">Бар</h2><nav class="category-list" id="sections" aria-label="Разделы бара">\n'+nav+'\n      </nav></section>\n    <div class="menu-content" hidden>\n'+'\n'.join(sections)+'\n    </div>\n    <noscript><style>.bar-choices[hidden],.menu-content[hidden]{display:block!important}</style></noscript>\n  </main>\n'+footer+\
'\n  <dialog class="food-dialog" id="food-description" aria-labelledby="food-dialog-title"><button class="food-dialog-close" type="button" aria-label="Закрыть описание">×</button>'+photo_placeholder.replace('menu-photo-placeholder','menu-photo-placeholder dialog-photo')+'<h2 id="food-dialog-title"></h2><p class="food-dialog-copy" id="food-dialog-copy"></p><p class="food-dialog-price" id="food-dialog-price"></p></dialog>\n'+\
'  <script type="application/json" id="food-details">'+payload+'</script>\n'+\
'  <script src="menu.js?v='+asset_version+'"></script>\n  <script src="food-details.js"></script>\n  <script src="../../green-coffee/motion.js"></script>\n</body>\n</html>\n'
(p/'index.html').write_text(page)
print('Rendered',sum(len(c['items']) for c in categories),'cards;',len(details),'descriptions available after card clicks.')
