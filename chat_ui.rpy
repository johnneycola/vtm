################################################################################
## Лента диалога (кастомный say-экран) + варианты ответа (кастомный choice)
################################################################################

default chat_history = []

init python:

    def chat_add(speaker_obj, text, stmt_id=None):
        # ВНИМАНИЕ: who приходит в say-экран уже строкой (именем персонажа),
        # а не объектом Character — поэтому сравниваем с d.name, а не с d.
        if speaker_obj is None:
            side = "narration"
            name = None
        elif speaker_obj == d.name:
            side = "damn"
            name = speaker_obj
        else:
            side = "npc"
            name = speaker_obj

        chat_history.append({
            "speaker": name,
            "text": text,
            "side": side,
            "stmt_id": stmt_id,
        })

    def _current_stmt():
        # Уникальный идентификатор текущей позиции в сценарии.
        # Нужен, чтобы не добавлять одну и ту же реплику в лог
        # повторно при перерисовке экрана.
        return renpy.game.context().current

    def _entry_widgets(entry):
        # Виджеты одной записи ленты — используются и для показа,
        # и для измерения высоты в _measure_chat_height().
        # ВАЖНО: xsize/size/italic здесь должны точно совпадать с тем,
        # что используется при реальном отображении в screen chat_log_view.
        widgets = []
        if entry["side"] == "narration":
            widgets.append(Text(entry["text"], italic=True, color="#999999", xsize=550))
        elif entry["side"] == "damn":
            widgets.append(Text(entry["speaker"], color="#3498db", size=18))
            widgets.append(Text(entry["text"], color="#ffffff", xsize=550))
        elif entry["side"] == "npc":
            widgets.append(Text(entry["speaker"], color="#e91e63", size=18))
            widgets.append(Text(entry["text"], color="#ffffff", xsize=500))
        return widgets

    def _measure_chat_height():
        # Суммарная "естественная" высота всей ленты — нужна, чтобы понять,
        # сколько пустого места добавить сверху, и прижать короткую ленту
        # к низу зоны, а не к верху.
        total = 0
        for entry in chat_history:
            for w in _entry_widgets(entry):
                r = renpy.render(w, 999, 10000, 0, 0)
                total += r.height
        if len(chat_history) > 1:
            total += 20 * (len(chat_history) - 1)
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
            ysize int(config.screen_height * 0.75)
            yinitial 1.0

            vbox:
                spacing 20
                xsize 550

                ## Пустой отступ сверху — прижимает короткую ленту
                ## к низу зоны. Когда лента заполняет всю зону и больше,
                ## отступ становится 0, и включается обычный скролл.
                $ _spacer = max(0, int(config.screen_height * 0.75) - _measure_chat_height())
                null height _spacer

                for entry in chat_history:
                    if entry["side"] == "narration":
                        text entry["text"] italic True color "#999999" text_align 0.0 xsize 550

                    elif entry["side"] == "damn":
                        vbox:
                            text entry["speaker"] color "#3498db" size 18 text_align 0.0
                            text entry["text"] color "#ffffff" text_align 0.0 xsize 550

                    elif entry["side"] == "npc":
                        vbox:
                            xoffset 50
                            text entry["speaker"] color "#e91e63" size 18 text_align 0.0
                            text entry["text"] color "#ffffff" text_align 0.0 xsize 500

        ## Кастомный тонкий скроллбар — вынесен за пределы панели чата.
        ## Панель шириной 550, правый край панели в 50px от края экрана,
        ## а бегунок должен быть в 30px от края экрана — то есть на 20px
        ## правее самой панели. 570 = 550 (ширина панели) + 20 (это смещение).
        vbar:
            value YScrollValue("chat_viewport")
            xsize 5
            ysize int(config.screen_height * 0.75)
            xpos 570
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

    python:
        stmt_id = _current_stmt()
        if not chat_history or chat_history[-1]["stmt_id"] != stmt_id:
            chat_add(who, what, stmt_id)

    frame:
        xsize 550
        ysize config.screen_height
        xanchor 1.0
        xpos config.screen_width - 50
        background "#1a1410"

        vbox:
            xfill True
            yfill True

            use chat_log_view

            ## Зарезервированная нижняя зона — ровно 1/4 экрана.
            frame:
                ysize int(config.screen_height * 0.25)
                xfill True
                background "#100c08"

                button:
                    align (0.5, 0.5)
                    action Return(True)

                    text "Дальше":
                        color "#ffffff"
                        size 24


################################################################################
## choice — варианты ответа. Та же лента сверху, а вместо кнопки "Дальше" —
## список вариантов (со своим скроллом, если не помещаются). При выборе —
## реплика добавляется в ленту от лица Дамьена.
################################################################################

screen choice(items):

    frame:
        xsize 550
        ysize config.screen_height
        xanchor 1.0
        xpos config.screen_width - 50
        background "#1a1410"

        vbox:
            xfill True
            yfill True

            use chat_log_view

            frame:
                ysize int(config.screen_height * 0.25)
                xfill True
                background "#100c08"

                fixed:
                    xfill True
                    yfill True

                    viewport:
                        id "choice_viewport"
                        mousewheel True
                        draggable True
                        xfill True
                        yfill True

                        vbox:
                            xfill True
                            spacing 10

                            for i in items:
                                textbutton i.caption:
                                    xoffset 50
                                    xsize 500
                                    text_color "#ffffff"
                                    text_hover_color "#e91e63"
                                    text_size 22
                                    action [Function(chat_add, d.name, i.caption), i.action]

                    ## Кастомный скроллбар зоны вариантов — та же логика
                    ## позиционирования, что и у ленты (570 = 550 ширина
                    ## панели + 20 смещения вправо, чтобы оказаться в 30px
                    ## от края экрана).
                    vbar:
                        value YScrollValue("choice_viewport")
                        xsize 5
                        yfill True
                        xpos 570
                        xanchor 1.0
                        bar_resizing False
                        top_bar Solid("#00000000")
                        bottom_bar Solid("#00000000")
                        thumb Solid("#ae5334", xsize=5, ysize=50)
                        thumb_offset 0
                        unscrollable "hide"
