# Вы можете расположить сценарий своей игры в этом файле.

# Спрайты персонажей
image damien_sprite = "characters/damien.webp"
image claire_sprite = "characters/claire.webp"

# Фоны
image bg bar_inside = "bg/bar_inside.webp"
image bg bar_outside = "bg/bar_outside.webp"
image bg car1 = "bg/car1.webp"
image bg car2 = "bg/car2.webp"
image bg inside_car1 = "bg/inside_car1.webp"
image bg inside_car2 = "bg/inside_car2.webp"

# Определение персонажей игры.
define damien = Character('Дамьен', color="#ff4d4d", image="damien_sprite")
define claire = Character('Клэр', color="#ff4dff", image="claire_sprite")
define stranger = Character('Незнакомка', color="#ff4dff", image="claire_sprite")

# Переменные для отслеживания выборов игрока
default ponyuhala_volosy = False
default slushal_pro_ostin = False

# Переменные для броска кубиков
default dice_rolls = []
default dice_successes = 0
default dice_needed = 2

# Переменные звуков
default saw_sound_event = False

# ── Мини-игра питания ──────────────────────────────────────────────
# feeding_difficulty  : 1 или 2 (определяет размер зелёной зоны)
# feeding_speed       : скорость курсора (0.0–1.0 за секунду), задаётся перед вызовом
# feeding_victim_dice : кол-во d10 для проверки жертвы (скрытый бросок)
# feeding_result      : итог после мини-игры ("safe" / "unconscious" / "dead")
# feeding_blood       : сколько точек крови выпито
default feeding_difficulty = 2
default feeding_speed = 0.004
default feeding_victim_dice = 4
default feeding_result = "safe"
default feeding_blood = 0

init python:
    import random

    def roll_dice(pool):
        """Бросает pool кубиков d10, возвращает список результатов и считает успехи (6+)."""
        store.dice_rolls = []
        store.dice_successes = 0
        for i in range(pool):
            roll = random.randint(1, 10)
            store.dice_rolls.append(roll)
            if roll >= 6:
                store.dice_successes += 1

    def feeding_victim_check(blood_points, victim_dice):
        """Скрытый бросок: нужно собрать blood_points успехов из victim_dice кубиков."""
        successes = sum(1 for _ in range(victim_dice) if random.randint(1, 10) >= 6)
        return successes >= blood_points

    def calc_feeding_zone(difficulty):
        """Размер зелёной зоны как доля от высоты шкалы."""
        if difficulty == 1:
            return 1.0 / 6.0
        else:
            return 1.0 / 7.0

# Высота шкалы в пикселях и ширина
define TRACK_H = 500
define TRACK_W = 60
define CURSOR_H = 20

screen feeding_rules():
    modal True
    frame:
        xalign 0.5
        yalign 0.5
        xsize 600
        padding (30, 30)
        vbox:
            spacing 16
            text "Как пить кровь" size 32 color "#cc3333" xalign 0.5
            text "На шкале движется курсор — вверх и вниз." size 22 color "#ffffff"
            text "Красная зона — момент когда можно остановиться." size 22 color "#ffffff"
            text "Нажми в нужный момент чтобы прекратить питание." size 22 color "#ffffff"
            text "Каждый полный проход вверх-вниз = +1 точка крови." size 22 color "#ffffff"
            text "Ты начинаешь с 1 точкой. После 5 точек — жертва умирает." size 22 color "#cc3333"
            text "Курсор полупрозрачный — клик временно недоступен." size 22 color "#aaaaaa"
            text "Курсор мигнул и исчез — промазал, продолжай." size 22 color "#aaaaaa"
            text "Красная подводка — попал, питание остановлено." size 22 color "#cc3333"
            textbutton "Понятно" action Return() xalign 0.5 text_size 26

