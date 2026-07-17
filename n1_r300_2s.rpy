# ==========================================
# n1_r300_2s — "Пошутить" (Харизма + Убеждение: успех)
# Доступно только если heard_claire_full_story == True
# ==========================================

label n1_r300_2s:

    show bg claire

    d "Если что, я никогда не был в Остине..."
    "Она выглядывает и с игривой улыбкой говорит..."
    c "Что, и Теслы у тебя тоже нет?"
    "Я оборачиваюсь, осматриваю парковку, пожимаю плечами..."
    d "Последний раз, когда я проверял, не было."
    c "Значит нам придётся обойтись как-нибудь без них."
    d "Ничего, у меня есть кое-что получше."
    c "Не сомневаюсь..."
    show bg claire_happy
    "Она заливается смехом и откидывается на заднее сиденье, закрыв глаза руками."
    "Съесть её теперь вообще не составит труда."
    "Я нависаю над ней. С лёгким хрустом прокусываю шею. Клэр обмякает и рот наполняет горячая кровь."

    show bg bar_outside_feed
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
