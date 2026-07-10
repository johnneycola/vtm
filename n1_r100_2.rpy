# ==========================================
# n1_r100_2 — "Гаражная распродажа..."
# ==========================================

label n1_r100_2:

    d "Ухватил на гаражной распродаже в СанФране."
# Дамьен — Клэр    
    hide bg
    hide damien front
    hide claire back
    pause char_transition_pause
    show bg bar_inside at bg_pos
    show claire front at claire_front_pos
    show damien back at damien_back_pos
    c "Ты жил там? Или тоже был проездом?"
    d "У меня там квартира. Сейчас вот отыграю концерт и поеду домой."
    c "Чего?"
    c "Это же почти пять часов на машине!"
# Клэр — Дамьен
    hide bg
    hide claire front
    hide damien back
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos
    show claire back at claire_back_pos
    d "Ну не в мотеле же напротив оставаться."
    "Она с интересом приподняла одну бровь."

    jump n1_r100_join
