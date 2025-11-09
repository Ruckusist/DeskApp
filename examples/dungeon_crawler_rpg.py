#!/usr/bin/env python3
"""
Dungeon Crawler RPG - Main Launcher
Epic RPG adventure game built with the DeskApp framework.

Features:
- 3 Character Classes: Fighter, Wizard, Rogue
- Turn-based Combat with ASCII Art Monsters
- Equipment System (Weapons, Armor, Shields)
- Magic System with Spells
- Town with Shop and Inn
- 5 Dungeon Floors with Boss Battles
- Persistent Save/Load System
- Epic Storyline with Victory/Defeat Endings

Controls:
- Navigate with keyboard shortcuts shown on each screen
- Enter your name and choose a class to begin
- Use S-Shop, R-Rest, D-Dungeon, I-Inventory in town
- Combat: A-Attack, M-Magic, I-Item, R-Run
- Q-Quit and auto-save at any time
"""
import random
import copy
import json
import os
import sys
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Add the parent directories to sys.path to import deskapp
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import deskapp
from deskapp import App, Module, callback, Keys


# =============================================================================
# GAME DATA STRUCTURES
# =============================================================================

class PlayerClass(Enum):
    FIGHTER = "Fighter"
    WIZARD = "Wizard"
    ROGUE = "Rogue"


class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    CONSUMABLE = "consumable"


class Spell:
    def __init__(self, name: str, mp_cost: int, damage: int, description: str):
        self.name = name
        self.mp_cost = mp_cost
        self.damage = damage
        self.description = description


class Item:
    def __init__(self, name: str, item_type: ItemType, value: int, 
                 damage: int = 0, defense: int = 0, description: str = ""):
        self.name = name
        self.type = item_type
        self.value = value
        self.damage = damage
        self.defense = defense
        self.description = description


class Player:
    def __init__(self, name: str, player_class: PlayerClass):
        self.name = name
        self.player_class = player_class
        self.level = 1
        self.experience = 0
        self.gold = 100
        
        # Base stats depend on class
        if player_class == PlayerClass.FIGHTER:
            self.max_hp = 120
            self.max_mp = 30
            self.base_attack = 15
            self.base_defense = 10
        elif player_class == PlayerClass.WIZARD:
            self.max_hp = 70
            self.max_mp = 100
            self.base_attack = 8
            self.base_defense = 5
        else:  # ROGUE
            self.max_hp = 90
            self.max_mp = 50
            self.base_attack = 12
            self.base_defense = 7
            
        self.hp = self.max_hp
        self.mp = self.max_mp
        
        # Equipment
        self.weapon: Optional[Item] = None
        self.armor: Optional[Item] = None
        self.shield: Optional[Item] = None
        self.inventory: List[Item] = []
        
        # Spells known
        self.spells: List[Spell] = []
        if player_class == PlayerClass.WIZARD:
            self.spells.append(Spell("Magic Missile", 5, 12, "Basic magic attack"))
        elif player_class == PlayerClass.ROGUE:
            self.spells.append(Spell("Heal", 8, -15, "Restore health"))
    
    @property
    def total_attack(self) -> int:
        weapon_damage = self.weapon.damage if self.weapon else 0
        return self.base_attack + weapon_damage + (self.level * 2)
    
    @property
    def total_defense(self) -> int:
        armor_def = self.armor.defense if self.armor else 0
        shield_def = self.shield.defense if self.shield else 0
        return self.base_defense + armor_def + shield_def + self.level
    
    def gain_experience(self, exp: int):
        self.experience += exp
        exp_needed = self.level * 100
        if self.experience >= exp_needed:
            self.level_up()
    
    def level_up(self):
        old_level = self.level
        self.level += 1
        self.experience = 0
        
        # Increase stats
        hp_gain = random.randint(8, 15)
        mp_gain = random.randint(3, 8)
        self.max_hp += hp_gain
        self.max_mp += mp_gain
        self.hp = self.max_hp  # Full heal on level up
        self.mp = self.max_mp
        
        return f"Level up! Now level {self.level}. HP+{hp_gain}, MP+{mp_gain}"
    
    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)
    
    def restore_mp(self, amount: int):
        self.mp = min(self.max_mp, self.mp + amount)
    
    def can_cast_spell(self, spell: Spell) -> bool:
        return self.mp >= spell.mp_cost and spell in self.spells
    
    def cast_spell(self, spell: Spell) -> int:
        if self.can_cast_spell(spell):
            self.mp -= spell.mp_cost
            if spell.damage < 0:  # Healing spell
                self.heal(-spell.damage)
                return -spell.damage
            return spell.damage + random.randint(-2, 3)
        return 0


