################################################################################
## Тестовые полигоны для подбора расположения персонажей на 2/3/4 человека.
## Без звука — только фон (бар/сцена) и персонажи. У каждой сцены два кадра:
## кадр 1 — одна сторона спиной, другая лицом; кадр 2 — меняются местами
## через обычный переход (hide+pause+show, как везде в игре).
##
## Прыгать сюда через дев-меню (Shift+D -> Jump to a Label), это не часть
## сюжета — обычный тестовый полигон, чтобы подбирать координаты.
################################################################################

# ------------------------------------------
# 2 персонажа — Дамьен + Клэр
# ------------------------------------------
label test_2_chars:

    show bg bar_inside at bg_pos
    show damien back at damien_back_pos zorder 1
    show claire front at claire_front_pos zorder 0
    "Кадр 1 — Дамьен спиной, Клэр лицом."

    hide bg
    hide damien back
    hide claire front
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos zorder 0
    show claire back at claire_back_pos zorder 1
    "Кадр 2 — поменялись местами."

    return


# ------------------------------------------
# 3 персонажа — Дамьен+Митч (пара) и Клифф (один)
# ------------------------------------------
label test_3_chars:

    show bg bar_inside at bg_pos
    show damien back at damien_back_pos_3left zorder 1
    show mitch back at mitch_back_pos_3right zorder 1
    show lance front at lance_front_pos_3 zorder 0
    "Кадр 1 — Дамьен+Митч спиной, Клифф лицом."

    hide bg
    hide damien back
    hide mitch back
    hide lance front
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos_3right zorder 0
    show mitch front at mitch_front_pos_3left zorder 0
    show lance back at lance_back_pos_3 zorder 1
    "Кадр 2 — поменялись местами."

    return


# ------------------------------------------
# 4 персонажа — Дамьен+Митч (пара) и Лэнс+Клэр (пара)
# ------------------------------------------
label test_4_chars:

    show bg bar_inside at bg_pos
    show damien back at damien_back_pos_4left zorder 1
    show mitch back at mitch_back_pos_4right zorder 1
    show lance front at lance_front_pos_4left zorder 0
    show claire front at claire_front_pos_4right zorder 0
    "Кадр 1 — Дамьен+Митч спиной, Лэнс+Клэр лицом."

    hide bg
    hide damien back
    hide mitch back
    hide lance front
    hide claire front
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos_4right zorder 0
    show mitch front at mitch_front_pos_4left zorder 0
    show lance back at lance_back_pos_4right zorder 1
    show claire back at claire_back_pos_4left zorder 1
    "Кадр 2 — поменялись местами."

    return
