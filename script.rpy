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

# Как дошли до сцены с Митчем/Клиффом (n1_r300_join) — влияет на то,
# какой блок диалога про еду там показывать:
#   "skipped" — n1_r200_1, Клэр ушла до всякой проверки питания
#   "failure" — n1_r300_f_join, проверка питания провалена
#   "success" — n1_r300_claire_survived, поел успешно
default feeding_outcome = None

# Название группы — вводится игроком в n1_r300_join (сцена с Лэнсом),
# дальше подтягивается по ходу игры через "[band_name]".
default band_name = ""

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
    show damien front at damien_front_pos zorder 0
    show claire back at claire_back_pos zorder 1
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
    show claire front at claire_front_pos zorder 0
    show damien back at damien_back_pos zorder 1
    c "Я Клэр."
    $ claire_name = "Клэр"
    "Она протягивает руку."
# Клэр — Дамьен
    hide bg
    hide claire front
    hide damien back
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos zorder 0
    show claire back at claire_back_pos zorder 1
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
    show claire front at claire_front_pos zorder 0
    show damien back at damien_back_pos zorder 1

    play ambience "audio/ambience/outside.ogg"
    c "Слушай... спасибо, что выслушал. Мне надо было выговориться."
# Клэр — Дамьен
    hide bg
    hide claire front
    hide damien back
    pause char_transition_pause
    show bg motel at bg_pos
    show damien front at damien_front_pos zorder 0
    show claire back at claire_back_pos zorder 1
    d "Не за что."
# Дамьен — Клэр
    hide bg
    hide damien front
    hide claire back
    pause char_transition_pause
    show bg bar_outside at bg_pos
    show claire front at claire_front_pos zorder 0
    show damien back at damien_back_pos zorder 1
    c "Я хотела кое-что взять в машине."
    c "Не ожидала кого-нибудь встретить сегодня в баре."
    "Её голос звучит иначе. Тише. Ниже. Вкрадчивее."
# Клэр уходит    
    show claire front at claire_front_leave zorder 0
    hide claire front
    "Она не спрашивает разрешения. Она уведомляет меня о том, что будет дальше."
    think "Дорогая, не ты ведёшь эту машину..."
# Дамьен уходит    
    show damien back at damien_back_leave zorder 1
    hide damien back
    play sfx "audio/sfx/carkey.ogg"
    pause 0.5
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
# Провал — Дамьен просто возвращается в бар.
# ------------------------------------------
label n1_r300_f_join:

    $ feeding_outcome = "failure"
    play sfx "audio/sfx/doorbell.ogg"
    jump n1_r300_join


# ------------------------------------------
# n1_r300_join — Дамьен возвращается в бар (сцена, где предстоит
# выступать). Общая точка схождения для:
#   - n1_r300_f_join (провал проверки питания)
#   - n1_r300_claire_survived (успех, Клэр выжила)
#   - n1_r200_1 (Клэр ушла ещё до проверки питания)
# "Клэр умерла" (n1_r300_claire_dead) сюда НЕ ведёт — это отдельная,
# альтернативная ветка.
#
# Фон и звук ставим защищённо (проверяем, что ещё не на bar_scene),
# чтобы не было лишней анимации фона, если он уже такой.
# ------------------------------------------
label n1_r300_join:

    hide damien front
    hide damien back
    hide claire front
    hide claire back

    if not renpy.showing("bg bar_scene"):
        hide bg
        pause char_transition_pause
        show bg bar_scene at bg_pos

    play ambience "audio/ambience/bar.ogg"

    show damien back at damien_back_pos zorder 1
    "Сцена на которой нам придётся выступать, конечно, мда…"
    "Платформа дюймов 10 высотой, пара комбиков, журавлей и стульев. Хорошо, хоть, ударка есть."

    show mitch front at mitch_front_pos zorder 0
    "Митч уже там и развешивает посуду."

    mitch "Damn!"
    d "Давно вернулся? Клифф где?"
    mitch "Только сел. Пацан ща придёт."

    "Я тянусь за своим Телекастером, подключаюсь к тюнеру и начинаю настраиваться."

    if feeding_outcome == "skipped":
        pass
    elif feeding_outcome == "failure":
        mitch "Ты тоже уже поел?"