class Monster:
    def __init__(self, name: str, hp: int, attack: int, defense: int, 
                 exp_reward: int, gold_reward: int, ascii_art: str, 
                 is_boss: bool = False, special_attack: str = ""):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.ascii_art = ascii_art
        self.is_boss = is_boss
        self.special_attack = special_attack
    
    def take_damage(self, damage: int) -> int:
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        return actual_damage
    
    def is_alive(self) -> bool:
        return self.hp > 0
    
    def attack_player(self) -> int:
        base_damage = self.attack + random.randint(-3, 3)
        
        # Boss special attacks
        if self.is_boss and random.randint(1, 4) == 1 and self.special_attack:
            return int(base_damage * 1.5)  # 50% more damage for special attack
        
        return max(1, base_damage)


# =============================================================================
# GAME DATA
# =============================================================================

MONSTERS = {
    "goblin": Monster("Goblin", 25, 8, 2, 15, 5, """
    ╭─────╮
    │ ◉ ◉ │
    │  ▽  │
    ╰─┬─┬─╯
      │ │
    """, False),
    
    "orc": Monster("Orc", 45, 12, 4, 25, 12, """
    ╔═════╗
    ║ ● ● ║
    ║  ∩  ║
    ║ ═══ ║
    ╚═┬═┬═╝
      ║ ║
    """, False),
    
    "demon": Monster("Demon", 80, 18, 6, 50, 25, """
    ╔═══════╗
    ║ ◄► ◄► ║
    ║   ♦   ║
    ║ ═════ ║
    ╚═══┬═══╝
        ║
      ▓▓▓▓▓
    """, False),
    
    "boss_orc_king": Monster("Orc King", 150, 25, 8, 100, 50, """
    ╔═══════════╗
    ║  ▲   ▲   ║
    ║ ◆ ● ● ◆  ║
    ║    ∩     ║
    ║  ═════   ║
    ╚═════┬═════╝
          ║
        ♔♔♔♔♔
    """, True, "Berserker Rage"),
    
    "boss_demon_lord": Monster("Demon Lord", 200, 30, 10, 150, 75, """
    ╔═══════════════╗
    ║ ♠ ◄► ◄► ♠   ║
    ║     ♦       ║
    ║   ═══════   ║
    ║  ▓▓▓▓▓▓▓   ║
    ╚═════┬═══════╝
          ║
      ☠☠☠☠☠☠☠
    """, True, "Hellfire Blast")
}

ITEMS = {
    "rusty_sword": Item("Rusty Sword", ItemType.WEAPON, 20, 5, 0, "A worn but sharp blade"),
    "iron_sword": Item("Iron Sword", ItemType.WEAPON, 75, 12, 0, "A sturdy iron weapon"),
    "steel_sword": Item("Steel Sword", ItemType.WEAPON, 150, 20, 0, "A gleaming steel blade"),
    
    "leather_armor": Item("Leather Armor", ItemType.ARMOR, 30, 0, 3, "Basic protection"),
    "chain_mail": Item("Chain Mail", ItemType.ARMOR, 100, 0, 8, "Interlocked metal rings"),
    "plate_armor": Item("Plate Armor", ItemType.ARMOR, 200, 0, 15, "Heavy metal protection"),
    
    "wooden_shield": Item("Wooden Shield", ItemType.SHIELD, 25, 0, 2, "Simple wood construction"),
    "iron_shield": Item("Iron Shield", ItemType.SHIELD, 60, 0, 5, "Reinforced with iron bands"),
    
    "healing_potion": Item("Healing Potion", ItemType.CONSUMABLE, 25, 0, 0, "Restores 30 HP"),
    "mana_potion": Item("Mana Potion", ItemType.CONSUMABLE, 35, 0, 0, "Restores 20 MP"),
}

