"""Render the existing ZÁDU menu as ordinary, directly linkable HTML documents."""
from html import escape
import json
import os
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
INTERIOR = ROOT / "interior"
MENU = INTERIOR / "menu"
DATA = json.loads((MENU / "menu-data.json").read_text())
VERSION = "20261014-photo-loading-fix"
LANDING_STYLE_VERSION = "20261015-cafe-hours"
BREAKFAST_HOURS_NOTE = '<p class="breakfast-hours">Завтраки до 20:00</p>'
PLATE_SHADOW_PREVIEW_IDS = {"dish-1", "dish-2", "dish-3", "dish-4", "dish-5", "dish-8", "dish-6", "dish-7", "dish-7-shrimp"}
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
    if entry.get("photo_variants"):
        return ('<div class="dish-photo-gallery">'+''.join(
            image({"name": entry["name"], **option}, page, extra_class)
            for option in entry["photo_variants"])+ '</div>')
    if entry.get("photo"):
        # The supplied screenshots contain a centred photograph. Clip only the
        # phone's black margins in the layout; retain the original photo pixels.
        framing = ' original-dish-photo' if entry.get("photo_framing") == "center-591x442" else ''
        if entry.get("photo_framing") == "transparent-cutout":
            framing = ' cutout-dish-photo'
        shadow = ' plate-shadow-preview' if entry.get("id") in PLATE_SHADOW_PREVIEW_IDS else ''
        source = ROOT / entry["photo"]
        dimensions = ''
        if entry.get("photo_width") and entry.get("photo_height"):
            dimensions = f' width="{int(entry["photo_width"])}" height="{int(entry["photo_height"])}"'
        elif source.suffix.lower() == ".png":
            with source.open("rb") as supplied_photo:
                header = supplied_photo.read(24)
            if header[:8] == b'\x89PNG\r\n\x1a\n' and len(header) == 24:
                width, height = struct.unpack(">II", header[16:24])
                dimensions = f' width="{width}" height="{height}"'
        loading = "eager" if framing or extra_class == "dish-photo" else "lazy"
        photo = ('<div class="item-photo'+framing+shadow+' '+extra_class+'"><img src="'+
                escape(url(source, page)+"?v="+VERSION, quote=True)+'" alt="'+
                escape(entry.get("photo_alt") or entry["name"], quote=True)+
                '"'+dimensions+' loading="'+loading+'" decoding="async"></div>')
        if entry.get("photo_caption"):
            return ('<figure class="dish-photo-figure">'+photo+'<figcaption class="dish-photo-caption">'+
                    escape(entry["photo_caption"])+ '</figcaption></figure>')
        return photo
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
    if entry.get("compact_variant_prices"):
        amounts = ' / '.join(str(v["price"]) for v in variants)
        labels = ' / '.join(v["label"] for v in variants)
        accessible = '; '.join(v["label"]+': '+str(v["price"])+' ₽' for v in variants)
        return ('<p class="item-price" aria-label="'+escape(accessible, quote=True)+'">'+
                escape(amounts)+' ₽</p><p class="item-portion">'+escape(labels)+'</p>')
    rows = []
    for v in variants:
        label = ' · '.join(x for x in [v.get("volume"), v.get("label")] if x)
        rows.append('<div class="variant-row"><span>'+escape(label)+'</span><strong>'+
                    escape(str(v["price"]))+' ₽</strong></div>')
    return '<div class="variant-list">'+''.join(rows)+'</div>'

def dish_views(entry):
    if not entry.get("separate_photo_variants"):
        return [entry]
    views = []
    for option in entry["photo_variants"]:
        label = option["photo_caption"]
        view = {**entry, **option}
        for key in ("photo_variants", "separate_photo_variants", "photo_caption"):
            view.pop(key, None)
        selected = next(v for v in entry["variants"] if v.get("label") == label)
        view["variants"] = [{**selected, "label": None}]
        if entry.get("nutrition_variants"):
            supplied = next(v for v in entry["nutrition_variants"] if v["label"] == label)
            view["nutrition"] = supplied["nutrition"]
            view["nutrition_status"] = supplied["nutrition_status"]
            view.pop("nutrition_variants", None)
        if label == "С курицей":
            view["photo_alt"] = view["name"]
        else:
            view["id"] = entry["id"]+"-shrimp"
            view["name"] = option["photo_alt"]
            view.pop("reference_price_style", None)
        views.append(view)
    return views

def card(entry, page, dish=False):
    if entry.get("separate_photo_variants"):
        return ''.join(card(view, page, dish) for view in dish_views(entry))
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
    if category_id == "breakfasts":
        note = BREAKFAST_HOURS_NOTE + note
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
    hours = '<p class="cafe-hours">Время работы: 08:00–00:00</p>' if landing else ''
    allergy = '' if landing else '<p class="allergy-note">'+escape(DATA["allergy_note"])+'</p>'
    return ('<footer class="page-footer '+('landing-footer' if landing else 'menu-footer')+'">'+
            allergy+'<div class="contact-block"><a class="location-link" href="'+
            escape(DATA["location"]["url"], quote=True)+'" target="_blank" rel="noopener noreferrer">'+
            escape(DATA["location"]["address"])+'</a>'+hours+'<a class="contact-phone" data-site-phone hidden>'
            '</a></div></footer>')

