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


# ------------------------------------------
# Анимированные фоны выступления — случайное no-repeat слайд-шоу
# по 3 кадрам с коротким дисолвом, 4 кадра/сек.
#
# ВАЖНО про тайминг: раньше стейт продвигался по параметру "st"
# (shown time), который DynamicDisplayable получает от Ren'Py — но во
# время call screen rhythm_intro/rhythm_game (много собственных
# таймеров и перерисовок: падающие ноты, отсчёт, подсветки) Ren'Py
# зовёт функцию рендера чаще и с не всегда монотонным "st" (в т.ч. для
# предиктивных проходов), а у нас внутри были побочные эффекты —
# отсюда бешеное мельтешение именно во время ритм-игр. Правильно тут,
# как и у подсветки стрелок/нот в rhythm_game.rpy (RhythmGameState.
# lane_flash_until/note_flashes) — считать по renpy.time.time()
# (настоящие системные часы). Тогда сколько раз функцию ни вызови при
# одном и том же реальном времени — результат один и тот же, лишние
# вызовы больше не двигают стейт непредсказуемо вперёд.
#
# ПОЧЕМУ НЕ ЧИСТЫЙ ATL: первая версия делала это через "марковскую
# цепь" из трёх image, ссылающихся друг на друга по имени — ловит
# RecursionError (Ren'Py на некоторых внутренних проходах, например
# find_focusable, обходит ATL-граф текущей сцены целиком через
# .visit(), не отслеживая посещённые узлы, а цикл из перекрёстных
# ссылок для такого обхода бесконечен). Поэтому весь стейт — на
# стороне Python, картинка отдаётся через DynamicDisplayable, никаких
# ссылок между image.
# ------------------------------------------

init python:

    class RandomSlideshowState(object):
        """No-repeat случайное слайд-шоу с коротким дисолвом между
        кадрами. Один инстанс на набор картинок. Продвигается по
        renpy.time.time() — реальным системным часам, не по "st" от
        DynamicDisplayable (см. комментарий выше). reset() вызывается
        вручную из script.rpy прямо перед каждым show, чтобы гарантирo-
        ванно начинать со свежего случайного кадра и без остатка
        прогресса от предыдущего показа этого же набора."""

        FPS = 4.0
        FRAME_SECONDS = 1.0 / FPS
        FADE_SECONDS = 0.08          # короткий фэйд между кадрами
        POLL_SECONDS = 0.02          # частота перерисовки — как у
                                      # остальных таймеров в проекте
                                      # (RhythmGameState и т.п.)

        def __init__(self, images):
            self.images = list(images)
            self.frame_start = None   # renpy.time.time() начала текущего кадра
            self.current = renpy.random.choice(self.images)
            self.previous = None

        def _advance(self):
            # Следующий кадр — случайно, но никогда не тот же самый,
            # что уже показан.
            choices = [i for i in self.images if i != self.current]
            self.previous = self.current
            self.current = renpy.random.choice(choices)

        def reset(self):
            self.frame_start = None
            self.previous = None
            self.current = renpy.random.choice(self.images)

        def render(self, st, at):
            now = renpy.time.time()
            if self.frame_start is None:
                self.frame_start = now

            elapsed = now - self.frame_start
            # На случай долгого перерыва между рендерами (например,
            # блокирующий call/пауза) досчитываем сколько угодно кадров
            # разом, а не как попало.
            while elapsed >= self.FRAME_SECONDS:
                self.frame_start += self.FRAME_SECONDS
                elapsed -= self.FRAME_SECONDS
                self._advance()

            if self.previous is not None and elapsed < self.FADE_SECONDS:
                frac = elapsed / self.FADE_SECONDS
                child = Fixed(
                    Image(self.previous),
                    Transform(Image(self.current), alpha=frac),
                )
            else:
                child = Image(self.current)

            return child, self.POLL_SECONDS

    _band_slideshow = RandomSlideshowState(["bg/band-1.webp", "bg/band-2.webp", "bg/band-3.webp"])
    _playing_slideshow = RandomSlideshowState(["bg/playing-1.webp", "bg/playing-2.webp", "bg/playing-3.webp"])
    _singing_slideshow = RandomSlideshowState(["bg/singing-1.webp", "bg/singing-2.webp", "bg/singing-3.webp"])
    _solo_slideshow = RandomSlideshowState(["bg/solo-1.webp", "bg/solo-2.webp", "bg/solo-3.webp"])

    def show_random_bg(slideshow, image_name):
        """Мгновенно переключает тег "bg" на анимированное слайд-шоу,
        предварительно сбросив его на свежий случайный кадр. Без
        hide/pause (в отличие от обычных переходов по сценарию) — эта
        функция вызывается изнутри уже идущего call screen rhythm_intro
        (см. on_countdown_end в RhythmIntroState), а там script-level
        "pause" недоступен. Переход всё равно плавный — bg_pos сама
        анимирует "on show" въезд новой картинки."""
        slideshow.reset()
        renpy.show(image_name, at_list=[bg_pos])

    def show_playing_bg():
        show_random_bg(_playing_slideshow, "bg playing_random")

    def show_solo_bg():
        show_random_bg(_solo_slideshow, "bg solo_random")

image bg band_random = DynamicDisplayable(_band_slideshow.render)
image bg playing_random = DynamicDisplayable(_playing_slideshow.render)
image bg singing_random = DynamicDisplayable(_singing_slideshow.render)
image bg solo_random = DynamicDisplayable(_solo_slideshow.render)
