"""
Game Mechanics for RPG
Combat system, dungeon generation, and core game logic.
"""
import random
import copy
from typing import List, Tuple, Optional
from .game_data import Player, Monster, Item, Spell, MONSTERS, ITEMS, SPELLS, ItemType


class CombatSystem:
    def __init__(self):
        self.combat_log = []
        
    def clear_log(self):
        self.combat_log = []
        
    def add_log(self, message: str):
        self.combat_log.append(message)
        if len(self.combat_log) > 10:  # Keep only last 10 messages
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
            
            level_msg = player.level_up() if player.experience >= player.level * 100 else None
            if level_msg:
                self.add_log(level_msg)
            
            return True
        return False
    
    def player_cast_spell(self, player: Player, spell: Spell, monster: Monster) -> bool:
        """Player casts spell. Returns True if monster dies."""
        if not player.can_cast_spell(spell):
            self.add_log(f"Not enough MP to cast {spell.name}!")
            return False
            
        spell_damage = player.cast_spell(spell)
        
        if spell.damage < 0:  # Healing spell
            self.add_log(f"You cast {spell.name} and heal for {spell_damage} HP!")
        else:
            actual_damage = monster.take_damage(spell_damage)
            self.add_log(f"You cast {spell.name} on {monster.name} for {actual_damage} damage!")
            
            if not monster.is_alive():
                self.add_log(f"{monster.name} is defeated by your magic!")
                exp_gained = monster.exp_reward
                gold_gained = monster.gold_reward
                
                player.gain_experience(exp_gained)
                player.gold += gold_gained
                
                self.add_log(f"You gain {exp_gained} EXP and {gold_gained} gold!")
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
    
    def use_item(self, player: Player, item: Item) -> str:
        """Use a consumable item. Returns result message."""
        if item.type != ItemType.CONSUMABLE:
            return "This item cannot be used!"
            
        if item.name == "Healing Potion":
            old_hp = player.hp
            player.heal(30)
            healed = player.hp - old_hp
            player.inventory.remove(item)
            return f"Used {item.name}! Restored {healed} HP."
            
        elif item.name == "Mana Potion":
            old_mp = player.mp
            player.restore_mp(20)
            restored = player.mp - old_mp
            player.inventory.remove(item)
            return f"Used {item.name}! Restored {restored} MP."
            
        return "Unknown item effect!"


class DungeonSystem:
    def __init__(self):
        self.floors_completed = 0
        
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
    
    def get_floor_description(self, floor: int) -> str:
        """Get the description for a specific floor."""
        from .art_assets import FLOOR_DESCRIPTIONS
        if floor <= len(FLOOR_DESCRIPTIONS):
            return FLOOR_DESCRIPTIONS[floor - 1]
        else:
            return f"The Unknown Depths - Floor {floor}"
    
    def is_boss_floor(self, floor: int) -> bool:
        """Check if this floor has a boss encounter."""
        return floor in [3, 5]  # Orc King on floor 3, Demon Lord on floor 5
    
    def get_boss_intro(self, monster: Monster) -> str:
        """Get the intro text for a boss encounter."""
        from .art_assets import BOSS_INTRO
        if monster.name == "Orc King":
            return BOSS_INTRO["boss_orc_king"]
        elif monster.name == "Demon Lord":
            return BOSS_INTRO["boss_demon_lord"]
        return f"A powerful {monster.name} blocks your path!"


