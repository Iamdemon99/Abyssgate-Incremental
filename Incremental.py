import pygame
import time
import os
import random

# --- User Configuration (EASY TO CHANGE) ---
# 1. Change the name of your game currency
CURRENCY_NAME = "Souls"
# 2. Change the symbol displayed next to your currency amount
CURRENCY_SYMBOL = "€" # E.g., '$', '€', '§', '🍪'
# 3. Put your image file (e.g., 'my_orb.png') in the same folder as this script, 
#    and change this variable to match the file name.
MAIN_ITEM_IMAGE_FILE = "soul.png" 

# --- Pygame Setup ---
pygame.init()

# Global Settings
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"Abyssal Clicker: {CURRENCY_NAME} soul")
clock = pygame.time.Clock()
FPS = 60

# --- Colors ---
BLACK = (25, 25, 35)      # Dark background
WHITE = (240, 240, 240)   # Text
RED = (180, 50, 50)       # Click Item Glow
DARK_RED = (80, 0, 0)     # Upgrade Panel
GREEN = (50, 180, 50)     # Buy button
GRAY = (50, 50, 60)       # Inactive button

# --- Fonts ---
FONT_LARGE = pygame.font.Font(None, 64)
FONT_MEDIUM = pygame.font.Font(None, 36)
FONT_SMALL = pygame.font.Font(None, 24)

# --- Game Components ---

class Upgrade:
    """Represents a purchasable upgrade."""
    def __init__(self, name, base_cost, click_effect, passive_effect, description):
        self.name = name
        self.base_cost = base_cost
        self.click_effect = click_effect
        self.passive_effect = passive_effect
        self.level = 0
        self.description = description
    
    @property
    def current_cost(self):
        # Exponential cost increase: cost = base_cost * 1.15^level
        return int(self.base_cost * (1.15 ** self.level))

