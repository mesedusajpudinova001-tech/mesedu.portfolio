"""Render the existing ZÁDU menu as ordinary, directly linkable HTML documents."""
from html import escape
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERIOR = ROOT / "interior"
MENU = INTERIOR / "menu"
DATA = json.loads((MENU / "menu-data.json").read_text())
VERSION = "20261013-balanced-brand-1"
CATEGORIES = {c["id"]: c for c in DATA["categories"]}
BAR = next(g for g in DATA["groups"] if g["id"] == "bar")
BREAKFASTS = CATEGORIES["breakfasts"]
DESSERTS = CATEGORIES["desserts"]

def url(target, page, directory=False):
    path = os.path.relpath(target, page.parent).replace(os.sep, "/")
    return path + "/" if directory else path

def nav_url(path):
    target, separator, anchor = path.partition('#')
    if '?v=' not in target:
        target += '?v='+VERSION
    return target+(separator+anchor if separator else '')

def image(entry, page, extra_class=""):
    if entry.get("photo"):
        return ('<div class="item-photo '+extra_class+'"><img src="'+
                escape(url(ROOT / entry["photo"], page), quote=True)+'" alt="'+
                escape(entry["name"], quote=True)+'" loading="lazy" decoding="async"></div>')
    return ('<div class="item-photo menu-photo-placeholder '+extra_class+'" aria-hidden="true">'
            '<svg viewBox="0 0 48 48" fill="none"><rect x="7" y="10" width="34" height="28" rx="4"/>'
            '<circle cx="17" cy="19" r="3"/><path d="m8 33 10-10 8 8 6-6 9 9"/></svg>'
            '<span>Здесь будет фото</span></div>')

def prices(entry):
    # A missing price stays invisible. Zero is never a temporary price.
    variants = [v for v in (entry.get("variants") or [])
                if isinstance(v.get("price"), (int, float))
                and not isinstance(v["price"], bool) and v["price"] > 0]
    if not variants:
        return ''
    if len(variants) == 1:
        v = variants[0]
        portion = ' · '.join(x for x in [v.get("volume"), v.get("label")] if x)
        return ('<p class="item-price">'+escape(str(v["price"]))+' ₽</p>'+
                ('<p class="item-portion">'+escape(portion)+'</p>' if portion else ''))
    rows = []
    for v in variants:
        label = ' · '.join(x for x in [v.get("volume"), v.get("label")] if x)
        rows.append('<div class="variant-row"><span>'+escape(label)+'</span><strong>'+
                    escape(str(v["price"]))+' ₽</strong></div>')
    return '<div class="variant-list">'+''.join(rows)+'</div>'

def card(entry, page, dish=False):
    hit = '<span class="menu-hit">Хит</span>' if entry.get("hit") else ''
    contents = (image(entry, page)+'<div class="item-copy"><div class="item-title"><h3>'+
                escape(entry["name"])+hit+'</h3></div>'+prices(entry)+'</div>')
    identifier = ' id="'+escape(entry["id"], quote=True)+'"' if dish else ''
    if dish:
        target = url(MENU / "breakfasts" / entry["id"], page, True)+"?v="+VERSION
        contents = ('<a class="dish-card-link" href="'+target+'" aria-label="'+
                    escape('Подробнее: '+entry["name"], quote=True)+'">'+contents+'</a>')
    return '<article'+identifier+' class="menu-item">'+contents+'</article>'

def category_section(category, page, heading_level=2, dish=False):
    category_id = category["id"]
    heading_id = "heading-"+category_id
    heading = 'h'+str(heading_level)
    note = '<p class="category-note">'+escape(category["note"])+'</p>' if category.get("note") else ''
    items = ''.join(card(entry, page, dish) for entry in category["items"])
    if items:
        content = '<div class="item-grid">'+items+'</div>'
    else:
        content = '<p class="empty-category">Скоро добавим десерты.</p>'
    return ('<section class="menu-category" id="'+category_id+'" aria-labelledby="'+heading_id+'">'+
            '<'+heading+' id="'+heading_id+'">'+escape(category["title"])+'</'+heading+'>'+note+content+'</section>')

def drink_sections(page, heading_level=2):
    return ''.join(category_section(CATEGORIES[category_id], page, heading_level)
                   for category_id in BAR["categories"])

def drink_navigation():
    return ('<nav class="drink-category-nav" aria-label="Категории напитков">'+
            ''.join('<a class="menu-group-card" href="#'+category_id+'">'+
                    escape(CATEGORIES[category_id]["title"])+'</a>' for category_id in BAR["categories"])+
            '</nav>')