SPELLS = {
    "heal": Spell("Heal", 8, -15, "Restore health"),
    "magic_missile": Spell("Magic Missile", 5, 12, "Basic magic attack"),
    "fireball": Spell("Fireball", 12, 20, "Explosive fire magic"),
}


def save_game(player: Player, current_floor: int, filename: str = "rpg_save.json"):
    """Save game state to JSON file"""
    save_data = {
        "player_name": player.name,
        "player_class": player.player_class.value,
        "level": player.level,
        "experience": player.experience,
        "hp": player.hp,
        "mp": player.mp,
        "max_hp": player.max_hp,
        "max_mp": player.max_mp,
        "gold": player.gold,
        "current_floor": current_floor,
        "weapon": player.weapon.name if player.weapon else None,
        "armor": player.armor.name if player.armor else None,
        "shield": player.shield.name if player.shield else None,
        "inventory": [item.name for item in player.inventory],
        "spells": [spell.name for spell in player.spells],
    }
    
    with open(filename, 'w') as f:
        json.dump(save_data, f, indent=2)


def load_game(filename: str = "rpg_save.json") -> tuple:
    """Load game state from JSON file"""
    try:
        with open(filename, 'r') as f:
            save_data = json.load(f)
        
        # Recreate player
        player_class = PlayerClass(save_data["player_class"])
        player = Player(save_data["player_name"], player_class)
        
        # Restore stats
        player.level = save_data["level"]
        player.experience = save_data["experience"]
        player.hp = save_data["hp"]
        player.mp = save_data["mp"]
        player.max_hp = save_data["max_hp"]
        player.max_mp = save_data["max_mp"]
        player.gold = save_data["gold"]
        
        # Restore equipment
        if save_data["weapon"]:
            player.weapon = ITEMS[save_data["weapon"]]
        if save_data["armor"]:
            player.armor = ITEMS[save_data["armor"]]
        if save_data["shield"]:
            player.shield = ITEMS[save_data["shield"]]
            
        # Restore inventory
        player.inventory = [ITEMS[item_name] for item_name in save_data["inventory"]]
        
        # Restore spells
        player.spells = [SPELLS[spell_name] for spell_name in save_data["spells"]]
        
        return player, save_data["current_floor"]
    
    except FileNotFoundError:
        return None, 0


# =============================================================================
# ASCII ART AND UI
# =============================================================================

SPLASH_SCREEN = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗        ║
║     ██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║        ║
║     ██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║        ║
║     ██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║        ║
║     ██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║        ║
║     ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝        ║
║                                                                               ║
║               ██████╗ ██████╗  █████╗ ██╗    ██╗██╗     ███████╗██████╗     ║
║              ██╔════╝ ██╔══██╗██╔══██╗██║    ██║██║     ██╔════╝██╔══██╗    ║
║              ██║      ██████╔╝███████║██║ █╗ ██║██║     █████╗  ██████╔╝    ║
║              ██║      ██╔══██╗██╔══██║██║███╗██║██║     ██╔══╝  ██╔══██╗    ║
║              ╚██████╗ ██║  ██║██║  ██║╚███╔███╔╝███████╗███████╗██║  ██║    ║
║               ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝  ╚═╝    ║
║                                                                               ║
║                          ⚔️  A Terminal RPG Adventure ⚔️                       ║
║                                                                               ║
║                         Press ENTER to begin your quest...                   ║
║                         Press L to load a saved game...                      ║
║                         Press Q to quit...                                   ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