class Game:
    def __init__(self):
        self.cookies = 0.0
        self.cps = 0.0          # Currency Per Second (passive income)
        self.click_multiplier = 1.0 # Currency earned per click
        
        self.last_update_time = time.time()
        
        # --- Load Main Item Image ---
        self.item_rect = None
        self.item_surface = None
        self.item_radius = 120
        
        # Flag to check if the user image was loaded successfully
        self.image_loaded = False 
        
        try:
            # Attempt to load the user's specified image
            img = pygame.image.load(MAIN_ITEM_IMAGE_FILE).convert_alpha()
            # Scale the image to a desirable size (e.g., 256x256)
            self.item_surface = pygame.transform.scale(img, (self.item_radius * 2, self.item_radius * 2))
            self.image_loaded = True
            print(f"Loaded image: {MAIN_ITEM_IMAGE_FILE}")
        except pygame.error:
            # Fallback if image file is not found
            print(f"WARNING: Image '{MAIN_ITEM_IMAGE_FILE}' not found. Using placeholder circle.")
            self.item_surface = self._create_placeholder_surface()
        
        # Define the clickable area (centered on the left side)
        self.item_rect = self.item_surface.get_rect(center=(WIDTH // 4, HEIGHT // 2))

        # --- Upgrades List ---
        self.upgrades = [
            Upgrade("Spectral Harvester", 15, 0.1, 0.0, "Increases click yield by 0.1"),
            Upgrade("Lesser Demon Imp", 100, 0, 1.0, "Generates 1 §/s passively"),
            Upgrade("Abyssal Portal I", 1100, 0, 8.0, "Generates 8 §/s passively"),
            Upgrade("Greater Demon Lord", 5000, 1.0, 50.0, "Big boost to click and passive income"),
        ]
        
    def _create_placeholder_surface(self):
        """Creates a circular surface to use if the image file is missing."""
        surf = pygame.Surface((self.item_radius * 2, self.item_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, RED, (self.item_radius, self.item_radius), self.item_radius)
        return surf

    def handle_click(self, pos):
        """Processes a click on the main item."""
        if self.item_rect.collidepoint(pos):
            self.cookies += self.click_multiplier
            
            # If using a placeholder, briefly change its color on click
            if not self.image_loaded:
                 pygame.draw.circle(screen, RED_GLOW, self.item_rect.center, self.item_radius + 5, 5)

            return True
        return False
        
    def handle_upgrade_buy(self, upgrade_index):
        """Processes an attempt to buy an upgrade."""
        upgrade = self.upgrades[upgrade_index]
        cost = upgrade.current_cost
        
        if self.cookies >= cost:
            self.cookies -= cost
            upgrade.level += 1
            
            # Apply effects
            self.click_multiplier += upgrade.click_effect
            self.cps += upgrade.passive_effect
            
            print(f"Bought {upgrade.name} (Lvl {upgrade.level})!")
            return True
        return False

    def update(self):
        """Calculates passive income."""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        
        # Calculate passive income earned since last frame
        self.cookies += self.cps * delta_time
        
        self.last_update_time = current_time

    def draw(self):
        """Draws all game elements."""
        screen.fill(BLACK)
        
        # --- 1. Draw Main Item ---
        screen.blit(self.item_surface, self.item_rect)

        # Currency display
        cookies_text = FONT_LARGE.render(f"{self.cookies:,.2f} {CURRENCY_SYMBOL}", True, WHITE)
        screen.blit(cookies_text, (WIDTH // 4 - cookies_text.get_width() // 2, 50))
        
        # CPS display
        cps_text = FONT_MEDIUM.render(f"{self.cps:.1f} {CURRENCY_SYMBOL}/s", True, WHITE)
        screen.blit(cps_text, (WIDTH // 4 - cps_text.get_width() // 2, 100))
        
        # --- 2. Draw Upgrade Panel ---
        # Panel Background
        panel_width = WIDTH // 2
        panel_x = WIDTH - panel_width
        pygame.draw.rect(screen, DARK_RED, (panel_x, 0, panel_width, HEIGHT))
        
        # Panel Title
        title_text = FONT_LARGE.render("Upgrades", True, WHITE)
        screen.blit(title_text, (panel_x + panel_width // 2 - title_text.get_width() // 2, 20))
        
        # Draw each upgrade item
        upgrade_y = 80
        self.upgrade_rects = []
        for i, upgrade in enumerate(self.upgrades):
            rect = self._draw_upgrade_item(i, upgrade, panel_x, upgrade_y)
            self.upgrade_rects.append(rect)
            upgrade_y += 120 # Space for next upgrade

    def _draw_upgrade_item(self, index, upgrade, panel_x, y_start):
        """Helper function to draw a single upgrade row."""
        
        # Background bar for the upgrade
        bar_rect = pygame.Rect(panel_x + 10, y_start, WIDTH // 2 - 20, 110)
        pygame.draw.rect(screen, GRAY, bar_rect, border_radius=5)

        # Name and Level
        name_text = FONT_MEDIUM.render(f"{upgrade.name} (Lvl {upgrade.level})", True, WHITE)
        screen.blit(name_text, (panel_x + 20, y_start + 5))
        
        # Description
        desc_text = FONT_SMALL.render(upgrade.description, True, WHITE)
        screen.blit(desc_text, (panel_x + 20, y_start + 35))

        # Cost Text
        cost_text = FONT_MEDIUM.render(f"Cost: {upgrade.current_cost:,} {CURRENCY_SYMBOL}", True, WHITE)
        screen.blit(cost_text, (panel_x + 20, y_start + 70))
        
        # Buy Button
        buy_button_width, buy_button_height = 100, 40
        buy_rect = pygame.Rect(panel_x + bar_rect.width - buy_button_width - 10, y_start + 60, buy_button_width, buy_button_height)
        
        can_afford = self.cookies >= upgrade.current_cost
        button_color = GREEN if can_afford else RED
        
        # Highlight on hover
        mouse_pos = pygame.mouse.get_pos()
        if buy_rect.collidepoint(mouse_pos) and can_afford:
            # Darken/brighten slightly for hover effect
            button_color = tuple(min(255, c + 30) for c in button_color)

        pygame.draw.rect(screen, button_color, buy_rect, border_radius=10)
        buy_text = FONT_MEDIUM.render("Buy", True, WHITE)
        buy_text_rect = buy_text.get_rect(center=buy_rect.center)
        screen.blit(buy_text, buy_text_rect)
        
        return buy_rect # Return the button rect for click detection


# --- Main Loop ---
def run_game():
    game = Game()
    global running
    running = True

    while running:
        # --- 1. Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    pos = event.pos
                    
                    # Check for main item click
                    game.handle_click(pos)

                    # Check for upgrade button clicks
                    for i, rect in enumerate(game.upgrade_rects):
                        if rect.collidepoint(pos):
                            game.handle_upgrade_buy(i)

        # --- 2. Game Logic Update ---
        game.update()

        # --- 3. Drawing ---
        game.draw()
        
        # --- 4. Display Update ---
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    run_game()
