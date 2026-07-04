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
#  На экране результата каждая грань — картинка из game/dice/, но не по
#  каждому конкретному значению, а по диапазону: d1–5.webp (провал),
#  d6–9.webp (успех), d10.webp — для обычных кубиков; hd1.webp,
#  hd2–5.webp, hd6–9.webp, hd10.webp — для голодных (1 и 10 выделены
#  отдельно — это значения, особые для правил V5: звериный провал /
#  грязный критический успех).
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

    def dice_face_image(value, hunger):
        """Путь к картинке кубика. Обычные кубики: провал 1-5, успех 6-9
        и отдельно 10 (нужна для подсчёта пары десяток на критический
        успех) — три картинки, без разбивки на точное число. Голодные
        кубики: отдельно 1 (риск звериного провала) и отдельно 10 (риск
        грязного критического успеха), 2-5 и 6-9 сгруппированы так же."""
        if hunger:
            if value == 1:
                return u"dice/hd1.webp"
            elif value == 10:
                return u"dice/hd10.webp"
            elif value <= 5:
                return u"dice/hd2\u20135.webp"
            else:
                return u"dice/hd6\u20139.webp"
        else:
            if value == 10:
                return u"dice/d10.webp"
            elif value <= 5:
                return u"dice/d1\u20135.webp"
            else:
                return u"dice/d6\u20139.webp"


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

                add dice_face_image(roll, is_hunger)

        text "Успехов: [dice_successes] / Нужно: [dice_needed]" xalign 0.5 size 28 color "#ffffff"

        if dice_hunger_count > 0:
            text "Голодных кубиков: [dice_hunger_count]" xalign 0.5 size 16 color "#cc6666"

        if dice_successes >= dice_needed:
            text "УСПЕХ" xalign 0.5 size 36 color "#33cc33"
        else:
            text "ПРОВАЛ" xalign 0.5 size 36 color "#cc3333"

        textbutton "Далее" action Return() xalign 0.5