screen feeding_minigame():
    modal True

    # Состояние хранится в screen-переменных
    default cursor_pos = 0.0        # 0.0 = низ, 1.0 = верх
    default moving_up = True
    default blood = 1               # Начинаем с 1 точки
    default in_timeout = False
    default timeout_progress = 0.0  # 0.0–1.0, таймаут = 1/4 полного пути
    default cursor_state = "normal" # normal / timeout / miss / hit
    default hit_flash = 0.0         # таймер для вспышки hit/miss
    default game_over = False
    default game_started = False

    # Размер зелёной зоны и позиция (фиксируем в центре)
    default zone_size = calc_feeding_zone(feeding_difficulty)
    default zone_pos = 0.5 - zone_size / 2.0   # верхний край зоны (доля)

    # Таймер движения курсора (каждые 16мс = ~60fps)
    if game_started and not game_over:
        timer 0.016 repeat True action [
            # Движение курсора
            If(moving_up,
                SetScreenVariable("cursor_pos",
                    min(1.0, cursor_pos + feeding_speed)),
                SetScreenVariable("cursor_pos",
                    max(0.0, cursor_pos - feeding_speed))
            ),
            # Смена направления и счёт очков
            If(moving_up and cursor_pos >= 1.0,
                SetScreenVariable("moving_up", False)
            ),
            If(not moving_up and cursor_pos <= 0.0, [
                SetScreenVariable("moving_up", True),
                SetScreenVariable("blood", blood + 1),
                If(blood + 1 >= 5, SetScreenVariable("game_over", True))
            ]),
            # Таймаут
            If(in_timeout, [
                SetScreenVariable("timeout_progress",
                    min(1.0, timeout_progress + feeding_speed * 4)),
                If(timeout_progress >= 1.0, [
                    SetScreenVariable("in_timeout", False),
                    SetScreenVariable("timeout_progress", 0.0),
                    SetScreenVariable("cursor_state", "normal")
                ])
            ]),
            # Сброс flash-состояния miss
            If(cursor_state == "miss" and hit_flash > 0, [
                SetScreenVariable("hit_flash", max(0.0, hit_flash - 0.016)),
                If(hit_flash <= 0.0, SetScreenVariable("cursor_state", "normal"))
            ])
        ]

    # Фон
    add Solid("#111111")

    hbox:
        xalign 0.5
        yalign 0.5
        spacing 40

        # Шкала слева
        frame:
            xsize TRACK_W
            ysize TRACK_H
            background Solid("#333333")

            # Красная зона
            add Solid("#cc0000"):
                xsize TRACK_W
                ysize int(TRACK_H * zone_size)
                xpos 0
                ypos int(TRACK_H * (1.0 - zone_pos - zone_size))

            # Курсор
            if cursor_state == "normal":
                add Solid("#ffffff"):
                    xsize TRACK_W
                    ysize CURSOR_H
                    xpos 0
                    ypos int(TRACK_H * (1.0 - cursor_pos) - CURSOR_H / 2)
            elif cursor_state == "timeout":
                add Solid("#ffffff88"):
                    xsize TRACK_W
                    ysize CURSOR_H
                    xpos 0
                    ypos int(TRACK_H * (1.0 - cursor_pos) - CURSOR_H / 2)
            elif cursor_state == "miss":
                pass
            elif cursor_state == "hit":
                add Solid("#ffffff"):
                    xsize TRACK_W
                    ysize CURSOR_H
                    xpos 0
                    ypos int(TRACK_H * (1.0 - cursor_pos) - CURSOR_H / 2)
                add Solid("#cc0000"):
                    xsize TRACK_W
                    ysize 3
                    xpos 0
                    ypos int(TRACK_H * (1.0 - cursor_pos) - CURSOR_H / 2) - 3
                add Solid("#cc0000"):
                    xsize TRACK_W
                    ysize 3
                    xpos 0
                    ypos int(TRACK_H * (1.0 - cursor_pos) + CURSOR_H / 2)

        # Правая колонка: точки и кнопки
        vbox:
            yalign 0.5
            spacing 30

            # Счётчик точек символами •
            vbox:
                spacing 8
                text "Кровь" size 22 color "#aaaaaa"
                hbox:
                    spacing 6
                    for i in range(5):
                        if i < blood:
                            text "•" size 48 color "#cc0000"
                        else:
                            text "•" size 48 color "#444444"

            # Кнопки
            if not game_started:
                textbutton "Начать" action SetScreenVariable("game_started", True) text_size 28
            elif game_over:
                textbutton "Готово" action [
                    SetVariable("feeding_blood", blood),
                    Return()
                ] text_size 28
            else:
                textbutton "Стоп" text_size 28:
                    action If(
                        not in_timeout,
                        If(
                            cursor_pos >= zone_pos and cursor_pos <= zone_pos + zone_size,
                            [
                                SetScreenVariable("cursor_state", "hit"),
                                SetScreenVariable("game_over", True),
                                SetVariable("feeding_blood", blood)
                            ],
                            [
                                SetScreenVariable("cursor_state", "miss"),
                                SetScreenVariable("hit_flash", 0.4),
                                SetScreenVariable("in_timeout", True),
                                SetScreenVariable("timeout_progress", 0.0)
                            ]
                        ),
                        NullAction()
                    )

