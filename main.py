import sys
import pygame
from game import run_game


if __name__ == "__main__":
    pygame.init()
    try:
        run_game()
    finally:
        pygame.quit()
        sys.exit()