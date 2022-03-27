import time, threading, random
from timeit import default_timer as timer
from collections import namedtuple
"""
MAP STRUCTURE!

a map is a 2d grid of Chunks, that become revealed as they are discovered.
a chunk is a 2d grid of Tiles.
a tile can be walkable
"""

class Names:
    PLACES = ['Tower', 'Dunes', 'Plains', 'Astral Plains', 'Lost Temple', 'Forgotten Lands', 'Mountain',
        'Test Module', 'Hallway', 'Zone', 'Land', 'Waste', 'Area', 'Belt', 'Sector', 'Ground', 'Region', 
        'Section', 'Chunk', 'Realm']

    FIRST = ['A', 'Ag', 'Ar', 'Ara', 'Anu', 'Bal', 'Bil', 'Boro', 'Bern', 'Bra', 'Cas', 'Cere', 'Co', 'Con',
        'Cor', 'Dag', 'Doo', 'Elen', 'El', 'En', 'Eo', 'Faf', 'Fan', 'Fara', 'Fre', 'Fro', 'Ga', 'Gala', 'Has', 
        'He', 'Heim', 'Ho', 'Isil', 'In', 'Ini', 'Is', 'Ka', 'Kuo', 'Lance', 'Lo', 'Ma', 'Mag', 'Mi', 'Mo', 
        'Moon', 'Mor', 'Mora', 'Nin', 'O', 'Obi', 'Og', 'Pelli', 'Por', 'Ran', 'Rud', 'Sam',  'She', 'Sheel', 
        'Shin', 'Shog', 'Son', 'Sur', 'Theo', 'Tho', 'Tris', 'U', 'Uh', 'Ul', 'Vap', 'Vish', 'Ya', 'Yo', 'Yyr']
 
    SECOND = ['ba', 'bis', 'bo', 'bus', 'da', 'dal', 'dagz', 'den', 'di', 'dil', 'din', 'do', 'dor', 'dra', 
        'dur', 'gi', 'gauble', 'gen', 'glum', 'go', 'gorn', 'goth', 'had', 'hard', 'is', 'ki', 'koon', 'ku', 
        'lad', 'ler', 'li', 'lot', 'ma', 'man', 'mir', 'mus', 'nan', 'ni', 'nor', 'nu', 'pian', 'ra', 'rak', 
        'ric', 'rin', 'rum', 'rus', 'rut', 'sek', 'sha', 'thos', 'thur', 'toa', 'tu', 'tur', 'tred', 'varl',
        'wain', 'wan', 'win', 'wise', 'ya']

    WAYS = ['Lost', 'Deserted', 'Consumed', 'Abandoned', 'Occupied', 'Forsaken', 'Clandestine', 'Forgiven']

    TASTE = ['Calamity', 'Doom', 'Tragedy', 'Ruin', 'Condemnation', 'Downfall', 'Grace', 'Pliancy', 'Consideration']
 
    def first_name():
        return random.choice(Names.FIRST) + random.choice(Names.SECOND)

    def last_name():
        return Names.first_name()

    def house_name():
        return Names.first_name()

    def _places_name():
        return random.choice(Names.PLACES)

    def zone_name():
        return random.choice(Names.ZONE)

    def ways_name():
        return random.choice(Names.WAYS)

    def taste_name():
        return random.choice(Names.TASTE)

    def place_name():
        return f"The {Names.ways_name()} {Names._places_name()} of {Names.taste_name()}"

    def player_name():
        return f"{Names.first_name()} {Names.last_name()} the {Names.ways_name()} of House {Names.house_name()}"

    def crazy():
        return f"{Names.player_name()}\nfrom the land of {Names._place_name()}"


class Player:

    sight_range = 2

    def __init__(self, name=Names.player_name()):
        self.name = name
        self.location = {
            'chunk_name': '',
            'coords': (50, 50)
        }

    def __repr__(self):
        return self.name


class Tile:
    elevation = 0
    walkable = True
    water = False
    resources = {}
    items = {}
    occupied = []

    def __init__(self, chunk_name, location):
        self.chunk_name = chunk_name
        coords = namedtuple('coord', 'x y')
        self.location = coords(location[0], location[1])

    @property
    def available(self):
        return False if self.occupied else True

    def __str__(self):
        if not self.occupied: return '.'
        else: return 'X'

    def __repr__(self):
        string = ''
        for k, v in self.__dict__.items():
            string += f'{k}: {v}' + '\n'
        return string


