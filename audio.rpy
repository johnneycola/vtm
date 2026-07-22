init -1 python:
    # Фоновые звуки (эмбиент) — зацикленные, отдельно от музыки
    renpy.music.register_channel("ambience", mixer="sound", loop=True)
    # Уникальные звуки поверх фона (двери, зажигалка, стакан и т.п.)
    renpy.music.register_channel("sfx", mixer="sound", loop=False)
    # Звуки интерфейса (клик "Дальше", выбор варианта)
    renpy.music.register_channel("ui", mixer="sound", loop=False)
    # Ритм-игра: бас+барабаны — играет всегда без остановки.
    renpy.music.register_channel("band", mixer="music", loop=False)
    # Ритм-игра: гитара — мьютится на промахах, играет отдельным файлом
    # синхронно с "band" (оба стартуют в один и тот же момент).
    renpy.music.register_channel("guitar", mixer="music", loop=False)


init python:
    # Общее правило (не завязано на конкретную сцену): пока играет
    # музыка (канал "music"), фоновые звуки (канал "ambience") тише
    # на 50%. Как только музыка останавливается — громкость эмбиента
    # возвращается к обычной. Проверяется каждый тик через
    # config.periodic_callbacks, так что срабатывает для любой музыки,
    # где бы её ни включили.
    _ambience_ducked = False

    def _duck_ambience_for_music():
        global _ambience_ducked
        should_duck = renpy.music.get_playing(channel="music") is not None
        if should_duck != _ambience_ducked:
            _ambience_ducked = should_duck
            renpy.music.set_volume(0.5 if should_duck else 1.0, delay=0.5, channel="ambience")

    config.periodic_callbacks.append(_duck_ambience_for_music)