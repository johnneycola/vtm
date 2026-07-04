# ============================================================
#  МОДУЛЬ: механика бросков d10 (правила VtM)
#
#  Используется для любых проверок вида "Атрибут + Навык".
#  Успех = выпало 6 и больше.
#
#  Два варианта использования:
#
#  1) Видимая проверка (игрок видит кубики на экране):
#         $ roll_dice(5, hunger=2)     # бросить 5 кубиков, 2 из них — голод
#         call screen dice_result     # показать результат, ждать "Далее"
#         if dice_successes >= dice_needed:
#             ...
#
#  2) Скрытая проверка (без визуализации, просто True/False):
#         if hidden_check(4, 3):      # 4 кубика, нужно 3 успеха
#             ...
#
#  ── Кубики голода (правило V5) ──────────────────────────────
#  hunger — сколько кубиков из пула являются кубиками голода. Этот
#  модуль ничего не знает про конкретного персонажа и его текущий
#  голод — значение передаёт вызывающий код (обычно cs_hunger_filled
#  из character_sheet_damien.rpy). Если голод больше самого пула —
#  берётся весь пул (кубиков голода не может быть больше, чем
#  кубиков в проверке вообще).
#
#  На экране результата голодные кубики подчёркнуты, а значения
#  1 и 10 окрашиваются красным — но только если они выпали именно
#  на голодном кубике (заготовка под "звериный провал"/"грязный
#  критический успех" — сама логика этих правил здесь не считается,
#  только визуальная подсветка).
# ============================================================

init python:
    import random

    def roll_dice(pool, hunger=0):
        """Бросает pool кубиков d10. hunger — сколько из них кубики голода
        (берутся с конца пула, не больше самого пула). Результат — в
        store.dice_rolls / store.dice_successes / store.dice_hunger_count."""
        store.dice_rolls = []
        store.dice_successes = 0
        store.dice_hunger_count = max(0, min(hunger, pool))
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
default dice_hunger_count = 0


screen dice_result():
    vbox:
        xalign 0.5
        yalign 0.4
        spacing 10

        hbox:
            xalign 0.5
            spacing 8
            for i in range(len(dice_rolls)):
                $ roll = dice_rolls[i]
                # Голодные кубики — последние dice_hunger_count в пуле.
                $ is_hunger = i >= (len(dice_rolls) - dice_hunger_count)

                if is_hunger and roll in (1, 10):
                    # Особая подсветка только на голодных 1 и 10.
                    $ roll_color = "#ff3333"
                    $ roll_outline = "#000000"
                elif roll >= 6:
                    $ roll_color = "#33cc33"
                    $ roll_outline = "#000000"
                else:
                    $ roll_color = "#000000"
                    $ roll_outline = "#888888"

                if is_hunger:
                    text "{u}[roll]{/u}" size 40 color roll_color outlines [(2, roll_outline, 0, 0)]
                else:
                    text "[roll]" size 40 color roll_color outlines [(2, roll_outline, 0, 0)]

        text "Успехов: [dice_successes] / Нужно: [dice_needed]" xalign 0.5 size 28 color "#ffffff"

        if dice_hunger_count > 0:
            text "Голодных кубиков (подчёркнуты): [dice_hunger_count]" xalign 0.5 size 16 color "#cc6666"

        if dice_successes >= dice_needed:
            text "УСПЕХ" xalign 0.5 size 36 color "#33cc33"
        else:
            text "ПРОВАЛ" xalign 0.5 size 36 color "#cc3333"

        textbutton "Далее" action Return() xalign 0.5
