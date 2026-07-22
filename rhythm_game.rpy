################################################################################
## Ритм-игра (первый рабочий прототип) — падающие кружки по 4 дорожкам,
## бьём по стрелкам в момент пересечения линии между зоной чата и зоной
## ответов. При промахе — гитара глохнет, пока не попадёшь снова.
##
## Пока БЕЗ склейки с лупом/диалогами — это следующий шаг. Сейчас просто
## сама механика на реальных таймингах, чтобы посмотреть, как ощущается.
##
## Тайминги — JSON из gp5_to_rhythm.py: [{"time_ms": .., "lane": ..}, ...]
## lane — одна из "left"/"up"/"down"/"right".
##
## Использование:
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

        def start(self):
            # Если трек уже играет на канале (например, его подхватили из
            # очереди сразу после лупа — см. queue_next_verse/wait_for_track
            # в script.rpy) — НЕ перезапускаем его повторно через play(),
            # это вызвало бы обрыв/рестарт трека. Просто начинаем считать
            # с той позиции, где он уже находится.
            self.started = True
            if renpy.music.get_playing(channel="band") != self.band_track:
                renpy.music.play(self.band_track, channel="band")
            if renpy.music.get_playing(channel="guitar") != self.guitar_track:
                renpy.music.play(self.guitar_track, channel="guitar")

        def song_pos_ms(self):
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
            if not self.started or self.finished:
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
            if not any_pending and renpy.music.get_playing(channel="band") is None:
                self.finished = True

        def attempt_hit(self, lane):
            now = self.song_pos_ms()
            candidates = [
                n for n in self.notes
                if n["lane"] == lane and not n["judged"]
                and abs(n["time_ms"] - now) <= self.HIT_WINDOW_MS
            ]
            if not candidates:
                # Мимо ноты — тоже промах: обрываем гитару и играем
                # тот же случайный fail-звук, что и на пропущенной ноте.
                self.mute_guitar()
                return
            note = min(candidates, key=lambda n: abs(n["time_ms"] - now))
            note["judged"] = True
            note["hit"] = True
            self.hits += 1
            self.unmute_guitar()

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


screen rhythm_game(notes_path, band_track, guitar_track):

    default state = RhythmGameState(notes_path, band_track, guitar_track)

    on "show" action Function(state.start)

    timer 0.02 repeat True action Function(state.tick)

    key "K_LEFT" action Function(state.attempt_hit, "left")
    key "K_UP" action Function(state.attempt_hit, "up")
    key "K_DOWN" action Function(state.attempt_hit, "down")
    key "K_RIGHT" action Function(state.attempt_hit, "right")

    frame:
        xsize CHAT_PANEL_WIDTH
        ysize config.screen_height
        xanchor 1.0
        xpos config.screen_width - 50
        background None

        vbox:
            xfill True
            yfill True

            ## Верхняя зона — трек падения нот, той же высоты, что и лента чата.
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

            ## Нижняя зона — та самая линия-граница чата вверху этого блока,
            ## а под ней подписи дорожек (стрелки), просто для ориентира.
            frame:
                ysize int(config.screen_height * 0.25)
                xfill True
                background None

                fixed:
                    xfill True
                    yfill True

                    add Solid("#ae5334") xsize CHAT_PANEL_WIDTH ysize 1 ypos 0

                    for lane, arrow in [("left", u"\u2190"), ("up", u"\u2191"), ("down", u"\u2193"), ("right", u"\u2192")]:
                        text arrow:
                            font "DejaVuSans.ttf"
                            size 28
                            color "#ae5334"
                            xpos (state.lane_x(lane, CHAT_PANEL_WIDTH))
                            xanchor 0.5
                            ypos 20

    if state.finished:
        timer 0.001 action Return({"hits": state.hits, "total": len(state.notes)})


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
##     call screen rhythm_game("verse1.json", ".../band-1.ogg", ".../guitar-1.ogg")
##     $ verse1_result = _return
##
##     $ start_loop(".../band-loop-1.ogg", ".../guitar-loop-1.ogg")
##     "Текст, который читаем, пока играет луп..."
##
##     $ queue_next_verse(".../band-2.ogg", ".../guitar-2.ogg")
##     call wait_for_track("band", ".../band-2.ogg")
##
##     call screen rhythm_game("verse2.json", ".../band-2.ogg", ".../guitar-2.ogg")
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
## Отсчёт перед стартом ритм-игры — по нажатию кнопки "Начать ритм-игру"
## (см. next_button_label в chat_ui.rpy) луп не обрывается сразу: сперва
## доигрывает текущий (возможно неполный) КРУГ ЛУПА (bars_per_loop тактов —
## обычно 4), затем играет ещё один ПОЛНЫЙ круг, и только во время этого
## второго круга на экране появляются цифры 4-3-2-1 (по одной на КАЖДЫЙ
## ТАКТ внутри этого круга, а не на каждую долю). Как только отсчёт
## доходит до конца — verse-треки стартуют жёстко (hard cut), это
## музыкально бесшовно, потому что момент высчитан точно по темпу лупа,
## а не подловлен на глаз.
##
## Использование в script.rpy:
##
##     $ start_loop(".../band-loop-1.ogg", ".../guitar-loop-1.ogg")
##     $ next_button_label = "Начать ритм-игру"
##     "Мы начинаем с AC/DC — Back in Black."
##     $ next_button_label = "Дальше"
##
##     call screen rhythm_countdown(94, ".../band-1.ogg", ".../guitar-1.ogg")
##
##     call screen rhythm_game("verse1.json", ".../band-1.ogg", ".../guitar-1.ogg")
##
## bpm/beats_per_bar — темп и размер такта лупа (4/4 — beats_per_bar=4).
## bars_per_loop — сколько тактов в одном круге лупа (по умолчанию 4) —
## это и определяет, сколько цифр будет в отсчёте (по одной на такт).
################################################################################

