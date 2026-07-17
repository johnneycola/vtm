# ==========================================
# ФОНЫ
# ==========================================

# Позиция фона с плавным въездом/выездом при смене.
# Картинка должна быть шире экрана минимум на 2*dist
# (у нас 2020 при экране 1920 — запас ровно 100,
# то есть по 50px на сторону, впритык под dist=50).
transform bg_pos(dist=50, time=0.4):
    on show:
        xanchor 0.5 yanchor 0.0
        xpos 960 - dist
        ypos 0
        easeout time xpos 960
    on hide:
        easein time xpos 960 + dist


# ------------------------------------------
# Сцены
# ------------------------------------------
image bg bar_scene = "bg/bar_scene.webp"
image bg bar_inside = "bg/bar_inside.webp"
image bg bar_outside = "bg/bar_outside.webp"
image bg motel = "bg/motel.webp"
image bg bar_outside_alarm = "bg/bar_outside_alarm.webp"
image bg bar_outside_door = "bg/bar_outside_door.webp"
image bg claire = "bg/claire.webp"
image bg claire_happy = "bg/claire_happy.webp"
image bg claire_sad = "bg/claire_sad.webp"
image bg bar_outside_feed = "bg/bar_outside_feed.webp"
image bg bar_outside_feed_blood = "bg/bar_outside_feed_blood.webp"