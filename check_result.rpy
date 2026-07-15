################################################################################
## Окно результата проверки — показывается вместо чата на время, пока игрок
## не нажмёт "Дальше". Использовать через:
##
##     call screen check_result(check_name, difficulty, dice, successes, result_text)
##
## check_name    — строка вида "Сила + Скрытность" (см. check_line в script.rpy —
##                 удобно собрать той же парой имён, что уже используется там).
## difficulty    — число (сложность, feeding_difficulty на данный момент).
## dice          — список кортежей (value, hunger), например:
##                 [(7, False), (3, False), (9, True), (2, True), (6, True)]
##                 value — грань 1..10, hunger — True для голодного кубика.
## successes     — число успехов (логику подсчёта пришлёшь позже — сюда просто
##                 подставляется готовое число).
## result_text   — итоговая строка, например "УСПЕХ" или "ПРОВАЛ".
##
## Чат ничего скрывать/показывать вручную не нужно: screen say/choice и так
## не висят на экране между репликами, "call screen" просто занимает это же
## место на время, а после Return() чат сам появится на следующей реплике.
################################################################################

init python:

    def _dice_image(value, hunger):
        # value — грань 1..10, hunger — голодный кубик или обычный.
        if hunger:
            if value == 1:
                return "dice/hd1.webp"
            elif value <= 5:
                return "dice/hd2–5.webp"
            elif value <= 9:
                return "dice/hd6–9.webp"
            else:
                return "dice/hd10.webp"
        else:
            if value <= 5:
                return "dice/d1–5.webp"
            elif value <= 9:
                return "dice/d6–9.webp"
            else:
                return "dice/d10.webp"

    def _dice_rows(dice, per_row=5):
        # Разбиваем список кубиков на строки по 5 штук для переноса.
        return [dice[i:i + per_row] for i in range(0, len(dice), per_row)]

    def roll_check(attr_value, skill_value, difficulty):
        # Реальный бросок: пул = атрибут + навык, голодные кубики забирают
        # часть пула (та же логика, что в check_line — сначала из навыка,
        # остаток из атрибута, но не больше cs_hunger и не больше пула).
        pool = attr_value + skill_value
        hunger_dice = min(cs_hunger, pool)
        skill_hunger = min(hunger_dice, skill_value)
        attr_hunger = hunger_dice - skill_hunger
        normal_dice = pool - hunger_dice

        dice = []
        for _ in range(normal_dice):
            dice.append((renpy.random.randint(1, 10), False))
        for _ in range(hunger_dice):
            dice.append((renpy.random.randint(1, 10), True))

        # Подсчёт успехов:
        # - 1-5: 0 успехов
        # - 6-9: 1 успех
        # - 10: 1 успех, но если десяток несколько — они считаются парами,
        #   и каждая пара даёт 4 успеха вместо 2 (прорыв). Непарный
        #   "лишний" десяток идёт как обычный 1 успех.
        #   (2 десятки = 4, 3 десятки = 4+1 = 5, 4 десятки = 4+4 = 8.)
        tens = sum(1 for value, hunger in dice if value == 10)
        pairs = tens // 2
        leftover_ten = tens % 2
        successes_6_9 = sum(1 for value, hunger in dice if 6 <= value <= 9)
        successes = successes_6_9 + pairs * 4 + leftover_ten

        # ВРЕМЕННО: три исхода без учёта голодных кубиков — Кровавый
        # провал/триумф добавим отдельно позже.
        if successes >= difficulty:
            success = True
            result_text = "УСПЕХ"
        elif successes == 0:
            success = False
            result_text = "ЖЕСТОКИЙ ПРОВАЛ"
        else:
            success = False
            result_text = "ПРОВАЛ"

        return dice, successes, success, result_text


screen check_result(check_name, difficulty, dice, successes, result_text, success):

    $ continue_sound = "audio/ui/success.ogg" if success else "audio/ui/fail.ogg"

    ## Тот же способ продолжить, что и в say/choice — но звук зависит
    ## от исхода проверки, а не стандартный next.ogg.
    key "K_SPACE" action [Play("ui", continue_sound), Return(True)]

    frame:
        xsize CHAT_PANEL_WIDTH
        ysize config.screen_height
        xanchor 1.0
        xpos config.screen_width - 50
        background None

        vbox:
            xfill True
            yfill True

            ## Верхняя зона — тот же размер, что у ленты чата (0.75 экрана),
            ## текст внутри центрирован по вертикали и горизонтали.
            frame:
                ysize int(config.screen_height * 0.75)
                xfill True
                background None

                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 4

                    text "ПРОВЕРКА":
                        font FONT_HEADING
                        size 24
                        color "#ffffff"
                        xalign 0.5

                    text check_name:
                        font FONT_BODY
                        size 18
                        color "#a9a9a9"
                        xalign 0.5

                    null height 50

                    for row in _dice_rows(dice):
                        hbox:
                            xalign 0.5
                            spacing 10
                            for value, hunger in row:
                                add _dice_image(value, hunger)

                    null height 50

                    text "Сложность: {color=#ffffff}[difficulty]{/color}":
                        font FONT_BODY
                        size 20
                        color "#a9a9a9"
                        xalign 0.5

                    text "Успехов: {color=#ffffff}[successes]{/color}":
                        font FONT_BODY
                        size 20
                        color "#a9a9a9"
                        xalign 0.5

                    null height 50

                    text result_text:
                        font FONT_HEADING
                        size 24
                        color "#ffffff"
                        xalign 0.5

            ## Нижняя зона с кнопкой "Дальше" — визуально идентична say/choice.
            frame:
                ysize int(config.screen_height * 0.25)
                xfill True
                background None

                fixed:
                    xfill True
                    yfill True

                    add Solid("#ae5334") xsize CHAT_PANEL_WIDTH ysize 1 ypos 0

                    button:
                        xsize CHAT_PANEL_WIDTH
                        yminimum 50
                        ypos 26
                        background None
                        hover_background "#ae533440"
                        action [Play("ui", continue_sound), Return(True)]

                        text "Дальше":
                            font FONT_BODY
                            color "#ae5334"
                            size 20
                            xoffset 50
                            yalign 0.5


################################################################################
## Тестовый лейбл — чтобы посмотреть окно вживую, без реальной механики.
## Повторяет данные со скриншота-примера. Можно временно вставить
## "call check_result_demo" куда угодно в сюжет или запустить с консоли.
################################################################################

label check_result_demo:

    call screen check_result(
        "Сила + Скрытность",
        2,
        [(7, False), (8, False), (9, True), (6, True), (2, True), (7, False), (3, False)],
        2,
        "УСПЕХ",
        True,
    )

    return