# Митч — Дамьен
        hide bg
        hide mitch front
        hide damien back
        pause char_transition_pause
        show bg bar_inside at bg_pos
        show damien front at damien_front_pos zorder 0
        show mitch back at mitch_back_pos zorder 1
        "Я качаю головой."
        d "Прикинь, сама ко мне в руки шла и сорвалась в последний момент."
        mitch "Всё нормально там? Не нужна какая-нибудь помощь?"
        d "Не парься, всё в порядке. Сидит у себя в тачке и хнычет."
        mitch "То есть она может и послушать нас придёт?"
        d "Не думаю, мужик."
    else:
        mitch "Ты тоже уже поел?"
# Митч — Дамьен
        hide bg
        hide mitch front
        hide damien back
        pause char_transition_pause
        show bg bar_inside at bg_pos
        show damien front at damien_front_pos zorder 0
        show mitch back at mitch_back_pos zorder 1
        d "Ага. Сама ко мне подошла."
        mitch "Всё нормально там? Не нужна какая-нибудь помощь?"
        d "Всё хорошо. Балдеет на заднем сиденье своей тачки."
        mitch "То есть она ещё и послушать нас придёт?"
        d "Ну, мои, в отличие от твоих, потом могут ходить."
        "Мы глупо улыбаемся друг другу."

# Приходит бас-гитарист
    hide bg
    hide damien front
    hide mitch back
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos_3left zorder 0
    show mitch front at mitch_front_pos_3right zorder 0
    show cliff back at cliff_back_pos_3 zorder 1
    "Внезапно появляется Клифф."
    cliff "Чо вы тут, жахались в дёсна пока меня не было?"
    d "Отсоси."
    "Клифф суетно закидывает Рикенбакер на себя, садится на карточки, чтобы лучше видеть тюнер и быстро проводит пальцами по струнам."
    mitch "Да, ладно, не настраивайся, тебя всё равно не слышно."
    hide bg
    hide damien front
    hide mitch front
    hide cliff back
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show cliff front at cliff_front_pos_3 zorder 0
    show damien back at damien_back_pos_3right zorder 1
    show mitch back at mitch_back_pos_3left zorder 1
    cliff "Как же ты заебал…"
    "Все смеются. Митч, кажется, только за этот вечер повторил эту шутку раз пятый и мы уже ржём как будто не над ней вовсе."

    "Нас прерывает хозяин бара."

# Хозяин бара (Лэнс) — Дамьен и Митч уходят из кадра, входит Лэнс
    hide bg
    hide damien front
    hide mitch front
    hide cliff back
    pause char_transition_pause
    show bg bar_inside at bg_pos
    show damien back at damien_back_pos zorder 1
    show lance front at lance_front_pos zorder 0
    lance "У вас всё готово, парни?"
    "Мы синхронно киваем."
    lance "Сколько песен играете?"

# Лэнс — Дамьен
    hide bg
    hide damien back
    hide lance front
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos zorder 0
    show lance back at lance_back_pos zorder 1
    d "Пять."
    lance "Окей, тогда буду вас объявлять."

# Лэнс у микрофона, обращается к залу
    hide bg
    hide damien front
    hide lance back
    pause char_transition_pause
    show bg bar_inside at bg_pos
    show lance back at lance_back_pos zorder 1
    play sfx "audio/sfx/mic-check.ogg"
    play ambience "audio/ambience/bar.ogg" fadein 5.0
    "Лэнс берёт микрофон, пару раз стучит по нему."
    lance "Доброй ночи всем, кто решил провести время в Jolley’s Club Saloon. У нас сегодня живая музыка, если вы не заметили. Ребята из кавер-группы…"
    "Лэнс прикрывает микрофон ладонью и наклоняется к нам."