label feeding_claire:
    $ feeding_difficulty = 1 if ponyuhala_volosy else 2
    # Чем больше успехов при проверке питания — тем медленнее курсор
    # Базовая скорость 0.006, каждый успех снижает на 0.0008 (минимум 0.002)
    $ feeding_speed = max(0.002, 0.006 - dice_successes * 0.0008)
    $ feeding_victim_dice = 4
    $ feeding_blood = 0

    menu:
        "Пить":
            pass
        "Правила":
            call screen feeding_rules
            jump feeding_claire

    call screen feeding_minigame

    if feeding_blood <= 2:
        $ feeding_result = "safe"
    elif feeding_blood == 5:
        $ feeding_result = "dead"
    else:
        # 3 или 4 точки — скрытый бросок жертвы
        # Нужно собрать не меньше feeding_blood успехов из feeding_victim_dice кубиков
        $ victim_survived = feeding_victim_check(feeding_blood, feeding_victim_dice)
        if victim_survived:
            $ feeding_result = "unconscious"
        else:
            $ feeding_result = "dead"

    if feeding_result == "safe":
        "Клэр обмякает в объятиях. Она жива — просто в полусознании и экстазе."
    elif feeding_result == "unconscious":
        "Клэр без сознания. Дышит. Повезло."
    else:
        "Клэр больше не дышит."

    return



screen dice_result():
    vbox:
        xalign 0.5
        yalign 0.4
        spacing 10

        hbox:
            xalign 0.5
            spacing 8
            for roll in dice_rolls:
                if roll >= 6:
                    text "[roll]" size 40 color "#33cc33" outlines [(2, "#000000", 0, 0)]
                else:
                    text "[roll]" size 40 color "#000000" outlines [(2, "#888888", 0, 0)]

        text "Успехов: [dice_successes] / Нужно: [dice_needed]" xalign 0.5 size 28 color "#ffffff"

        if dice_successes >= dice_needed:
            text "УСПЕХ" xalign 0.5 size 36 color "#33cc33"
        else:
            text "ПРОВАЛ" xalign 0.5 size 36 color "#cc3333"

        textbutton "Далее" action Return() xalign 0.5

# Игра начинается здесь:
label start:

    scene bg bar_outside

    hide damien_sprite
    hide claire_sprite
    play music "ambience/outside.ogg" fadein 1.0

    "Калифорния"

    "Ирика — небольшой город у границы с Орегоном"
    
    "Бар Jolley’s Club Saloon"

    "9:30 PM"

    scene bg bar_inside

    show claire_sprite at left
    hide damien_sprite
    play music "ambience/bar.ogg"
    stranger "Ты сегодня выступаешь?"

    show damien_sprite at right
    hide claire_sprite
    damien "А?"

    show claire_sprite at left
    hide damien_sprite
    stranger "Говорю, привет, ты сегодня выступаешь?"

    show damien_sprite at right
    hide claire_sprite
    damien "Да. Как ты догадалась?"

    show claire_sprite at left
    hide damien_sprite
    stranger "Куртка у тебя крутая. Здесь в таких не ходят."

    show claire_sprite at left
    hide damien_sprite
    stranger "Я Клэр."

    hide damien_sprite
    hide claire_sprite
    "Она протягивает руку."

    show damien_sprite at right
    hide claire_sprite
    damien "Damn."

    show claire_sprite at left
    hide damien_sprite
    claire "M?"

    show damien_sprite at right
    hide claire_sprite
    damien "Я Дамьен, но вообще Damn."

    hide damien_sprite
    hide claire_sprite
    "Я пожимаю её руку. У неё мягкая, влажная, пухлая ладонь."

    show damien_sprite at right
    hide claire_sprite
    damien "Так, значит ты увидела мою куртку и потому решила, что я сегодня выступаю?"

    show claire_sprite at left
    hide damien_sprite
    claire "Йеп. Где ты её достал? Мне очень нравится!"

    hide damien_sprite
    hide claire_sprite
    "Я на секунду задумался — имеет ли смысл, что я скажу? Ей, кажется, это вообще на самом деле не интересно. Можно навешать любую лапшу на уши..."

    hide damien_sprite
    hide claire_sprite
    "Или сказать правду — звучать будет одинаково."

    menu:
        "Купил на Сицилии...":
            jump kurtka_sicilia
        "Гаражная распродажа...":
            jump kurtka_garage
        "Это кастом...":
            jump kurtka_kastom

label kurtka_sicilia:

    show damien_sprite at right
    hide claire_sprite
    damien "Это итальянский винтаж. Купил, когда отдыхал на Сицилии."

    show claire_sprite at left
    hide damien_sprite
    claire "Ага..."

    hide damien_sprite
    hide claire_sprite
    "Она замолчала. Видно как шестерёнки со скрипом зашевелились у неё в голове. Думаю, пытается вспомнить, где находится Сицилия."

    show claire_sprite at left
    hide damien_sprite
    claire "И как там?"

    show damien_sprite at right
    hide claire_sprite
    damien "Где? На Сицилии? Нормально. Звали выступать на корпоративе у местного босса мафии."

    hide damien_sprite
    hide claire_sprite
    "Она оживилась."

    show claire_sprite at left
    hide damien_sprite
    claire "Правда?!"

    show damien_sprite at right
    hide claire_sprite
    damien "Нет."

    hide damien_sprite
    hide claire_sprite
    "Она излишне громко рассмеялась."

    jump posle_kurtki

