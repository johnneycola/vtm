################################################################################
## Мини-игра "Питание" — полоска с бегающим курсором, надо остановить его
## в зоне по центру. Показывается вместо чата, как и check_result.
##
## Использовать так (в конце _s-веток, перед jump n1_r300_s_join):
##
##     $ excess_successes = successes - feeding_difficulty
##     call screen feeding_minigame(feeding_difficulty, excess_successes)
##
## difficulty        — сложность питания (feeding_difficulty на момент вызова).
## excess_successes  — успехи сверх сложности (может быть 0, не бывает
##                      отрицательным по смыслу, но на всякий случай
##                      подстраховано внутри).
##
## Ничего не кэширует между вызовами — каждый call создаёт свежий объект
## состояния из переданных аргументов, так что если по сюжету мини-игра
## понадобится снова с другими цифрами — просто передай их.
################################################################################

init python:

    class FeedingMinigameState(object):

        BAR_WIDTH = 400
        BAR_HEIGHT = 25
        CURSOR_WIDTH = 4
        BASE_ROUND_TRIP = 1.5  # секунд на один проход туда-обратно на БАЗОВОЙ скорости
                                # (успехов ровно столько, сколько требовала сложность)

        DIFFICULTY_MIN = 1
        DIFFICULTY_MAX = 8
        ZONE_AT_MIN_DIFFICULTY = 100   # ширина зоны при сложности 1 (самая большая)
        ZONE_AT_MAX_DIFFICULTY = CURSOR_WIDTH * 3  # ширина зоны при сложности 8 (самая маленькая)

        # За каждый успех сверх сложности скорость падает на эту долю.
        # За каждый пройденный круг скорость растёт на 1/4 этой же доли —
        # то есть 4 круга ощущаются как один такой "успех", но в обратную
        # сторону (быстрее, а не медленнее).
        EXCESS_SPEED_STEP = 0.35
        LAP_SPEED_STEP = EXCESS_SPEED_STEP / 4.0

        TOTAL_LAPS = 4          # завершённых проходов до конца (счётчик 1 -> 5)
        MISS_COOLDOWN = 0.4     # сколько курсор не виден/не кликабелен после промаха
        TICK = 0.02             # шаг симуляции, сек

        def __init__(self, difficulty, excess_successes):
            self.difficulty = difficulty

            # Зона: чем больше сложность, тем она меньше. Линейная
            # интерполяция между границами 1 и 8, со сжатием в эти рамки,
            # если сложность вдруг окажется вне диапазона.
            d = min(max(difficulty, self.DIFFICULTY_MIN), self.DIFFICULTY_MAX)
            span = float(self.DIFFICULTY_MAX - self.DIFFICULTY_MIN)
            t = (d - self.DIFFICULTY_MIN) / span if span else 0.0
            self.zone_width = self.ZONE_AT_MIN_DIFFICULTY - t * (self.ZONE_AT_MIN_DIFFICULTY - self.ZONE_AT_MAX_DIFFICULTY)

            # Успехи сверх сложности — 0, если ровно совпало со сложностью
            # (это и есть базовая скорость), не бывает отрицательным.
            self.excess = max(excess_successes, 0)

            self.travel_range = self.BAR_WIDTH - self.CURSOR_WIDTH

            self.laps = 0            # засчитанных полных проходов (точка = laps+1)
            self.running = False
            self.finished = False
            self.success = False

            self.pos = 0.0           # левый край курсора, 0..travel_range
            self.direction = 1       # 1 = едет вправо, -1 = едет влево
            self.miss_until = 0.0

        def _speed_px_per_sec(self):
            base_speed = (2.0 * self.travel_range) / self.BASE_ROUND_TRIP
            mult = (1.0 + self.laps * self.LAP_SPEED_STEP) / (1.0 + self.excess * self.EXCESS_SPEED_STEP)
            return base_speed * mult

        def start(self):
            self.running = True

        def tick(self, dt):
            # Вызывается таймером каждые TICK секунд, пока идёт игра —
            # ровно тут двигается курсор и ровно тут, в момент разворота
            # у левого края, засчитывается пройденный круг и точка.
            if not self.running:
                return
            self.pos += self.direction * self._speed_px_per_sec() * dt

            if self.pos >= self.travel_range:
                self.pos = self.travel_range - (self.pos - self.travel_range)
                self.direction = -1
            elif self.pos <= 0:
                self.pos = -self.pos
                self.direction = 1
                # Полный проход (влево-вправо-влево) завершился именно
                # тут — разворот у левого края.
                self.laps += 1
                if self.laps >= self.TOTAL_LAPS:
                    self.running = False
                    self.finished = True
                    self.success = False  # доиграла до конца сама, не по клику игрока

        def cursor_hidden(self, now):
            return now < self.miss_until

        def cursor_center(self):
            return self.pos + self.CURSOR_WIDTH / 2.0

        def attempt_stop(self):
            now = renpy.time.time()
            if not self.running or self.cursor_hidden(now):
                return
            bar_center = self.BAR_WIDTH / 2.0
            if abs(self.cursor_center() - bar_center) <= self.zone_width / 2.0:
                self.running = False
                self.finished = True
                self.success = True
            else:
                self.miss_until = now + self.MISS_COOLDOWN


default feeding_minigame_intro_dismissed = False


