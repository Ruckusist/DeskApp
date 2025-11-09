"""
ASCII Art and Story Assets for RPG Game
Contains splash screens, UI elements, and story text.
"""

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

SHOP_HEADER = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                            GRELDORN'S SHOP                                   ║
║                        💰 Finest Goods in Haven 💰                          ║
║                                                                               ║
║  "Welcome, adventurer! I have the finest weapons and armor                   ║
║   in all the land. What catches your eye?"                                   ║
║                                                                               ║
║  Commands: B <item> - Buy item, S - Sell items, Q - Quit shop              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

DUNGEON_ENTRANCE = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         THE CURSED DUNGEON                                   ║
║                          💀 Floor {} 💀                                      ║
║                                                                               ║
║     ████████████████████████████████████                                    ║
║     ██                                ██                                    ║
║     ██    The darkness grows deeper   ██                                    ║
║     ██    with each passing floor...  ██                                    ║
║     ██                                ██                                    ║
║     ██         🚪 ENTER 🚪            ██                                    ║
║     ██                                ██                                    ║
║     ████████████████████████████████████                                    ║
║                                                                               ║
║  Press ENTER to explore this floor                                          ║
║  Press B to return to town                                                  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

COMBAT_UI = """
╔════════════════════════════════════════════════╦══════════════════════════════╗
║ {monster_name:<46} ║ {player_name:<28} ║
║ HP: {monster_hp:>3}/{monster_max_hp:<3}                                   ║ Level: {player_level:<21} ║
║                                                ║ HP: {player_hp:>3}/{player_max_hp:<3}                  ║
║                                                ║ MP: {player_mp:>3}/{player_max_mp:<3}                  ║
║                                                ║ Gold: {player_gold:<21} ║
╠════════════════════════════════════════════════╩══════════════════════════════╣
║                            COMBAT                                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
"""

VICTORY_BANNER = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                VICTORY!                                      ║
║                          ⭐ Monster Defeated! ⭐                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

DEFEAT_BANNER = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                               DEFEAT!                                        ║
║                          💀 You have fallen... 💀                           ║
║                                                                               ║
║           Your adventure ends here, but legends speak of heroes              ║
║           who rise again to face the darkness...                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

BOSS_INTRO = {
    "boss_orc_king": """
The ground trembles as a massive figure emerges from the shadows...

"HUMAN! You dare enter MY domain? I am GRAX THE ORC KING,
 ruler of these cursed halls! Your bones will join the
 countless others who thought they could challenge me!"

*The Orc King raises his massive war hammer, eyes burning with rage*

PREPARE FOR BATTLE!
""",
    
    "boss_demon_lord": """
The very air grows cold as reality itself seems to bend...

"Foolish mortal... You have descended far enough into my realm.
 I am MALTHARION, LORD OF THE ABYSS! Your soul will fuel
 my power for eternity!"

*Dark flames dance around the Demon Lord as he spreads his wings*

"Let us see if you are worthy of my attention..."

THE FINAL BATTLE BEGINS!
"""
}

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

FLOOR_DESCRIPTIONS = [
    "The Upper Catacombs - Ancient burial chambers filled with restless spirits",
    "The Goblin Warrens - Twisting tunnels where goblin tribes make their nests",
    "The Orcish Stronghold - Fortified halls where orc warriors train for battle", 
    "The Demon's Gate - Where reality grows thin and hellish creatures emerge",
    "The Abyssal Throne - The deepest depths where the Demon Lord awaits"
]

GAME_OVER_STORY = """
Your legend will be remembered in Haven Town...

Though you fell in the cursed dungeon, your bravery inspired others.
The merchants speak of your courage, the children sing songs of your
adventures, and somewhere, another hero prepares to take up your quest.

The darkness may have claimed you, but it has not won. Light endures
in the hearts of the brave, and your sacrifice was not in vain.

THANK YOU FOR PLAYING DUNGEON CRAWLER!
"""

VICTORY_STORY = """
THE DEMON LORD HAS FALLEN!

With Maltharion's defeat, his dark magic unravels. The cursed dungeon
begins to crumble as centuries of evil are purged from its depths.
You emerge into the sunlight as birds sing and flowers bloom.

Haven Town erupts in celebration! You have saved not just the town,
but the entire kingdom. Bards will sing of your heroic deeds for
generations to come.

The King offers you any reward you desire, but you need only the
knowledge that peace has returned to the land.

CONGRATULATIONS, HERO! YOU HAVE COMPLETED YOUR QUEST!
"""

def get_player_status_display(player, floor):
    """Generate a formatted status display for the player"""
    return f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              ADVENTURER STATUS                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Name: {player.name:<20} Class: {player.player_class.value:<20} Floor: {floor:<8} ║
║ Level: {player.level:<19} Experience: {player.experience}/{player.level * 100:<20} ║
║ HP: {player.hp}/{player.max_hp:<25} MP: {player.mp}/{player.max_mp:<25} ║
║ Attack: {player.total_attack:<18} Defense: {player.total_defense:<25} Gold: {player.gold:<8} ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                 EQUIPMENT                                    ║
║ Weapon: {(player.weapon.name if player.weapon else "None"):<30} Damage: {(player.weapon.damage if player.weapon else 0):<8} ║
║ Armor:  {(player.armor.name if player.armor else "None"):<30} Defense: {(player.armor.defense if player.armor else 0):<7} ║
║ Shield: {(player.shield.name if player.shield else "None"):<30} Defense: {(player.shield.defense if player.shield else 0):<7} ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                 INVENTORY                                    ║
"""