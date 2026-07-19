default claire_name = "Незнакомка"
define c = Character("[claire_name]")
define d = Character("Дамьен")
define mitch = Character("Митч")
define cliff = Character("Клифф")
define lance = Character("Лэнс")
define char_transition_pause = 0.4

# ==========================================
# ПЕРСОНАЖИ: спрайты и позиции
# ==========================================

# Статичная позиция по координатам ЦЕНТРА спрайта
# (в пикселях, от верхнего левого угла экрана/фона).
# Без анимации — мгновенное появление на месте.
transform at_point(x, y):
    xanchor 0.5 yanchor 0.5
    xpos x ypos y


# Позиция с плавным въездом/выездом.
# При show: спрайт стартует на (x - dist) и едет к (x, y).
# При hide: спрайт едет от текущей позиции к (x + dist), затем скрывается.
# dist и time — необязательные параметры, можно переопределить точечно.
# mirror=True — отзеркалить спрайт по горизонтали (для "оборотных" ракурсов).
#
# zorder сюда не добавить — это не свойство трансформа/ATL, оно живёт
# в списке сцены и назначается только через сам show (см. script.rpy:
# "show ... zorder 0/1" — front/back).
transform char_pos(x, y, dist=800, time=0.4, mirror=False):
    on show:
        xanchor 0.5 yanchor 0.5
        xpos x - dist
        ypos y
        xzoom (-1 if mirror else 1)
        easeout time xpos x
    on hide:
        easein time xpos x + dist


# Уход персонажа из кадра целиком (не смена ракурса, а прощание со сценой).
# Базовые xanchor/xpos/ypos применяются сразу, без анимации на входе —
# это нужно, чтобы show...at этим transform'ом не вызвал лишний скачок,
# если персонаж уже стоит в этой точке (см. использование ниже).
# Анимация целиком в on hide: дальний сдвиг + плавное растворение.
transform char_leave(x, y, dist=800, time=0.4, mirror=False):
    xanchor 0.5 yanchor 0.5
    xpos x
    ypos y
    xzoom (-1 if mirror else 1)
    on hide:
        easein time xpos x + dist alpha 0.0


# Сдвиг уже показанного персонажа с текущего места — не появление и не
# уход, просто смещение по горизонтали (например, чтобы "сфокусировать"
# говорящего, подвинув пару фронт-портретов вправо/влево). dx — это
# смещение ОТ базовой позиции (положительное — вправо, отрицательное —
# влево), не абсолютная координата: `char_shift(560)` двигает персонажа
# на 560px правее того места, что уже задано его pos-трансформом.
# Чтобы вернуть на место — тот же show ...at ..., char_shift(0) с тем же
# базовым pos-трансформом.
transform char_shift(dx, time=0.4):
    ease time xoffset dx


# ==========================================
# ШАБЛОН РАСКЛАДКИ (см. Дамьена ниже для примера использования)
#
# ОДИН НА ОДИН       — x_front_pos / x_front_leave / x_back_pos / x_back_leave
#                       (без суффикса, уже готово и не трогается —
#                       у каждого персонажа своё X И Y, ничего общего)
# ОДИН ПРОТИВ ДВОИХ   — x_front_pos_3 / x_back_pos_3 (+_leave)
#                       (этот персонаж один, X универсален: 650 / 700)
# ДВА ПРОТИВ ОДНОГО   — x_front_pos_3left/_3right, x_back_pos_3left/_3right (+_leave)
#                       (этот персонаж в паре, X универсален:
#                       фронт 300/1100, спина 100/1450)
# ДВА НА ДВА          — x_front_pos_4left/_4right, x_back_pos_4left/_4right (+_leave)
#                       (X универсален: фронт 400/900, спина 100/1450)
#
# Во всех случаях Y берётся из СОБСТВЕННЫХ x_front_pos/x_back_pos
# персонажа (один на один) — по вертикали персонажи не меняются.
# ==========================================


# ------------------------------------------
# Дамьен
# ------------------------------------------

# ------------------------------------------
# ОДИН НА ОДИН

# Один на один ЛИЦО
# ------------------------------------------
image damien front = "ch/damien-front.webp"
transform damien_front_pos:
    char_pos(960, 1005, dist=200)
transform damien_front_leave:
    char_leave(960, 1005, dist=600)

# Один на один СПИНА
# ------------------------------------------
image damien back = "ch/damien-back.webp"
transform damien_back_pos:
    char_pos(305, 1864, dist=600)
transform damien_back_leave:
    char_leave(305, 1864, dist=1800)

# ------------------------------------------
# ОДИН ПРОТИВ ДВОИХ

# Один против двоих ЛИЦО
# ------------------------------------------
transform damien_front_pos_3:
    char_pos(650, 1005, dist=200)
transform damien_front_leave_3:
    char_leave(650, 1005, dist=600)

