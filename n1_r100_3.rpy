# ==========================================
# n1_r100_3 — "Это кастом..."
# ==========================================

label n1_r100_3:

    d "Мне сделал её на заказ один мастер из Мельбурна."
# Дамьен — Клэр    
    hide bg
    hide damien front
    hide claire back
    pause char_transition_pause
    show bg bar_inside at bg_pos
    show claire front at claire_front_pos
    show damien back at damien_back_pos
    c "Ничего себе! Дорогущая небось? Или это экокожа?"
    d "Кенгуру."
    c "Чего?"
    "Она заливается смехом. Излишне громко."
    c "Ты прикалываешься?"
# Клэр — Дамьен
    hide bg
    hide claire front
    hide damien back
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos
    show claire back at claire_back_pos
    d "Я серьёзно. В Австралии какие-то типа квоты на добычу кожи кенгуру, так что всё легально и никакого браконьерства."
    c "Не знаю... всё равно как-то это дико и бесчеловечно."
    d "Тебе просто надо её примерить. Держи."
# Дамьен — Клэр    
    hide bg
    hide damien front
    hide claire back
    pause char_transition_pause
    show bg bar_inside at bg_pos
    show claire front at claire_front_pos
    show damien back at damien_back_pos
    "Она немного смущается когда я протягиваю куртку, но после секунды сомнения берёт и накидывает на плечи. Ей не идёт, но она расплывается в улыбке."
    d "Круто выглядишь. Нравится?"
    c "Ну, если ты говоришь, что в Австралии квоты и всё легально, то да. Действительно крутая."
# Клэр — Дамьен
    hide bg
    hide claire front
    hide damien back
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos
    show claire back at claire_back_pos

    jump n1_r100_join
