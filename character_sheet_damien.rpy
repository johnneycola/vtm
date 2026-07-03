# ============================================================
#  ЛИСТ ПЕРСОНАЖА — Дамьен «Damn» Грегори (Vampire: The Masquerade)
#
#  Открывается/закрывается через Show()/Hide(), а не через
#  call screen — так его можно вызвать в любой момент поверх
#  игры (см. кнопку в углу экрана в character_sheet_button.rpy),
#  не завязываясь на сюжетный стек call/return.
#
#      action Show("character_sheet_damien")   # открыть
#      action Hide("character_sheet_damien")   # закрыть
# ============================================================

init python:

    def cs_dots(value, maximum=5):
        """Возвращает строку из закрашенных/пустых точек: ●●●○○"""
        value = max(0, min(value, maximum))
        return u"\u25CF" * value + u"\u25CB" * (maximum - value)

    def cs_checks(filled, maximum):
        """Галочки для человечности: ✓ ✓ ✓ □ □"""
        filled = max(0, min(filled, maximum))
        return (u"\u2713 " * filled) + (u"\u25A1 " * (maximum - filled))

    def cs_find_stat_entry(name):
        """Ищет атрибут или навык по точному названию, возвращает
        (значение, список_специализаций). У атрибутов специализаций
        не бывает — для них вернётся пустой список.

        Специально бросает ошибку, если название не найдено — если в
        проверке опечататься в названии, это сразу будет видно (краш
        с понятным сообщением), а не тихо даст 0 кубиков в проверке."""
        for label, value in (cs_attr_physical + cs_attr_social + cs_attr_mental):
            if label == name:
                return value, []
        for label, value, specs in (cs_skills_physical + cs_skills_social + cs_skills_mental):
            if label == name:
                return value, specs
        raise Exception(
            "cs_find_stat_entry: на листе персонажа нет атрибута/навыка с названием '%s'. "
            "Проверь точное написание в cs_attr_*/cs_skills_* в character_sheet_damien.rpy."
            % name
        )

    def cs_find_stat(name):
        """Возвращает только значение атрибута/навыка (без специализаций)."""
        value, _ = cs_find_stat_entry(name)
        return value

    def cs_skill_label(name, specs):
        """Формирует подпись навыка со специализациями в скобках,
        как принято в VtM: 'Убеждение (соблазнение)'."""
        if specs:
            return u"%s (%s)" % (name, u", ".join(specs))
        return name

    def cs_dice_pool(*names, **kwargs):
        """Считает пул кубиков для проверки: сумма указанных атрибутов
        и/или навыков + бонус за специализацию (если указана и совпадает
        с одной из специализаций хотя бы одного из навыков) + свободный
        бонус.

        Пример без специализации:
            cs_dice_pool("Сила", "Скрытность")

        Пример со специализацией — если Дамьен убеждает через соблазнение,
        а не как-то иначе, добавляется +1 за специализацию навыка:
            cs_dice_pool("Харизма", "Убеждение", specialization="соблазнение")

        Пример с произвольным бонусом:
            cs_dice_pool("Харизма", "Обман", bonus=1)
        """
        bonus = kwargs.get("bonus", 0)
        specialization = kwargs.get("specialization", None)
        norm_spec = specialization.strip().lower() if specialization else None

        total = bonus
        for name in names:
            value, specs = cs_find_stat_entry(name)
            total += value
            if norm_spec and any(norm_spec == s.strip().lower() for s in specs):
                total += 1
        return total


# ---------------------------------------------------------------
# Данные листа персонажа. Вынесены в default, чтобы при желании
# их можно было менять по ходу игры (например, Hunger, Health).
# ---------------------------------------------------------------

default cs_name        = "Дамьен «Damn» Грегори"
default cs_clan         = "Отрекшийся (Caitiff)"
default cs_predator     = "Сирена (Siren)"
default cs_generation   = "13-е поколение"
default cs_sect         = "—"
default cs_ambition     = "Стать рок-легендой"
default cs_desire       = "Написать хит"

default cs_attr_physical = [("Сила", 2), ("Ловкость", 3), ("Выносливость", 2)]
default cs_attr_social   = [("Харизма", 4), ("Манипуляция", 3), ("Самообладание", 3)]
default cs_attr_mental   = [("Интеллект", 3), ("Сообразительность", 3), ("Решимость", 2)]

# Формат записи навыка: (название, значение, [список специализаций]).
# Специализация даёт +1 кубик, если конкретная проверка ей соответствует
# (передаётся через cs_dice_pool(..., specialization="...")). Навыков без
# специализации — пустой список.

