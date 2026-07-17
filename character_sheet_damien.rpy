################################################################################
## Лист персонажа — Дамьен «Damn» Грегори
## Полностью переверстано с нуля. Терминология сверена с vtm-5.com.
################################################################################

################################################################################
## ДАННЫЕ. Каждый показатель — отдельная переменная (используются дальше
## в игре для бросков/проверок), а не просто значение внутри списка.
################################################################################

# ---------- Общее ----------
default cs_name        = "Дамьен «Damn» Грегори"
default cs_clan         = "Каитифф"
default cs_predator     = "Искуситель"
default cs_generation   = "13"
default cs_ambition     = "Стать легендой рока"
default cs_desire       = "Написать хит"

# ---------- Атрибуты (Физические / Социальные / Ментальные) ----------
default cs_strength     = 2
default cs_dexterity    = 2
default cs_stamina      = 3

default cs_charisma     = 4
default cs_manipulation = 3
default cs_composure    = 1

default cs_intelligence = 2
default cs_wits         = 3
default cs_resolve      = 2

# ---------- Навыки (Физические / Социальные / Ментальные) ----------
default cs_athletics    = 1
default cs_brawl        = 2
default cs_craft        = 0
default cs_drive        = 2
default cs_firearms     = 1
default cs_larceny      = 0
default cs_melee        = 1
default cs_stealth      = 1
default cs_survival     = 0

default cs_animal_ken   = 0
default cs_etiquette    = 1
default cs_insight      = 2
default cs_intimidation = 1
default cs_leadership   = 2
default cs_performance  = 3
default cs_persuasion   = 3
default cs_streetwise   = 2
default cs_subterfuge   = 3

default cs_academics     = 0
default cs_awareness     = 1
default cs_finance       = 0
default cs_investigation = 0
default cs_medicine      = 0
default cs_occult        = 0
default cs_politics      = 0
default cs_science       = 0
default cs_technology    = 0

# Специализации навыков — без скобок, отдельной строкой под навыком.
default cs_specializations = {
    "leadership": ["группа"],
    "performance": ["гитара", "вокал"],
    "persuasion": ["соблазнение"],
}

# ---------- Дисциплины ----------
default cs_disc_presence = 2   # Величие (Presence)
default cs_disc_auspex   = 2   # Ясновидение (Auspex)

default cs_presence_powers = [
    ("Трепет", "Делает Дамьена привлекательным и харизматичным; добавляет "
               "рейтинг Величия к проверкам Убеждения и Исполнения."),
    ("Мельпомена", "Позволяет использовать силы Величия на целях, которые "
                   "не видят, но слышат Дамьена."),
]

default cs_auspex_powers = [
    ("Обострённые чувства", "Сверхъестественно обостряет чувства; добавляет "
                            "рейтинг Ясновидения к проверкам Наблюдательности."),
    ("Предчувствие", "Даёт смутные видения о надвигающейся опасности или "
                     "важном событии."),
]

# ---------- Показатели ----------
default cs_health_damage    = 0   # сколько клеток здоровья повреждено
default cs_willpower_damage = 0   # сколько клеток силы воли потрачено
default cs_humanity         = 7   # из 10
default cs_doubts           = 1   # из (10 - cs_humanity) — заполняются с конца трека
default cs_hunger           = 3   # из 5


