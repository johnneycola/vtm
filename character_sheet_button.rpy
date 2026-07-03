# ============================================================
#  МОДУЛЬ: кнопка "Лист персонажа" — постоянно доступна в игре
#
#  Иконка + подпись в правом верхнем углу экрана. По клику
#  открывает попап character_sheet_damien.rpy (через Show/Hide,
#  так что не мешает основному сюжетному потоку call/return).
#
#  Кнопка добавлена в config.overlay_screens — это тот же
#  механизм, которым в Ren'Py по умолчанию рисуется quick_menu:
#  экран рисуется поверх во время диалогов и меню автоматически,
#  без необходимости вручную вызывать "show screen" в каждом label.
# ============================================================

screen character_sheet_button():
    zorder 200

    # Не показываем кнопку поверх главного меню и поверх уже
    # открытого листа персонажа (он и так модальный и её накроет,
    # но так чище).
    if not main_menu and not renpy.get_screen("character_sheet_damien"):

        button:
            xalign 1.0
            yalign 0.0
            xoffset -24
            yoffset 20

            padding (16, 10)
            background Solid("#1a1414cc")
            hover_background Solid("#3a1a1acc")

            action Show("character_sheet_damien")

            hbox:
                spacing 10

                # "Иконка" нарисована фигурами — не зависит от шрифта.
                # Когда появится нормальная картинка-иконка (png/svg),
                # можно заменить весь этот vbox на:
                #     add "icons/char_sheet_icon.png" size (20, 20)
                vbox:
                    yalign 0.5
                    spacing 4
                    frame:
                        xsize 20
                        ysize 24
                        background Solid("#dddddd")
                        padding (3, 4)
                        vbox:
                            spacing 4
                            add Solid("#1a1414"):
                                xsize 14
                                ysize 2
                            add Solid("#1a1414"):
                                xsize 14
                                ysize 2
                            add Solid("#1a1414"):
                                xsize 9
                                ysize 2

                text "Лист персонажа" size 16 color "#dddddd"


init python:
    if "character_sheet_button" not in config.overlay_screens:
        config.overlay_screens.append("character_sheet_button")
