# ==========================================
# n1_r400 — Сцена в баре, куда Дамьен идёт выступать.
# Точка входа из двух мест:
#   - n1_r300_claire_survived (звук двери играется ДО jump, там же)
#   - n1_r200_1 (без звука двери)
# Фон и звук ставим защищённо (проверяем, что ещё не на bar_scene),
# чтобы не было лишней анимации фона, если он уже такой.
# ==========================================

label n1_r400:

    hide damien front
    hide damien back
    hide claire front
    hide claire back

    if not renpy.showing("bg bar_scene"):
        hide bg
        pause char_transition_pause
        show bg bar_scene at bg_pos

    play ambience "audio/ambience/bar.ogg" fadeout 1.0 fadein 1.0

    "Сцена на которой нам придётся выступать, конечно, мда…"
    "Платформа дюймов 10 высотой, пара комбиков, журавлей и стульев. Хорошо, хоть, ударка есть."

    return
