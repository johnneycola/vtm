# ============================================================
#  МОДУЛЬ: статус персонажей (жив / без сознания / мёртв)
#
#  Единое хранилище состояния NPC (и, при желании, ПЕРСОНАЖА
#  игрока), чтобы в любой точке сюжета можно было проверить,
#  что случилось с персонажем, и подобрать нужные реплики/ветки.
#
#  Идентификатор персонажа (char_id) — просто строка, например
#  "claire". Не обязательно заводить её заранее: если статус
#  ни разу не задавался, персонаж считается живым.
#
#  Использование:
#
#      $ set_character_status("claire", STATUS_DEAD)
#      ...
#      if is_dead("claire"):
#          "Клэр больше не дышит."
#      elif is_unconscious("claire"):
#          "Клэр без сознания."
#      else:
#          "Клэр жива и в сознании."
# ============================================================

default character_status = {}

init python:

    STATUS_ALIVE       = "alive"
    STATUS_UNCONSCIOUS = "unconscious"
    STATUS_DEAD        = "dead"

    def set_character_status(char_id, status):
        store.character_status[char_id] = status

    def get_character_status(char_id):
        """Если статус ещё не задан — персонаж по умолчанию жив."""
        return store.character_status.get(char_id, STATUS_ALIVE)

    def is_alive(char_id):
        return get_character_status(char_id) != STATUS_DEAD

    def is_dead(char_id):
        return get_character_status(char_id) == STATUS_DEAD

    def is_unconscious(char_id):
        return get_character_status(char_id) == STATUS_UNCONSCIOUS
