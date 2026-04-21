import pygame
import time

class Player:
    def __init__(self):
        self.playlist = [
            "A:\KBTU_PP\PP2\practice 9\music_player\music\overdose.mp3.mp3",
            "A:\KBTU_PP\PP2\practice 9\music_player\music\KanariaBRAIN.mp3"
        ]
        self.index = 0
        self.playing = False
        self.loaded = False
        self.pause_pos = 0
        self.start_time = 0
        self.paused_time = 0

        pygame.mixer.init()

    def play(self):
        if not self.loaded:
            pygame.mixer.music.load(self.playlist[self.index])
            self.loaded = True
            self.pause_pos = 0
            self.paused_time = 0
        
        if self.pause_pos > 0:
            pygame.mixer.music.play(start=self.pause_pos / 1000.0)
            self.start_time = time.time() - (self.pause_pos / 1000.0)
            self.pause_pos = 0
        else:
            pygame.mixer.music.play()
            self.start_time = time.time()
        
        self.playing = True

    def pause(self):
        if self.playing:
            self.pause_pos = self.get_current_position_ms()
            self.paused_time = time.time()
            pygame.mixer.music.pause()
            self.playing = False

    def unpause(self):
        if self.pause_pos > 0:
            self.play()
        else:
            pygame.mixer.music.unpause()
            self.start_time = time.time() - (self.get_current_position_ms() / 1000.0)
            self.playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.loaded = False
        self.pause_pos = 0
        self.start_time = 0
        self.paused_time = 0

    def next(self):
        self.index = (self.index + 1) % len(self.playlist)
        self.loaded = False
        self.pause_pos = 0
        self.start_time = 0
        self.paused_time = 0
        self.play()

    def prev(self):
        self.index = (self.index - 1) % len(self.playlist)
        self.loaded = False
        self.pause_pos = 0
        self.start_time = 0
        self.paused_time = 0
        self.play()

    def get_current_track(self):
        return self.playlist[self.index]

    def get_current_position_ms(self):
        if self.playing:
            elapsed = (time.time() - self.start_time) * 1000
            return max(0, int(elapsed))
        else:
            return self.pause_pos

    def get_position(self):
        return self.get_current_position_ms() // 1000