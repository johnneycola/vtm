# ==========================================
# ОБЩИЙ СЮЖЕТ
# Ночь 1
# ==========================================

label start:

    jump n1


label n1:
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos
    show claire back at claire_back_pos
    c "Ты сегодня выступаешь?"
    d "А?"
    c "Говорю, привет, ты сегодня выступаешь?"
    d "Да. Как ты догадалась?"
    c "Куртка у тебя крутая. Здесь в таких не ходят."
# Дамьен — Клэр    
    hide bg
    hide damien front
    hide claire back
    pause char_transition_pause
    show bg bar_inside at bg_pos
    show claire front at claire_front_pos
    show damien back at damien_back_pos
    c "Я Клэр."
    "Она протягивает руку."
# Клэр — Дамьен
    hide bg
    hide claire front
    hide damien back
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos
    show claire back at claire_back_pos
    d "Damn."
    c "M?"
    d "Я Дамьен, но вообще Damn."
    "Я пожимаю её руку. У неё мягкая, влажная, пухлая ладонь."
    d "Так, значит ты увидела мою куртку и потому решила, что я сегодня выступаю?"
    c "Йеп. Где ты её достал? Мне очень нравится!"
    "Я на секунду задумался — имеет ли смысл, что я скажу? Ей, кажется, это вообще на самом деле не интересно. Можно навешать любую лапшу на уши..."
    "Или сказать правду — звучать будет одинаково."

    jump n1_r100


# ------------------------------------------
# Разветвление n1_r100 — про куртку
# Варианты лежат в n1_r100_1.rpy,
# n1_r100_2.rpy, n1_r100_3.rpy
# ------------------------------------------
label n1_r100:

    menu:
        "Купил на Сицилии...":
            jump n1_r100_1

        "Гаражная распродажа...":
            jump n1_r100_2

        "Это кастом...":
            jump n1_r100_3


# ------------------------------------------
# Точка схождения веток n1_r100
# ------------------------------------------
label n1_r100_join:

    "Чем дольше я смотрю на неё, тем сильнее чувствую голод. Не думал, что удастся поесть перед концертом, но она сама идёт ко мне в руки..."
    d "Ну, а ты? Живёшь здесь?"
    c "В Ирике? Да. У меня здесь родители и я вернулась полгода назад, когда рассталась с парнем."
    d "Оу... прости. Сочувствую... наверное. Он должно быть тот ещё козёл?"
    "Соберись, Damn. Это звучит очень фальшиво. Ты можешь лучше. Давай, надо немного постараться иначе будешь выступать голодным. Сделай вид, что тебе реально интересно."

    jump n1_r200


# ------------------------------------------
# Разветвление n1_r200 — реакция на историю Клэр
# Варианты лежат в n1_r200_1.rpy, n1_r200_2.rpy,
# n1_r200_3.rpy
# ------------------------------------------
label n1_r200:

    menu:
        "Ты хорошая...":
            jump n1_r200_1

        "Что у вас случилось?":
            jump n1_r200_2

        "Выйдем?":
            jump n1_r200_3


label n1_r200_join:

# Если фон ещё не bar_outside (пришли из барной ветки) — переключаем.
# Если уже bar_outside (пришли из уличной ветки) — просто оставляем как есть.
    if not renpy.showing("bg bar_outside"):
        hide bg
        pause char_transition_pause
        show bg bar_outside at bg_pos

# Персонажи после сцены на улице были спрятаны — показываем заново
    show claire front at claire_front_pos
    show damien back at damien_back_pos

    c "Слушай... спасибо, что выслушал. Мне надо было выговориться."
# Клэр — Дамьен
    hide claire front
    hide damien back
    pause char_transition_pause
    show damien front at damien_front_pos
    show claire back at claire_back_pos
    d "Не за что."
# Дамьен — Клэр
    hide damien front
    hide claire back
    pause char_transition_pause
    show claire front at claire_front_pos
    show damien back at damien_back_pos
    c "Я хотела кое-что взять в машине."
    c "Не ожидала кого-нибудь встретить сегодня в баре."
    "Её голос звучит иначе. Тише. Ниже. Вкрадчивее."
# Клэр уходит    
    show claire front at claire_front_leave
    hide claire front
    "Она не спрашивает разрешения. Она уведомляет меня о том, что будет дальше."
    "Дорогая, не ты ведёшь эту машину..."
# Дамьен уходит    
    show damien back at damien_back_leave
    hide damien back
    "Клэр пикает сигналкой, оборачивается, чтобы проверить, что я всё ещё иду за ней и... открывает пассажирскую дверь."
    "Она с ногами забирается на заднее сиденье."
    c "Так и будешь там стоять?"

    return
