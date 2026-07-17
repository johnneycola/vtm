# ==========================================
# n1_r200_1 — "Ты хорошая..."
# Клэр уходит, дальше — сцена в баре (n1_r300_join)
# ==========================================

label n1_r200_1:

    d "В смысле... я хотел сказать, что ты производишь впечатление довольно заботливого и чуткого человека. Как тебя можно было бросить?"
# Дамьен — Клэр
    hide bg
    hide damien front
    hide claire back
    pause char_transition_pause
    show bg bar_inside at bg_pos
    show claire front at claire_front_pos
    show damien back at damien_back_pos
    c "Мы знакомы, что-то типа... две минуты. Быстро ты сделал выводы."
# Клэр — Дамьен
    hide bg
    hide claire front
    hide damien back
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos
    show claire back at claire_back_pos
    d "Я хорошо разбираюсь в людях."
    think "Ты нихера не разбираешься в людях."
# Дамьен — Клэр
    hide bg
    hide damien front
    hide claire back
    pause char_transition_pause
    show bg bar_inside at bg_pos
    show claire front at claire_front_pos
    show damien back at damien_back_pos
    c "Я изменила ему."
    d "А... Ну... Я думаю, у тебя на то были причины."
    c "Может быть. Ладно, давай закроем эту тему."
    c "Хорошо тебе выступить, Damn."
# Клэр уходит    
    show claire front at claire_front_leave
    hide claire front
    "Она взяла сигареты со стойки и ушла."
    think "Молодец."
    "Я оборачиваюсь."

    jump n1_r300_join
