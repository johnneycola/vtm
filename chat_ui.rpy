################################################################################
## Лента диалога (кастомный say-экран) + варианты ответа (кастомный choice)
################################################################################

default chat_history = []

# Звук клика по варианту ответа. Обычно "audio/ui/choice.ogg" — но можно
# временно переопределить перед конкретным "menu:" (например, на dice.ogg
# для вариантов с проверкой), сбросив обратно сразу внутри самого варианта.
default current_choice_sound = "audio/ui/choice.ogg"

define FONT_NARRATION = "fonts/TTNormsProSerif-Normal.otf"
define FONT_THOUGHT = "fonts/TTNormsProSerif-NormalItalic.otf"
define FONT_BODY = "fonts/TTNormsProSerif-Normal.otf"
define FONT_HEADING = "fonts/TTNormsProSerif-Normal.otf"
define CHAT_TOP_MARGIN = 125
define CHAT_PANEL_WIDTH = 550
## Небольшой запас, чтобы Text не рендерился впритык к границе своего
## контейнера — иначе на некоторых буквах/шрифтах последний пиксель-два
## обрезается вьюпортом (характерная проблема, когда xsize текста в точности
## равен ширине родителя). Реальная ширина текста = CHAT_PANEL_WIDTH - CHAT_TEXT_MARGIN.
define CHAT_TEXT_MARGIN = 12

## "Мысли" — это не полноценный персонаж (нет имени, нет своей реплики
## в обычном понимании), а технический объект-нарратор: нужен только затем,
## чтобы renpy.exports.say() получал в "who" что-то, отличное от None,
## и мы могли различить действие/описание и мысль персонажа.
define think = Character(None)

init -1 python:
    # Звуки интерфейса — отдельный канал, чтобы не перебивать
    # фон и уникальные звуки сцены.
    renpy.music.register_channel("ui", mixer="sound", loop=False)

init python:

    import os

    def _chat_reset_on_start():
        # На случай, если "Новая игра" в этом проекте не делает полный
        # renpy.full_restart(), а просто прыгает на label start в рамках
        # того же сеанса — chat_history иначе не очистится сама, и в неё
        # будут наслаиваться реплики от каждого нового прохождения.
        chat_history[:] = []

    config.start_callbacks.append(_chat_reset_on_start)

    ## Раньше клик в любое место экрана (и Enter/Space) продолжал диалог —
    ## это стандартное поведение Ren'Py, завязанное на config.keymap
    ## ['dismiss']. Отключаем его полностью: теперь единственный способ
    ## продолжить — клик по кнопке "Дальше" (её action Return(True)
    ## работает независимо от keymap).
    config.keymap["dismiss"] = []

    def _chat_debug(msg):
        # ВРЕМЕННО — для диагностики. Пишет в папку сохранений
        # (гарантированно доступна для записи).
        try:
            path = os.path.join(config.savedir, "chat_debug.log")
            with open(path, "a", encoding="utf-8") as f:
                f.write(str(msg) + "\n")
        except Exception as e:
            renpy.notify("chat_debug write failed: %r" % e)

    def chat_add(speaker, text):
        # speaker может быть: None (нарратив), объектом Character (d/c/...),
        # или строкой-именем (для выбора варианта ответа, см. _chat_on_choice).
        if speaker is None:
            side = "narration"
            name = None
        elif speaker is think:
            side = "thought"
            name = None
        elif speaker is d or speaker == getattr(d, "name", object()):
            side = "damn"
            name = d.name
        else:
            side = "npc"
            name = speaker.name if hasattr(speaker, "name") else speaker

        chat_history.append({
            "speaker": name,
            "text": text,
            "side": side,
        })

    ## КЛЮЧЕВОЙ МОМЕНТ: раньше мы добавляли реплики в chat_history прямо
    ## внутри screen say(who, what) — но код экрана может выполняться не
    ## только при реальном показе игроку, а ещё и во время предиктивного
    ## рендеринга (Ren'Py прогревает экраны заранее, чтобы подгрузить
    ## ресурсы) — из-за этого реплики добавлялись не в том порядке или
    ## пропускались. Правильная точка входа — renpy.exports.say(), через
    ## неё проходит КАЖДАЯ реплика РОВНО ОДИН РАЗ, только по-настоящему.
    _orig_renpy_say = renpy.exports.say

    def _chat_say_hook(who, what, *args, **kwargs):
        chat_add(who, what)
        return _orig_renpy_say(who, what, *args, **kwargs)

    renpy.exports.say = _chat_say_hook

    def _entry_widgets(entry, show_name=True):
        # Виджеты одной записи ленты — используются и для показа,
        # и для измерения высоты в _measure_chat_height().
        # ВАЖНО: xsize/size/italic здесь должны точно совпадать с тем,
        # что используется при реальном отображении в screen chat_log_view.
        widgets = []
        if entry["side"] == "narration":
            widgets.append(Text(entry["text"], font=FONT_NARRATION, size=20, color="#a9a9a9", xsize=CHAT_PANEL_WIDTH - CHAT_TEXT_MARGIN))
        elif entry["side"] == "thought":
            widgets.append(Text(entry["text"], font=FONT_THOUGHT, size=20, color="#a9a9a9", xsize=CHAT_PANEL_WIDTH - CHAT_TEXT_MARGIN))
        elif entry["side"] == "damn":
            if show_name:
                widgets.append(Text(entry["speaker"].upper(), font=FONT_HEADING, size=20, color="#ffffff"))
            widgets.append(Text(entry["text"], font=FONT_BODY, size=20, color="#ffffff", xsize=CHAT_PANEL_WIDTH - CHAT_TEXT_MARGIN))
        elif entry["side"] == "npc":
            if show_name:
                widgets.append(Text(entry["speaker"].upper(), font=FONT_HEADING, size=20, color="#ffffff"))
            widgets.append(Text(entry["text"], font=FONT_BODY, size=20, color="#ffffff", xsize=CHAT_PANEL_WIDTH - 50 - CHAT_TEXT_MARGIN))
        return widgets

    def _chat_show_name(index):
        # Показываем имя, только если это первая реплика этого говорящего
        # подряд — то есть либо это первая запись, либо перед ней стоит
        # нарратив, либо говорил кто-то другой.
        entry = chat_history[index]
        if entry["side"] in ("narration", "thought"):
            return False
        if index == 0:
            return True
        prev = chat_history[index - 1]
        if prev["side"] in ("narration", "thought"):
            return True
        return prev["speaker"] != entry["speaker"]

    def _chat_color(index, base_color):
        # Все прошлые реплики — приглушённый серый, актуальная (последняя
        # в истории) сохраняет свой обычный цвет.
        if index == len(chat_history) - 1:
            return base_color
        return "#5c5c5c"

    def _chat_gap(index):
        # Отступ ПЕРЕД записью с данным индексом: обычный (40), либо
        # уменьшенный вдвое (20), если это продолжение реплики того же
        # говорящего подряд (когда имя не повторяется).
        if index == 0:
            return 40
        return 20 if not _chat_show_name(index) else 40

    def _measure_chat_height():
        # Суммарная "естественная" высота всей ленты — нужна, чтобы понять,
        # сколько пустого места добавить сверху, и прижать короткую ленту
        # к низу зоны, а не к верху.
        total = 0
        for i, entry in enumerate(chat_history):
            for w in _entry_widgets(entry, _chat_show_name(i)):
                r = renpy.render(w, 999, 10000, 0, 0)
                total += r.height
        for i in range(len(chat_history)):
            total += _chat_gap(i)
        # + отступ перед разделительной линией (40 обычный + 25 хвостовой, см. chat_log_view)
        total += 40 + 25
        return total