label kurtka_garage:

    show damien_sprite at right
    hide claire_sprite
    damien "Ухватил на гаражной распродаже в СанФране."

    show claire_sprite at left
    hide damien_sprite
    claire "Ты жил там? Или тоже был проездом?"

    show damien_sprite at right
    hide claire_sprite
    damien "У меня там квартира. Сейчас вот отыграю концерт и поеду домой."

    show claire_sprite at left
    hide damien_sprite
    claire "Чего?"

    show claire_sprite at left
    hide damien_sprite
    claire "Это же почти пять часов на машине!"

    show damien_sprite at right
    hide claire_sprite
    damien "Ну не в мотеле же напротив оставаться."

    hide damien_sprite
    hide claire_sprite
    "Она с интересом приподняла одну бровь."

    jump posle_kurtki

label kurtka_kastom:

    show damien_sprite at right
    hide claire_sprite
    damien "Мне сделал её на заказ один мастер из Мельбурна."

    show claire_sprite at left
    hide damien_sprite
    claire "Ничего себе! Дорогущая небось? Или это экокожа?"

    show damien_sprite at right
    hide claire_sprite
    damien "Кенгуру."

    show claire_sprite at left
    hide damien_sprite
    claire "Чего?"

    hide damien_sprite
    hide claire_sprite
    "Она заливается смехом. Излишне громко."

    show claire_sprite at left
    hide damien_sprite
    claire "Ты прикалываешься?"

    show damien_sprite at right
    hide claire_sprite
    damien "Я серьёзно. В Австралии какие-то типа квоты на добычу кожи кенгуру, так что всё легально и никакого браконьерства."

    show claire_sprite at left
    hide damien_sprite
    claire "Не знаю... всё равно как-то это дико и бесчеловечно."

    show damien_sprite at right
    hide claire_sprite
    damien "Тебе просто надо её примерить. Держи."

    hide damien_sprite
    hide claire_sprite
    "Она немного смущается когда я протягиваю куртку, но после секунды сомнения берёт и накидывает на плечи. Ей не идёт, но она расплывается в улыбке."

    show damien_sprite at right
    hide claire_sprite
    damien "Круто выглядишь. Нравится?"

    show claire_sprite at left
    hide damien_sprite
    claire "Ну, если ты говоришь, что в Австралии квоты и всё легально, то да. Действительно крутая."

    jump posle_kurtki

label posle_kurtki:

    hide damien_sprite
    hide claire_sprite
    "Чем дольше я смотрю на неё, тем сильнее чувствую голод. Не думал, что удастся поесть перед концертом, но она сама идёт ко мне в руки..."

    show damien_sprite at right
    hide claire_sprite
    damien "Ну, а ты? Живёшь здесь?"

    show claire_sprite at left
    hide damien_sprite
    claire "В Ирике? Да. У меня здесь родители и я вернулась полгода назад, когда рассталась с парнем."

    show damien_sprite at right
    hide claire_sprite
    damien "Оу... прости. Сочувствую... наверное. Он должно быть тот ещё козёл?"

    hide damien_sprite
    hide claire_sprite
    "Соберись, Damn. Это звучит очень фальшиво. Ты можешь лучше. Давай, надо немного постараться иначе будешь выступать голодным. Сделай вид, что тебе реально интересно."

    menu:
        "Ты хорошая...":
            jump ty_horoshaya
        "Что у вас случилось?":
            jump chto_sluchilos
        "Выйдем?":
            jump vyidem

label ty_horoshaya:

    show damien_sprite at right
    hide claire_sprite
    damien "В смысле... я хотел сказать, что ты производишь впечатление довольно заботливого и чуткого человека. Как тебя можно было бросить?"

    show claire_sprite at left
    hide damien_sprite
    claire "Мы знакомы, что-то типа... две минуты. Быстро ты сделал выводы."

    show damien_sprite at right
    hide claire_sprite
    damien "Я хорошо разбираюсь в людях."

    hide damien_sprite
    hide claire_sprite
    "Ты нихера не разбираешься в людях."

    show claire_sprite at left
    hide damien_sprite
    claire "Я изменила ему."

    show damien_sprite at right
    hide claire_sprite
    damien "А... Ну... Я думаю, у тебя на то были причины."

    show claire_sprite at left
    hide damien_sprite
    claire "Может быть. Ладно, давай закроем эту тему."

    show claire_sprite at left
    hide damien_sprite
    claire "Хорошо тебе выступить, Damn."

    hide damien_sprite
    hide claire_sprite
    "Она взяла сигареты со стойки и ушла. Молодец."

    return

