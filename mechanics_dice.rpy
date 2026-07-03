# ============================================================
#  МОДУЛЬ: механика бросков d10 (правила VtM)
#
#  Используется для любых проверок вида "Атрибут + Навык".
#  Успех = выпало 6 и больше.
#
#  Два варианта использования:
#
#  1) Видимая проверка (игрок видит кубики на экране):
#         $ roll_dice(5)              # бросить 5 кубиков
#         call screen dice_result     # показать результат, ждать "Далее"
#         if dice_successes >= dice_needed:
#             ...
#
#  2) Скрытая проверка (без визуализации, просто True/False):
#         if hidden_check(4, 3):      # 4 кубика, нужно 3 успеха
#             ...
# ============================================================

init python:
    import random

    def roll_dice(pool):
        """Бросает pool кубиков d10, кладёт результат в store.dice_rolls /
        store.dice_successes — для показа через screen dice_result."""
        store.dice_rolls = []
        store.dice_successes = 0
        for i in range(pool):
            roll = random.randint(1, 10)
            store.dice_rolls.append(roll)
            if roll >= 6:
                store.dice_successes += 1

    def hidden_check_successes(pool):
        """Как roll_dice, но без визуализации — просто число успехов."""
        return sum(1 for _ in range(pool) if random.randint(1, 10) >= 6)

    def hidden_check(pool, needed):
        """Скрытая проверка: True, если набрано >= needed успехов из pool кубиков."""
        return hidden_check_successes(pool) >= needed


default dice_rolls = []
default dice_successes = 0
default dice_needed = 2


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
