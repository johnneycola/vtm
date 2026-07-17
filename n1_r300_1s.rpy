# ==========================================
# n1_r300_1s — "Молча съесть её" (Сила + Скрытность: успех)
# ==========================================

label n1_r300_1s:

    show bg bar_outside_feed

    "Я молча запрыгиваю следом и нависаю над ней. В её глазах проскакивает игривый блеск, но она, кажется, не готова к такому резкому развитию событий."
    c "Подожди..."
    think "Я не собираюсь ждать, дорогая."
    "Я обхватываю оба её запястья одной рукой и второй зажимаю ей рот. Игривый огонёк всё ещё скачет в её глазах."
    "С лёгким хрустом я прокусываю её шею. Клэр обмякает, я ослабляю хватку и рот наполняет горячая кровь."

    $ excess_successes = successes - feeding_difficulty
    $ cs_hunger = 3
    call screen feeding_minigame(feeding_difficulty, excess_successes)
    $ earned = _return
    $ cs_hunger = 0 if earned >= 5 else max(cs_hunger - earned, 1)
    if earned >= 5 and cs_humanity + cs_doubts < 10:
        $ cs_doubts += 1

    if earned >= 5:
        show bg bar_outside_feed_blood
    else:
        show bg bar_outside_feed

    jump n1_r300_s_join