label chto_sluchilos:

    show damien_sprite at right
    hide claire_sprite
    damien "Прости, не стоило так говорить. Расскажи, что у вас случилось?"

    hide damien_sprite
    hide claire_sprite
    "Она хихикнула."

    show claire_sprite at left
    hide damien_sprite
    claire "Вообще, это я ему изменила. Но он, конечно, козёл. Иначе я бы этого не сделала."

    show damien_sprite at right
    hide claire_sprite
    damien "Ты намеренно изменила ему?"

    show claire_sprite at left
    hide damien_sprite
    claire "Слушай, как тебе сказать... я из Ирики, он из Остина. Он прикатил сюда на Тесле и покорил меня..."

    menu:
        "Пропустить мимо ушей...":
            jump vyidem
        "Слушать дальше...":
            jump slushat_dalshe

label slushat_dalshe:

    $ slushal_pro_ostin = True

    show damien_sprite at right
    hide claire_sprite
    damien "Ого!"

    show claire_sprite at left
    hide damien_sprite
    claire "Ага! Стоял, курил, ждал пока машина зарядится."

    show claire_sprite at left
    hide damien_sprite
    claire "Я стрельнула у него сигарету, он предложил прокатиться. В общем, слово за слово и я уже с ним на заднем сиденье."

    hide damien_sprite
    hide claire_sprite
    "Не надо. Не улыбайся."

    show claire_sprite at left
    hide damien_sprite
    claire "Короче, он рассказывал, что у него там какой-то стартап, что-то про нейросети и удобрения. Типа он изобрёл какую-то бактерию, которая что-то там делает с навозом... ладно, не буду делать вид, что я что-то поняла."

    hide damien_sprite
    hide claire_sprite
    "Она снова хихикнула."

    show claire_sprite at left
    hide damien_sprite
    claire "Я подумала: «ну, звучит, как много денег». Трахался он, конечно, так себе..."

    hide damien_sprite
    hide claire_sprite
    "А вот теперь можно и улыбнуться."

    show claire_sprite at left
    hide damien_sprite
    claire "Короче, я поехала к нему в Остин и, знаешь что? Тесла была самым дорогим, что у него было!"

    show claire_sprite at left
    hide damien_sprite
    claire "«Ну, ладно,» — подумала я, — «дай парню шанс». Но это был просто какой-то кошмар."

    show damien_sprite at right
    hide claire_sprite
    damien "В каком смысле?"

    show claire_sprite at left
    hide damien_sprite
    claire "Этот хрен не мог даже яичницу себе пожарить! Серьёзно, у него все ящики были забиты блядскими кукурузными хлопьями!"

    show claire_sprite at left
    hide damien_sprite
    claire "Фу, мне аж противно вспоминать. Ещё эта вонища была повсюду от его удобрений. Мне кажется у меня до сих пор волосы пахнут..."

    hide damien_sprite
    hide claire_sprite
    "Она нюхает прядь волос и затем протягивает её мне."

    menu:
        "Отказаться.":
            jump otkazatsya_nyuhat
        "Понюхать. [[сложность питания -1]":
            jump ponyuhat

label otkazatsya_nyuhat:

    jump posle_volos

label ponyuhat:

    $ ponyuhala_volosy = True

    hide damien_sprite
    hide claire_sprite
    "Не напрягайся. Сделай вид, что вдыхаешь. Она не заметит."

    show damien_sprite at right
    hide claire_sprite
    damien "Пахнет шампунем."

    show claire_sprite at left
    hide damien_sprite
    claire "Серьёзно?"

    hide damien_sprite
    hide claire_sprite
    "Она нюхает прядь ещё раз, пожимает плечами и продолжает."

    show claire_sprite at left
    hide damien_sprite
    claire "Странно, я вообще вчера голову мыла, до сих пор держится что ли?"

    show claire_sprite at left
    hide damien_sprite
    claire "Короче, у меня теперь ПТСР! Я не могу есть хлопья, мне от каждой коробки воняет коровьим говном!"

    jump posle_volos