def footer(landing=False):
    allergy = '' if landing else '<p class="allergy-note">'+escape(DATA["allergy_note"])+'</p>'
    return ('<footer class="page-footer '+('landing-footer' if landing else 'menu-footer')+'">'+
            allergy+'<div class="contact-block"><a class="location-link" href="'+
            escape(DATA["location"]["url"], quote=True)+'" target="_blank" rel="noopener noreferrer">'+
            escape(DATA["location"]["address"])+'</a><a class="contact-phone" data-site-phone hidden>'
            '</a></div></footer>')

def document(page, title, description, content, body_class, back=None):
    back_link = '' if not back else '<a class="back-home" href="'+nav_url(back[0])+'">'+escape(back[1])+'</a>'
    landing = body_class == "landing-page"
    header_class = "landing-header" if landing else "menu-header"
    logo = url(ROOT / DATA.get("branding", {}).get("logo", "assets/logo.svg"), page)
    compat = '<script src="menu.js?v='+VERSION+'"></script>' if page == MENU / "index.html" else ''
    output = (
        '<!doctype html>\n<html lang="ru">\n<head>\n'
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '  <meta name="theme-color" content="#ffffff">\n'
        '  <meta name="description" content="'+escape(description, quote=True)+'">\n'
        '  <title>'+escape(title)+'</title>\n'
        '  <link rel="icon" type="image/svg+xml" href="'+url(ROOT / "assets/favicon.svg", page)+'">\n'
        '  <link rel="preload" href="'+url(ROOT / "assets/fonts/montserrat-brand-600.woff", page)+'" as="font" type="font/woff" crossorigin>\n'
        '  <link rel="stylesheet" href="'+url(INTERIOR / "interior.css", page)+'?v='+VERSION+'">\n'
        '</head>\n<body class="'+body_class+'">\n'
        '  <header class="site-header '+header_class+'"><a class="brand-logo" href="'+
        nav_url(url(INTERIOR, page, True))+'" aria-label="ZÁDU — главная"><img data-brand-logo src="'+logo+
        '" width="64" height="60" alt="Фирменный знак кофейни ZÁDU" decoding="async"><span class="brand-name">ZÁDU</span></a>'+
        back_link+'</header>\n  '+content+'\n  '+footer(landing)+
        '\n  <script src="'+url(INTERIOR / "site.js", page)+'?v='+VERSION+'"></script>\n  '+
        compat+'\n</body>\n</html>\n')
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text('\n'.join(line.rstrip() for line in output.splitlines())+'\n')

def nutrition_values(values):
    values = values or {}
    # Display only supplied values. Never calculate or estimate from a recipe.
    labels = [("calories", "Калории", "ккал"), ("protein", "Белки", "г"),
              ("fat", "Жиры", "г"), ("carbohydrates", "Углеводы", "г")]
    basis = '<p class="nutrition-basis">'+escape(values["basis"])+'</p>' if values.get("basis") else ''
    rows = []
    for key, label, unit in labels:
        value = values.get(key)
        text = escape(str(value))+' '+unit if value is not None else 'Уточняется'
        rows.append('<div><dt>'+label+'</dt><dd>'+text+'</dd></div>')
    return basis+'<dl class="nutrition-grid">'+''.join(rows)+'</dl>'

def nutrition(entry):
    options = entry.get("nutrition_variants")
    if options:
        return ''.join(
            '<div class="nutrition-option"><h3>'+escape(option["label"])+
            '</h3>'+nutrition_values(option.get("nutrition"))+'</div>'
            for option in options)
    return nutrition_values(entry.get("nutrition"))

# Keep the already distributed QR address. A fresh landing URL avoids a cached
# homepage sending guests into an earlier revision of the menu.
(ROOT / "index.html").write_text(
    '<!doctype html>\n<html lang="ru"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<meta name="theme-color" content="#ffffff"><title>ZÁDU — меню</title>'
    '<script>window.location.replace("interior/?visit="+Date.now());</script>'
    '<noscript><meta http-equiv="refresh" content="0;url=interior/?v='+VERSION+'"></noscript>'
    '</head><body style="margin:0;padding:40px;background:#fff;color:#4f523d;font-family:Arial,sans-serif">'
    '<a href="interior/?v='+VERSION+'" style="color:inherit">Открыть меню ZÁDU</a>'
    '</body></html>\n')

landing_page = INTERIOR / "index.html"
landing_content = (
    '<main class="landing-main"><h1 class="visually-hidden">Кондитерская и кофейня ZÁDU</h1>'
    '<div class="interior-frame"><img class="interior-photo" data-interior-photo hidden'
    ' alt="Интерьер кофейни ZÁDU" decoding="async">'
    '<div class="interior-placeholder" data-interior-placeholder aria-hidden="true">'
    '<svg class="interior-placeholder-icon" viewBox="0 0 96 96" fill="none">'
    '<path d="M17 13h62v45H17zM48 13v45M17 35h62M27 76h42M34 76v12M62 76v12'
    'M12 62v26M12 75h14M84 62v26M70 75h14" stroke="currentColor" stroke-width="1.5"'
    ' stroke-linecap="round"/></svg><span>Место для фото интерьера</span></div>'
    '<nav class="interior-actions" aria-label="Меню и отзыв о кофейне">'
    '<a class="interior-action" href="menu/?v='+VERSION+'">Посмотреть меню</a>'
    '<a class="interior-action" href="https://2gis.ru/makhachkala/firm/70000001098754589/tab/reviews"'
    ' target="_blank" rel="noopener noreferrer"'
    ' aria-label="Отзыв о ZÁDU в 2ГИС, откроется новая вкладка">Отзыв</a></nav></div></main>')