init python:

    def cs_health_max():
        return cs_stamina + 3

    def cs_willpower_max():
        return cs_composure + cs_resolve

    def cs_health_filled():
        return max(0, cs_health_max() - cs_health_damage)

    def cs_willpower_filled():
        return max(0, cs_willpower_max() - cs_willpower_damage)

    def cs_dots(value, maximum=5, filled_color="#ae5334", empty_color="#ffffff"):
        """Строка из закрашенных/пустых точек: ●●●○○. Закрашенные —
        filled_color, пустые — empty_color (через встроенные текстовые
        теги Ren'Py)."""
        value = max(0, min(value, maximum))
        filled = u"\u25CF" * value
        empty = u"\u25CB" * (maximum - value)
        return u"{color=%s}%s{/color}{color=%s}%s{/color}" % (filled_color, filled, empty_color, empty)

    def cs_dots_grouped(value, maximum, group=5, filled_color="#ae5334", empty_color="#ffffff"):
        """То же самое, но с разбивкой на группы по 5 через пробел —
        для Здоровья/Силы воли/Человечности, где точек может быть больше 5."""
        parts = []
        remaining_value = value
        remaining_max = maximum
        while remaining_max > 0:
            chunk = min(group, remaining_max)
            chunk_value = max(0, min(remaining_value, chunk))
            parts.append(cs_dots(chunk_value, chunk, filled_color, empty_color))
            remaining_value -= chunk_value
            remaining_max -= chunk
        return u" ".join(parts)

    def cs_humanity_dots(humanity, doubts, maximum=10, group=5,
                          filled_color="#ae5334", empty_color="#ffffff", doubt_color="#ffffff"):
        """Трек Человечности с третьим состоянием — Сомнения: ● закрашено,
        ○ пусто, ◐ сомнение. Порядок вдоль всего трека: сначала закрашенные,
        потом пустые, и только в самом конце — сомнения (то есть сомнения
        "съедают" пустые клетки с конца трека, не трогая закрашенные)."""
        humanity = max(0, min(humanity, maximum))
        doubts = max(0, min(doubts, maximum - humanity))
        empty_count = maximum - humanity - doubts

        cells = ([(u"\u25CF", filled_color)] * humanity +
                 [(u"\u25CB", empty_color)] * empty_count +
                 [(u"\u25D0", doubt_color)] * doubts)

        parts = []
        for i in range(0, maximum, group):
            chunk = cells[i:i + group]
            chunk_str = u""
            run_char = u""
            run_color = None
            for ch, color in chunk:
                if color == run_color:
                    run_char += ch
                else:
                    if run_color is not None:
                        chunk_str += u"{color=%s}%s{/color}" % (run_color, run_char)
                    run_color = color
                    run_char = ch
            if run_color is not None:
                chunk_str += u"{color=%s}%s{/color}" % (run_color, run_char)
            parts.append(chunk_str)

        return u" ".join(parts)

    def cs_specs_line(skill_key):
        specs = cs_specializations.get(skill_key)
        return u", ".join(specs) if specs else u""


################################################################################
## ЭКРАН
################################################################################

define CS_WIDTH = 1220
define CS_HEIGHT = 780
define CS_PADDING = 10
define CS_COL_WIDTH = 360
define CS_COL_GUTTER = 20
define CS_COL_TEXT_WIDTH = CS_COL_WIDTH - (CS_COL_GUTTER * 2)
define CS_DOTS_COL_WIDTH = 110
define CS_LABEL_COL_WIDTH = CS_COL_TEXT_WIDTH - CS_DOTS_COL_WIDTH
define CS_CONTENT_WIDTH = CS_WIDTH - 2 - (CS_PADDING * 2)
define CS_VIEWPORT_WIDTH = CS_CONTENT_WIDTH - 30   # с запасом под скроллбар
define CS_VBAR_TOP_GAP = 45   # скроллбар начинается ниже крестика закрытия


################################################################################
## Переиспользуемая строка "подпись + точки" — две жёстко зафиксированные
## под-колонки: слева подпись (левый край), справа точки (правый край).
## Так надёжнее, чем xfill/расчёт ширины — выравнивание не зависит от
## того, насколько точно посчитана ширина текста.
################################################################################

screen cs_stat_line(label, value, maximum=5):
    hbox:
        xsize CS_COL_TEXT_WIDTH
        fixed:
            xsize CS_LABEL_COL_WIDTH
            ysize 24
            text label font FONT_BODY size 15 color "#ffffff" xalign 0.0
        fixed:
            xsize CS_DOTS_COL_WIDTH
            ysize 24
            text cs_dots(value, maximum) font "DejaVuSans.ttf" size 15 xalign 1.0


################################################################################
## Кнопка вызова листа персонажа — всегда на экране (оверлей), поверх
## диалогов, вариантов ответа, мини-игры и т.п. Сам лист (modal True,
## zorder 300) при открытии перекрывает её — второй раз нажать нельзя,
## пока не закрыт крестиком, это ожидаемо.
################################################################################