screen feeding_minigame(difficulty, excess_successes):

    default state = FeedingMinigameState(difficulty, excess_successes)
    ## Зафиксировано один раз на весь текущий показ экрана — если игрок
    ## поставит галочку прямо сейчас, инструкция всё равно достоит здесь
    ## до конца, спрячется только при следующем вызове мини-игры.
    default show_intro = not feeding_minigame_intro_dismissed

    frame:
        xsize CHAT_PANEL_WIDTH
        ysize config.screen_height
        xanchor 1.0
        xpos config.screen_width - 50
        background None

        vbox:
            xfill True
            yfill True

            frame:
                ysize int(config.screen_height * 0.75)
                xfill True
                background None

                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 4

                    if show_intro:
                        text "ПИТАНИЕ":
                            font FONT_HEADING
                            size 20
                            color "#ffffff"
                            xalign 0.5

                        text "По шкале вправо и влево движется курсор. Его скорость зависит от количества успехов в проверке питания.\n\nВыделенная область — момент когда можно остановиться. Её размер зависит от сложности проверки питания.\n\nНажми в нужный момент чтобы прекратить питание. При промахе курсор исчезает и пока будет не виден — клик недоступен.\n\nТы начинаешь с {font=DejaVuSans.ttf}●{/font}. Каждый полный проход влево-вправо добавляет {font=DejaVuSans.ttf}●{/font} и немного ускоряет курсор. На {font=DejaVuSans.ttf}●●●●●{/font} мини-игра завершится — жертва умирает, а Дамьен получает {font=DejaVuSans.ttf}●{/font} на Человечности и ему нужно будет избавиться от тела, пропуская важные события.\n\nСколько {font=DejaVuSans.ttf}●{/font} ты выпьешь, столько голода утолишь, но не меньше {font=DejaVuSans.ttf}●○○○○{/font}. Утолить голод целиком можно только выпив {font=DejaVuSans.ttf}●●●●●{/font}.":
                            font FONT_BODY
                            size 16
                            color "#a9a9a9"
                            xsize CHAT_PANEL_WIDTH - 60
                            xalign 0.5

                        textbutton ("{font=DejaVuSans.ttf}☑{/font} Понятно" if feeding_minigame_intro_dismissed else "{font=DejaVuSans.ttf}☐{/font} Понятно"):
                            xalign 0.5
                            text_font FONT_BODY
                            text_size 16
                            text_color "#a9a9a9"
                            text_hover_color "#ffffff"
                            background None
                            action ToggleVariable("feeding_minigame_intro_dismissed")

                        null height 30

                    fixed:
                        xsize FeedingMinigameState.BAR_WIDTH
                        ysize FeedingMinigameState.BAR_HEIGHT
                        xalign 0.5

                        add Solid("#ae533480", xsize=state.BAR_WIDTH, ysize=state.BAR_HEIGHT)
                        add Solid("#ae5334bf", xsize=int(state.zone_width), ysize=state.BAR_HEIGHT) xalign 0.5

                        if state.running and not state.cursor_hidden(renpy.time.time()):
                            # Белый, не #ae5334 как в исходном ТЗ — на том же
                            # оттенке, только с разной прозрачностью, тонкая
                            # 4px полоска была почти не видна на глаз.
                            add Solid("#ffffff", xsize=state.CURSOR_WIDTH, ysize=state.BAR_HEIGHT) xpos int(state.pos) ypos 0

                    ## Счётчик — начинается с одной закрашенной точки.
                    text ("●" * (state.laps + 1)) + ("○" * (FeedingMinigameState.TOTAL_LAPS - state.laps)):
                        font "DejaVuSans.ttf"
                        size 20
                        color "#ae5334"
                        xalign 0.5

            frame:
                ysize int(config.screen_height * 0.25)
                xfill True
                background None

                fixed:
                    xfill True
                    yfill True

                    add Solid("#ae5334") xsize CHAT_PANEL_WIDTH ysize 1 ypos 0

                    if not state.running and not state.finished:
                        ## Ещё не начали.
                        key "K_SPACE" action [Play("ui", "audio/ui/next.ogg"), Function(state.start)]

                        button:
                            xsize CHAT_PANEL_WIDTH
                            yminimum 50
                            ypos 26
                            background None
                            hover_background "#ae533440"
                            action [Play("ui", "audio/ui/next.ogg"), Function(state.start)]

                            text "Начать":
                                font FONT_BODY
                                color "#ae5334"
                                size 20
                                xoffset 50
                                yalign 0.5

                    elif state.running:
                        ## Игра идёт — пробел/кнопка пытаются остановить курсор.
                        key "K_SPACE" action Function(state.attempt_stop)

                        button:
                            xsize CHAT_PANEL_WIDTH
                            yminimum 50
                            ypos 26
                            background None
                            hover_background "#ae533440"
                            action Function(state.attempt_stop)

                            text "Остановиться":
                                font FONT_BODY
                                color "#ae5334"
                                size 20
                                xoffset 50
                                yalign 0.5

                    else:
                        ## Закончили (успешно остановили или дошли до 5 точек) — на выход.
                        $ continue_sound = "audio/ui/success.ogg" if state.success else "audio/ui/fail.ogg"

                        key "K_SPACE" action [Play("ui", continue_sound), Return(True)]

                        button:
                            xsize CHAT_PANEL_WIDTH
                            yminimum 50
                            ypos 26
                            background None
                            hover_background "#ae533440"
                            action [Play("ui", continue_sound), Return(True)]

                            text "Дальше":
                                font FONT_BODY
                                color "#ae5334"
                                size 20
                                xoffset 50
                                yalign 0.5

    ## Пока идёт игра (или в кулдауне после промаха) — двигаем симуляцию
    ## и одновременно перерисовываем экран (счётчик, кнопку, курсор).
    if state.running:
        timer 0.02 repeat True action Function(state.tick, 0.02)


################################################################################
## Тестовый лейбл — посмотреть мини-игру вживую с произвольными цифрами.
################################################################################

label feeding_minigame_demo:

    call screen feeding_minigame(2, 2)

    return