# Один против двоих СПИНА
# ------------------------------------------
transform damien_back_pos_3:
    char_pos(700, 1864, dist=600)
transform damien_back_leave_3:
    char_leave(700, 1864, dist=1800)

# ------------------------------------------
# ДВА ПРОТИВ ОДНОГО

# Два против одного ЛИЦО
# ------------------------------------------
    #Слева
transform damien_front_pos_3left:
    char_pos(300, 1005, dist=200, mirror=True)
transform damien_front_leave_3left:
    char_leave(300, 1005, dist=600, mirror=True)

    #Справа
transform damien_front_pos_3right:
    char_pos(1100, 1005, dist=200)
transform damien_front_leave_3right:
    char_leave(1100, 1005, dist=600)

# Два против одного СПИНА
# ------------------------------------------
    #Слева
transform damien_back_pos_3left:
    char_pos(100, 1864, dist=600)
transform damien_back_leave_3left:
    char_leave(100, 1864, dist=1800)

    #Справа
transform damien_back_pos_3right:
    char_pos(1300, 1864, dist=600, mirror=True)
transform damien_back_leave_3right:
    char_leave(1300, 1864, dist=1800, mirror=True)

# ------------------------------------------
# ДВА НА ДВА

# Два на два ЛИЦО
# ------------------------------------------
    #Слева
transform damien_front_pos_4left:
    char_pos(400, 1005, dist=200, mirror=True)
transform damien_front_leave_4left:
    char_leave(400, 1005, dist=600, mirror=True)

    #Справа
transform damien_front_pos_4right:
    char_pos(900, 1005, dist=200)
transform damien_front_leave_4right:
    char_leave(900, 1005, dist=600)

# Два на два СПИНА
# ------------------------------------------
    #Слева
transform damien_back_pos_4left:
    char_pos(100, 1864, dist=600)
transform damien_back_leave_4left:
    char_leave(100, 1864, dist=1800)

    #Справа
transform damien_back_pos_4right:
    char_pos(1450, 1864, dist=600, mirror=True)
transform damien_back_leave_4right:
    char_leave(1450, 1864, dist=1800, mirror=True)


# ------------------------------------------
# Клэр
# ------------------------------------------

# ------------------------------------------
# ОДИН НА ОДИН

# Один на один ЛИЦО
# ------------------------------------------
image claire front = "ch/claire-front.webp"
transform claire_front_pos:
    char_pos(934, 1092, dist=200)
transform claire_front_leave:
    char_leave(934, 1092, dist=600)

# Один на один СПИНА
# ------------------------------------------
image claire back = "ch/claire-back.webp"
transform claire_back_pos:
    char_pos(294, 1746, dist=600)
transform claire_back_leave:
    char_leave(294, 1746, dist=1800)

# ------------------------------------------
# ОДИН ПРОТИВ ДВОИХ

# Один против двоих ЛИЦО
# ------------------------------------------
transform claire_front_pos_3:
    char_pos(650, 1092, dist=200)
transform claire_front_leave_3:
    char_leave(650, 1092, dist=600)

# Один против двоих СПИНА
# ------------------------------------------
transform claire_back_pos_3:
    char_pos(700, 1746, dist=600)
transform claire_back_leave_3:
    char_leave(700, 1746, dist=1800)

# ------------------------------------------
# ДВА ПРОТИВ ОДНОГО

# Два против одного ЛИЦО
# ------------------------------------------
    #Слева
transform claire_front_pos_3left:
    char_pos(300, 1092, dist=200, mirror=True)
transform claire_front_leave_3left:
    char_leave(300, 1092, dist=600, mirror=True)

    #Справа
transform claire_front_pos_3right:
    char_pos(1100, 1092, dist=200)
transform claire_front_leave_3right:
    char_leave(1100, 1092, dist=600)

# Два против одного СПИНА
# ------------------------------------------
    #Слева
transform claire_back_pos_3left:
    char_pos(100, 1746, dist=600)
transform claire_back_leave_3left:
    char_leave(100, 1746, dist=1800)

    #Справа
transform claire_back_pos_3right:
    char_pos(1450, 1746, dist=600, mirror=True)
transform claire_back_leave_3right:
    char_leave(1450, 1746, dist=1800, mirror=True)

# ------------------------------------------
# ДВА НА ДВА

# Два на два ЛИЦО
# ------------------------------------------
    #Слева
transform claire_front_pos_4left:
    char_pos(400, 1092, dist=200, mirror=True)
transform claire_front_leave_4left:
    char_leave(400, 1092, dist=600, mirror=True)

    #Справа
transform claire_front_pos_4right:
    char_pos(900, 1092, dist=200)
transform claire_front_leave_4right:
    char_leave(900, 1092, dist=600)

# Два на два СПИНА
# ------------------------------------------
    #Слева