label posle_volos:

    show damien_sprite at right
    hide claire_sprite
    damien "Понятно почему ты изменила ему. Быть мамашей ты не нанималась."

    show claire_sprite at left
    hide damien_sprite
    claire "Да! Ну и я просто от обиды пошла накидалась в баре и отсосала какому-то фермеру..."

    show claire_sprite at left
    hide damien_sprite
    claire "Которого видимо не очень парило, что от девушки воняет навозом."

    show claire_sprite at left
    hide damien_sprite
    claire "Ох... как рассказываю, снова аж злость берёт. Не хочешь выйти покурить?"

    hide damien_sprite
    hide claire_sprite
    "Она хватает со стойки пачку сигарет и зажигалку, кивая мне на выход и приглашает пойти за ней. Мы выходим из бара на парковку."

    hide damien_sprite
    hide claire_sprite
    "Приятного аппетита."

    jump u_mashiny

label vyidem:

    hide damien_sprite
    hide claire_sprite
    "Я не хочу слушать её душераздирающую историю. Быстро оборачиваюсь на дверь и кивком предлагаю ей выйти покурить."

    hide damien_sprite
    hide claire_sprite
    "Она кивает в ответ, мы встаём и выходим. Клэр что-то щебечет всё это время, но я лишь время от времени угукаю... хах... подавая признаки жизни."

    hide damien_sprite
    hide claire_sprite
    scene bg bar_outside
    play music "ambience/outside.ogg" fadeout 1.0 fadein 1.0

    if not saw_sound_event:
        play sound "sfx/doorbell.ogg"
        $ saw_sound_event = True
    
    "Мы выходим на парковку перед баром. Я облокачиваюсь одной рукой рядом с ней и внимательно смотрю, будто изучая её лицо."

    hide damien_sprite
    hide claire_sprite
    "Но меня не интересуют её морщины в уголках глаз и нервная улыбка, которую она натягивает после каждой фразы."

    hide damien_sprite
    hide claire_sprite
    play sound "sfx/parking.ogg"
    "Меня интересуют другие люди. Вокруг почти никого, только троица подростков шумно пытается приткнуть на полупустой парковке свой пикап."

    hide damien_sprite
    hide claire_sprite
    "Машина мигает своими стоп-сигналами, пока наконец водитель не глушит двигатель и троица с пьяной руганью не вываливается наружу."

    hide damien_sprite
    hide claire_sprite
    "Клэр, продолжая рассказывать о своём бывшем и как она с ним рассталась, то и дело зажигает перед моим лицом свой табачный стоп-сигнал, будто говорит мне: «нет, ещё рано, ты не можешь сожрать человека прямо на парковке!»"

    hide damien_sprite
    hide claire_sprite
    "Я действительно не могу."

    hide damien_sprite
    hide claire_sprite
    "Наконец крики подростков затихают где-то вдали и мы с Клэр остаёмся на улице вдвоём."

    hide damien_sprite
    hide claire_sprite
    "Она, кажется, может ещё долго жаловаться на экс-бойфренда, но вот от сигареты уже ничего не осталось и она просто теребит фильтр."

    hide damien_sprite
    hide claire_sprite
    "Я облокачиваюсь на вторую руку, нависая над ней, пристально глядя в глаза и медленно приближаясь."

    jump u_mashiny

label u_mashiny:

    scene bg bar_outside
    play music "ambience/outside.ogg" if_changed

    show claire_sprite at left
    hide damien_sprite

    if not saw_sound_event:
        play sound "sfx/doorbell.ogg"
        $ saw_sound_event = True

    claire "Слушай... спасибо, что выслушал. Мне надо было выговориться."

    show damien_sprite at right
    hide claire_sprite
    damien "Не за что."

    show claire_sprite at left
    hide damien_sprite
    claire "Я хотела кое-что взять в машине."

    show claire_sprite at left
    hide damien_sprite
    claire "Не ожидала кого-нибудь встретить сегодня в баре."

    hide damien_sprite
    hide claire_sprite
    scene bg car1
    "Её голос звучит иначе. Тише. Ниже. Вкрадчивее."

    hide damien_sprite
    hide claire_sprite
    "Она не спрашивает разрешения. Она уведомляет меня о том, что будет дальше."

    hide damien_sprite
    hide claire_sprite
    "Дорогая, не ты ведёшь эту машину..."

    hide damien_sprite
    hide claire_sprite
    play sound "sfx/carkey.ogg"
    "Клэр пикает сигналкой, оборачивается, чтобы проверить, что я всё ещё иду за ней и... открывает пассажирскую дверь."

    hide damien_sprite
    hide claire_sprite
    play sound "sfx/open_door.ogg"
    "Она с ногами забирается на заднее сиденье."

    hide claire_sprite

    hide claire_sprite
    hide damien_sprite
    scene bg car2
    claire "Так и будешь там стоять?"

    $ dice_needed = 1 if ponyuhala_volosy else 2

    menu:
        "Молча съесть её\n[[Проверка: Strength + Stealth, 3 кубика]":
            $ roll_dice(3)
            call screen dice_result
            if dice_successes >= dice_needed:
                jump molcha_uspeh
            else:
                jump molcha_proval

        "Пошутить\n[[Проверка: Charisma + Persuasion (Seduction), 8 кубиков]" if slushal_pro_ostin:
            $ roll_dice(8)
            call screen dice_result
            if dice_successes >= dice_needed:
                jump poshutit_uspeh
            else:
                jump poshutit_proval

        "Быть романтичным\n[[Проверка: Composure + Persuasion (Seduction), 5 кубиков]":
            $ roll_dice(5)
            call screen dice_result
            if dice_successes >= dice_needed:
                jump romantika_uspeh
            else:
                jump romantika_proval

