################################################################################
## Ритм-игра — падающие кружки по 4 дорожкам, бьём по стрелкам в момент
## пересечения линии между зоной чата и зоной ответов. При промахе — гитара
## глохнет, пока не попадёшь снова.
##
## Тайминги — JSON из gp5_to_rhythm.py: [{"time_ms": .., "lane": ..}, ...]
## lane — одна из "left"/"up"/"down"/"right".
##
## Прямое использование (без интро/отсчёта):
##     call screen rhythm_game("verse1.json", "audio/music/back-in-black-band-1.ogg",
##                              "audio/music/back-in-black-guitar-1.ogg")
################################################################################

init python:

    import json as _json

    class RhythmGameState(object):

        LANES = ["left", "up", "down", "right"]
        HIT_WINDOW_MS = 150   # окно попадания, ±мс от точного времени ноты
        FALL_TIME_MS = 1200   # сколько кружок падает сверху до линии
        NOTE_SIZE = 36
        LANE_FLASH_SEC = 0.12   # подсветка стрелки при нажатии клавиши
        NOTE_FLASH_SEC = 0.12   # подсветка ноты при попадании по ней
        FAIL_SOUNDS = [
            "audio/ui/fail-1.ogg",
            "audio/ui/fail-2.ogg",
            "audio/ui/fail-3.ogg",
            "audio/ui/fail-4.ogg",
            "audio/ui/fail-5.ogg",
            "audio/ui/fail-6.ogg",
        ]

        def __init__(self, notes_path, band_track, guitar_track):
            with renpy.file(notes_path) as f:
                self.notes = _json.load(f)
            for n in self.notes:
                n["judged"] = False
                n["hit"] = False
            self.notes.sort(key=lambda n: n["time_ms"])

            self.band_track = band_track
            self.guitar_track = guitar_track
            self.guitar_muted = False
            self.started = False
            self.finished = False
            self.hits = 0
            self.score = 0
            self.success = False

            # Подсветка стрелки при нажатии клавиши — используем
            # реальное время (renpy.time.time()), а не время песни:
            # подсветка должна мигать одинаково что на виртуальном
            # предпоказе, что во время самой игры.
            self.lane_flash_until = dict((lane, 0.0) for lane in self.LANES)

            # Подсветка попавших нот — список ещё не погасших вспышек,
            # каждая {"lane":, "until":}. Сама нота к этому моменту уже
            # judged=True и пропадает из visible_notes(), поэтому вспышка
            # рисуется отдельно, всегда прямо на линии попадания.
            self.note_flashes = []

            # Пока None — song_pos_ms() берёт время из реальной позиции
            # канала "band", как и раньше. Если сюда подставить число —
            # song_pos_ms() будет отдавать ЕГО вместо реальной позиции.
            # Это нужно, чтобы можно было отрисовывать и обсчитывать
            # падающие ноты ДО того, как verse-трек реально начал
            # играть (см. RhythmIntroState ниже) — тогда сюда кладётся
            # "виртуальное" время относительно точно посчитанного
            # момента старта verse, отрицательное, пока этот момент ещё
            # не наступил, и совпадающее с реальным get_pos() сразу
            # после — переход бесшовный.
            self.external_now_ms = None

        def start(self):
            # Если трек уже играет на канале (например, его подхватили
            # заранее — либо через очередь, как в queue_next_verse, либо
            # хардкатом из RhythmIntroState) — НЕ перезапускаем его
            # повторно через play(), это вызвало бы обрыв/рестарт трека.
            # Просто начинаем считать с той позиции, где он уже
            # находится.
            self.started = True
            if renpy.music.get_playing(channel="band") != self.band_track:
                renpy.music.play(self.band_track, channel="band")
            if renpy.music.get_playing(channel="guitar") != self.guitar_track:
                renpy.music.play(self.guitar_track, channel="guitar")

        def song_pos_ms(self):
            if self.external_now_ms is not None:
                return self.external_now_ms
            pos = renpy.music.get_pos(channel="band")
            if pos is None:
                return 0.0
            return pos * 1000.0

        def mute_guitar(self):
            # Звук промаха играет каждый раз, даже если гитара уже
            # молчит — а вот саму громкость трогаем только один раз
            # (повторный set_volume(0.0) ничего не меняет, но незачем).
            renpy.music.play(renpy.random.choice(self.FAIL_SOUNDS), channel="sfx")
            if not self.guitar_muted:
                self.guitar_muted = True
                renpy.music.set_volume(0.0, channel="guitar")

        def unmute_guitar(self):
            if self.guitar_muted:
                self.guitar_muted = False
                renpy.music.set_volume(1.0, channel="guitar")

        def tick(self):
            # Вызывается таймером — считаем пропущенные ноты. Работает,
            # если игра "по-настоящему" началась (self.started), ИЛИ
            # если сейчас идёт предпоказ на виртуальном времени (см.
            # RhythmIntroState) — тогда тоже можно честно судить ноты,
            # чей интервал попадания уже прошёл.
            now_real = renpy.time.time()
            self.note_flashes = [f for f in self.note_flashes if f["until"] > now_real]

            if self.finished:
                return
            if not self.started and self.external_now_ms is None:
                return
            now = self.song_pos_ms()
            any_pending = False
            for n in self.notes:
                if not n["judged"]:
                    any_pending = True
                    if now > n["time_ms"] + self.HIT_WINDOW_MS:
                        n["judged"] = True
                        n["hit"] = False
                        self.mute_guitar()
            if not any_pending and self.started and renpy.music.get_playing(channel="band") is None:
                self.finished = True
                total = len(self.notes)
                self.success = total == 0 or self.score >= total * 0.75

        def attempt_hit(self, lane):
            # Стрелка подсвечивается на любое нажатие клавиши — попал
            # игрок по ноте или нет.
            now_real = renpy.time.time()
            self.lane_flash_until[lane] = now_real + self.LANE_FLASH_SEC

            now = self.song_pos_ms()
            candidates = [
                n for n in self.notes
                if n["lane"] == lane and not n["judged"]
                and abs(n["time_ms"] - now) <= self.HIT_WINDOW_MS
            ]
            if not candidates:
                # Мимо ноты — тоже промах: обрываем гитару, играем
                # тот же случайный fail-звук, что и на пропущенной ноте,
                # и списываем очко со счётчика.
                self.mute_guitar()
                self.score -= 1
                return
            note = min(candidates, key=lambda n: abs(n["time_ms"] - now))
            note["judged"] = True
            note["hit"] = True
            self.hits += 1
            self.score += 1
            self.unmute_guitar()
            self.note_flashes.append({"lane": lane, "until": now_real + self.NOTE_FLASH_SEC})

        def lane_x(self, lane, track_width):
            idx = self.LANES.index(lane)
            return int((idx + 0.5) * track_width / len(self.LANES))

        def visible_notes(self, hit_line_y):
            # (lane, y) для ещё не сыгранных нот, которые сейчас видны на экране.
            now = self.song_pos_ms()
            result = []
            for n in self.notes:
                if n["judged"]:
                    continue
                dt = n["time_ms"] - now
                if -self.HIT_WINDOW_MS <= dt <= self.FALL_TIME_MS:
                    frac = 1.0 - (dt / float(self.FALL_TIME_MS))
                    y = int(frac * hit_line_y)
                    result.append((n["lane"], y))
            return result

        def visible_flashes(self, hit_line_y):
            # Вспышки попавших нот — всегда рисуются прямо на линии
            # попадания (сама нота к этому моменту уже пропала из
            # visible_notes(), см. note_flashes выше).
            return [(f["lane"], hit_line_y) for f in self.note_flashes]