class Chunk:
    def __init__(self, chunk_name='Noob Zone', chunk_size=[10, 10]):
        print(f"making new chunk! {chunk_name} | ({chunk_size[0]}, {chunk_size[1]})")
        self.chunk_size = chunk_size
        self.name = chunk_name
        self.grid = [[Tile(self.name, (x,y)) for x in range(self.chunk_size[0])] for y in range(self.chunk_size[1])]
        self.start_coords = [5, 5]
        self.players = []
        self.npcs = []

        self.startup_time = timer()
        self._shutdown = False
        self.tick = 0

    def __str__(self):
        x = '\n'.join( ' '.join(str(z) for z in self.grid[x]) for x in range(len(self.grid)) )
        return x

    def __repr__(self):
        x = '\n'.join( ' '.join(str(z) for z in self.grid[x]) for x in range(len(self.grid)) )
        return f'{self.name}\n'+x

    @property
    def should_shutdown(self):
        return self._shutdown
    @should_shutdown.setter
    def should_shutdown(self, *args, **kwargs):
        if not self._shutdown:
            self._shutdown = True

    @property
    def num_players(self):
        return len(self.players)

    @property
    def num_npcs(self):
        return len(self.npcs)

    def get(self, coords):
        print(f"trying to get coords: ({coords[0]}, {coords[1]})")
        return self.grid[coords[0]][coords[1]]

    def place(self, coords):
        print(f"grid len: {len(self.grid)}")
        tile = self.grid[coords[0]][coords[1]]
        if tile.available:
            return tile
        else:
            tile = self.grid[self.start_coords[0]][self.start_coords[1]]
            if tile.available:
                return tile
            else:
                # THE STARTING ZONE IS FULL FIND A NEARBY SPOT.
                # maybe the tile should be available if the tile only has
                # players in it. and not monsters or items. or stuff.

                # returning starting area anyway for now.
                return tile

    def tick_report(self):
        line = f"T:{self.tick} | {self.name} | P: {self.num_players} | N: {self.num_npcs}"
        print(line)
        self.tick += 1

    def main_loop(self):
        while not self.should_shutdown:
            self.tick_report()
            time.sleep(.5)


class Map:
    """
    MAP NEEDS:
    *--0| know which new zone to add when needed.
    *--0| should the map know where the players are?
    """

    def __init__(self, map_config={}):
        print(map_config)
        self.config = map_config
        self.chunk_size = self.config['chunk_size']
        # the Grid of Chunks should be 3d and the zones 
        # could have stairs up and stairs down, as well as 
        # side tunnels.
        self.map = [
            [None, Chunk(Names.place_name(), self.chunk_size), None],
            [Chunk(Names.place_name(), self.chunk_size), Chunk('Noob Zone', self.chunk_size), Chunk(Names.place_name(), self.chunk_size)],
            [None, Chunk(Names.place_name(), self.chunk_size), None]
        ]

        self.chunks = {}
        self.get_chunks()

    def __repr__(self) -> str:
        return '\n'.join(x for x in self.chunks)

    def get_chunks(self):
        for i in self.map:
            for zone in i:
                if zone:
                    self.chunks[zone.name] = zone
    
    @property
    def num_chunks(self):
        counter = 0
        for x in range(len(self.map)):
            for y in range(len(self.map[0])):
                if self.map[x][y]:
                    counter += 1
        return counter

    @property
    def chunk_names(self):
        list_of_names = []
        for row in self.map:
            for chunk in row:
                if chunk: list_of_names.append(chunk.name)
        return list_of_names

    def place_player(self, player):
        player_location = player.location
        print(f"Trying to place player in zone({player_location['chunk_name']}). {player_location['coords']}")
        if player_location['chunk_name'] in self.chunk_names:
            chunk = self.chunks[ player_location['chunk_name'] ]
        else:
            chunk = self.chunks['Noob Zone']
        print(f"Chunk Size: {chunk.chunk_size}")
        player_coords = player_location['coords']
        place = chunk.place(player_coords)
        print("a little about this tile:")
        print(place.__repr__())
        place.occupied.append(player)
        chunk.players.append(player)
        player.location['chunk_name'] = chunk.name
        player.location['coords'] = place.location


class Game:
    def __init__(self, config={}):
        self.config = {
            'map': {
                'chunk_size': [100, 100],
                'mapsave_filename': 'test.map'
            },
            'gamesave_filename': 'test.game',
        }
        self.map = Map(self.config['map'])
        self.map_threads = []

        # PLAYERS
        self.players = {}

        # RUNTIME
        self.should_shutdown = False

    def startup(self):
        for chunk_name in self.map.chunks:
            chunk = self.map.chunks[chunk_name]
            thread = threading.Thread(target=chunk.main_loop, args=())
            thread.start()
            self.map_threads.append(thread)

    def test(self):
        print(f"Zones on the Map({self.map.num_chunks}):")
        print(self.map)
        self.player_login()
        self.game_loop()

    def player_login(self, player_name='test'):
        
        # GET THE PLAYER CHARACTER
        if player_name not in self.players:
            new_player = Player(player_name)
            self.players[player_name] = new_player
        
        player = self.players[player_name]
        print(f"Player: {player} is joining the game!")

        # PLACE THE PLAYER BACK IN THE GAME
        # EITHER AT THEIR LAST POSITION OR
        # AT THE STARTING AREA.
        self.map.place_player(player)

    def broadcast(self, msg):
        self.server.broadcast(msg)

    def game_loop(self):
        self.startup()
        try:
            while True:
                if self.should_shutdown == True: break
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print("Error!!")
            print(e)
            
        self.end_safely()

    def end_safely(self):
        for chunk_name in self.map.chunks:
            chunk = self.map.chunks[chunk_name]
            chunk.should_shutdown = True
        for thread in self.map_threads:
            thread.join()
        print("ended Safely")


x = Game()
x.test()