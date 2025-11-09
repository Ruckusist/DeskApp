"""
Dungeon Crawler RPG - Main Game Module
Epic RPG adventure game built with the DeskApp framework.
"""
import random
import os
import sys

# Add the parent directory to sys.path to import deskapp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import deskapp
from deskapp import App, Module, callback, Keys

from .game_data import save_game, load_game, ITEMS, SPELLS, PlayerClass
from .game_mechanics import GameState
from .art_assets import (
    SPLASH_SCREEN, CHARACTER_CREATION, TOWN_SPLASH, SHOP_HEADER,
    DUNGEON_ENTRANCE, COMBAT_UI, VICTORY_BANNER, DEFEAT_BANNER,
    STORY_INTRO, GAME_OVER_STORY, VICTORY_STORY, get_player_status_display
)


class DungeonCrawlerRPG(Module):
    name = "Dungeon Crawler RPG"
    
    def __init__(self, app):
        super().__init__(app, "DungeonCrawler")
        self.game_state = GameState()
        self.current_screen = "splash"  # splash, char_creation, story, town, shop, dungeon, combat, inventory
        self.message = ""
        self.input_buffer = ""
        self.waiting_for_input = False
        self.input_prompt = ""
        
        # Character creation state
        self.creating_character = False
        self.character_name = ""
        self.character_class = ""
        
        # Shop state
        self.shop_page = 0
        
        # Input handling
        self.last_key = ""
    
    def update_header(self):
        """Update the app header with current game info"""
        if self.game_state.player:
            header = f"Dungeon Crawler - {self.game_state.player.name} ({self.game_state.player.player_class.value})"
            if self.game_state.in_combat and self.game_state.current_monster:
                header += f" - Fighting {self.game_state.current_monster.name}"
            elif not self.game_state.in_town:
                header += f" - Floor {self.game_state.current_floor}"
            else:
                header += " - Haven Town"
            self.app.set_header(header)
        else:
            self.app.set_header("Dungeon Crawler RPG")
    
    def page(self, panel):
        """Main render function"""
        self.update_header()
        
        # Clear the panel
        panel.win.clear()
        
        if self.current_screen == "splash":
            self.render_splash_screen(panel)
        elif self.current_screen == "char_creation":
            self.render_character_creation(panel)
        elif self.current_screen == "story":
            self.render_story_intro(panel)
        elif self.current_screen == "town":
            self.render_town(panel)
        elif self.current_screen == "shop":
            self.render_shop(panel)
        elif self.current_screen == "dungeon_entrance":
            self.render_dungeon_entrance(panel)
        elif self.current_screen == "combat":
            self.render_combat(panel)
        elif self.current_screen == "inventory":
            self.render_inventory(panel)
        elif self.current_screen == "victory":
            self.render_victory(panel)
        elif self.current_screen == "game_over":
            self.render_game_over(panel)
        
        # Show messages
        if self.message:
            self.write(panel, self.h - 3, 2, f"Message: {self.message}")
        
        # Show input prompt if waiting for input
        if self.waiting_for_input:
            self.write(panel, self.h - 2, 2, f"{self.input_prompt}: {self.input_buffer}")
    
    def render_splash_screen(self, panel):
        """Render the splash screen"""
        lines = SPLASH_SCREEN.strip().split('\n')
        start_y = max(0, (self.h - len(lines)) // 2)
        
        for i, line in enumerate(lines):
            if start_y + i < self.h - 1:
                self.write(panel, start_y + i, 0, line[:self.w])
    
    def render_character_creation(self, panel):
        """Render character creation screen"""
        lines = CHARACTER_CREATION.strip().split('\n')
        start_y = max(0, (self.h - len(lines)) // 2)
        
        for i, line in enumerate(lines):
            if start_y + i < self.h - 1:
                self.write(panel, start_y + i, 0, line[:self.w])
    
    def render_story_intro(self, panel):
        """Render story introduction"""
        self.write(panel, 2, 2, "THE LEGEND BEGINS...")
        
        story_lines = STORY_INTRO.strip().split('\n')
        for i, line in enumerate(story_lines):
            if i + 4 < self.h - 3:
                self.write(panel, i + 4, 2, line[:self.w-4])
        
        self.write(panel, self.h - 5, 2, "Press ENTER to continue to Haven Town...")
    
    def render_town(self, panel):
        """Render town screen"""
        lines = TOWN_SPLASH.strip().split('\n')
        for i, line in enumerate(lines):
            if i < self.h - 1:
                self.write(panel, i, 0, line[:self.w])
        
        # Show player status at bottom
        if self.game_state.player:
            status_line = (f"HP: {self.game_state.player.hp}/{self.game_state.player.max_hp} | "
                          f"MP: {self.game_state.player.mp}/{self.game_state.player.max_mp} | "
                          f"Gold: {self.game_state.player.gold} | Floor: {self.game_state.current_floor}")
            self.write(panel, self.h - 4, 2, status_line)
    
    def render_shop(self, panel):
        """Render shop screen"""
        self.write(panel, 0, 0, SHOP_HEADER.strip())
        
        shop_display = self.game_state.shop.get_shop_display(self.game_state.player)
        lines = shop_display.split('\n')
        
        for i, line in enumerate(lines):
            if i + 8 < self.h - 3:
                self.write(panel, i + 8, 2, line[:self.w-4])
    
    def render_dungeon_entrance(self, panel):
        """Render dungeon entrance"""
        entrance_text = DUNGEON_ENTRANCE.format(self.game_state.current_floor)
        lines = entrance_text.strip().split('\n')
        
        for i, line in enumerate(lines):
            if i < self.h - 1:
                self.write(panel, i, 0, line[:self.w])
        
        # Show floor description
        description = self.game_state.dungeon.get_floor_description(self.game_state.current_floor)
        self.write(panel, self.h - 6, 2, f"Floor {self.game_state.current_floor}: {description}")
    
    def render_combat(self, panel):
        """Render combat screen"""
        if not self.game_state.current_monster:
            return
        
        monster = self.game_state.current_monster
        player = self.game_state.player
        
        # Combat header
        combat_header = COMBAT_UI.format(
            monster_name=monster.name,
            monster_hp=monster.hp,
            monster_max_hp=monster.max_hp,
            player_name=player.name,
            player_level=player.level,
            player_hp=player.hp,
            player_max_hp=player.max_hp,
            player_mp=player.mp,
            player_max_mp=player.max_mp,
            player_gold=player.gold
        )
        
        lines = combat_header.strip().split('\n')
        for i, line in enumerate(lines):
            self.write(panel, i, 0, line[:self.w])
        
        # Monster ASCII art
        art_lines = monster.ascii_art.strip().split('\n')
        art_start_y = len(lines) + 1
        for i, line in enumerate(art_lines):
            if art_start_y + i < self.h - 10:
                self.write(panel, art_start_y + i, 5, line)
        
        # Combat log
        log_start_y = art_start_y + len(art_lines) + 1
        self.write(panel, log_start_y, 2, "Combat Log:")
        for i, log_entry in enumerate(self.game_state.combat.combat_log[-5:]):  # Show last 5 entries
            if log_start_y + 1 + i < self.h - 5:
                self.write(panel, log_start_y + 1 + i, 2, f"  {log_entry}")
        
        # Combat options
        options_y = self.h - 4
        self.write(panel, options_y, 2, "Actions: A-Attack | M-Magic | I-Item | R-Run")
    
    def render_inventory(self, panel):
        """Render inventory/status screen"""
        if not self.game_state.player:
            return
        
        # Use the status display function
        status_display = get_player_status_display(self.game_state.player, self.game_state.current_floor)
        lines = status_display.strip().split('\n')
        
        for i, line in enumerate(lines):
            if i < self.h - 8:
                self.write(panel, i, 0, line[:self.w])
        
        # Show inventory items
        inv_start_y = len(lines)
        if self.game_state.player.inventory:
            for i, item in enumerate(self.game_state.player.inventory):
                if inv_start_y + i < self.h - 3:
                    self.write(panel, inv_start_y + i, 2, f"{i+1}. {item.name} - {item.description}")
        else:
            self.write(panel, inv_start_y, 2, "No items in inventory")
        
        # Show spells
        spells_y = self.h - 5
        self.write(panel, spells_y, 2, "Spells:")
        for i, spell in enumerate(self.game_state.player.spells):
            self.write(panel, spells_y + 1 + i, 4, f"{spell.name} (MP: {spell.mp_cost}) - {spell.description}")
        
        self.write(panel, self.h - 2, 2, "Press B to go back")
    
    def render_victory(self, panel):
        """Render victory screen"""
        self.write(panel, 2, 0, VICTORY_BANNER.strip())
        
        story_lines = VICTORY_STORY.strip().split('\n')
        for i, line in enumerate(story_lines):
            if i + 6 < self.h - 3:
                self.write(panel, i + 6, 2, line[:self.w-4])
        
        self.write(panel, self.h - 3, 2, "Press Q to quit or R to restart")
    
    def render_game_over(self, panel):
        """Render game over screen"""
        self.write(panel, 2, 0, DEFEAT_BANNER.strip())
        
        story_lines = GAME_OVER_STORY.strip().split('\n')
        for i, line in enumerate(story_lines):
            if i + 10 < self.h - 3:
                self.write(panel, i + 10, 2, line[:self.w-4])
        
        self.write(panel, self.h - 3, 2, "Press Q to quit or R to restart")
    
    # Event handlers for different screens
    @callback("DungeonCrawler", Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.current_screen == "splash":
            self.current_screen = "char_creation"
            self.waiting_for_input = True
            self.input_prompt = "Enter your name"
            self.input_buffer = ""
            
        elif self.current_screen == "char_creation":
            if self.character_name == "":
                if self.input_buffer.strip():
                    self.character_name = self.input_buffer.strip()
                    self.input_buffer = ""
                    self.input_prompt = "Choose class (1-3)"
            elif self.character_class == "":
                if self.input_buffer in ["1", "2", "3"]:
                    self.character_class = self.input_buffer
                    self.game_state.create_player(self.character_name, self.character_class)
                    self.waiting_for_input = False
                    self.current_screen = "story"
                    self.input_buffer = ""
                else:
                    self.message = "Please choose 1, 2, or 3"
                    self.input_buffer = ""
                    
        elif self.current_screen == "story":
            self.current_screen = "town"
            
        elif self.current_screen == "dungeon_entrance":
            self.game_state.enter_dungeon_floor(self.game_state.current_floor)
            self.current_screen = "combat"
            self.message = ""
    
    @callback("DungeonCrawler", Keys.L)
    def on_load_game(self, *args, **kwargs):
        if self.current_screen == "splash":
            player, floor = load_game()
            if player:
                self.game_state.player = player
                self.game_state.current_floor = floor
                self.current_screen = "town"
                self.message = "Game loaded successfully!"
            else:
                self.message = "No saved game found!"
    
    @callback("DungeonCrawler", Keys.S)
    def on_shop_or_save(self, *args, **kwargs):
        if self.current_screen == "town":
            self.current_screen = "shop"
            self.game_state.in_shop = True
    
    @callback("DungeonCrawler", Keys.R)
    def on_rest_or_run(self, *args, **kwargs):
        if self.current_screen == "town":
            result = self.game_state.rest_at_inn()
            self.message = result
        elif self.current_screen == "combat":
            # Run from combat
            if random.randint(1, 3) == 1:  # 33% chance to fail
                self.message = "You couldn't escape!"
                # Monster attacks
                self.game_state.combat.monster_attack(
                    self.game_state.current_monster, 
                    self.game_state.player
                )
            else:
                self.message = "You escaped!"
                self.game_state.return_to_town()
                self.current_screen = "town"
        elif self.current_screen in ["victory", "game_over"]:
            # Restart game
            self.game_state = GameState()
            self.current_screen = "splash"
            self.message = ""
            self.character_name = ""
            self.character_class = ""
    
    @callback("DungeonCrawler", Keys.D)
    def on_dungeon(self, *args, **kwargs):
        if self.current_screen == "town":
            self.current_screen = "dungeon_entrance"
    
    @callback("DungeonCrawler", Keys.I)
    def on_inventory(self, *args, **kwargs):
        if self.current_screen == "town":
            self.current_screen = "inventory"
    
    @callback("DungeonCrawler", Keys.A)
    def on_attack(self, *args, **kwargs):
        if self.current_screen == "combat" and self.game_state.current_monster:
            # Player attacks
            monster_died = self.game_state.combat.player_attack(
                self.game_state.player, 
                self.game_state.current_monster
            )
            
            if monster_died:
                self.current_screen = "town" if self.game_state.current_floor < 5 else "victory"
                if self.game_state.current_floor < 5:
                    self.game_state.current_floor += 1
                    self.game_state.return_to_town()
                else:
                    self.game_state.victory = True
                    self.current_screen = "victory"
            else:
                # Monster attacks back
                player_died = self.game_state.combat.monster_attack(
                    self.game_state.current_monster, 
                    self.game_state.player
                )
                if player_died:
                    self.current_screen = "game_over"
    
    @callback("DungeonCrawler", Keys.B)
    def on_back(self, *args, **kwargs):
        if self.current_screen in ["shop", "inventory"]:
            self.current_screen = "town"
            self.game_state.in_shop = False
        elif self.current_screen == "dungeon_entrance":
            self.current_screen = "town"
    
    @callback("DungeonCrawler", Keys.Q)
    def on_quit(self, *args, **kwargs):
        if self.current_screen in ["town", "shop", "inventory"] and self.game_state.player:
            save_game(self.game_state.player, self.game_state.current_floor)
            self.message = "Game saved!"
        
        if self.current_screen in ["splash", "victory", "game_over"]:
            self.logic.should_stop = True
        else:
            self.current_screen = "splash"
    
    # Handle text input for character creation
    def handle_text_input(self, key):
        """Handle text input for various screens"""
        if self.waiting_for_input:
            if key == Keys.BACKSPACE:
                if self.input_buffer:
                    self.input_buffer = self.input_buffer[:-1]
            elif key == Keys.ENTER:
                # This will be handled by the ENTER callback
                pass
            elif len(key) == 1 and key.isprintable():
                self.input_buffer += key
    
    # Add callbacks for text input
    @callback("DungeonCrawler", Keys.BACKSPACE)
    def on_backspace(self, *args, **kwargs):
        self.handle_text_input(Keys.BACKSPACE)
    
    # Add callbacks for letter keys for text input
    for i in range(26):
        letter = chr(ord('A') + i)
        locals()[f'on_{letter.lower()}'] = callback("DungeonCrawler", getattr(Keys, letter))(
            lambda self, *args, letter=letter, **kwargs: self.handle_text_input(letter.lower()) if self.waiting_for_input else None
        )
    
    # Add callbacks for number keys
    for i in range(10):
        locals()[f'on_{i}'] = callback("DungeonCrawler", getattr(Keys, f'_{i}'))(
            lambda self, *args, num=str(i), **kwargs: self.handle_text_input(num) if self.waiting_for_input else None
        )


if __name__ == "__main__":
    app = App(
        name="Dungeon Crawler RPG",
        title="Epic Terminal RPG Adventure",
        splash_screen=False,
        demo_mode=False,
        
        show_footer=False,
        show_header=True,
        show_messages=False,
        show_menu=False,
        show_banner=False,
        show_box=True,
        
        disable_footer=True,
        disable_header=False,
        disable_menu=True,
        disable_messages=True,
        
        modules=[DungeonCrawlerRPG]
    )