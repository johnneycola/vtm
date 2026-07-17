# ==========================================
# ОБЩИЙ СЮЖЕТ
# Ночь 1
# ==========================================

# Ставится в label n1_r201_2 (n1_r200_2.rpy) — правда только если игрок
# выбрал "Что у вас случилось?" И ЗАТЕМ "Слушать дальше...".
default heard_claire_full_story = False

# Сложность проверки в n1_r300 (шаг 3: сколько успехов нужно набрать).
# По умолчанию 2, понижается до 1, если игрок обнюхал волосы Клэр
# в n1_r202_2 (см. n1_r200_2.rpy).
default feeding_difficulty = 2

# Цвет текста в скобках у вариантов ответа, где показывается сложность/
# эффект выбора (пипсы кубов и т.п.) — белый, чтобы выделяться на фоне
# обычного оранжевого текста варианта. Меняешь тут — меняется везде.
define DIFFICULTY_TEXT_COLOR = "#ffffff"

init python:

    def difficulty_note(text):
        # Оборачивает текст в круглые скобки белым цветом — используем
        # в вариантах ответа для пометок вида "(сложность: ●●)".
        # text может содержать теги вроде {image=...} — это ок, они
        # применяются поверх цвета.
        return "{color=%s}(%s){/color}" % (DIFFICULTY_TEXT_COLOR, text)

    def check_line(attr_name, attr_value, skill_name, skill_value):
        # Вторая строка под вариантом ответа: "Атрибут + Навык: ●● + ●".
        # attr_name/skill_name бери строго как в листе персонажа
        # (character_sheet_damien.rpy), attr_value/skill_value —
        # соответствующие cs_* переменные оттуда же.
        # Серая, мельче основного текста (15 вместо 20), пипсы — картинкой
        # dice/d-mini.webp, а не символом. Атрибут и навык показываются
        # раздельными группами через " + ", а не суммой.
        #
        # Голодные кубики (cs_hunger) заменяют обычные в пуле — но не
        # больше, чем всего кубиков в пуле. Забирают сначала из навыка,
        # если навыка не хватает — переходят на атрибут.
        pool = attr_value + skill_value
        hunger_dice = min(cs_hunger, pool)
        skill_hunger = min(hunger_dice, skill_value)
        attr_hunger = hunger_dice - skill_hunger

        def pips(total, hunger):
            normal = total - hunger
            return "{image=dice/d-mini.webp}" * normal + "{image=dice/hd-mini.webp}" * hunger

        attr_pips = pips(attr_value, attr_hunger)
        skill_pips = pips(skill_value, skill_hunger)

        return "{size=15}{color=#a9a9a9}%s + %s: %s + %s{/color}{/size}" % (attr_name, skill_name, attr_pips, skill_pips)

label start:

    play ambience "audio/ambience/outside.ogg"
    show bg bar_outside
    "Северная Калифорния."
    "Ирика — небольшой город возле границы с Орегоном."
    "Бар Jolley's Club Saloon."
    "9:30 PM."
    hide bg
    play ambience "audio/ambience/bar.ogg"
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
    $ c.name = "Клэр"
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
    think "Соберись, Damn. Это звучит очень фальшиво. Ты можешь лучше. Давай, надо немного постараться иначе будешь выступать голодным. Сделай вид, что тебе реально интересно."

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

    play ambience "audio/ambience/outside.ogg"
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
    think "Дорогая, не ты ведёшь эту машину..."
# Дамьен уходит    
    show damien back at damien_back_leave
    hide damien back
    play sfx "audio/sfx/carkey.ogg"
    pause 1.0
    show bg bar_outside_alarm
    pause 0.5
    show bg bar_outside
    "Клэр пикает сигналкой, оборачивается, чтобы проверить, что я всё ещё иду за ней и..."
    show bg bar_outside_door
    play sfx "audio/sfx/open_door.ogg"
    "Открывает пассажирскую дверь."
    "Она с ногами забирается на заднее сиденье."
    show bg claire
    c "Так и будешь там стоять?"

    jump n1_r300


# ------------------------------------------
# Разветвление n1_r300 — как съесть Клэр
# Варианты лежат в n1_r300_1s.rpy / n1_r300_1f.rpy,
# n1_r300_2s.rpy / n1_r300_2f.rpy, n1_r300_3s.rpy / n1_r300_3f.rpy
# ------------------------------------------
label n1_r300:

    $ feeding_note = difficulty_note("сложность: %d" % feeding_difficulty)

    $ check_1 = check_line("Сила", cs_strength, "Скрытность", cs_stealth)
    $ check_2 = check_line("Харизма", cs_charisma, "Убеждение", cs_persuasion)
    $ check_3 = check_line("Самообладание", cs_composure, "Убеждение", cs_persuasion)

    $ current_choice_sound = "audio/ui/dice.ogg"

    menu:
        "Молча съесть её [feeding_note]\n[check_1]":
            $ current_choice_sound = "audio/ui/choice.ogg"
            $ dice, successes, success, result_text = roll_check(cs_strength, cs_stealth, feeding_difficulty)
            call screen check_result("Сила + Скрытность", feeding_difficulty, dice, successes, result_text, success)
            if success:
                jump n1_r300_1s
            else:
                jump n1_r300_1f

        "Пошутить [feeding_note]\n[check_2]" if heard_claire_full_story:
            $ current_choice_sound = "audio/ui/choice.ogg"
            $ dice, successes, success, result_text = roll_check(cs_charisma, cs_persuasion, feeding_difficulty)
            call screen check_result("Харизма + Убеждение", feeding_difficulty, dice, successes, result_text, success)
            if success:
                jump n1_r300_2s
            else:
                jump n1_r300_2f

        "Быть романтичным [feeding_note]\n[check_3]":
            $ current_choice_sound = "audio/ui/choice.ogg"
            $ dice, successes, success, result_text = roll_check(cs_composure, cs_persuasion, feeding_difficulty)
            call screen check_result("Самообладание + Убеждение", feeding_difficulty, dice, successes, result_text, success)
            if success:
                jump n1_r300_3s
            else:
                jump n1_r300_3f


# ------------------------------------------
# Точка схождения успешных исходов (1s/2s/3s)
# ------------------------------------------
label n1_r300_s_join:

    if earned >= 5:
        jump n1_r300_claire_dead
    else:
        jump n1_r300_claire_survived


# ------------------------------------------
# Точка схождения провальных исходов (1f/2f/3f)
# ------------------------------------------
label n1_r300_f_join:

    # TODO: текст продолжения после провала — общий
    # для всех трёх вариантов.

    return