default cs_skills_physical = [
    ("Атлетика", 1, []), ("Драка", 2, []), ("Ремесло", 0, []), ("Вождение", 2, []),
    ("Стрельба", 1, []), ("Кражи", 0, []), ("Холодное оружие", 1, []),
    ("Скрытность", 1, []), ("Выживание", 0, []),
]
default cs_skills_social = [
    ("Обращение с животными", 0, []), ("Этикет", 1, []), ("Проницательность", 2, []),
    ("Запугивание", 1, []), ("Лидерство", 2, ["группа"]), ("Выступление", 3, ["гитара", "вокал"]),
    ("Убеждение", 3, ["соблазнение"]), ("Уличное чутьё", 2, []), ("Обман", 3, []),
]
default cs_skills_mental = [
    ("Академические знания", 0, []), ("Внимательность", 1, []), ("Финансы", 0, []),
    ("Расследование", 0, []), ("Медицина", 0, []), ("Оккультизм", 0, []),
    ("Политика", 0, []), ("Наука", 0, []), ("Технологии", 0, []),
]

# powers: список (название, описание)
default cs_disciplines = [
    {
        "name": "Присутствие (Presence)",
        "level": 2,
        "powers": [
            ("Внушение (Awe)",
             "Делает Дамьена привлекательным и харизматичным; добавляет рейтинг "
             "Присутствия к проверкам Убеждения и Выступления."),
            ("Мелпомина (Melpominee)",
             "Позволяет использовать силы Присутствия на целях, которые не видят, "
             "но слышат Дамьена."),
        ],
    },
    {
        "name": "Прозрение (Auspex)",
        "level": 2,
        "powers": [
            ("Обострённые чувства (Heightened Senses)",
             "Сверхъестественно обостряет чувства; добавляет рейтинг Прозрения "
             "к проверкам восприятия."),
            ("Предчувствие (Premonition)",
             "Позволяет получать видения будущего."),
        ],
    },
]

default cs_health_max     = 6
default cs_health_filled  = 6
default cs_willpower_max    = 3
default cs_willpower_filled = 3
default cs_humanity_max    = 10
default cs_humanity_filled = 7
default cs_hunger_max    = 5
default cs_hunger_filled = 3

default cs_blood_potency = 1
default cs_blood_surge   = 2
default cs_bane_severity = 2
default cs_mend_amount   = "1 (поверхностный урон)"
default cs_rouse_reroll  = "Уровень 1"
default cs_clan_bane        = "Отверженный: повышение уровня дисциплин стоит XP, равное 6x нового уровня (вместо 5x)."
default cs_clan_compulsion  = "У Отрекшихся нет принуждения клана."

default cs_merits = [
    ("Ресурсы: доход и накопления", 1),
    ("Известность: узкая субкультура", 1),
    ("«Загляни в багажник»: лёгкий доступ", 1),
    ("Контакты: смертные информаторы", 1),
    ("Союзники: группа смертных советчиков", 1),
    ("Помощник: преданный смертный слуга", 2),
    ("Красавец: +1 кубик в социальных бросках", 2),
    ("Нет убежища (недостаток)", 1),
    ("Сталкеры: навязчивые поклонники (недостаток)", 1),
    ("Враг: бывшая любовница или ревнивец (недостаток)", 1),
]

default cs_conviction       = "Я никогда не продамся ради популярности (Говард Лич)"
default cs_touchstone_name  = "Говард Лич"
default cs_touchstone_desc  = (
    "Говард и Дамьен когда-то играли в одной группе. Говард в итоге продался — "
    "начал выкладывать ролики, гнаться за трендами и набрал аудиторию. Теперь он "
    "живёт безбедно, пока Дамьен выступает в дешёвых барах за бензин. Дамьен считает "
    "его предателем, но не может перестать издалека следить за его успехом."
)

default cs_sire        = "Неизвестен"
default cs_description = (
    "24-летний парень с длинными волосами, острыми скулами и томным взглядом, "
    "подчёркнутым чёрной подводкой. Носит винтажную кожаную косуху поверх майки, "
    "рваные скинни-джинсы и остроносые сапоги из змеиной кожи."
)
default cs_xp   = 15
default cs_rank = "—"


# ---------------------------------------------------------------
# Экран листа персонажа
#
# Ширина панели фиксирована. Высота — тоже: заголовок и
# переключатель страниц не прокручиваются, а под ними в фиксированной
# по высоте области (cs_viewport) крутится содержимое конкретной
# страницы — так на любой странице появляется скролл, если контент
# не влезает, а сама панель не растягивается на весь экран и на
# любом разрешении остаётся отступ сверху и снизу.
#
# Если хочется больше/меньше видимой области — поменяй ysize у
# viewport ниже (сейчас 520).
# ---------------------------------------------------------------

