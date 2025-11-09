#!/usr/bin/env python3
"""
Battle Screen Test - Debug version to test combat
"""
import random

# Simple test to show what the battle screen looks like
def show_battle_example():
    print("="*80)
    print("DUNGEON CRAWLER RPG - BATTLE SCREEN PREVIEW")
    print("="*80)
    print()

    # Example battle screen layout
    battle_screen = """
╔════════════════════════════════════════════════╦══════════════════════════════╗
║ Goblin                                         ║ Hero                         ║
║ HP: 25/25                                      ║ Level: 1                     ║
║                                                ║ HP: 120/120                  ║
║                                                ║ MP: 30/30                    ║
║                                                ║ Gold: 100                    ║
╠════════════════════════════════════════════════╩══════════════════════════════╣
║                            COMBAT                                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║    ╭─────╮                                                                   ║
║    │ ◉ ◉ │                                                                   ║
║    │  ▽  │                                                                   ║
║    ╰─┬─┬─╯                                                                   ║
║      │ │                                                                     ║
║                                                                               ║
║ Combat Log:                                                                   ║
║   A wild Goblin appears!                                                     ║
║   You attack Goblin for 12 damage!                                          ║
║   Goblin attacks you for 3 damage!                                          ║
║                                                                               ║
║ Actions: A-Attack | M-Magic | I-Item | R-Run                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

    print(battle_screen)
    print()
    print("BATTLE FEATURES:")
    print("- Dedicated combat screen (separate from dungeon map)")
    print("- Real-time ASCII monster art")
    print("- Turn-based combat with detailed combat log")
    print("- Player stats display (HP, MP, Level, Gold)")
    print("- Monster health tracking")
    print("- Multiple combat options (Attack, Magic, Items, Run)")
    print()

    # Show different monsters
    monsters = {
        "Goblin": """
    ╭─────╮
    │ ◉ ◉ │
    │  ▽  │
    ╰─┬─┬─╯
      │ │""",

        "Orc": """
    ╔═════╗
    ║ ● ● ║
    ║  ∩  ║
    ║ ═══ ║
    ╚═┬═┬═╝
      ║ ║""",

        "Demon": """
    ╔═══════╗
    ║ ◄► ◄► ║
    ║   ♦   ║
    ║ ═════ ║
    ╚═══┬═══╝
        ║
      ▓▓▓▓▓""",

        "Orc King (BOSS)": """
    ╔═══════════╗
    ║  ▲   ▲   ║
    ║ ◆ ● ● ◆  ║
    ║    ∩     ║
    ║  ═════   ║
    ╚═════┬═════╝
          ║
        ♔♔♔♔♔""",

        "Demon Lord (FINAL BOSS)": """
    ╔═══════════════╗
    ║   ♠ ◄► ◄► ♠   ║
    ║       ♦       ║
    ║  ══════════   ║
    ║  ▓▓▓▓▓▓▓▓▓▓   ║
    ╚═════┬═════════╝
          ║
      ☠☠☠☠☠☠☠"""
    }

    print("MONSTER GALLERY:")
    print("-" * 40)
    for name, art in monsters.items():
        print(f"{name}:")
        print(art)
        print()

if __name__ == "__main__":
    show_battle_example()