screen cs_open_button():

    button:
        xpos 50
        ypos 10
        background None
        hover_background "#ae533440"
        action Show("character_sheet_damien")

        add "ui/ch-sh.webp"


## Гарантирует, что кнопка показана в игре всегда, как и quick_menu в
## screens.rpy (тот же приём: config.overlay_screens).
init python:
    config.overlay_screens.append("cs_open_button")


screen character_sheet_damien():

    modal True
    zorder 300

    fixed:
        xpos 50
        yalign 0.5
        xsize CS_WIDTH
        ysize CS_HEIGHT

        # Чёрная полупрозрачная подложка на всю панель.
        add Solid("#00000080") xsize CS_WIDTH ysize CS_HEIGHT

        # Контур 1px — четыре тонкие линии поверх подложки, а не
        # вложенные frame+padding (тот способ не сжимался как надо).
        add Solid("#ae5334") xsize CS_WIDTH ysize 1 xpos 0 ypos 0
        add Solid("#ae5334") xsize CS_WIDTH ysize 1 xpos 0 ypos (CS_HEIGHT - 1)
        add Solid("#ae5334") xsize 1 ysize CS_HEIGHT xpos 0 ypos 0
        add Solid("#ae5334") xsize 1 ysize CS_HEIGHT xpos (CS_WIDTH - 1) ypos 0

        frame:
            xfill True
            yfill True
            background None
            padding (CS_PADDING, CS_PADDING)

            fixed:
                xfill True
                yfill True

                viewport:
                    id "cs_viewport"
                    xsize CS_VIEWPORT_WIDTH
                    yfill True
                    mousewheel True
                    draggable True

                    vbox:
                        xsize CS_VIEWPORT_WIDTH
                        spacing 14

                        use cs_row_1_name
                        use cs_row_2_clan
                        use cs_row_3_ambition
                        use cs_row_4_attr_header
                        use cs_row_5_attr_subheaders
                        use cs_row_6_attr_values
                        use cs_row_7_skills_header
                        use cs_row_8_skills_values
                        use cs_row_9_disc_header
                        use cs_row_10_disc_values
                        use cs_row_11_disc_powers
                        use cs_row_12_stats_a
                        use cs_row_13_stats_b

                vbar:
                    value YScrollValue("cs_viewport")
                    xsize 5
                    ypos CS_VBAR_TOP_GAP
                    ysize (CS_HEIGHT - (CS_PADDING * 2) - CS_VBAR_TOP_GAP)
                    xpos CS_VIEWPORT_WIDTH + 15
                    bar_resizing False
                    top_bar Solid("#00000000")
                    bottom_bar Solid("#00000000")
                    thumb Solid("#ae5334", xsize=5, ysize=50)
                    thumb_offset 0
                    unscrollable "hide"

        textbutton "✕":
            action Hide("character_sheet_damien")
            xalign 1.0
            yalign 0.0
            xoffset -18
            yoffset 14
            text_font "DejaVuSans.ttf"
            text_size 28
            text_color "#a9a9a9"
            text_hover_color "#ffffff"


################################################################################
## Строка 1 — Имя
################################################################################

screen cs_row_1_name():
    text "[cs_name]" font FONT_HEADING size 25 color "#ffffff" xoffset CS_COL_GUTTER


################################################################################
## Строка 2 — Клан / Поколение / Тип питания
################################################################################

screen cs_row_2_clan():
    hbox:
        spacing 0
        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                text "Клан: [cs_clan]" font FONT_BODY size 15 color "#ffffff"
        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                text "Поколение: [cs_generation]" font FONT_BODY size 15 color "#ffffff"
        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                text "Тип питания: [cs_predator]" font FONT_BODY size 15 color "#ffffff"


################################################################################
## Строка 3 — Цель / Желание / пусто
################################################################################

screen cs_row_3_ambition():
    hbox:
        spacing 0
        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                text "Цель: [cs_ambition]" font FONT_BODY size 15 color "#ffffff"
        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                text "Желание: [cs_desire]" font FONT_BODY size 15 color "#ffffff"
        vbox:
            xsize CS_COL_WIDTH