## Переиспользуемый визуал: дорожки + падающие ноты + стрелки внизу.
## Используется и обычной игрой (rhythm_game), и предпоказом во время
## последнего такта интро (rhythm_intro) — на одном и том же объекте
## RhythmGameState, без пересоздания.
screen rhythm_track_view(state):

    frame:
        ysize int(config.screen_height * 0.75)
        xfill True
        background None

        fixed:
            xfill True
            yfill True

            ## Дорожки-направляющие (тонкие линии), просто для ориентира.
            for lane in RhythmGameState.LANES:
                add Solid("#ffffff20", xsize=2, ysize=int(config.screen_height * 0.75)):
                    xpos (state.lane_x(lane, CHAT_PANEL_WIDTH) - 1)

            ## Сами падающие кружки.
            for lane, y in state.visible_notes(int(config.screen_height * 0.75)):
                add Solid("#e5322e", xsize=RhythmGameState.NOTE_SIZE, ysize=RhythmGameState.NOTE_SIZE):
                    xpos (state.lane_x(lane, CHAT_PANEL_WIDTH) - RhythmGameState.NOTE_SIZE // 2)
                    ypos (y - RhythmGameState.NOTE_SIZE // 2)

            ## Белая вспышка на месте только что пойманной ноты.
            for lane, y in state.visible_flashes(int(config.screen_height * 0.75)):
                add Solid("#ffffff", xsize=RhythmGameState.NOTE_SIZE, ysize=RhythmGameState.NOTE_SIZE):
                    xpos (state.lane_x(lane, CHAT_PANEL_WIDTH) - RhythmGameState.NOTE_SIZE // 2)
                    ypos (y - RhythmGameState.NOTE_SIZE // 2)

    frame:
        ysize int(config.screen_height * 0.25)
        xfill True
        background None

        fixed:
            xfill True
            yfill True

            add Solid("#ae5334") xsize CHAT_PANEL_WIDTH ysize 1 ypos 0

            for lane, arrow in [("left", u"\u2190"), ("up", u"\u2191"), ("down", u"\u2193"), ("right", u"\u2192")]:
                $ _arrow_color = "#ffffff" if renpy.time.time() < state.lane_flash_until.get(lane, 0.0) else "#ae5334"
                text arrow:
                    font "DejaVuSans.ttf"
                    size 28
                    color _arrow_color
                    xpos (state.lane_x(lane, CHAT_PANEL_WIDTH))
                    xanchor 0.5
                    ypos 20

            ## Счётчик успешных/провальных нажатий — под стрелками.
            text ("%+d" % state.score if state.score != 0 else "0"):
                font FONT_BODY
                size 25
                color "#ffffff"
                text_align 0.0
                xpos 50
                ypos 90


## state=None — обычный самостоятельный запуск (создаёт свой RhythmGameState).
## state=<готовый RhythmGameState> — продолжение уже "прогретого" предпоказом
## объекта из rhythm_intro (см. ниже), без пересоздания и без потери прогресса
## по нотам.
screen rhythm_game(notes_path, band_track, guitar_track, state=None):

    default _state = state if state is not None else RhythmGameState(notes_path, band_track, guitar_track)

    on "show" action Function(_state.start)

    timer 0.02 repeat True action Function(_state.tick)

    key "K_LEFT" action Function(_state.attempt_hit, "left")
    key "K_UP" action Function(_state.attempt_hit, "up")
    key "K_DOWN" action Function(_state.attempt_hit, "down")
    key "K_RIGHT" action Function(_state.attempt_hit, "right")

    frame:
        xsize CHAT_PANEL_WIDTH
        ysize config.screen_height
        xanchor 1.0
        xpos config.screen_width - 50
        background None

        vbox:
            xfill True
            yfill True

            use rhythm_track_view(_state)

    if _state.finished:
        timer 0.001 action Return({
            "hits": _state.hits,
            "total": len(_state.notes),
            "score": _state.score,
            "success": _state.success,
        })


################################################################################
## Склейка с лупом — без швов между verse/loop/verse/loop.
##
## Идея: "loop=True" в play()/queue() — это не "зациклить прямо сейчас",
## а "когда очередь опустеет — сама себя туда добавь". Поэтому чтобы
## перейти С ЛУПА на следующий verse БЕЗ обрыва текущего повтора, нужно
## не звать play() (это обрывает немедленно), а queue() с clear_queue=False —
## трек просто встаёт в конец очереди и заиграет сам, когда текущий
## повтор лупа доиграет до конца.
##
## Использование в script.rpy:
##
##     call screen rhythm_intro(94, ".../band-2.ogg", ".../guitar-2.ogg", "verse2.json")
##     $ pregame_state = _return
##
##     call screen rhythm_game("verse2.json", ".../band-2.ogg", ".../guitar-2.ogg", state=pregame_state)
##
## wait_for_track блокирует сценарий (без анимаций/показа экрана — просто
## тихо ждёт), пока текущий повтор лупа не доиграет и на канале не
## реально начнёт играть уже нужный verse-трек — только тогда сценарий
## идёт дальше, и call screen rhythm_game() подхватывает его без рестарта
## (см. "умный" RhythmGameState.start() выше).
################################################################################

init python:

    def start_loop(band_loop, guitar_loop):
        # Если verse закончился на промахе, гитара могла остаться
        # замьюченной (volume 0 на канале) — это чисто игровая штрафная
        # механика, к лупу/диалогу отношения не имеет, так что сбрасываем
        # громкость перед стартом лупа, иначе он может звучать наполовину
        # беззвучно и выглядеть как "луп не запустился".
        renpy.music.set_volume(1.0, channel="guitar")
        renpy.music.play(band_loop, channel="band", loop=True)
        renpy.music.play(guitar_loop, channel="guitar", loop=True)

    def queue_next_verse(band_verse, guitar_verse):
        renpy.music.queue(band_verse, channel="band", loop=False, clear_queue=False)
        renpy.music.queue(guitar_verse, channel="guitar", loop=False, clear_queue=False)


################################################################################
## Интро с отсчётом ПЕРЕД первым verse — по нажатию кнопки "Начать
## ритм-игру" луп не обрывается сразу: сперва доигрывает текущий
## (возможно неполный) КРУГ ЛУПА (bars_per_loop тактов — обычно 4), затем
## играет ещё один ПОЛНЫЙ круг — во время него на экране идёт отсчёт по
## тактам, а на ПОСЛЕДНЕМ такте этого круга отсчёт сменяется живым
## интерфейсом минигры с уже падающими нотами (чтобы игрок успел
## сориентироваться до реального начала verse). Момент старта verse
## посчитан точно по темпу лупа, поэтому переход хардкатом бесшовный —
## как музыкально, так и по внутреннему времени падения нот.
##
## Раскладка отсчёта при bars_per_loop=4:
##   такт 1 — "3"
##   такт 2 — "2"
##   такт 3 — "1"
##   такт 4 — интерфейс минигры (вместо цифры)
##
## Использование в script.rpy:
##
##     $ start_loop(".../band-loop-1.ogg", ".../guitar-loop-1.ogg")
##     $ next_button_label = "Начать ритм-игру"
##     "Мы начинаем с AC/DC — Back in Black."
##     $ next_button_label = "Дальше"
##
##     call screen rhythm_intro(94, ".../band-1.ogg", ".../guitar-1.ogg", "verse1.json")
##     $ pregame_state = _return
##
##     call screen rhythm_game("verse1.json", ".../band-1.ogg", ".../guitar-1.ogg", state=pregame_state)
##
## ВАЖНО: rhythm_game здесь вызывается с state=pregame_state — это тот же
## самый RhythmGameState, что уже "прогрелся" во время предпоказа
## (никакого пересоздания и потери судейства по нотам).
##
## bpm/beats_per_bar — темп и размер такта лупа (4/4 — beats_per_bar=4).
## bars_per_loop — сколько тактов в одном круге лупа (по умолчанию 4).
################################################################################

init python:

    class RhythmIntroState(object):

        def __init__(self, bpm, band_verse, guitar_verse, notes_path, beats_per_bar=4, bars_per_loop=4, on_countdown_end=None):
            self.bpm = bpm
            self.beats_per_bar = beats_per_bar
            self.bars_per_loop = bars_per_loop
            self.beat_length = 60.0 / bpm
            self.bar_length = self.beat_length * beats_per_bar
            self.loop_length = self.bar_length * bars_per_loop

            # Вызывается РОВНО ОДИН РАЗ — в момент, когда отсчёт
            # заканчивается и вместо цифры впервые показывается
            # интерфейс минигры (последний такт последнего лупа). Нужен,
            # чтобы можно было переключить фон именно на этом моменте,
            # а не раньше (см. использование в script.rpy).
            self.on_countdown_end = on_countdown_end
            self._countdown_end_fired = False

            # Последний такт последнего лупа — вместо цифры в нём уже
            # показываем интерфейс минигры с падающими нотами.
            self.preview_bar_index = bars_per_loop - 1

            self.band_verse = band_verse
            self.guitar_verse = guitar_verse

            # Общий на весь показ игровой стейт — создаём его СРАЗУ, ещё
            # до того, как реально заиграет verse-трек, чтобы падающие
            # ноты можно было отрисовывать уже во время последнего такта
            # лупа. Когда наступит хардкат — просто продолжаем с этим же
            # объектом, никакого пересоздания (см. tick() ниже и
            # использование state.game при вызове screen rhythm_game).
            self.game = RhythmGameState(notes_path, band_verse, guitar_verse)

            # renpy.music.get_pos() сбрасывается к 0 при каждом
            # перезапуске зацикленного трека — она НЕ копится через
            # повторы. Поэтому ловим сам момент сброса (позиция
            # скакнула вниз), а не абсолютную "накопленную" точку.
            self.last_pos = renpy.music.get_pos(channel="band") or 0.0
            self.loops_seen = 0
            self.done = False

        def current_bar_index(self):
            bar_index = int(self.last_pos / self.bar_length)
            return min(bar_index, self.bars_per_loop - 1)

        def show_minigame(self):
            if self.loops_seen >= 2:
                return True
            return self.loops_seen == 1 and self.current_bar_index() >= self.preview_bar_index

        def current_number(self):
            # "3"-"2"-"1" на первых тактах последнего лупа. На самом
            # последнем такте (preview_bar_index) вместо цифры уже
            # интерфейс минигры — тут возвращаем None.
            if self.loops_seen != 1:
                return None
            bar_index = self.current_bar_index()
            if bar_index >= self.preview_bar_index:
                return None
            return self.preview_bar_index - bar_index

        def virtual_song_pos_ms(self):
            # "Виртуальное" время относительно точно посчитанного
            # момента старта verse-трека — отрицательное, пока сам
            # хардкат ещё не наступил, и ровно 0 в момент, когда он
            # наступает (та же нулевая точка, что и у настоящего
            # RhythmGameState.song_pos_ms() сразу после старта —
            # переход бесшовный).
            return (self.last_pos - self.loop_length) * 1000.0

        def tick(self):
            if self.done:
                return

            pos = renpy.music.get_pos(channel="band")
            if pos is None:
                return

            if pos + 0.001 < self.last_pos:
                self.loops_seen += 1

            self.last_pos = pos

            if self.loops_seen >= 2:
                # Хардкат — ровно посчитанный по темпу лупа момент.
                self.done = True
                # Громкость гитары на всякий случай возвращаем к норме —
                # если во время предпоказа последнего такта (см. ниже)
                # игрок промазал мимо ноты, канал "guitar" мог быть
                # приглушён ЕЩЁ ДО того, как реально заиграл verse; та
                # же защита, что и в start_loop().
                renpy.music.set_volume(1.0, channel="guitar")
                self.game.guitar_muted = False
                self.game.external_now_ms = None
                self.game.started = True
                renpy.music.play(self.band_verse, channel="band")
                renpy.music.play(self.guitar_verse, channel="guitar")
                return

            if self.loops_seen == 1 and self.current_bar_index() >= self.preview_bar_index:
                # Последний такт последнего лупа — уже двигаем и судим
                # ноты минигры на виртуальном времени, хоть verse ещё
                # не стартовал по-настоящему.
                if not self._countdown_end_fired:
                    self._countdown_end_fired = True
                    if self.on_countdown_end is not None:
                        self.on_countdown_end()
                self.game.external_now_ms = self.virtual_song_pos_ms()
                self.game.tick()


screen rhythm_intro(bpm, band_verse, guitar_verse, notes_path, beats_per_bar=4, bars_per_loop=4, on_countdown_end=None):

    default state = RhythmIntroState(bpm, band_verse, guitar_verse, notes_path, beats_per_bar, bars_per_loop, on_countdown_end)

    timer 0.02 repeat True action Function(state.tick)

    ## Как только начался предпоказ (последний такт), можно уже бить по
    ## нотам — attempt_hit сам разберётся, есть ли поблизости нота,
    ## опираясь на то же виртуальное время, что и отрисовка.
    key "K_LEFT" action Function(state.game.attempt_hit, "left")
    key "K_UP" action Function(state.game.attempt_hit, "up")
    key "K_DOWN" action Function(state.game.attempt_hit, "down")
    key "K_RIGHT" action Function(state.game.attempt_hit, "right")

    frame:
        xsize CHAT_PANEL_WIDTH
        ysize config.screen_height
        xanchor 1.0
        xpos config.screen_width - 50
        background None

        vbox:
            xfill True
            yfill True

            if state.show_minigame():
                use rhythm_track_view(state.game)
            else:
                frame:
                    ysize int(config.screen_height * 0.75)
                    xfill True
                    background None

                    $ number = state.current_number()
                    if number:
                        text str(number):
                            font FONT_HEADING
                            size 72
                            color "#ffffff"
                            xalign 0.5
                            yalign 0.5
                    else:
                        text "Приготовиться":
                            font FONT_NARRATION
                            size 20
                            color "#a9a9a9"
                            xalign 0.5
                            yalign 0.5

                frame:
                    ysize int(config.screen_height * 0.25)
                    xfill True
                    background None

    ## Отдаём наружу уже "прогретый" RhythmGameState — его и нужно
    ## передать следующим в screen rhythm_game(..., state=...), а не
    ## создавать заново.
    if state.done:
        timer 0.001 action Return(state.game)


################################################################################
## Тестовый лейбл интро: реплика с лупом на фоне, отсчёт по такту с
## предпоказом нот на последнем такте, сам verse без пересоздания стейта,
## а затем — ветка по результату (успех/провал первого куплета). В ОБОИХ
## случаях дальше играет луп и на последней реплике ветки появляется
## кнопка "Сыграть соло", уводящая на сольную ритм-игру (verse2.json,
## back-in-black-band-2.ogg/guitar-2.ogg) по той же схеме (интро+отсчёт).
## После соло — один раз (без луп) финальный трек *-end.ogg и ветка по
## результату соло.
################################################################################

label rhythm_intro_demo:

    $ start_loop("audio/music/back-in-black-band-loop-1.ogg", "audio/music/back-in-black-guitar-loop-1.ogg")

    "Мы начинаем с AC/DC — Back in Black."
    "В баре сразу оживляются. Люди за стойкой оборачиваются на нас, очередь у туалета даёт немного шума…"

    $ next_button_label = "Начать ритм-игру"
    "Я пропеваю первые строчки и все начинают качать головами."
    $ next_button_label = "Дальше"

    call screen rhythm_intro(94, "audio/music/back-in-black-band-1.ogg", "audio/music/back-in-black-guitar-1.ogg", "verse1.json")
    $ pregame_state = _return

    call screen rhythm_game(
        "verse1.json",
        "audio/music/back-in-black-band-1.ogg",
        "audio/music/back-in-black-guitar-1.ogg",
        state=pregame_state,
    )
    $ verse1_result = _return

    if verse1_result["success"]:

        $ start_loop("audio/music/back-in-black-band-loop-1.ogg", "audio/music/back-in-black-guitar-loop-1.ogg")

        "В самом конце куплета публика замирает и последние строчки припева мы уже поём вместе."
        "Второй куплет бар уже ритмично притопывает и прихлопывает в такт песне."
        think "Всё, они на крючке. Работает безотказно."
        "Кто-то закидывает купюру в банку."

        $ next_button_label = "Сыграть соло"
        "Я дотягиваю до финального соло и наконец отлипаю от микрофона."
        $ next_button_label = "Дальше"

    else:

        $ start_loop("audio/music/back-in-black-band-loop-1.ogg", "audio/music/back-in-black-guitar-loop-1.ogg")

        think "Соберись, Damn. Ты же отлично знаешь этот трек!"
        "Судя по тому, что мужики за барной стойкой не отлипают от телека, никто особо не заметил как я налажал."

        $ next_button_label = "Сыграть соло"
        "Ладно, впереди соло, я ещё смогу отыграться и зацепить их."
        $ next_button_label = "Дальше"

    ## Общий код для соло — сюда ведут ОБЕ ветки (и успех, и провал
    ## первого куплета), луп на момент этого места уже играет в любом
    ## случае (см. start_loop() выше в обеих ветках).
    call screen rhythm_intro(94, "audio/music/back-in-black-band-2.ogg", "audio/music/back-in-black-guitar-2.ogg", "verse2.json")
    $ pregame_state = _return

    call screen rhythm_game(
        "verse2.json",
        "audio/music/back-in-black-band-2.ogg",
        "audio/music/back-in-black-guitar-2.ogg",
        state=pregame_state,
    )
    $ solo_result = _return

    ## Финальный трек — один раз, без луп (play() без loop=True), на тех
    ## же каналах, что и всё остальное.
    $ renpy.music.play("audio/music/back-in-black-band-end.ogg", channel="band")
    $ renpy.music.play("audio/music/back-in-black-guitar-end.ogg", channel="guitar")

    if solo_result["success"]:

        "Я бросаю взгляд на банку и там больше чем было в прошлый раз."
        "Бар хлопает в такт."
        "Я заканчиваю соло и даю ещё пару тактов риффа, чтобы мы смогли закончить одновременно."
        "Митч с Клиффом хорошо знают этот приём и всё проходит гладко, под оглушительный крэш в конце."

    else:

        think "Да ну, блять... Что за херня?!"
        "Я начинаю терять самообладание и понемногу выходить из себя."
        "Тем не менее, даю ещё пару тактов риффа, чтобы мы смогли закончить одновременно."
        "Митч с Клиффом хорошо знают этот приём и хоть здесь всё проходит гладко, под оглушительный крэш в конце."

    return


label wait_for_track(channel, track):
    while renpy.music.get_playing(channel) != track:
        $ renpy.pause(0.05)
    return


label wait_for_channel_silence(channel):
    # В отличие от wait_for_track (ждёт, пока НАЧНЁТ играть конкретный
    # трек), этот ждёт, пока канал полностью ЗАМОЛЧИТ — то есть трек
    # (без loop=True) доиграл до конца сам. Используется, чтобы не
    # показывать следующую реплику раньше, чем закончится музыка.
    while renpy.music.get_playing(channel) is not None:
        $ renpy.pause(0.05)
    return


################################################################################
## Тестовый лейбл — прогнать через консоль (Shift+O): jump rhythm_game_demo
## Файлы аудио пока не существуют в проекте (только .gp5 был прислан) —
## поставь свои .ogg по этим путям или поправь имена, прежде чем тестить.
################################################################################

label rhythm_game_demo:

    call screen rhythm_game(
        "verse1.json",
        "audio/music/back-in-black-band-1.ogg",
        "audio/music/back-in-black-guitar-1.ogg",
    )

    return


################################################################################
## Тестовый лейбл ПОЛНОЙ последовательности verse -> loop -> verse -> loop.
## Verse2 тут — тот же самый verse1.json/файлы, просто для проверки склейки
## (реального второго verse-файла и JSON под него пока нет).
################################################################################

label rhythm_sequence_demo:

    call screen rhythm_game(
        "verse1.json",
        "audio/music/back-in-black-band-1.ogg",
        "audio/music/back-in-black-guitar-1.ogg",
    )
    $ verse1_result = _return

    $ start_loop("audio/music/back-in-black-band-loop-1.ogg", "audio/music/back-in-black-guitar-loop-1.ogg")

    "В баре сразу оживляются. Люди за стойкой оборачиваются на нас, очередь у туалета даёт немного шума…"
    "Я пропеваю первые строчки и все начинают качать головами."
    "В самом конце куплета публика замирает и последние строчки припева мы уже поём вместе."
    "Второй куплет бар уже ритмично притопывает и прихлопывает в такт песне."
    think "Всё, они на крючке. Работает безотказно."
    "Я дотягиваю до финального соло и наконец отлипаю от микрофона."

    $ queue_next_verse("audio/music/back-in-black-band-1.ogg", "audio/music/back-in-black-guitar-1.ogg")
    call wait_for_track("band", "audio/music/back-in-black-band-1.ogg")

    call screen rhythm_game(
        "verse1.json",
        "audio/music/back-in-black-band-1.ogg",
        "audio/music/back-in-black-guitar-1.ogg",
    )
    $ verse2_result = _return

    $ start_loop("audio/music/back-in-black-band-loop-1.ogg", "audio/music/back-in-black-guitar-loop-1.ogg")

    "Финальный текст, пока играет второй луп..."

    $ renpy.music.stop(channel="band", fadeout=1.0)
    $ renpy.music.stop(channel="guitar", fadeout=1.0)

    return
