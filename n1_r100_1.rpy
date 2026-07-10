# ==========================================
# n1_r100_1 — "Купил на Сицилии..."
# ==========================================

label n1_r100_1:

    d "Это итальянский винтаж. Купил, когда отдыхал на Сицилии."
# Дамьен — Клэр    
    hide bg
    hide damien front
    hide claire back
    pause char_transition_pause
    show bg bar_inside at bg_pos
    show claire front at claire_front_pos
    show damien back at damien_back_pos
    c "Ага..."
    "Она замолчала. Видно как шестерёнки со скрипом зашевелились у неё в голове. Думаю, пытается вспомнить, где находится Сицилия."
    c "И как там?"
# Клэр — Дамьен
    hide bg
    hide claire front
    hide damien back
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos
    show claire back at claire_back_pos
    d "Где? На Сицилии? Нормально. Звали выступать на корпоративе у местного босса мафии."
    "Она оживилась."
# Дамьен — Клэр    
    hide bg
    hide damien front
    hide claire back
    pause char_transition_pause
    show bg bar_inside at bg_pos
    show claire front at claire_front_pos
    show damien back at damien_back_pos
    c "Правда?!"
# Клэр — Дамьен
    hide bg
    hide claire front
    hide damien back
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos
    show claire back at claire_back_pos
    d "Нет."
    "Она излишне громко рассмеялась."

    jump n1_r100_join