################################################################################
## Строка 4 — пусто / АТРИБУТЫ / пусто
################################################################################

screen cs_row_4_attr_header():
    hbox:
        spacing 0
        vbox:
            xsize CS_COL_WIDTH
        vbox:
            xsize CS_COL_WIDTH
            text "АТРИБУТЫ" font FONT_HEADING size 20 color "#ffffff" xalign 0.5
        vbox:
            xsize CS_COL_WIDTH


################################################################################
## Строка 5 — Физические / Социальные / Ментальные (курсив, серый, центр)
################################################################################

screen cs_row_5_attr_subheaders():
    hbox:
        spacing 0
        vbox:
            xsize CS_COL_WIDTH
            text "Физические" font FONT_NARRATION size 15 color "#a9a9a9" xalign 0.5
        vbox:
            xsize CS_COL_WIDTH
            text "Социальные" font FONT_NARRATION size 15 color "#a9a9a9" xalign 0.5
        vbox:
            xsize CS_COL_WIDTH
            text "Ментальные" font FONT_NARRATION size 15 color "#a9a9a9" xalign 0.5


################################################################################
## Строка 6 — атрибуты со значениями (выключка по двум краям)
################################################################################

screen cs_row_6_attr_values():
    hbox:
        spacing 0

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                xsize CS_COL_TEXT_WIDTH
                spacing 4
                use cs_stat_line("Сила", cs_strength)
                use cs_stat_line("Ловкость", cs_dexterity)
                use cs_stat_line("Выносливость", cs_stamina)

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                xsize CS_COL_TEXT_WIDTH
                spacing 4
                use cs_stat_line("Харизма", cs_charisma)
                use cs_stat_line("Манипуляция", cs_manipulation)
                use cs_stat_line("Самообладание", cs_composure)

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                xsize CS_COL_TEXT_WIDTH
                spacing 4
                use cs_stat_line("Интеллект", cs_intelligence)
                use cs_stat_line("Смекалка", cs_wits)
                use cs_stat_line("Упорство", cs_resolve)


################################################################################
## Строка 7 — пусто / НАВЫКИ / пусто
################################################################################

screen cs_row_7_skills_header():
    hbox:
        spacing 0
        vbox:
            xsize CS_COL_WIDTH
        vbox:
            xsize CS_COL_WIDTH
            text "НАВЫКИ" font FONT_HEADING size 20 color "#ffffff" xalign 0.5
        vbox:
            xsize CS_COL_WIDTH


################################################################################
## Строка 8 — навыки со значениями + специализация под навыком
################################################################################

screen cs_skill_line(label, value, spec_key):
    vbox:
        spacing 0
        use cs_stat_line(label, value)
        if cs_specs_line(spec_key):
            text cs_specs_line(spec_key) font FONT_NARRATION size 15 color "#a9a9a9"


screen cs_row_8_skills_values():
    hbox:
        spacing 0

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                xsize CS_COL_TEXT_WIDTH
                spacing 4
                use cs_skill_line("Атлетика", cs_athletics, "athletics")
                use cs_skill_line("Драка", cs_brawl, "brawl")
                use cs_skill_line("Ремесло", cs_craft, "craft")
                use cs_skill_line("Вождение", cs_drive, "drive")
                use cs_skill_line("Стрельба", cs_firearms, "firearms")
                use cs_skill_line("Воровство", cs_larceny, "larceny")
                use cs_skill_line("Фехтование", cs_melee, "melee")
                use cs_skill_line("Скрытность", cs_stealth, "stealth")
                use cs_skill_line("Выживание", cs_survival, "survival")

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                xsize CS_COL_TEXT_WIDTH
                spacing 4
                use cs_skill_line("Обращение с животными", cs_animal_ken, "animal_ken")
                use cs_skill_line("Этикет", cs_etiquette, "etiquette")
                use cs_skill_line("Проницательность", cs_insight, "insight")
                use cs_skill_line("Запугивание", cs_intimidation, "intimidation")
                use cs_skill_line("Лидерство", cs_leadership, "leadership")
                use cs_skill_line("Исполнение", cs_performance, "performance")
                use cs_skill_line("Убеждение", cs_persuasion, "persuasion")
                use cs_skill_line("Уличное чутьё", cs_streetwise, "streetwise")
                use cs_skill_line("Хитрость", cs_subterfuge, "subterfuge")

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                xsize CS_COL_TEXT_WIDTH
                spacing 4
                use cs_skill_line("Гуманитарные науки", cs_academics, "academics")
                use cs_skill_line("Наблюдательность", cs_awareness, "awareness")
                use cs_skill_line("Финансы", cs_finance, "finance")
                use cs_skill_line("Расследование", cs_investigation, "investigation")
                use cs_skill_line("Медицина", cs_medicine, "medicine")
                use cs_skill_line("Оккультизм", cs_occult, "occult")
                use cs_skill_line("Политика", cs_politics, "politics")
                use cs_skill_line("Естественные науки", cs_science, "science")
                use cs_skill_line("Техника", cs_technology, "technology")