# Лэнс наклонился к Дамьену — приватный вопрос (тот же фон, без смены)
    hide bg
    hide lance back
    pause char_transition_pause
    show bg bar_scene at bg_pos
    show damien front at damien_front_pos zorder 0
    show lance back at lance_back_pos zorder 1
    lance "Блин, парни, забыл спросить, как вы называетесь?"
    "По залу пробегают смешки."

# Дамьен — Лэнс, ввод названия группы
    $ band_name = renpy.input("Введите название группы и нажмите Enter", default="", length=30).strip()
    if not band_name:
        $ band_name = "Без названия"

# Лэнс объявляет группу залу
    hide bg
    hide damien front
    hide lance back
    pause char_transition_pause
    show bg bar_inside at bg_pos
    show lance back at lance_back_pos zorder 1
    "Лэнс убирает ладонь и продолжает говорить в микрофон."
    lance "Группа [band_name]! Давайте, похлопайте им, я видел их сет-лист у парней там хит за хитом."

# Дамьен и Митч встречают тишину зала (2 персонажа спиной, слева/справа)
    hide lance back
    pause char_transition_pause
    think "У нас нет сет-листа."
    show damien back at damien_back_pos zorder 1
    "Нам никто особо не хлопает. Мужики за стойкой увлечены каким-то матчем по телеку."
    play sfx "audio/sfx/feedback.ogg"
    "Парочки за столиками воркуют друг с другом."
    "По-моему, нам хлопали только люди из очереди в туалет."
    "Два человека."
    think "Ладно, держитесь!"

    ## feedback.ogg (канал "sfx") мог ещё не доиграть к этому моменту —
    ## обрываем его резко (без fadeout), чтобы луп начался сразу, без
    ## паузы и наложения звука.
    $ renpy.music.stop(channel="sfx", fadeout=0)

    ## На всё время выступления (все треки back-in-black-...) фоновый
    ## гул бара выключаем — иначе он будет играть поверх песни.
    ## Возвращаем его обратно на реплике "Доброй ночи, Ирика!.." ниже.
    $ renpy.music.stop(channel="ambience", fadeout=1.0)

    $ start_loop("audio/music/back-in-black-band-loop-1.ogg", "audio/music/back-in-black-guitar-loop-1.ogg")

    hide bg
    hide damien back
    pause char_transition_pause
    $ _band_slideshow.reset()
    show bg band_random at bg_pos

    "Мы начинаем с AC/DC — Back in Black."
    "В баре сразу оживляются. Люди за стойкой оборачиваются на нас, очередь у туалета даёт немного шума…"

    $ next_button_label = "Начать ритм-игру"
    "Я пропеваю первые строчки и все начинают качать головами."
    $ next_button_label = "Дальше"

    call screen rhythm_intro(94, "audio/music/back-in-black-band-1.ogg", "audio/music/back-in-black-guitar-1.ogg", "verse1.json", on_countdown_end=show_playing_bg)
    $ pregame_state = _return

    call screen rhythm_game(
        "verse1.json",
        "audio/music/back-in-black-band-1.ogg",
        "audio/music/back-in-black-guitar-1.ogg",
        state=pregame_state,
    )
    $ verse1_result = _return

    if verse1_result["success"]:

        $ start_loop("audio/music/back-in-black-band-loop-1.ogg", "audio/music/back-in-black-guitar-loop-1.ogg")

        hide bg
        pause char_transition_pause
        $ _singing_slideshow.reset()
        show bg singing_random at bg_pos

        "В самом конце куплета публика замирает и последние строчки припева мы уже поём вместе."
        "Второй куплет бар уже ритмично притопывает и прихлопывает в такт песне."
        think "Всё, они на крючке. Работает безотказно."
        "Кто-то закидывает купюру в банку."

        $ next_button_label = "Сыграть соло"
        "Я дотягиваю до финального соло и наконец отлипаю от микрофона."
        $ next_button_label = "Дальше"

    else:

        $ start_loop("audio/music/back-in-black-band-loop-1.ogg", "audio/music/back-in-black-guitar-loop-1.ogg")

        hide bg
        pause char_transition_pause
        $ _singing_slideshow.reset()
        show bg singing_random at bg_pos

        think "Соберись, Damn. Ты же отлично знаешь этот трек!"
        "Судя по тому, что мужики за барной стойкой не отлипают от телека, никто особо не заметил как я налажал."

        $ next_button_label = "Сыграть соло"
        "Ладно, впереди соло, я ещё смогу отыграться и зацепить их."
        $ next_button_label = "Дальше"

    ## Общий код для соло — сюда ведут ОБЕ ветки (и успех, и провал
    ## первого куплета), луп на момент этого места уже играет в любом
    ## случае (см. start_loop() выше в обеих ветках).
    call screen rhythm_intro(94, "audio/music/back-in-black-band-2.ogg", "audio/music/back-in-black-guitar-2.ogg", "verse2.json", on_countdown_end=show_solo_bg)
    $ pregame_state = _return

    call screen rhythm_game(
        "verse2.json",
        "audio/music/back-in-black-band-2.ogg",
        "audio/music/back-in-black-guitar-2.ogg",
        state=pregame_state,
    )
    $ solo_result = _return

    ## Финальный трек стартует СРАЗУ, ещё до визуального перехода —
    ## та же логика, что у start_loop() в ветках выше: звук уже идёт,
    ## пока фон меняется, поэтому переход бесшовный, без паузы тишины.
    ## Громкость канала "guitar" сбрасываем на всякий случай: если
    ## игрок промазал мимо последней ноты второй ритм-игры,
    ## mute_guitar() мог оставить канал приглушённым (volume 0) — без
    ## сброса guitar-end.ogg заиграла бы беззвучно.
    $ renpy.music.set_volume(1.0, channel="guitar")
    $ renpy.music.play("audio/music/back-in-black-band-end.ogg", channel="band")
    $ renpy.music.play("audio/music/back-in-black-guitar-end.ogg", channel="guitar")

    hide bg
    pause char_transition_pause
    $ _band_slideshow.reset()
    show bg band_random at bg_pos

    if solo_result["success"]:

        "Я бросаю взгляд на банку и там больше чем было в прошлый раз."
        "Бар хлопает в такт."
        "Я заканчиваю соло и даю ещё пару тактов риффа, чтобы мы смогли закончить одновременно."
        "Митч с Клиффом хорошо знают этот приём и всё проходит гладко, под оглушительный крэш в конце."

    else:

        think "Да ну, блять... Что за херня?!"
        "Я начинаю терять самообладание и понемногу выходить из себя."
        "Тем не менее, даю ещё пару тактов риффа, чтобы мы смогли закончить одновременно."
        "Митч с Клиффом хорошо знают этот приём и хоть здесь всё проходит гладко, под оглушительный крэш в конце."

    ## Ждём, пока полностью доиграет финальный трек (*-end.ogg на канале
    ## "band") — только после этого показываем следующую реплику, чтобы
    ## музыка не обрывалась и не наслаивалась на новый диалог.
    call wait_for_channel_silence("band")

    hide bg
    pause char_transition_pause
    show bg bar_inside at bg_pos
    show damien back at damien_back_pos zorder 1

    play sfx "audio/sfx/mic-check.ogg"
    play ambience "audio/ambience/bar.ogg" fadein 5.0

    d "Доброй ночи, Ирика! Мы здесь проездом, заметили, что у вас в городке слишком тихо и решили это исправить."
    d "Если вы хотели покурить, то сейчас самое время, потому что дальше мы собираемся сделать кое-что незаконное."
    "Клифф наклоняется ко мне и шепчет на ухо."
    cliff "Breaking the Law следующая?"
    "Я киваю."

    return