screen character_sheet_damien():

    modal True
    zorder 300

    default cs_page = 1

    # затемнение фона
    add "#000000cc"

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1206
        background Solid("#5c1a1a")
        padding (3, 3)

        # fixed — чтобы крестик закрытия лежал поверх содержимого
        # отдельным слоем и не был частью прокручиваемой области.
        # fit_first True — иначе fixed по умолчанию растягивается на
        # всё доступное место, а не подстраивается под размер панели.
        fixed:
            xsize 1200
            fit_first True

            frame:
                xsize 1200
                background Solid("#141014")
                padding (44, 30)

                vbox:
                    spacing 10
                    xsize 1112

                    # ---------- Шапка (не прокручивается) ----------
                    text "VAMPIRE" size 40 color "#d8d8d8" xalign 0.5
                    text "T H E   M A S Q U E R A D E" size 14 color "#8a8a8a" xalign 0.5

                    null height 6

                    hbox:
                        xsize 1112

                        add "damien_sprite":
                            xsize 110
                            ysize 110

                        null width 20

                        vbox:
                            spacing 2
                            xsize 640
                            text "[cs_name]" size 26 color "#ffffff"
                            text "Клан: [cs_clan]" size 15 color "#bbbbbb"
                            text "Тип хищника: [cs_predator]   •   Поколение: [cs_generation]" size 15 color "#bbbbbb"

                        vbox:
                            xsize 342
                            text "Амбиция: [cs_ambition]" size 14 color "#999999" xalign 1.0
                            text "Желание: [cs_desire]" size 14 color "#999999" xalign 1.0

                    null height 4
                    add Solid("#5c1a1a"):
                        xsize 1112
                        ysize 2

                    # ---------- Переключатель страниц (не прокручивается) ----------
                    hbox:
                        xalign 0.5
                        spacing 16

                        textbutton "Страница 1 — Лист":
                            action SetScreenVariable("cs_page", 1)
                            text_color "#888888"
                            text_hover_color "#ffffff"
                            text_selected_color "#cc3333"
                            selected (cs_page == 1)

                        textbutton "Страница 2 — Биография":
                            action SetScreenVariable("cs_page", 2)
                            text_color "#888888"
                            text_hover_color "#ffffff"
                            text_selected_color "#cc3333"
                            selected (cs_page == 2)

                    null height 8

                    # ---------- Содержимое (прокручивается) ----------
                    viewport:
                        id "cs_viewport"
                        xsize 1112
                        ysize 520
                        scrollbars "vertical"
                        mousewheel True
                        draggable True

                        vbox:
                            spacing 16
                            xsize 1088

                            if cs_page == 1:
                                use cs_sheet_page_1
                            else:
                                use cs_sheet_page_2

            # ---------- Крестик закрытия ----------
            # Лежит поверх панели отдельным слоем (внутри fixed, а не
            # внутри viewport), поэтому при скролле контента остаётся
            # на месте — в правом верхнем углу.
            textbutton "✕":
                action Hide("character_sheet_damien")
                xalign 1.0
                yalign 0.0
                xoffset -18
                yoffset 14
                text_size 28
                text_color "#999999"
                text_hover_color "#ffffff"


# ---------------------------------------------------------------
# Страница 1: Атрибуты / Навыки / Дисциплины / Показатели
# ---------------------------------------------------------------