################################################################################
## Переиспользуемый фрагмент — сама лента (используется и в say, и в choice).
################################################################################

screen chat_log_view():
    fixed:
        xfill True
        ysize int(config.screen_height * 0.75)

        viewport:
            id "chat_viewport"
            mousewheel True
            draggable True
            xfill True
            ysize int(config.screen_height * 0.75) - CHAT_TOP_MARGIN
            ypos CHAT_TOP_MARGIN
            yinitial 1.0

            vbox:
                spacing 0
                xsize CHAT_PANEL_WIDTH

                ## Пустой отступ сверху — прижимает короткую ленту
                ## к низу зоны. Когда лента заполняет всю зону и больше,
                ## отступ становится 0, и включается обычный скролл.
                $ _spacer = max(0, int(config.screen_height * 0.75) - CHAT_TOP_MARGIN - _measure_chat_height())
                null height _spacer

                for i, entry in enumerate(chat_history):
                    null height _chat_gap(i)

                    if entry["side"] == "narration":
                        text entry["text"] font FONT_NARRATION size 20 color _chat_color(i, "#a9a9a9") text_align 0.0 xsize CHAT_PANEL_WIDTH - CHAT_TEXT_MARGIN

                    elif entry["side"] == "thought":
                        text entry["text"] font FONT_THOUGHT size 20 color _chat_color(i, "#a9a9a9") text_align 0.0 xsize CHAT_PANEL_WIDTH - CHAT_TEXT_MARGIN

                    elif entry["side"] == "damn":
                        vbox:
                            if _chat_show_name(i):
                                text entry["speaker"].upper() font FONT_HEADING size 20 color _chat_color(i, "#ffffff") text_align 0.0
                            text entry["text"] font FONT_BODY size 20 color _chat_color(i, "#ffffff") text_align 0.0 xsize CHAT_PANEL_WIDTH - CHAT_TEXT_MARGIN

                    elif entry["side"] == "npc":
                        vbox:
                            xoffset 50
                            if _chat_show_name(i):
                                text entry["speaker"].upper() font FONT_HEADING size 20 color _chat_color(i, "#ffffff") text_align 0.0
                            text entry["text"] font FONT_BODY size 20 color _chat_color(i, "#ffffff") text_align 0.0 xsize CHAT_PANEL_WIDTH - 50 - CHAT_TEXT_MARGIN

                ## Отступ перед разделительной линией: обычный (40) + хвостовой (25).
                null height 40
                null height 25

        ## Кастомный тонкий скроллбар — вынесен за пределы панели чата.
        ## ВАЖНО: xpos/xanchor здесь считаются в ЛОКАЛЬНЫХ координатах
        ## этого фрагмента экрана (он вложен внутрь frame шириной
        ## CHAT_PANEL_WIDTH через vbox в screen say/choice) — а не от
        ## реального разрешения экрана. Поэтому "screen_width - 30" тут
        ## был ошибкой: он трактовался как локальное смещение и уводил
        ## бегунок далеко за пределы видимой области. Правильно — просто
        ## вынести бегунок на 20px правее локальной ширины панели.
        vbar:
            value YScrollValue("chat_viewport")
            xsize 5
            ysize int(config.screen_height * 0.75) - CHAT_TOP_MARGIN
            ypos CHAT_TOP_MARGIN
            xpos CHAT_PANEL_WIDTH + 20
            xanchor 1.0
            bar_resizing False
            top_bar Solid("#00000000")
            bottom_bar Solid("#00000000")
            thumb Solid("#ffffff", xsize=5, ysize=50)
            thumb_offset 0
            unscrollable "hide"