transform claire_back_pos_4left:
    char_pos(100, 1746, dist=600)
transform claire_back_leave_4left:
    char_leave(100, 1746, dist=1800)

    #Справа
transform claire_back_pos_4right:
    char_pos(1450, 1746, dist=600, mirror=True)
transform claire_back_leave_4right:
    char_leave(1450, 1746, dist=1800, mirror=True)


# ------------------------------------------
# Митч
# ------------------------------------------

# ------------------------------------------
# ОДИН НА ОДИН

# Один на один ЛИЦО
# ------------------------------------------
image mitch front = "ch/mitch-front.webp"
transform mitch_front_pos:
    char_pos(960, 1020, dist=200)
transform mitch_front_leave:
    char_leave(960, 1020, dist=600)

# Один на один СПИНА
# ------------------------------------------
image mitch back = "ch/mitch-back.webp"
transform mitch_back_pos:
    char_pos(305, 1864, dist=600)
transform mitch_back_leave:
    char_leave(305, 1864, dist=1800)

# ------------------------------------------
# ОДИН ПРОТИВ ДВОИХ

# Один против двоих ЛИЦО
# ------------------------------------------
transform mitch_front_pos_3:
    char_pos(650, 1020, dist=200)
transform mitch_front_leave_3:
    char_leave(650, 1020, dist=600)

# Один против двоих СПИНА
# ------------------------------------------
transform mitch_back_pos_3:
    char_pos(700, 1864, dist=600)
transform mitch_back_leave_3:
    char_leave(700, 1864, dist=1800)

# ------------------------------------------
# ДВА ПРОТИВ ОДНОГО

# Два против одного ЛИЦО
# ------------------------------------------
    #Слева
transform mitch_front_pos_3left:
    char_pos(300, 1020, dist=200, mirror=True)
transform mitch_front_leave_3left:
    char_leave(300, 1020, dist=600, mirror=True)

    #Справа
transform mitch_front_pos_3right:
    char_pos(1100, 1020, dist=200)
transform mitch_front_leave_3right:
    char_leave(1100, 1020, dist=600)

# Два против одного СПИНА
# ------------------------------------------
    #Слева
transform mitch_back_pos_3left:
    char_pos(100, 1864, dist=600)
transform mitch_back_leave_3left:
    char_leave(100, 1864, dist=1800)

    #Справа
transform mitch_back_pos_3right:
    char_pos(1300, 1864, dist=600, mirror=True)
transform mitch_back_leave_3right:
    char_leave(1300, 1864, dist=1800, mirror=True)

# ------------------------------------------
# ДВА НА ДВА

# Два на два ЛИЦО
# ------------------------------------------
    #Слева
transform mitch_front_pos_4left:
    char_pos(400, 1020, dist=200, mirror=True)
transform mitch_front_leave_4left:
    char_leave(400, 1020, dist=600, mirror=True)

    #Справа
transform mitch_front_pos_4right:
    char_pos(900, 1020, dist=200)
transform mitch_front_leave_4right:
    char_leave(900, 1020, dist=600)

# Два на два СПИНА
# ------------------------------------------
    #Слева
transform mitch_back_pos_4left:
    char_pos(100, 1864, dist=600)
transform mitch_back_leave_4left:
    char_leave(100, 1864, dist=1800)

    #Справа
transform mitch_back_pos_4right:
    char_pos(1450, 1864, dist=600, mirror=True)
transform mitch_back_leave_4right:
    char_leave(1450, 1864, dist=1800, mirror=True)


# ------------------------------------------
# Клифф
# ------------------------------------------

# ------------------------------------------
# ОДИН НА ОДИН

# Один на один ЛИЦО
# ------------------------------------------
image cliff front = "ch/cliff-front.webp"
transform cliff_front_pos:
    char_pos(930, 1005, dist=200)
transform cliff_front_leave:
    char_leave(930, 1005, dist=600)

# Один на один СПИНА
# ------------------------------------------
image cliff back = "ch/cliff-back.webp"
transform cliff_back_pos:
    char_pos(305, 1864, dist=600)
transform cliff_back_leave:
    char_leave(305, 1864, dist=1800)

# ------------------------------------------
# ОДИН ПРОТИВ ДВОИХ

# Один против двоих ЛИЦО
# ------------------------------------------
transform cliff_front_pos_3:
    char_pos(650, 1005, dist=200)
transform cliff_front_leave_3:
    char_leave(650, 1005, dist=600)

# Один против двоих СПИНА
# ------------------------------------------
transform cliff_back_pos_3:
    char_pos(700, 1864, dist=600)
transform cliff_back_leave_3:
    char_leave(700, 1864, dist=1800)

# ------------------------------------------
# ДВА ПРОТИВ ОДНОГО

# Два против одного ЛИЦО
# ------------------------------------------
    #Слева
