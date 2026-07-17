# ==========================================
# n1_r300_3s — "Быть романтичным" (Самообладание + Убеждение: успех)
# ==========================================

label n1_r300_3s:

    show bg bar_outside_door

    "Я залезаю следом. В её глазах проскакивает игривый блеск, но я сажусь рядом и нежно беру её ладонь. Она на секунду замирает."
    c "У тебя такие холодные руки."
    "Она явно ждёт, что я что-нибудь отвечу, но я просто молча смотрю на неё, всеми силами изображая очарование."
    c "Ну и... что дальше?"
    "Я немного наклоняюсь к ней, она тоже подаётся вперёд и в тот момент, как она закрывает глаза для поцелуя, я целюсь чуть ниже."
    "С лёгким хрустом я прокусываю её шею. Клэр обмякает и рот наполняет горячая кровь."

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