class ShopSystem:
    def __init__(self):
        self.available_items = self._generate_shop_inventory()
    
    def _generate_shop_inventory(self) -> List[Item]:
        """Generate the shop's inventory."""
        shop_items = [
            ITEMS["rusty_sword"], ITEMS["iron_sword"], ITEMS["steel_sword"],
            ITEMS["leather_armor"], ITEMS["chain_mail"], ITEMS["plate_armor"],
            ITEMS["wooden_shield"], ITEMS["iron_shield"], ITEMS["magic_shield"],
            ITEMS["healing_potion"], ITEMS["mana_potion"]
        ]
        return shop_items
    
    def can_afford(self, player: Player, item: Item) -> bool:
        """Check if player can afford an item."""
        return player.gold >= item.value
    
    def buy_item(self, player: Player, item: Item) -> str:
        """Player buys an item. Returns result message."""
        if not self.can_afford(player, item):
            return f"You cannot afford {item.name}! (Cost: {item.value} gold)"
        
        player.gold -= item.value
        
        # Equipment items are equipped immediately if slot is empty
        if item.type == ItemType.WEAPON:
            if player.weapon is None:
                player.weapon = item
                return f"Bought and equipped {item.name}!"
            else:
                player.inventory.append(item)
                return f"Bought {item.name}! (Added to inventory)"
        
        elif item.type == ItemType.ARMOR:
            if player.armor is None:
                player.armor = item
                return f"Bought and equipped {item.name}!"
            else:
                player.inventory.append(item)
                return f"Bought {item.name}! (Added to inventory)"
        
        elif item.type == ItemType.SHIELD:
            if player.shield is None:
                player.shield = item
                return f"Bought and equipped {item.name}!"
            else:
                player.inventory.append(item)
                return f"Bought {item.name}! (Added to inventory)"
        
        else:  # Consumables
            player.inventory.append(item)
            return f"Bought {item.name}!"
    
    def sell_item(self, player: Player, item: Item) -> str:
        """Player sells an item. Returns result message."""
        if item in player.inventory:
            sell_price = item.value // 2  # Sell for half price
            player.gold += sell_price
            player.inventory.remove(item)
            return f"Sold {item.name} for {sell_price} gold!"
        elif item == player.weapon:
            sell_price = item.value // 2
            player.gold += sell_price
            player.weapon = None
            return f"Sold equipped {item.name} for {sell_price} gold!"
        elif item == player.armor:
            sell_price = item.value // 2
            player.gold += sell_price
            player.armor = None
            return f"Sold equipped {item.name} for {sell_price} gold!"
        elif item == player.shield:
            sell_price = item.value // 2
            player.gold += sell_price
            player.shield = None
            return f"Sold equipped {item.name} for {sell_price} gold!"
        else:
            return "You don't have that item!"
    
    def get_shop_display(self, player: Player) -> str:
        """Generate shop display text."""
        display = f"Your gold: {player.gold}\n\n"
        display += "AVAILABLE ITEMS:\n"
        display += "-" * 50 + "\n"
        
        for i, item in enumerate(self.available_items, 1):
            affordable = "✓" if self.can_afford(player, item) else "✗"
            display += f"{i:2d}. {item.name:<20} - {item.value:>3} gold {affordable}\n"
            display += f"    {item.description}\n"
            if item.damage > 0:
                display += f"    Damage: +{item.damage}\n"
            if item.defense > 0:
                display += f"    Defense: +{item.defense}\n"
            display += "\n"
        
        return display


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
        self.dungeon = DungeonSystem()
        self.shop = ShopSystem()
    
    def create_player(self, name: str, player_class: str) -> Player:
        """Create a new player character."""
        from .game_data import PlayerClass
        
        class_map = {
            "1": PlayerClass.FIGHTER,
            "2": PlayerClass.WIZARD,
            "3": PlayerClass.ROGUE
        }
        
        self.player = Player(name, class_map[player_class])
        return self.player
    
    def enter_dungeon_floor(self, floor: int):
        """Enter a specific dungeon floor."""
        self.current_floor = floor
        self.current_monster = self.dungeon.generate_monster_for_floor(floor)
        self.in_town = False
        self.in_combat = True
        self.combat.clear_log()
        
        if self.dungeon.is_boss_floor(floor):
            intro = self.dungeon.get_boss_intro(self.current_monster)
            self.combat.add_log(intro)
    
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
    
    def equip_item(self, item: Item) -> str:
        """Equip an item from inventory."""
        if item not in self.player.inventory:
            return "You don't have that item!"
        
        if item.type == ItemType.WEAPON:
            # Swap weapons
            old_weapon = self.player.weapon
            self.player.weapon = item
            self.player.inventory.remove(item)
            if old_weapon:
                self.player.inventory.append(old_weapon)
                return f"Equipped {item.name}! (Unequipped {old_weapon.name})"
            return f"Equipped {item.name}!"
        
        elif item.type == ItemType.ARMOR:
            old_armor = self.player.armor
            self.player.armor = item
            self.player.inventory.remove(item)
            if old_armor:
                self.player.inventory.append(old_armor)
                return f"Equipped {item.name}! (Unequipped {old_armor.name})"
            return f"Equipped {item.name}!"
        
        elif item.type == ItemType.SHIELD:
            old_shield = self.player.shield
            self.player.shield = item
            self.player.inventory.remove(item)
            if old_shield:
                self.player.inventory.append(old_shield)
                return f"Equipped {item.name}! (Unequipped {old_shield.name})"
            return f"Equipped {item.name}!"
        
        else:
            return "This item cannot be equipped!"
    
    def check_victory_conditions(self):
        """Check if the player has won the game."""
        if self.current_floor > 5:  # Completed final floor
            self.victory = True
            self.game_over = True
    
    def check_defeat_conditions(self):
        """Check if the player has lost the game."""
        if self.player and self.player.hp <= 0:
            self.game_over = True