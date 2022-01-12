from typing import Any

import pygame
import copy
import sys
import random
import os

SCREENRECT = pygame.Rect(0, 0, 1200, 800)


def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join(os.path.split(os.path.abspath(__file__))[0], "res", file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pygame.get_error()))
    return surface.convert_alpha()


class GrimDawnCard(pygame.sprite.Sprite):
    RUNNING_GAP = 100
    BACKGROUND_CARD = None
    GRIMDAWNCARD = []
    IMG_WIDTH = 330
    IMG_HEIGHT = 230
    TOP_MARGIN = 30
    LEFT_MARGIN = 50
    EXPEND_MARGIN = 10

    def __init__(self, uuid, containers=None):
        super(GrimDawnCard, self).__init__(containers)
        self.status = "cover"  # hover, rotate, reveal
        self.uuid = uuid
        self.image = GrimDawnCard.BACKGROUND_CARD
        self._front_image = GrimDawnCard.GRIMDAWNCARD[self.uuid]
        self._back_image = GrimDawnCard.BACKGROUND_CARD
        self._top = GrimDawnCard.IMG_HEIGHT * (self.uuid // 3) + GrimDawnCard.TOP_MARGIN * (1 + self.uuid // 3)
        self._left = GrimDawnCard.IMG_WIDTH * (self.uuid % 3) + GrimDawnCard.LEFT_MARGIN * (1 + self.uuid % 3)
        self._rect = self.image.get_rect(left=self._left, top=self._top)
        self.rect = self._rect

        self._expand_back_image = pygame.transform.scale(self._back_image, (
        GrimDawnCard.IMG_WIDTH + GrimDawnCard.EXPEND_MARGIN, GrimDawnCard.IMG_HEIGHT + GrimDawnCard.EXPEND_MARGIN))
        self.time = pygame.time.get_ticks()
        self.back_times = 9
        self.front_times = 10

    def update(self, *args: Any, **kwargs: Any) -> None:
        if self.status == "cover":
            self.image = self._back_image
        elif self.status == "hover":
            self.image = self._expand_back_image
        elif self.status == "rotate":
            if pygame.time.get_ticks() >= self.time + GrimDawnCard.RUNNING_GAP:
                if self.back_times == 0 and self.front_times != 0:
                    self.image = pygame.transform.scale(self._front_image, (
                    GrimDawnCard.IMG_WIDTH // self.front_times, GrimDawnCard.IMG_HEIGHT))
                    self.rect = self.image.get_rect(centerx=self._left + GrimDawnCard.IMG_WIDTH // 2,
                                                    centery=self._top + GrimDawnCard.IMG_HEIGHT // 2)
                    self.rect.width = self.image.get_width()
                    self.front_times -= 1
                elif self.back_times != 0 and self.front_times == 10:
                    self.image = pygame.transform.scale(self._back_image, (
                    GrimDawnCard.IMG_WIDTH // (10 - self.back_times), GrimDawnCard.IMG_HEIGHT))
                    self.rect = self.image.get_rect(centerx=self._left + GrimDawnCard.IMG_WIDTH // 2,
                                                    centery=self._top + GrimDawnCard.IMG_HEIGHT // 2)
                    self.rect.width = self.image.get_width()
                    self.back_times -= 1
                else:
                    self.status = "reveal"

                self.time = pygame.time.get_ticks()
        elif self.status == "reveal":
            self.rect = self._rect
            self.image = self._front_image

    def locate(self, ix, iy):
        if (self.rect.x <= ix <= self.rect.x + self.rect.width) and (
                self.rect.y <= iy <= self.rect.y + self.rect.height):
            return self.uuid
        else:
            return None

    def change_status(self, status):
        self.status = status

    def get_status(self):
        return self.status


if __name__ == "__main__":
    pygame.init()
    # Set the display mode
    screen = pygame.display.set_mode(SCREENRECT.size)
    background = pygame.Surface(SCREENRECT.size)
    background.blit(pygame.transform.scale(load_image("galaxy.jpg"), SCREENRECT.size), (0, 0))
    screen.blit(background, (0, 0))

    GrimDawnCard.BACKGROUND_CARD = pygame.transform.scale(pygame.transform.rotate(load_image("Cardback.png"), -90),
                                                          (GrimDawnCard.IMG_WIDTH, GrimDawnCard.IMG_HEIGHT))
    cards = pygame.sprite.Group()

    random.seed()
    GrimDawnRandomList = ["Acranist.jpg", "Demolitionist.jpg", "Inquisitor.jpg", "Necromancer.jpg", "Nightblade.jpg",
                          "Oathkeeper.jpg", "Occultist.jpg", "Shaman.jpg", "Soldier.jpg"]
    for _ in range(random.randint(100, 1000)):
        n1, n2 = random.randint(0, len(GrimDawnRandomList) - 1), random.randint(0, len(GrimDawnRandomList) - 1)
        GrimDawnRandomList[n1], GrimDawnRandomList[n2] = GrimDawnRandomList[n2], GrimDawnRandomList[n1]

    for card in GrimDawnRandomList:
        GrimDawnCard.GRIMDAWNCARD.append(
            pygame.transform.scale(load_image(card), (GrimDawnCard.IMG_WIDTH, GrimDawnCard.IMG_HEIGHT)))

    for i in range(len(GrimDawnRandomList)):
        GrimDawnCard(uuid=i, containers=cards)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                for sprite in cards.sprites():
                    if sprite.get_status() in ("hover", "cover"):
                        locate = sprite.locate(*event.pos)
                        if locate is not None:
                            sprite.change_status("hover")
                        else:
                            sprite.change_status("cover")
            if event.type == pygame.MOUSEBUTTONDOWN:
                for sprite in cards.sprites():
                    locate = sprite.locate(*event.pos)
                    if locate is not None:
                        sprite.change_status("rotate")

        cards.clear(screen, background)

        cards.update()
        cards.draw(screen)
        pygame.display.update()