label molcha_uspeh:

    hide damien_sprite
    hide claire_sprite
    scene bg inside_car1
    play music "music/song.ogg" fadeout 1.0 fadein 1.0 noloop
    "Я молча запрыгиваю следом и нависаю над ней. В её глазах проскакивает игривый блеск, но она, кажется, не готова к такому резкому развитию событий."

    hide damien_sprite
    hide claire_sprite
    claire "Подожди..."

    hide damien_sprite
    hide claire_sprite
    "Я не собираюсь ждать, дорогая. Я обхватываю оба её запястья одной рукой и второй зажимаю ей рот. Игривый огонёк всё ещё скачет в её глазах."

    hide damien_sprite
    hide claire_sprite
    "С лёгким хрустом я прокусываю её шею. Клэр обмякает, я ослабляю хватку и рот наполняет горячая кровь."
    jump feeding_claire

    return

label molcha_proval:

    hide damien_sprite
    hide claire_sprite
    scene bg inside_car1
    play music "music/song.ogg" fadeout 1.0 fadein 1.0 noloop
    "Я молча запрыгиваю следом и нависаю над ней. В её глазах проскакивает игривый блеск, но она, кажется, не готова к такому резкому развитию событий."

    hide damien_sprite
    hide claire_sprite
    claire "Подожди..."

    hide damien_sprite
    hide claire_sprite
    "Я не собираюсь ждать, дорогая. Я обхватываю оба её запястья одной рукой и собираюсь другой зажать ей рот, как она начинает кричать."

    hide damien_sprite
    hide claire_sprite
    scene bg inside_car2
    claire "Да, блять, остановись!"

    hide damien_sprite
    hide claire_sprite
    "Огонёк пропал. Она свела брови. Нет, так дела не делаются. Я замираю и ослабляю хватку. Наверное, у меня сейчас самое тупое выражение лица на свете."

    hide damien_sprite
    hide claire_sprite
    claire "Прости, я... я не могу. Извини."

    hide damien_sprite
    hide claire_sprite
    damien "Не извиняйся. Всё норм."

    hide damien_sprite
    hide claire_sprite
    damien "Наверное ты хочешь побыть одна... я пойду. Мне ещё выступать сегодня."

    hide damien_sprite
    hide claire_sprite
    scene bg car1
    play sound "sfx/slam_door.ogg"
    "Она кивает и шмыгает носом. Я вылезаю и хлопаю дверью. Чуть сильнее, чем следовало. Блять, идти на сцену голодным херовая идея, но я не буду есть её в таком состоянии."

    return

label poshutit_uspeh:

    hide damien_sprite
    hide claire_sprite
    play music "music/song.ogg" fadeout 1.0 fadein 1.0 noloop
    damien "Если что, я никогда не был в Остине..."

    hide damien_sprite
    hide claire_sprite
    "Она выглядывает и с игривой улыбкой говорит..."

    hide damien_sprite
    hide claire_sprite
    claire "Что, и Теслы у тебя тоже нет?"

    hide damien_sprite
    hide claire_sprite
    "Я оборачиваюсь, осматриваю парковку, пожимаю плечами..."

    show damien_sprite at right
    hide claire_sprite
    damien "Последний раз, когда я проверял, не было."

    hide damien_sprite
    hide claire_sprite
    scene bg inside_car1
    claire "Значит нам придётся обойтись как-нибудь без них."

    hide damien_sprite
    hide claire_sprite
    damien "Ничего, у меня есть кое-что получше."

    hide damien_sprite
    hide claire_sprite
    claire "Не сомневаюсь..."

    hide damien_sprite
    hide claire_sprite
    "Она заливается смехом и откидывается на заднее сиденье, закрыв глаза руками."

    hide damien_sprite
    hide claire_sprite
    "Съесть её теперь вообще не составит труда."

    hide damien_sprite
    hide claire_sprite
    "Я нависаю над ней. С лёгким хрустом я прокусываю шею. Клэр обмякает и рот наполняет горячая кровь."
    jump feeding_claire

    return

