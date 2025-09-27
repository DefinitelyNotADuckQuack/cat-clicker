import os
import pygame

# explicit track index and state
_TRACKS = [os.path.join(os.path.dirname(__file__), "music", f"track{i}.mp3") for i in range(1, 7)]
_idx = 0
_enabled = False
_paused = False
_last_toggle_ts = 0
_COOLDOWN_MS = 400


def init_music():
    global _enabled, _idx, _paused
    try:
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.4)
        _idx = 0
        _paused = False
        if os.path.exists(_TRACKS[_idx]):
            pygame.mixer.music.load(_TRACKS[_idx])
            pygame.mixer.music.play()
        _enabled = True
        return True
    except pygame.error:
        _enabled = False
        return False


def music_is_enabled():
    return _enabled and pygame.mixer.get_init() is not None


def music_is_paused():
    return _paused


def music_toggle():
    # strictly pause/unpause current track, NO index change
    global _paused, _last_toggle_ts
    if not music_is_enabled():
        return
    if _paused:
        pygame.mixer.music.unpause()
        _paused = False
    else:
        pygame.mixer.music.pause()
        _paused = True
    # record time to prevent update_music() from thinking track ended
    _last_toggle_ts = pygame.time.get_ticks() if pygame.get_init() else 0


def _play_index():
    try:
        pygame.mixer.music.load(_TRACKS[_idx])
        pygame.mixer.music.play()
    except Exception:
        pass


def music_next():
    global _idx, _paused
    if not music_is_enabled():
        return
    _idx = (_idx + 1) % len(_TRACKS)
    _paused = False
    _play_index()


def music_prev():
    global _idx, _paused
    if not music_is_enabled():
        return
    _idx = (_idx - 1) % len(_TRACKS)
    _paused = False
    _play_index()


def volume_up(step=0.1):
    if music_is_enabled():
        pygame.mixer.music.set_volume(min(1.0, pygame.mixer.music.get_volume() + step))


def volume_down(step=0.1):
    if music_is_enabled():
        pygame.mixer.music.set_volume(max(0.0, pygame.mixer.music.get_volume() - step))


def update_music():
    # auto-advance only when not paused, ignore right after toggle
    if not music_is_enabled() or _paused:
        return
    now = pygame.time.get_ticks() if pygame.get_init() else 0
    if now and (now - _last_toggle_ts) < _COOLDOWN_MS:
        return
    if not pygame.mixer.music.get_busy():
        music_next()