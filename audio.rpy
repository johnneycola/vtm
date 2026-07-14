init -1 python:
    # Фоновые звуки (эмбиент) — зацикленные, отдельно от музыки
    renpy.music.register_channel("ambience", mixer="sound", loop=True)
    # Уникальные звуки поверх фона (двери, зажигалка, стакан и т.п.)
    renpy.music.register_channel("sfx", mixer="sound", loop=False)
    # Звуки интерфейса (клик "Дальше", выбор варианта)
    renpy.music.register_channel("ui", mixer="sound", loop=False)