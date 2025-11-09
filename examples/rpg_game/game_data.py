"""
RPG Game Data Structures
Core classes for the dungeon crawler RPG game.
"""
import random
import json
from typing import Dict, List, Optional
from enum import Enum


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


# Game data
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
    "magic_sword": Item("Enchanted Sword", ItemType.WEAPON, 300, 30, 0, "Crackling with magical energy"),
    
    "leather_armor": Item("Leather Armor", ItemType.ARMOR, 30, 0, 3, "Basic protection"),
    "chain_mail": Item("Chain Mail", ItemType.ARMOR, 100, 0, 8, "Interlocked metal rings"),
    "plate_armor": Item("Plate Armor", ItemType.ARMOR, 200, 0, 15, "Heavy metal protection"),
    
    "wooden_shield": Item("Wooden Shield", ItemType.SHIELD, 25, 0, 2, "Simple wood construction"),
    "iron_shield": Item("Iron Shield", ItemType.SHIELD, 60, 0, 5, "Reinforced with iron bands"),
    "magic_shield": Item("Magic Shield", ItemType.SHIELD, 150, 0, 12, "Shimmers with protective magic"),
    
    "healing_potion": Item("Healing Potion", ItemType.CONSUMABLE, 25, 0, 0, "Restores 30 HP"),
    "mana_potion": Item("Mana Potion", ItemType.CONSUMABLE, 35, 0, 0, "Restores 20 MP"),
}

SPELLS = {
    "heal": Spell("Heal", 8, -15, "Restore health"),
    "magic_missile": Spell("Magic Missile", 5, 12, "Basic magic attack"),
    "fireball": Spell("Fireball", 12, 20, "Explosive fire magic"),
    "lightning": Spell("Lightning Bolt", 15, 25, "Electric devastation"),
    "ice_shard": Spell("Ice Shard", 10, 18, "Freezing projectile"),
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