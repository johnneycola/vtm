default claire_name = "Незнакомка"
define c = Character("[claire_name]")
define d = Character("Дамьен")
define mitch = Character("Митч")
define cliff = Character("Клифф")
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


# ------------------------------------------
# Дамьен
# ------------------------------------------
# image damien front = "ch/damien-front.webp"
# Такая запись (имя + attribute через пробел) — это
# стандартная схема Ren'Py для "layered image":
# позволяет потом просто писать "show damien front",
# а если добавишь другие позы (damien-angry.webp и т.д.),
# они автоматически подхватятся как атрибуты того же
# персонажа: "show damien angry".
image damien front = "ch/damien-front.webp"
transform damien_front_pos:
    char_pos(960, 1005, dist=200)
transform damien_front_leave:
    char_leave(960, 1005, dist=600)

image damien back = "ch/damien-back.webp"
transform damien_back_pos:
    char_pos(305, 1864, dist=600)
transform damien_back_leave:
    char_leave(305, 1864, dist=1800)

# Стили "2 персонажа и этот слева/справа" — отличаются только позицией
# по горизонтали. Пока координаты те же, что и у обычных front/back —
# подвинешь сам, когда будешь расставлять кадр под троих.
transform damien_front_pos_left:
    char_pos(150, 1005, dist=200)
transform damien_front_pos_right:
    char_pos(900, 1005, dist=200)
transform damien_front_leave_left:
    char_leave(150, 1005, dist=600)
transform damien_front_leave_right:
    char_leave(900, 1005, dist=600)

transform damien_back_pos_left:
    char_pos(500, 1864, dist=600)
transform damien_back_pos_right:
    char_pos(1450, 1864, dist=600, mirror=True)
transform damien_back_leave_left:
    char_leave(500, 1864, dist=1800)
transform damien_back_leave_right:
    char_leave(1450, 1864, dist=1800, mirror=True)


# ------------------------------------------
# Клэр
# ------------------------------------------
image claire front = "ch/claire-front.webp"
transform claire_front_pos:
    char_pos(934, 1092, dist=200)
transform claire_front_leave:
    char_leave(934, 1092, dist=600)

image claire back = "ch/claire-back.webp"
transform claire_back_pos:
    char_pos(294, 1746, dist=600)
transform claire_back_leave:
    char_leave(294, 1746, dist=1800)

# Стили "2 персонажа и этот слева/справа" — см. комментарий у Дамьена.
transform claire_front_pos_left:
    char_pos(150, 1092, dist=200)
transform claire_front_pos_right:
    char_pos(900, 1092, dist=200)
transform claire_front_leave_left:
    char_leave(150, 1092, dist=600)
transform claire_front_leave_right:
    char_leave(900, 1092, dist=600)

transform claire_back_pos_left:
    char_pos(500, 1746, dist=600)
transform claire_back_pos_right:
    char_pos(1450, 1746, dist=600, mirror=True)
transform claire_back_leave_left:
    char_leave(500, 1746, dist=1800)
transform claire_back_leave_right:
    char_leave(1450, 1746, dist=1800, mirror=True)


# ------------------------------------------
# Митч
# ------------------------------------------
image mitch front = "ch/mitch-front.webp"
transform mitch_front_pos:
    char_pos(960, 1020, dist=200)
transform mitch_front_leave:
    char_leave(960, 1020, dist=600)

image mitch back = "ch/mitch-back.webp"
transform mitch_back_pos:
    char_pos(305, 1864, dist=600)
transform mitch_back_leave:
    char_leave(305, 1864, dist=1800)

# Стили "2 персонажа и этот слева/справа" — см. комментарий у Дамьена.
transform mitch_front_pos_left:
    char_pos(150, 1020, dist=200)
transform mitch_front_pos_right:
    char_pos(900, 1020, dist=200)
transform mitch_front_leave_left:
    char_leave(150, 1020, dist=600)
transform mitch_front_leave_right:
    char_leave(900, 1020, dist=600)

transform mitch_back_pos_left:
    char_pos(500, 1864, dist=600)
transform mitch_back_pos_right:
    char_pos(1450, 1864, dist=600, mirror=True)
transform mitch_back_leave_left:
    char_leave(500, 1864, dist=1800)
transform mitch_back_leave_right:
    char_leave(1450, 1864, dist=1800, mirror=True)


# ------------------------------------------
# Клифф
# ------------------------------------------
image cliff front = "ch/cliff-front.webp"
transform cliff_front_pos:
    char_pos(930, 1005, dist=200)
transform cliff_front_leave:
    char_leave(930, 1005, dist=600)

image cliff back = "ch/cliff-back.webp"
transform cliff_back_pos:
    char_pos(305, 1864, dist=600)
transform cliff_back_leave:
    char_leave(305, 1864, dist=1800)

# Стили "2 персонажа и этот слева/справа" — см. комментарий у Дамьена.
transform cliff_front_pos_left:
    char_pos(150, 1005, dist=200)
transform cliff_front_pos_right:
    char_pos(900, 1005, dist=200)
transform cliff_front_leave_left:
    char_leave(150, 1005, dist=600)
transform cliff_front_leave_right:
    char_leave(900, 1005, dist=600)

transform cliff_back_pos_left:
    char_pos(500, 1864, dist=600)
transform cliff_back_pos_right:
    char_pos(1450, 1864, dist=600, mirror=True)
transform cliff_back_leave_left:
    char_leave(500, 1864, dist=1800)
transform cliff_back_leave_right:
    char_leave(1450, 1864, dist=1800, mirror=True)