################################################################################
## Строка 9 — пусто / ДИСЦИПЛИНЫ / пусто
################################################################################

screen cs_row_9_disc_header():
    hbox:
        spacing 0
        vbox:
            xsize CS_COL_WIDTH
        vbox:
            xsize CS_COL_WIDTH
            text "ДИСЦИПЛИНЫ" font FONT_HEADING size 20 color "#ffffff" xalign 0.5
        vbox:
            xsize CS_COL_WIDTH


################################################################################
## Строка 10 — Величие / Ясновидение / пусто (название + значение)
################################################################################

screen cs_row_10_disc_values():
    hbox:
        spacing 0

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                xsize CS_COL_TEXT_WIDTH
                use cs_stat_line("Величие", cs_disc_presence)

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                xsize CS_COL_TEXT_WIDTH
                use cs_stat_line("Ясновидение", cs_disc_auspex)

        vbox:
            xsize CS_COL_WIDTH


################################################################################
## Строка 11 — Силы дисциплин (название белым, описание серым, слева)
################################################################################

screen cs_power_line(power_name, power_desc):
    vbox:
        spacing 0
        text power_name font FONT_BODY size 15 color "#ffffff"
        text power_desc font FONT_BODY size 15 color "#a9a9a9" xsize CS_COL_TEXT_WIDTH


screen cs_row_11_disc_powers():
    hbox:
        spacing 0

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                xsize CS_COL_TEXT_WIDTH
                spacing 8
                for power_name, power_desc in cs_presence_powers:
                    use cs_power_line(power_name, power_desc)

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                xsize CS_COL_TEXT_WIDTH
                spacing 8
                for power_name, power_desc in cs_auspex_powers:
                    use cs_power_line(power_name, power_desc)

        vbox:
            xsize CS_COL_WIDTH


################################################################################
## Строка 12 — Здоровье / Человечность / Голод
################################################################################

screen cs_row_12_stats_a():
    hbox:
        spacing 0

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                text "Здоровье" font FONT_BODY size 15 color "#ffffff"
                text cs_dots_grouped(cs_health_filled(), 10) font "DejaVuSans.ttf" size 15

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                text "Человечность" font FONT_BODY size 15 color "#ffffff"
                text cs_humanity_dots(cs_humanity, cs_doubts) font "DejaVuSans.ttf" size 15

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                text "Голод" font FONT_BODY size 15 color "#ffffff"
                text cs_dots(cs_hunger, 5) font "DejaVuSans.ttf" size 15


################################################################################
## Строка 13 — Сила воли / пусто / пусто
################################################################################

screen cs_row_13_stats_b():
    hbox:
        spacing 0

        vbox:
            xsize CS_COL_WIDTH
            vbox:
                xoffset CS_COL_GUTTER
                text "Сила воли" font FONT_BODY size 15 color "#ffffff"
                text cs_dots_grouped(cs_willpower_filled(), 10) font "DejaVuSans.ttf" size 15

        vbox:
            xsize CS_COL_WIDTH

        vbox:
            xsize CS_COL_WIDTH