init python:

    class CountdownState(object):

        def __init__(self, bpm, band_verse, guitar_verse, beats_per_bar=4, bars_per_loop=4):
            self.bpm = bpm
            self.beats_per_bar = beats_per_bar
            self.bars_per_loop = bars_per_loop
            self.beat_length = 60.0 / bpm
            self.bar_length = self.beat_length * beats_per_bar
            self.loop_length = self.bar_length * bars_per_loop

            self.band_verse = band_verse
            self.guitar_verse = guitar_verse

            pos = renpy.music.get_pos(channel="band") or 0.0
            into_loop = pos % self.loop_length
            # Момент (в системе координат позиции канала "band"), когда
            # заканчивается текущий (возможно неполный) круг лупа и
            # начинается тот самый добавочный ПОЛНЫЙ круг с отсчётом.
            self.phase2_start = pos + (self.loop_length - into_loop)
            self.phase2_end = self.phase2_start + self.loop_length

            self.done = False

        def current_number(self):
            # None — до отсчёта ещё рано (доигрывает неполный круг) или
            # уже поздно (доиграли, ждём срабатывания done).
            pos = renpy.music.get_pos(channel="band")
            if pos is None:
                return None
            if pos < self.phase2_start:
                return None
            if pos >= self.phase2_end:
                if not self.done:
                    self.done = True
                    renpy.music.play(self.band_verse, channel="band")
                    renpy.music.play(self.guitar_verse, channel="guitar")
                return None
            bar_index = int((pos - self.phase2_start) / self.bar_length)
            bar_index = min(bar_index, self.bars_per_loop - 1)
            return self.bars_per_loop - bar_index


screen rhythm_countdown(bpm, band_verse, guitar_verse, beats_per_bar=4, bars_per_loop=4):

    default cd = CountdownState(bpm, band_verse, guitar_verse, beats_per_bar, bars_per_loop)

    timer 0.02 repeat True action Function(cd.current_number)

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

                $ number = cd.current_number()
                if number:
                    text str(number):
                        font FONT_HEADING
                        size 72
                        color "#ffffff"
                        xalign 0.5
                        yalign 0.5

            frame:
                ysize int(config.screen_height * 0.25)
                xfill True
                background None

    if cd.done:
        timer 0.001 action Return()


################################################################################
## Тестовый лейбл интро: реплика с лупом на фоне, кнопка "Начать
## ритм-игру" вместо "Дальше", отсчёт по такту, затем сам verse.
################################################################################

label rhythm_intro_demo:

    $ start_loop("audio/music/back-in-black-band-loop-1.ogg", "audio/music/back-in-black-guitar-loop-1.ogg")

    $ next_button_label = "Начать ритм-игру"
    "Мы начинаем с AC/DC — Back in Black."
    $ next_button_label = "Дальше"

    call screen rhythm_countdown(94, "audio/music/back-in-black-band-1.ogg", "audio/music/back-in-black-guitar-1.ogg")

    call screen rhythm_game(
        "verse1.json",
        "audio/music/back-in-black-band-1.ogg",
        "audio/music/back-in-black-guitar-1.ogg",
    )

    return


label wait_for_track(channel, track):
    while renpy.music.get_playing(channel) != track:
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