label poshutit_proval:

    show damien_sprite at right
    hide claire_sprite
    play music "music/song.ogg" fadeout 1.0 fadein 1.0 noloop
    damien "Если что, я никогда не был в Остине..."

    hide damien_sprite
    hide claire_sprite
    "Она внезапно замолчала."

    show damien_sprite at right
    hide claire_sprite
    damien "Клэр?"

    hide damien_sprite
    hide claire_sprite
    "Я слышу всхлипывание из машины."

    hide damien_sprite
    hide claire_sprite
    scene bg inside_car2
    "Заглядываю внутрь. Клэр сидит с ногами на заднем сиденье, обхватив руками колени. Из глаз катятся слёзы и гримаса на её лице делает её прямо противоположной слову «сексуальная»."

    hide damien_sprite
    hide claire_sprite
    claire "Господи, да что же я за шалава... зачем я это делаю..."

    hide damien_sprite
    hide claire_sprite
    claire "Прости, я не должна была... ты не... ох, блять..."

    hide damien_sprite
    hide claire_sprite
    damien "Не извиняйся. Всё норм."

    hide damien_sprite
    hide claire_sprite
    damien "Наверное ты хочешь побыть одна... я пойду. Мне ещё выступать сегодня."

    hide damien_sprite
    hide claire_sprite
    scene bg car1
    play sound "sfx/slam_door.ogg"
    "Она кивает и шмыгает носом. Я хлопаю дверью. Чуть сильнее, чем следовало. Блять, идти на сцену голодным херовая идея, но я не буду есть её в таком состоянии."

    return

label romantika_uspeh:

    hide damien_sprite
    hide claire_sprite
    scene bg inside_car1
    play music "music/song.ogg" fadeout 1.0 fadein 1.0 noloop
    "Я залезаю следом. В её глазах проскакивает игривый блеск, но я сажусь рядом и нежно беру её ладонь. Она на секунду замирает."

    hide damien_sprite
    hide claire_sprite
    claire "У тебя такие холодные руки."

    hide damien_sprite
    hide claire_sprite
    "Она явно ждёт, что я что-нибудь отвечу, но я просто молча смотрю на неё, всеми силами изображая очарование."

    hide damien_sprite
    hide claire_sprite
    claire "Ну и... что дальше?"

    hide damien_sprite
    hide claire_sprite
    "Я немного наклоняюсь к ней, она тоже подаётся вперёд и в тот момент, как она закрывает глаза для поцелуя, я целюсь чуть ниже."

    hide damien_sprite
    hide claire_sprite
    "С лёгким хрустом я прокусываю её шею. Клэр обмякает и рот наполняет горячая кровь."
    jump feeding_claire


    return

label romantika_proval:

    hide damien_sprite
    hide claire_sprite
    scene bg inside_car1
    play music "music/song.ogg" fadeout 1.0 fadein 1.0 noloop
    "Я залезаю следом. В её глазах проскакивает игривый блеск, но я сажусь рядом и нежно беру её ладонь. Она на секунду замирает."

    hide damien_sprite
    hide claire_sprite
    claire "У тебя такие холодные руки."

    hide damien_sprite
    hide claire_sprite
    "Она явно ждёт, что я что-нибудь отвечу, но я просто молча смотрю на неё, всеми силами изображая очарование."

    hide damien_sprite
    hide claire_sprite
    claire "Ну и... что дальше?"

    hide damien_sprite
    hide claire_sprite
    "Я продолжаю влюблённо смотреть на неё и, кажется, слишком долго. Настолько, что это начинает выглядеть крипово. Она нервно смеётся."

    hide damien_sprite
    hide claire_sprite
    claire "Эй, ты в порядке?"

    hide damien_sprite
    hide claire_sprite
    "Кажется, момент упущен. Молодец."

    hide damien_sprite
    hide claire_sprite
    scene bg inside_car2
    claire "Эм... слушай, может нам не стоит..."

    hide damien_sprite
    hide claire_sprite
    claire "Извини, я что-то..."

    hide damien_sprite
    hide claire_sprite
    damien "Не извиняйся. Всё норм."

    hide damien_sprite
    hide claire_sprite
    damien "Наверное ты хочешь побыть одна... я пойду. Мне ещё выступать сегодня."

    hide damien_sprite
    hide claire_sprite
    scene bg car1
    play sound "sfx/slam_door.ogg"
    "Она кивает и шмыгает носом. Я хлопаю дверью. Чуть сильнее, чем следовало. Блять, идти на сцену голодным херовая идея, но я не буду есть её в таком состоянии."

    return