CHARACTER_CREATION = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                          CHARACTER CREATION                                   ║
║                                                                               ║
║  Choose your class, brave adventurer:                                        ║
║                                                                               ║
║  1. FIGHTER - Master of combat and warfare                                   ║
║     ⚔️  High HP and Attack                                                    ║
║     🛡️  Strong Defense                                                        ║
║     ❤️  HP: 120  MP: 30  ATK: 15  DEF: 10                                    ║
║                                                                               ║
║  2. WIZARD - Wielder of arcane mysteries                                     ║
║     🔮 High MP and Spell Damage                                              ║
║     ⚡ Powerful Magic Attacks                                                ║
║     ❤️  HP: 70   MP: 100 ATK: 8   DEF: 5                                     ║
║                                                                               ║
║  3. ROGUE - Swift and cunning                                                ║
║     🗡️  Balanced stats                                                        ║
║     💚 Healing abilities                                                      ║
║     ❤️  HP: 90   MP: 50  ATK: 12  DEF: 7                                     ║
║                                                                               ║
║  Enter your choice (1, 2, or 3):                                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

TOWN_SPLASH = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              HAVEN TOWN                                      ║
║                        ⛪ The Last Safe Haven ⛪                             ║
║                                                                               ║
║     🏠     🏪      🏛️      ⚒️                                                   ║
║    House   Shop   Temple  Forge                                              ║
║                                                                               ║
║  Welcome, traveler! What would you like to do?                              ║
║                                                                               ║
║  S - Visit the SHOP to buy equipment and items                              ║
║  R - REST at the inn to restore HP/MP                                       ║
║  D - Enter the DUNGEON to face monsters                                     ║
║  I - View your INVENTORY and status                                         ║
║  Q - QUIT and save your progress                                            ║
║                                                                               ║
║  The dungeon grows darker with each floor...                                ║
║  Are you prepared for the challenges ahead?                                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

STORY_INTRO = """
Long ago, the kingdom of Aethermoor was a land of peace and prosperity.
But darkness crept in from the depths of the earth - an ancient evil
that corrupted all it touched.

The great heroes of old descended into the cursed dungeon to face
this evil, but none returned. Now the monsters grow bolder, venturing
closer to the last safe haven: the town of Haven.

You are the kingdom's last hope. Will you succeed where the heroes
of legend have failed? Will you cleanse the dungeon and restore
peace to the land?

Your quest begins in Haven Town. Prepare yourself well, for the
dangers ahead test both courage and cunning...
"""


# =============================================================================
# GAME SYSTEMS
# =============================================================================

class CombatSystem:
    def __init__(self):
        self.combat_log = []
        
    def clear_log(self):
        self.combat_log = []
        
    def add_log(self, message: str):
        self.combat_log.append(message)
        if len(self.combat_log) > 8:  # Keep only last 8 messages
            self.combat_log.pop(0)
    
    def player_attack(self, player: Player, monster: Monster) -> bool:
        """Player attacks monster. Returns True if monster dies."""
        damage = player.total_attack + random.randint(-2, 4)
        actual_damage = monster.take_damage(damage)
        
        self.add_log(f"You attack {monster.name} for {actual_damage} damage!")
        
        if not monster.is_alive():
            self.add_log(f"{monster.name} is defeated!")
            exp_gained = monster.exp_reward
            gold_gained = monster.gold_reward
            
            player.gain_experience(exp_gained)
            player.gold += gold_gained
            
            self.add_log(f"You gain {exp_gained} EXP and {gold_gained} gold!")
            
            # Check for level up
            if player.experience >= player.level * 100:
                level_msg = player.level_up()
                self.add_log(level_msg)
            
            return True
        return False
    
    def monster_attack(self, monster: Monster, player: Player) -> bool:
        """Monster attacks player. Returns True if player dies."""
        damage = monster.attack_player()
        
        # Special attack message for bosses
        if monster.is_boss and damage > monster.attack and monster.special_attack:
            self.add_log(f"{monster.name} uses {monster.special_attack}!")
        
        actual_damage = max(1, damage - player.total_defense)
        player.hp -= actual_damage
        
        self.add_log(f"{monster.name} attacks you for {actual_damage} damage!")
        
        if player.hp <= 0:
            player.hp = 0
            self.add_log("You have been defeated!")
            return True
        return False