################################################################################
## say — обычные реплики. Нижняя зона: кнопка "Дальше".
################################################################################

screen say(who, what):
    style_prefix "say"

    ## Технически обязательный элемент для внутренней механики Ren'Py
    ## (self-voicing, точный клик по тексту и т.п.). Сам текст уже
    ## показывается в ленте ниже, поэтому этот экземпляр прячем за экран.
    fixed:
        xpos -9999
        text what id "what"

    ## Пробел — альтернативный способ продолжить, наравне с кликом
    ## по кнопке "Дальше" (клик в любое другое место по-прежнему
    ## не работает — см. config.keymap["dismiss"] = []).
    key "K_SPACE" action [Play("ui", "audio/ui/next.ogg"), Return(True)]

    frame:
        xsize CHAT_PANEL_WIDTH
        ysize config.screen_height
        xanchor 1.0
        xpos config.screen_width - 50
        background None

        vbox:
            xfill True
            yfill True

            use chat_log_view

            ## Зарезервированная нижняя зона — ровно 1/4 экрана.
            frame:
                ysize int(config.screen_height * 0.25)
                xfill True
                background None

                fixed:
                    xfill True
                    yfill True

                    add Solid("#ae5334") xsize CHAT_PANEL_WIDTH ysize 1 ypos 0

                    button:
                        xsize CHAT_PANEL_WIDTH
                        yminimum 50
                        ypos 26
                        background None
                        hover_background "#ae533440"
                        action [Play("ui", "audio/ui/next.ogg"), Return(True)]

                        text "Дальше":
                            font FONT_BODY
                            color "#ae5334"
                            size 20
                            xoffset 50
                            yalign 0.5


################################################################################
## choice — варианты ответа. Та же лента сверху, а вместо кнопки "Дальше" —
## список вариантов (со своим скроллом, если не помещаются). При выборе —
## реплика добавляется в ленту от лица Дамьена.
################################################################################

screen choice(items):

    on "show" action Play("ui", "audio/ui/choice_appear.ogg")

    frame:
        xsize CHAT_PANEL_WIDTH
        ysize config.screen_height
        xanchor 1.0
        xpos config.screen_width - 50
        background None

        vbox:
            xfill True
            yfill True

            use chat_log_view

            frame:
                ysize int(config.screen_height * 0.25)
                xfill True
                background None

                fixed:
                    xfill True
                    yfill True

                    add Solid("#ae5334") xsize CHAT_PANEL_WIDTH ysize 1 ypos 0

                    fixed:
                        xfill True
                        ysize int(config.screen_height * 0.25) - 26
                        ypos 26

                        viewport:
                            id "choice_viewport"
                            mousewheel True
                            draggable True
                            xfill True
                            yfill True

                            vbox:
                                xfill True
                                spacing 10

                                for idx, i in enumerate(items):
                                    if idx < 9:
                                        key "K_%d" % (idx + 1) action [Play("ui", current_choice_sound), i.action]

                                    button:
                                        xsize CHAT_PANEL_WIDTH
                                        yminimum 50
                                        background None
                                        hover_background "#ae533440"
                                        action [Play("ui", current_choice_sound), i.action]

                                        text "%d. %s" % (idx + 1, i.caption):
                                            font FONT_BODY
                                            color "#ae5334"
                                            size 20
                                            xoffset 50
                                            yalign 0.5

                    ## Кастомный скроллбар зоны вариантов — та же логика,
                    ## что и у ленты выше (локальные координаты, см.
                    ## комментарий у первого vbar).
                    vbar:
                        value YScrollValue("choice_viewport")
                        xsize 5
                        ysize int(config.screen_height * 0.25) - 26
                        ypos 26
                        xpos CHAT_PANEL_WIDTH + 20
                        xanchor 1.0
                        bar_resizing False
                        top_bar Solid("#00000000")
                        bottom_bar Solid("#00000000")
                        thumb Solid("#ae5334", xsize=5, ysize=50)
                        thumb_offset 0
                        unscrollable "hide"