screen cs_sheet_page_1():

    vbox:
        spacing 16
        xsize 1112

        # ---------- Атрибуты ----------
        text "АТРИБУТЫ" size 20 color "#cc3333"

        hbox:
            spacing 40

            vbox:
                spacing 4
                text "Физические" size 13 color "#888888" italic True
                for label, val in cs_attr_physical:
                    hbox:
                        text label size 16 color "#dddddd" xsize 190
                        text cs_dots(val, 5) size 16 color "#cc3333"

            vbox:
                spacing 4
                text "Социальные" size 13 color "#888888" italic True
                for label, val in cs_attr_social:
                    hbox:
                        text label size 16 color "#dddddd" xsize 190
                        text cs_dots(val, 5) size 16 color "#cc3333"

            vbox:
                spacing 4
                text "Ментальные" size 13 color "#888888" italic True
                for label, val in cs_attr_mental:
                    hbox:
                        text label size 16 color "#dddddd" xsize 190
                        text cs_dots(val, 5) size 16 color "#cc3333"

        # ---------- Навыки ----------
        text "НАВЫКИ" size 20 color "#cc3333"

        hbox:
            spacing 40

            vbox:
                spacing 3
                for name, val, specs in cs_skills_physical:
                    hbox:
                        text cs_skill_label(name, specs) size 14 color "#cccccc" xsize 190
                        text cs_dots(val, 5) size 14 color "#cc3333"

            vbox:
                spacing 3
                for name, val, specs in cs_skills_social:
                    hbox:
                        text cs_skill_label(name, specs) size 14 color "#cccccc" xsize 240
                        text cs_dots(val, 5) size 14 color "#cc3333"

            vbox:
                spacing 3
                for name, val, specs in cs_skills_mental:
                    hbox:
                        text cs_skill_label(name, specs) size 14 color "#cccccc" xsize 190
                        text cs_dots(val, 5) size 14 color "#cc3333"

        # ---------- Дисциплины ----------
        text "ДИСЦИПЛИНЫ" size 20 color "#cc3333"

        hbox:
            spacing 50

            for disc in cs_disciplines:
                vbox:
                    spacing 4
                    xsize 520
                    hbox:
                        text disc["name"] size 17 color "#b58ce0"
                        text "  " + cs_dots(disc["level"], 5) size 17 color "#cc3333"
                    for power_name, power_desc in disc["powers"]:
                        vbox:
                            spacing 0
                            text ("— " + power_name) size 13 color "#dddddd"
                            text power_desc size 12 color "#999999" xsize 500

        # ---------- Показатели ----------
        text "ПОКАЗАТЕЛИ" size 20 color "#cc3333"

        hbox:
            spacing 50

            vbox:
                spacing 2
                text "Здоровье" size 14 color "#888888"
                text cs_dots(cs_health_filled, cs_health_max) size 20 color "#dddddd"

            vbox:
                spacing 2
                text "Сила воли" size 14 color "#888888"
                text cs_dots(cs_willpower_filled, cs_willpower_max) size 20 color "#dddddd"

            vbox:
                spacing 2
                text "Человечность" size 14 color "#888888"
                text cs_checks(cs_humanity_filled, cs_humanity_max) size 16 color "#dddddd"

            vbox:
                spacing 2
                text "Голод" size 14 color "#888888"
                text cs_dots(cs_hunger_filled, cs_hunger_max) size 20 color "#cc3333"


# ---------------------------------------------------------------
# Страница 2: Убеждения / Кровь / Достоинства / Профиль
# ---------------------------------------------------------------

screen cs_sheet_page_2():

    vbox:
        spacing 16
        xsize 1112

        # ---------- Убеждения ----------
        text "УБЕЖДЕНИЯ" size 20 color "#cc3333"

        text "Догма: [cs_conviction]" size 14 color "#cccccc"

        vbox:
            spacing 2
            text "Точка опоры: [cs_touchstone_name]" size 14 color "#dddddd" bold True
            text "[cs_touchstone_desc]" size 13 color "#aaaaaa"

        # ---------- Кровь ----------
        text "КРОВЬ" size 20 color "#cc3333"

        hbox:
            text "Потенция крови  " size 15 color "#dddddd"
            text cs_dots(cs_blood_potency, 10) size 15 color "#cc3333"

        hbox:
            spacing 60
            text "Всплеск крови: [cs_blood_surge]" size 14 color "#cccccc"
            text "Тяжесть проклятия: [cs_bane_severity]" size 14 color "#cccccc"
            text "Восстановление: [cs_mend_amount]" size 14 color "#cccccc"
            text "Переброс пробуждения: [cs_rouse_reroll]" size 14 color "#cccccc"

        text "Проклятие клана:" size 14 color "#888888"
        text "[cs_clan_bane]" size 14 color "#cccccc"

        text "Принуждение клана:" size 14 color "#888888"
        text "[cs_clan_compulsion]" size 14 color "#cccccc"

        # ---------- Достоинства и недостатки ----------
        text "ДОСТОИНСТВА И НЕДОСТАТКИ" size 20 color "#cc3333"

        for label, val in cs_merits:
            hbox:
                text label size 14 color "#cccccc" xsize 420
                text cs_dots(val, 5) size 14 color "#cc3333"

        # ---------- Профиль ----------
        text "ОБРАЗ" size 20 color "#cc3333"

        text "[cs_description]" size 14 color "#cccccc"
        text "Прародитель: [cs_sire]" size 14 color "#999999"

        # ---------- Опыт ----------
        text "ОПЫТ: [cs_xp] XP   •   Ранг: [cs_rank]" size 14 color "#888888"
