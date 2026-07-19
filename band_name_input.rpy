################################################################################
## Переопределяем стандартный экран "input", который использует
## renpy.input() под капотом. Единственное, что реально обязательно
## для движка — виджет input с id "input" (оттуда renpy.input() потом
## забирает введённый текст); всё остальное — просто оформление под
## тот же вид, что у чата/check_result/мини-игры.
##
## Работает с уже существующим вызовом в script.rpy:
##     $ band_name = renpy.input("Введите название группы и нажмите Enter", length=30).strip()
## Enter сам подтверждает ввод — это встроенное поведение виджета input,
## отдельно прописывать не нужно.
################################################################################

screen input(prompt):

    frame:
        xsize CHAT_PANEL_WIDTH
        ysize config.screen_height
        xanchor 1.0
        xpos config.screen_width - 50
        background None

        vbox:
            xfill True
            yfill True

            ## Верхняя зона — вместо чата, тот же размер (0.75 экрана).
            frame:
                ysize int(config.screen_height * 0.75)
                xfill True
                background None

                text prompt:
                    font FONT_BODY
                    size 20
                    color "#ffffff"
                    xpos CHAT_TEXT_MARGIN
                    yalign 0.5
                    xsize CHAT_PANEL_WIDTH - CHAT_TEXT_MARGIN
                    text_align 0.0

            ## Нижняя зона — вместо кнопки "Дальше", тут сама строка ввода.
            frame:
                ysize int(config.screen_height * 0.25)
                xfill True
                background None

                fixed:
                    xfill True
                    yfill True

                    add Solid("#ae5334") xsize CHAT_PANEL_WIDTH ysize 1 ypos 0

                    input id "input":
                        xsize CHAT_PANEL_WIDTH - 50 - CHAT_TEXT_MARGIN
                        xoffset 50
                        ypos 26
                        font FONT_BODY
                        size 20
                        color "#ae5334"