class GameState:
    """Manages the overall game state and flow."""
    
    def __init__(self):
        self.player: Optional[Player] = None
        self.current_floor = 1
        self.current_monster: Optional[Monster] = None
        self.in_combat = False
        self.in_town = True
        self.in_shop = False
        self.game_over = False
        self.victory = False
        
        # Systems
        self.combat = CombatSystem()
    
    def create_player(self, name: str, player_class: str) -> Player:
        """Create a new player character."""
        class_map = {
            "1": PlayerClass.FIGHTER,
            "2": PlayerClass.WIZARD,
            "3": PlayerClass.ROGUE
        }
        
        self.player = Player(name, class_map[player_class])
        return self.player
    
    def generate_monster_for_floor(self, floor: int) -> Monster:
        """Generate a monster appropriate for the given floor."""
        if floor == 3:  # Boss floor
            boss = copy.deepcopy(MONSTERS["boss_orc_king"])
            # Scale boss based on progress
            boss.hp = boss.max_hp = int(boss.max_hp * (1 + floor * 0.1))
            boss.attack = int(boss.attack * (1 + floor * 0.1))
            return boss
        elif floor == 5:  # Final boss
            boss = copy.deepcopy(MONSTERS["boss_demon_lord"])
            boss.hp = boss.max_hp = int(boss.max_hp * (1 + floor * 0.1))
            boss.attack = int(boss.attack * (1 + floor * 0.1))
            return boss
        else:
            # Regular monsters based on floor
            if floor <= 1:
                monster_types = ["goblin"]
            elif floor <= 2:
                monster_types = ["goblin", "orc"]
            else:
                monster_types = ["orc", "demon"]
                
            monster_name = random.choice(monster_types)
            monster = copy.deepcopy(MONSTERS[monster_name])
            
            # Scale monster stats based on floor
            scale_factor = 1 + (floor - 1) * 0.2
            monster.hp = monster.max_hp = int(monster.hp * scale_factor)
            monster.attack = int(monster.attack * scale_factor)
            monster.exp_reward = int(monster.exp_reward * scale_factor)
            monster.gold_reward = int(monster.gold_reward * scale_factor)
            
            return monster
    
    def enter_dungeon_floor(self, floor: int):
        """Enter a specific dungeon floor."""
        self.current_floor = floor
        self.current_monster = self.generate_monster_for_floor(floor)
        self.in_town = False
        self.in_combat = True
        self.combat.clear_log()
        
        if floor in [3, 5]:  # Boss floors
            if floor == 3:
                self.combat.add_log("The ground trembles as a massive figure emerges...")
                self.combat.add_log("\"HUMAN! You dare enter MY domain? I am GRAX THE ORC KING!\"")
                self.combat.add_log("\"Your bones will join the countless others!\"")
                self.combat.add_log("PREPARE FOR BATTLE!")
            else:
                self.combat.add_log("The air grows cold as reality bends...")
                self.combat.add_log("\"Foolish mortal... I am MALTHARION, LORD OF THE ABYSS!\"")
                self.combat.add_log("\"Your soul will fuel my power for eternity!\"")
                self.combat.add_log("THE FINAL BATTLE BEGINS!")
    
    def return_to_town(self):
        """Return to town."""
        self.in_town = True
        self.in_combat = False
        self.in_shop = False
        self.current_monster = None
    
    def rest_at_inn(self) -> str:
        """Rest at the inn to restore HP/MP."""
        if self.player.hp == self.player.max_hp and self.player.mp == self.player.max_mp:
            return "You are already fully rested!"
        
        inn_cost = 10 + (self.current_floor * 5)
        if self.player.gold < inn_cost:
            return f"You need {inn_cost} gold to rest at the inn!"
        
        self.player.gold -= inn_cost
        self.player.hp = self.player.max_hp
        self.player.mp = self.player.max_mp
        
        return f"You rest at the inn for {inn_cost} gold. HP and MP fully restored!"


# =============================================================================
# MAIN GAME MODULE
# =============================================================================