transform cliff_front_pos_3left:
    char_pos(300, 1005, dist=200, mirror=True)
transform cliff_front_leave_3left:
    char_leave(300, 1005, dist=600, mirror=True)

    #Справа
transform cliff_front_pos_3right:
    char_pos(1100, 1005, dist=200)
transform cliff_front_leave_3right:
    char_leave(1100, 1005, dist=600)

# Два против одного СПИНА
# ------------------------------------------
    #Слева
transform cliff_back_pos_3left:
    char_pos(100, 1864, dist=600)
transform cliff_back_leave_3left:
    char_leave(100, 1864, dist=1800)

    #Справа
transform cliff_back_pos_3right:
    char_pos(1450, 1864, dist=600, mirror=True)
transform cliff_back_leave_3right:
    char_leave(1450, 1864, dist=1800, mirror=True)

# ------------------------------------------
# ДВА НА ДВА

# Два на два ЛИЦО
# ------------------------------------------
    #Слева
transform cliff_front_pos_4left:
    char_pos(400, 1005, dist=200, mirror=True)
transform cliff_front_leave_4left:
    char_leave(400, 1005, dist=600, mirror=True)

    #Справа
transform cliff_front_pos_4right:
    char_pos(900, 1005, dist=200)
transform cliff_front_leave_4right:
    char_leave(900, 1005, dist=600)

# Два на два СПИНА
# ------------------------------------------
    #Слева
transform cliff_back_pos_4left:
    char_pos(100, 1864, dist=600)
transform cliff_back_leave_4left:
    char_leave(100, 1864, dist=1800)

    #Справа
transform cliff_back_pos_4right:
    char_pos(1450, 1864, dist=600, mirror=True)
transform cliff_back_leave_4right:
    char_leave(1450, 1864, dist=1800, mirror=True)


# ------------------------------------------
# Лэнс
# ------------------------------------------

# ------------------------------------------
# ОДИН НА ОДИН

# Один на один ЛИЦО
# ------------------------------------------
image lance front = "ch/lance-front.webp"
transform lance_front_pos:
    char_pos(960, 1100, dist=200)
transform lance_front_leave:
    char_leave(960, 1100, dist=600)

# Один на один СПИНА
# ------------------------------------------
image lance back = "ch/lance-back.webp"
transform lance_back_pos:
    char_pos(305, 1864, dist=600)
transform lance_back_leave:
    char_leave(305, 1864, dist=1800)

# ------------------------------------------
# ОДИН ПРОТИВ ДВОИХ

# Один против двоих ЛИЦО
# ------------------------------------------
transform lance_front_pos_3:
    char_pos(650, 1100, dist=200)
transform lance_front_leave_3:
    char_leave(650, 1100, dist=600)

# Один против двоих СПИНА
# ------------------------------------------
transform lance_back_pos_3:
    char_pos(700, 1864, dist=600)
transform lance_back_leave_3:
    char_leave(700, 1864, dist=1800)

# ------------------------------------------
# ДВА ПРОТИВ ОДНОГО

# Два против одного ЛИЦО
# ------------------------------------------
    #Слева
transform lance_front_pos_3left:
    char_pos(300, 1100, dist=200, mirror=True)
transform lance_front_leave_3left:
    char_leave(300, 1100, dist=600, mirror=True)

    #Справа
transform lance_front_pos_3right:
    char_pos(1100, 1100, dist=200)
transform lance_front_leave_3right:
    char_leave(1100, 1100, dist=600)

# Два против одного СПИНА
# ------------------------------------------
    #Слева
transform lance_back_pos_3left:
    char_pos(100, 1864, dist=600)
transform lance_back_leave_3left:
    char_leave(100, 1864, dist=1800)

    #Справа
transform lance_back_pos_3right:
    char_pos(1450, 1864, dist=600, mirror=True)
transform lance_back_leave_3right:
    char_leave(1450, 1864, dist=1800, mirror=True)

# ------------------------------------------
# ДВА НА ДВА

# Два на два ЛИЦО
# ------------------------------------------
    #Слева
transform lance_front_pos_4left:
    char_pos(400, 1100, dist=200, mirror=True)
transform lance_front_leave_4left:
    char_leave(400, 1100, dist=600, mirror=True)

    #Справа
transform lance_front_pos_4right:
    char_pos(900, 1100, dist=200)
transform lance_front_leave_4right:
    char_leave(900, 1100, dist=600)

# Два на два СПИНА
# ------------------------------------------
    #Слева
transform lance_back_pos_4left:
    char_pos(100, 1864, dist=600)
transform lance_back_leave_4left:
    char_leave(100, 1864, dist=1800)

    #Справа
transform lance_back_pos_4right:
    char_pos(1450, 1864, dist=600, mirror=True)
transform lance_back_leave_4right:
    char_leave(1450, 1864, dist=1800, mirror=True)
