import pygame

class Player:
    def __init__(self):
        self.playlist = [
            "music/KanariaBRAIN.mp3",
            "music/なとり - Overdose(1).mp3"
        ]
        self.index = 0
        self.playing = False

        pygame.mixer.init()

    def play(self):
        pygame.mixer.music.load(self.playlist[self.index])
        pygame.mixer.music.play()
        self.playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False

    def next(self):
        self.index += 1
        if self.index >= len(self.playlist):
            self.index = 0
        self.play()

    def prev(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.playlist) - 1
        self.play()

    def get_current_track(self):
        return self.playlist[self.index]

    def get_position(self):
        return pygame.mixer.music.get_pos() // 1000