class DungeonCrawlerRPG(Module):
    name = "Dungeon Crawler RPG"
    
    def __init__(self, app):
        super().__init__(app, "DungeonCrawler")
        self.game_state = GameState()
        self.current_screen = "splash"
        self.message = ""
        self.input_buffer = ""
        self.waiting_for_input = False
        self.input_prompt = ""
        
        # Character creation state
        self.character_name = ""
        self.character_class = ""
        
        # Shop items
        self.shop_items = [
            ITEMS["rusty_sword"], ITEMS["iron_sword"], ITEMS["steel_sword"],
            ITEMS["leather_armor"], ITEMS["chain_mail"], ITEMS["plate_armor"],
            ITEMS["wooden_shield"], ITEMS["iron_shield"],
            ITEMS["healing_potion"], ITEMS["mana_potion"]
        ]
    
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
        self.write(panel, 0, 2, "GRELDORN'S SHOP - Finest Goods in Haven")
        self.write(panel, 1, 2, "=" * 50)
        self.write(panel, 3, 2, f"Your gold: {self.game_state.player.gold}")
        self.write(panel, 5, 2, "AVAILABLE ITEMS:")
        
        for i, item in enumerate(self.shop_items):
            if i + 6 < self.h - 5:
                affordable = "✓" if self.game_state.player.gold >= item.value else "✗"
                self.write(panel, i + 6, 2, f"{i+1:2d}. {item.name:<20} - {item.value:>3} gold {affordable}")
                self.write(panel, i + 6, 70, f"{item.description[:20]}")
        
        self.write(panel, self.h - 4, 2, "Commands: Type number to buy, B to go back")
    
    def render_dungeon_entrance(self, panel):
        """Render dungeon entrance"""
        self.write(panel, 2, 2, "THE CURSED DUNGEON")
        self.write(panel, 3, 2, f"Floor {self.game_state.current_floor}")
        self.write(panel, 5, 2, "The darkness grows deeper with each floor...")
        
        floor_descriptions = [
            "The Upper Catacombs - Ancient burial chambers",
            "The Goblin Warrens - Twisting tunnels", 
            "The Orcish Stronghold - BOSS: Orc King awaits",
            "The Demon's Gate - Where reality grows thin",
            "The Abyssal Throne - FINAL BOSS: Demon Lord"
        ]
        
        if self.game_state.current_floor <= len(floor_descriptions):
            desc = floor_descriptions[self.game_state.current_floor - 1]
            self.write(panel, 7, 2, desc)
        
        self.write(panel, self.h - 5, 2, "Press ENTER to explore this floor")
        self.write(panel, self.h - 4, 2, "Press B to return to town")
    
    def render_combat(self, panel):
        """Render combat screen"""
        if not self.game_state.current_monster:
            return
        
        monster = self.game_state.current_monster
        player = self.game_state.player
        
        # Combat header
        self.write(panel, 0, 2, f"COMBAT - Floor {self.game_state.current_floor}")
        self.write(panel, 1, 2, "=" * 50)
        
        self.write(panel, 2, 2, f"{monster.name:<25} HP: {monster.hp:>3}/{monster.max_hp}")
        self.write(panel, 2, 50, f"{player.name:<15} Lv.{player.level}")
        
        self.write(panel, 3, 50, f"HP: {player.hp:>3}/{player.max_hp}  MP: {player.mp:>3}/{player.max_mp}")
        
        # Monster ASCII art
        art_lines = monster.ascii_art.strip().split('\n')
        for i, line in enumerate(art_lines):
            if i + 5 < self.h - 12:
                self.write(panel, i + 5, 5, line)
        
        # Combat log
        log_start_y = 5 + len(art_lines) + 1
        self.write(panel, log_start_y, 2, "Combat Log:")
        for i, log_entry in enumerate(self.game_state.combat.combat_log[-6:]):
            if log_start_y + 1 + i < self.h - 6:
                self.write(panel, log_start_y + 1 + i, 2, f"  {log_entry}")
        
        # Combat options
        self.write(panel, self.h - 4, 2, "Actions: A-Attack | M-Magic | I-Item | R-Run")
    
    def render_inventory(self, panel):
        """Render inventory/status screen"""
        if not self.game_state.player:
            return
        
        player = self.game_state.player
        
        self.write(panel, 0, 2, "ADVENTURER STATUS")
        self.write(panel, 1, 2, "=" * 50)
        
        self.write(panel, 3, 2, f"Name: {player.name:<20} Class: {player.player_class.value}")
        self.write(panel, 4, 2, f"Level: {player.level:<19} Experience: {player.experience}/{player.level * 100}")
        self.write(panel, 5, 2, f"HP: {player.hp}/{player.max_hp:<25} MP: {player.mp}/{player.max_mp}")
        self.write(panel, 6, 2, f"Attack: {player.total_attack:<18} Defense: {player.total_defense:<10} Gold: {player.gold}")
        
        self.write(panel, 8, 2, "EQUIPMENT")
        self.write(panel, 9, 2, f"Weapon: {(player.weapon.name if player.weapon else 'None'):<25} Damage: {(player.weapon.damage if player.weapon else 0)}")
        self.write(panel, 10, 2, f"Armor:  {(player.armor.name if player.armor else 'None'):<25} Defense: {(player.armor.defense if player.armor else 0)}")
        self.write(panel, 11, 2, f"Shield: {(player.shield.name if player.shield else 'None'):<25} Defense: {(player.shield.defense if player.shield else 0)}")
        
        self.write(panel, 13, 2, "INVENTORY")
        if player.inventory:
            for i, item in enumerate(player.inventory):
                if 14 + i < self.h - 5:
                    self.write(panel, 14 + i, 2, f"{i+1}. {item.name} - {item.description}")
        else:
            self.write(panel, 14, 2, "No items in inventory")
        
        # Show spells
        spells_y = self.h - 4
        if player.spells:
            self.write(panel, spells_y - 1, 2, "SPELLS")
            for i, spell in enumerate(player.spells):
                if spells_y + i < self.h - 2:
                    self.write(panel, spells_y + i, 2, f"{spell.name} (MP: {spell.mp_cost}) - {spell.description}")
        
        self.write(panel, self.h - 2, 2, "Press B to go back")
    
    def render_victory(self, panel):
        """Render victory screen"""
        self.write(panel, 2, 20, "VICTORY!")
        self.write(panel, 3, 15, "Monster Defeated!")
        
        victory_text = """
THE DEMON LORD HAS FALLEN!

With Maltharion's defeat, his dark magic unravels. The cursed dungeon
begins to crumble as centuries of evil are purged from its depths.
You emerge into the sunlight as birds sing and flowers bloom.

Haven Town erupts in celebration! You have saved not just the town,
but the entire kingdom. Bards will sing of your heroic deeds for
generations to come.

CONGRATULATIONS, HERO! YOU HAVE COMPLETED YOUR QUEST!
        """
        
        lines = victory_text.strip().split('\n')
        for i, line in enumerate(lines):
            if i + 5 < self.h - 3:
                self.write(panel, i + 5, 2, line[:self.w-4])
        
        self.write(panel, self.h - 3, 2, "Press Q to quit or R to restart")
    
    def render_game_over(self, panel):
        """Render game over screen"""
        self.write(panel, 2, 20, "DEFEAT!")
        self.write(panel, 3, 12, "You have fallen...")
        
        defeat_text = """
Your legend will be remembered in Haven Town...

Though you fell in the cursed dungeon, your bravery inspired others.
The merchants speak of your courage, the children sing songs of your
adventures, and somewhere, another hero prepares to take up your quest.

The darkness may have claimed you, but it has not won. Light endures
in the hearts of the brave, and your sacrifice was not in vain.

THANK YOU FOR PLAYING DUNGEON CRAWLER!
        """
        
        lines = defeat_text.strip().split('\n')
        for i, line in enumerate(lines):
            if i + 5 < self.h - 3:
                self.write(panel, i + 5, 2, line[:self.w-4])
        
        self.write(panel, self.h - 3, 2, "Press Q to quit or R to restart")
    
    # Event handlers
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
    def on_shop(self, *args, **kwargs):
        if self.current_screen == "town":
            self.current_screen = "shop"
    
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
                player_died = self.game_state.combat.monster_attack(
                    self.game_state.current_monster, 
                    self.game_state.player
                )
                if player_died:
                    self.current_screen = "game_over"
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
                if self.game_state.current_floor < 5:
                    self.game_state.current_floor += 1
                    self.game_state.return_to_town()
                    self.current_screen = "town"
                    self.message = f"Floor {self.game_state.current_floor - 1} cleared! Advancing to floor {self.game_state.current_floor}."
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
    @callback("DungeonCrawler", Keys.BACKSPACE)
    def on_backspace(self, *args, **kwargs):
        if self.waiting_for_input and self.input_buffer:
            self.input_buffer = self.input_buffer[:-1]
    
    # Handle shop purchases
    def handle_number_input(self, num: str):
        """Handle number input for shop purchases"""
        if self.current_screen == "shop":
            try:
                item_index = int(num) - 1
                if 0 <= item_index < len(self.shop_items):
                    item = self.shop_items[item_index]
                    if self.game_state.player.gold >= item.value:
                        self.game_state.player.gold -= item.value
                        
                        # Equipment items are equipped immediately if slot is empty
                        if item.type == ItemType.WEAPON:
                            if self.game_state.player.weapon is None:
                                self.game_state.player.weapon = item
                                self.message = f"Bought and equipped {item.name}!"
                            else:
                                self.game_state.player.inventory.append(item)
                                self.message = f"Bought {item.name}!"
                        
                        elif item.type == ItemType.ARMOR:
                            if self.game_state.player.armor is None:
                                self.game_state.player.armor = item
                                self.message = f"Bought and equipped {item.name}!"
                            else:
                                self.game_state.player.inventory.append(item)
                                self.message = f"Bought {item.name}!"
                        
                        elif item.type == ItemType.SHIELD:
                            if self.game_state.player.shield is None:
                                self.game_state.player.shield = item
                                self.message = f"Bought and equipped {item.name}!"
                            else:
                                self.game_state.player.inventory.append(item)
                                self.message = f"Bought {item.name}!"
                        
                        else:  # Consumables
                            self.game_state.player.inventory.append(item)
                            self.message = f"Bought {item.name}!"
                    else:
                        self.message = f"You cannot afford {item.name}!"
                else:
                    self.message = "Invalid item number!"
            except ValueError:
                pass
        elif self.waiting_for_input:
            self.input_buffer += num
    
    # Number key handlers
    @callback("DungeonCrawler", Keys.NUM1)
    def on_1(self, *args, **kwargs):
        self.handle_number_input("1")
    
    @callback("DungeonCrawler", Keys.NUM2)
    def on_2(self, *args, **kwargs):
        self.handle_number_input("2")
    
    @callback("DungeonCrawler", Keys.NUM3)
    def on_3(self, *args, **kwargs):
        self.handle_number_input("3")
    
    @callback("DungeonCrawler", Keys.NUM4)
    def on_4(self, *args, **kwargs):
        self.handle_number_input("4")
        
    @callback("DungeonCrawler", Keys.NUM5)
    def on_5(self, *args, **kwargs):
        self.handle_number_input("5")
    
    @callback("DungeonCrawler", Keys.NUM6)
    def on_6(self, *args, **kwargs):
        self.handle_number_input("6")
    
    @callback("DungeonCrawler", Keys.NUM7)
    def on_7(self, *args, **kwargs):
        self.handle_number_input("7")
    
    @callback("DungeonCrawler", Keys.NUM8)
    def on_8(self, *args, **kwargs):
        self.handle_number_input("8")
    
    @callback("DungeonCrawler", Keys.NUM9)
    def on_9(self, *args, **kwargs):
        self.handle_number_input("9")
    
    # Letter input for character creation
    def handle_letter_input(self, letter: str):
        if self.waiting_for_input:
            self.input_buffer += letter.lower()
    
    # Letter key handlers (just a few for name input)
    @callback("DungeonCrawler", Keys.A)
    def on_a_key(self, *args, **kwargs):
        if not self.waiting_for_input:
            self.on_attack()
        else:
            self.handle_letter_input("a")
    
    # Add more letter handlers as needed for name input
    for letter in "BCDEFGHIJKLMNOPQRSTUVWXYZ":
        locals()[f'on_{letter.lower()}_key'] = callback("DungeonCrawler", getattr(Keys, letter))(
            lambda self, *args, l=letter.lower(), **kwargs: self.handle_letter_input(l) if self.waiting_for_input else None
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