def whatsapp_contact():
    number = DATA.get("location", {}).get("whatsapp", "")
    if not (isinstance(number, str) and number.isascii() and number.isdigit()
            and 7 <= len(number) <= 15):
        return ''
    return (
        '<a class="whatsapp-float" href="https://wa.me/'+number+'" target="_blank"'
        ' rel="noopener noreferrer" aria-label="Связаться с ZÁDU в WhatsApp, откроется новая вкладка">'
        '<span class="whatsapp-float-label">Связаться в Whatsapp</span>'
        '<span class="whatsapp-float-icon" aria-hidden="true">'
        '<svg viewBox="0 0 48 48" focusable="false">'
        '<path d="M40 23a17 17 0 0 1-25 15l-8 3 2.7-8.5A17 17 0 1 1 40 23Z"/>'
        '<path d="M15 18h16M15 22h16M15 26h12"/></svg></span></a>')

def document(page, title, description, content, body_class, back=None):
    back_link = '' if not back else '<a class="back-home" href="'+nav_url(back[0])+'">'+escape(back[1])+'</a>'
    landing = body_class == "landing-page"
    style_version = (LANDING_STYLE_VERSION if landing else
                     "20261015-breakfast-hours" if 'class="breakfast-hours"' in content else
                     "20261015-plate-shadow-preview" if "cutout-dish-photo" in content else VERSION)
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
        '  <link rel="stylesheet" href="'+url(INTERIOR / "interior.css", page)+'?v='+
        style_version+'">\n'
        '</head>\n<body class="'+body_class+'">\n'
        '  <header class="site-header '+header_class+'"><a class="brand-logo" href="'+
        nav_url(url(INTERIOR, page, True))+'" aria-label="ZÁDU — главная"><img data-brand-logo src="'+logo+
        '" width="64" height="60" alt="Фирменный знак кофейни ZÁDU" decoding="async"><span class="brand-name">ZÁDU</span></a>'+
        back_link+'</header>\n  '+content+'\n  '+footer(landing)+
        ('\n  '+whatsapp_contact() if landing else '')+
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
            '<div class="nutrition-option"><h3>'+escape(option["label"].rstrip(':'))+':'+
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
interior = DATA.get("interior", {})
interior_source = (' src="'+escape(url(ROOT / interior["photo"], landing_page), quote=True)+'"'
                   if interior.get("photo") else ' hidden')
interior_alt = escape(interior.get("photo_alt") or "Интерьер кофейни ZÁDU", quote=True)
placeholder_hidden = ' hidden' if interior.get("photo") else ''
landing_content = (
    '<main class="landing-main"><h1 class="visually-hidden">Кондитерская и кофейня ZÁDU</h1>'
    '<div class="interior-frame"><img class="interior-photo" data-interior-photo'+interior_source+
    ' alt="'+interior_alt+'" decoding="async" fetchpriority="high">'
    '<div class="interior-placeholder" data-interior-placeholder'+placeholder_hidden+' aria-hidden="true">'
    '<svg class="interior-placeholder-icon" viewBox="0 0 96 96" fill="none">'
    '<path d="M17 13h62v45H17zM48 13v45M17 35h62M27 76h42M34 76v12M62 76v12'
    'M12 62v26M12 75h14M84 62v26M70 75h14" stroke="currentColor" stroke-width="1.5"'
    ' stroke-linecap="round"/></svg><span>Место для фото интерьера</span></div>'
    '<nav class="interior-actions" aria-label="Меню и отзыв о кофейне">'
    '<a class="interior-action" href="menu/?v='+VERSION+'">Меню</a>'
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
breakfast_content = ('<main class="breakfast-layout" id="breakfasts"><h1>Завтраки</h1>'+BREAKFAST_HOURS_NOTE+'<div class="item-grid">'+
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

DISH_VIEWS = [view for entry in BREAKFASTS["items"] for view in dish_views(entry)]
for entry in DISH_VIEWS:
    dish_page = MENU / "breakfasts" / entry["id"] / "index.html"
    description = escape(entry["description"]) if entry.get("description") else 'Описание уточняется.'
    return_to_card = nav_url(url(MENU / "breakfasts", dish_page, True)+'#'+entry["id"])
    price_content = prices(entry)
    price_section = ('<section class="dish-section dish-price" aria-label="Цена">'+
                     price_content+'</section>') if price_content else ''
    details = (
        '<main class="dish-layout"><div class="dish-image">'+image(entry, dish_page, "dish-photo")+
        '</div><div class="dish-copy"><h1>'+escape(entry["name"])+'</h1>'
        '<section class="dish-section"><p>'+description+'</p></section>'+
        price_section+
        '<section class="dish-section"><h2>КБЖУ</h2>'+nutrition(entry)+'</section>'+
        '<a class="return-to-breakfasts" href="'+return_to_card+'">← Все завтраки</a></div></main>')
    document(dish_page, entry["name"]+" — ZÁDU", entry.get("description", entry["name"]), details,
             "menu-page dish-page", (return_to_card, "← К завтракам"))

print("Rendered landing, menu,", len(DISH_VIEWS), "dish pages and",
      sum(len(CATEGORIES[key]["items"]) for key in BAR["categories"]), "drinks in the bar.")
