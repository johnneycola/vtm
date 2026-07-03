# ============================================================
#  МОДУЛЬ: универсальная мини-игра питания
#
#  Ничего не знает о конкретных персонажах и сюжете. Задача —
#  прокрутить "весы" и вернуть наружу feeding_blood: сколько
#  точек крови выпил игрок (1-5).
#
#  Единственное жёсткое правило внутри модуля: на 5 точках
#  мини-игра сама останавливается (game_over) — считается, что
#  жертва в любом случае умирает. Всё, что означают 1-4 точки
#  для конкретной жертвы, решает вызывающая сцена (см. пример
#  ниже и character_state.rpy для хранения статуса жертвы).
#
#  Как пользоваться из сюжетного лейбла:
#
#      label feeding_someone:
#          $ feeding_difficulty = 2      # 1 (легко) или 2 (сложнее)
#          $ feeding_speed = 0.004       # скорость курсора, чем меньше — тем легче
#
#          call feeding_start
#
#          # feeding_blood теперь содержит 1-5 — решаем сами, что случилось
#          if feeding_blood <= 2:
#              $ set_character_status("someone", STATUS_ALIVE)
#              "Жертва жива и в сознании."
#          elif feeding_blood == 5:
#              $ set_character_status("someone", STATUS_DEAD)
#              "Жертва мертва."
#          else:
#              # 3 и 4 — на усмотрение сцены: фиксированный исход,
#              # скрытая проверка через hidden_check(), что угодно
#              if hidden_check(4, feeding_blood):
#                  $ set_character_status("someone", STATUS_UNCONSCIOUS)
#                  "Жертва без сознания, но жива."
#              else:
#                  $ set_character_status("someone", STATUS_DEAD)
#                  "Жертва мертва."
#
#          return
# ============================================================

init python:
    def calc_feeding_zone(difficulty):
        """Размер зелёной зоны как доля от высоты шкалы."""
        if difficulty == 1:
            return 1.0 / 6.0
        else:
            return 1.0 / 7.0


default feeding_difficulty = 2      # 1 или 2 — размер зелёной зоны
default feeding_speed      = 0.004  # скорость курсора (0.0-1.0 за секунду)
default feeding_blood      = 0      # РЕЗУЛЬТАТ: сколько точек крови выпито (1-5)

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
    default timeout_progress = 0.0  # 0.0-1.0, таймаут = 1/4 полного пути
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


label feeding_start:
    # Общее меню-обёртка: даёт посмотреть правила перед началом.
    # feeding_difficulty и feeding_speed должны быть выставлены
    # ДО вызова этого лейбла (call feeding_start).
    menu:
        "Пить":
            pass
        "Правила":
            call screen feeding_rules
            jump feeding_start

    $ feeding_blood = 0
    call screen feeding_minigame
    return