document(landing_page, "ZÁDU — кофейня и меню", "Кондитерская и кофейня ZÁDU. Меню и контакты.",
         landing_content, "landing-page")

menu_page = MENU / "index.html"
group_content = (
    '<main class="menu-layout"><h1>Меню</h1><nav class="menu-group-list" aria-label="Основные разделы меню">'
    '<a class="menu-group-card" href="breakfasts/?v='+VERSION+'">Завтраки</a>'
    '<a class="menu-group-card" href="desserts/?v='+VERSION+'">Десерты</a>'
    '<a class="menu-group-card" href="bar/?v='+VERSION+'">Напитки</a></nav>'
    '<p class="menu-help">Нажми на фото блюда, чтобы посмотреть описание и КБЖУ.</p>'+
    category_section(BREAKFASTS, menu_page, dish=True)+category_section(DESSERTS, menu_page)+
    '<section class="drinks-section" id="drinks" aria-labelledby="heading-drinks">'
    '<h2 id="heading-drinks">Напитки</h2>'+drink_sections(menu_page, 3)+'</section></main>')
document(menu_page, "Меню — ZÁDU", "Завтраки, десерты и напитки кофейни ZÁDU — всё меню на одной странице.", group_content, "menu-page",
         (url(INTERIOR, menu_page, True), "← На главную"))

breakfast_page = MENU / "breakfasts/index.html"
breakfast_content = ('<main class="breakfast-layout" id="breakfasts"><h1>Завтраки</h1><div class="item-grid">'+
                     ''.join(card(e, breakfast_page, True) for e in BREAKFASTS["items"])+'</div></main>')
document(breakfast_page, "Завтраки — ZÁDU", "Завтраки ZÁDU. Выберите блюдо, чтобы посмотреть подробности.",
         breakfast_content, "menu-page breakfast-page", (url(MENU, breakfast_page, True), "← К меню"))

dessert_page = MENU / "desserts/index.html"
dessert_content = ('<main class="dessert-layout"><h1>Десерты</h1>'+
                   ('<div class="item-grid">'+''.join(card(e, dessert_page) for e in DESSERTS["items"])+
                    '</div>' if DESSERTS["items"] else '<p class="empty-category">Скоро добавим десерты.</p>')+'</main>')
document(dessert_page, "Десерты — ZÁDU", "Десерты кофейни ZÁDU.", dessert_content,
         "menu-page dessert-page", (url(MENU, dessert_page, True), "← К меню"))

bar_page = MENU / "bar/index.html"
document(bar_page, "Напитки — бар ZÁDU", "Кофе, чай, коктейли, фреши, шоты и лимонады ZÁDU.",
         '<main class="bar-layout"><h1>Напитки</h1>'+drink_navigation()+drink_sections(bar_page)+'</main>',
         "menu-page bar-page", (url(MENU, bar_page, True), "← К меню"))

for entry in BREAKFASTS["items"]:
    dish_page = MENU / "breakfasts" / entry["id"] / "index.html"
    description = escape(entry["description"]) if entry.get("description") else 'Описание уточняется.'
    return_to_card = nav_url(url(MENU / "breakfasts", dish_page, True)+'#'+entry["id"])
    price_content = prices(entry)
    price_section = ('<section class="dish-section dish-price"><h2>Цена</h2>'+
                     price_content+'</section>') if price_content else ''
    details = (
        '<main class="dish-layout"><div class="dish-image">'+image(entry, dish_page, "dish-photo")+
        '</div><div class="dish-copy"><h1>'+escape(entry["name"])+'</h1>'
        '<section class="dish-section"><p>'+description+'</p></section>'
        '<section class="dish-section"><h2>КБЖУ</h2>'+nutrition(entry)+'</section>'+
        price_section+
        '<a class="return-to-breakfasts" href="'+return_to_card+'">← Все завтраки</a></div></main>')
    document(dish_page, entry["name"]+" — ZÁDU", entry.get("description", entry["name"]), details,
             "menu-page dish-page", (return_to_card, "← К завтракам"))

print("Rendered landing, menu,", len(BREAKFASTS["items"]), "dish pages and",
      sum(len(CATEGORIES[key]["items"]) for key in BAR["categories"]), "drinks in the bar.")
