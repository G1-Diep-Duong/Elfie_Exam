"""
Gives the name of any RGB color.

If the exact color doesn't have a name, the closest match will be used instead.
"""

__all__ = ["find"]

import functools


@functools.singledispatch
def find(r=0, g=0, b=0):
    """Finds a color's name.

    The color may be expressed in either of the following formats:
     - three ints (r, g, b) in the range 0 <= x < 256,
     - a tuple of three ints (r, g, b) in the range 0 <= x < 256, or
     - a hexadecimal representation (3 or 6 digits, '#' prefix optional).
    """
    if type(r) is not int or type(g) is not int or type(b) is not int:
        raise TypeError("R, G and B values must be int")
    if not (0 <= r < 256 and 0 <= g < 256 and 0 <= b < 256):
        raise ValueError("Invalid color value: must be 0 <= x < 256")
    return _search(_searchtree, r, g, b)


@find.register(str)
def _find_hex(color):
    if color[0] == '#':
        color = color[1:]
    if len(color) == 3:
        return find(*[int(c * 2, 16) for c in color])
    if len(color) == 6:
        return find(*[int(color[i:i + 2], 16) for i in (0, 2, 4)])
    raise ValueError("Malformed hexadecimal color representation")


@find.register(tuple)
def _find_tuple(color):
    if len(color) != 3:
        raise ValueError("Malformed color tuple: must be of size 3 (r, g, b)")
    return find(*color)


def _octree_index(r, g, b, d):
    return ((r >> d & 1) << 2) | ((g >> d & 1) << 1) | (b >> d & 1)


def _search(tree, r, g, b, d=7):
    i = _octree_index(r, g, b, d)
    if i not in tree:
        return _approximate(tree, r, g, b)
    return tree[i] if type(tree[i]) is str else _search(tree[i], r, g, b, d - 1)


def _approximate(tree, r, g, b):

    def _distance(colorname):
        x, y, z = _colors[colorname]
        return (r - x)**2 + (g - y)**2 + (b - z)**2

    return min(_descendants(tree), key=_distance)


def _descendants(tree):
    for i, child in tree.items():
        if type(child) is str:
            yield child
        else:
            yield from _descendants(child)


_colors = {
    "Abbey": (76, 79, 86),
    "Acadia": (27, 20, 4),
    "Acapulco": (124, 176, 161),
    "Aero Blue": (201, 255, 229),
    "Affair": (113, 70, 147),
    "Akaroa": (212, 196, 168),
    "Alabaster": (250, 250, 250),
    "Albescent White": (245, 233, 211),
    "Algae Green": (147, 223, 184),
    "Alice Blue": (240, 248, 255),
    "Alizarin Crimson": (227, 38, 54),
    "Allports": (0, 118, 163),
    "Almond": (238, 217, 196),
    "Almond Frost": (144, 123, 113),
    "Alpine": (175, 143, 44),
    "Alto": (219, 219, 219),
    "Aluminium": (169, 172, 182),
    "Amaranth": (229, 43, 80),
    "Amazon": (59, 122, 87),
    "Amber": (255, 191, 0),
    "Americano": (135, 117, 110),
    "Amethyst": (153, 102, 204),
    "Amethyst Smoke": (163, 151, 180),
    "Amour": (249, 234, 243),
    "Amulet": (123, 159, 128),
    "Anakiwa": (157, 229, 255),
    "Antique Brass": (200, 138, 101),
    "Antique Bronze": (112, 74, 7),
    "Anzac": (224, 182, 70),
    "Apache": (223, 190, 111),
    "Apple": (79, 168, 61),
    "Apple Blossom": (175, 77, 67),
    "Apple Green": (226, 243, 236),
    "Apricot": (235, 147, 115),
    "Apricot Peach": (251, 206, 177),
    "Apricot White": (255, 254, 236),
    "Aqua Deep": (1, 75, 67),
    "Aqua Forest": (95, 167, 119),
    "Aqua Haze": (237, 245, 245),
    "Aqua Island": (161, 218, 215),
    "Aqua Spring": (234, 249, 245),
    "Aqua Squeeze": (232, 245, 242),
    "Aquamarine": (127, 255, 212),
    "Aquamarine Blue": (113, 217, 226),
    "Arapawa": (17, 12, 108),
    "Armadillo": (67, 62, 55),
    "Arrowtown": (148, 135, 113),
    "Ash": (198, 195, 181),
    "Asparagus": (123, 160, 91),
    "Asphalt": (19, 10, 6),
    "Astra": (250, 234, 185),
    "Astral": (50, 125, 160),
    "Astronaut": (40, 58, 119),
    "Astronaut Blue": (1, 62, 98),
    "Athens Gray": (238, 240, 243),
    "Aths Special": (236, 235, 206),
    "Atlantis": (151, 205, 45),
    "Atoll": (10, 111, 117),
    "Atomic Tangerine": (255, 153, 102),
    "Au Chico": (151, 96, 93),
    "Aubergine": (59, 9, 16),
    "Australian Mint": (245, 255, 190),
    "Avocado": (136, 141, 101),
    "Axolotl": (78, 102, 73),
    "Azalea": (247, 200, 218),
    "Aztec": (13, 28, 25),
    "Azure": (49, 91, 161),
    "Azure Radiance": (0, 127, 255),
    "Baby Blue": (224, 255, 255),
    "Bahama Blue": (2, 99, 149),
    "Bahia": (165, 203, 12),
    "Baja White": (255, 248, 209),
    "Bali Hai": (133, 159, 175),
    "Baltic Sea": (42, 38, 48),
    "Bamboo": (218, 99, 4),
    "Banana Mania": (251, 231, 178),
    "Bandicoot": (133, 132, 112),
    "Barberry": (222, 215, 23),
    "Barley Corn": (166, 139, 91),
    "Barley White": (255, 244, 206),
    "Barossa": (68, 1, 45),
    "Bastille": (41, 33, 48),
    "Battleship Gray": (130, 143, 114),
    "Bay Leaf": (125, 169, 141),
    "Bay of Many": (39, 58, 129),
    "Bazaar": (152, 119, 123),
    "Bean  ": (61, 12, 2),
    "Beauty Bush": (238, 193, 190),
    "Beaver": (146, 111, 91),
    "Beeswax": (254, 242, 199),
    "Beige": (245, 245, 220),
    "Bermuda": (125, 216, 198),
    "Bermuda Gray": (107, 139, 162),
    "Beryl Green": (222, 229, 192),
    "Bianca": (252, 251, 243),
    "Big Stone": (22, 42, 64),
    "Bilbao": (50, 124, 20),
    "Biloba Flower": (178, 161, 234),
    "Birch": (55, 48, 33),
    "Bird Flower": (212, 205, 22),
    "Biscay": (27, 49, 98),
    "Bismark": (73, 113, 131),
    "Bison Hide": (193, 183, 164),
    "Bistre": (61, 43, 31),
    "Bitter": (134, 137, 116),
    "Bitter Lemon": (202, 224, 13),
    "Bittersweet": (254, 111, 94),
    "Bizarre": (238, 222, 218),
    "Black": (0, 0, 0),
    "Black Bean": (8, 25, 16),
    "Black Forest": (11, 19, 4),
    "Black Haze": (246, 247, 247),
    "Black Marlin": (62, 44, 28),
    "Black Olive": (36, 46, 22),
    "Black Pearl": (4, 19, 34),
    "Black Rock": (13, 3, 50),
    "Black Rose": (103, 3, 45),
    "Black Russian": (10, 0, 28),
    "Black Squeeze": (242, 250, 250),
    "Black White": (255, 254, 246),
    "Blackberry": (77, 1, 53),
    "Blackcurrant": (50, 41, 58),
    "Blaze Orange": (255, 102, 0),
    "Bleach White": (254, 243, 216),
    "Bleached Cedar": (44, 33, 51),
    "Blizzard Blue": (163, 227, 237),
    "Blossom": (220, 180, 188),
    "Blue": (0, 0, 255),
    "Blue Bayoux": (73, 102, 121),
    "Blue Bell": (153, 153, 204),
    "Blue Chalk": (241, 233, 255),
    "Blue Charcoal": (1, 13, 26),
    "Blue Chill": (12, 137, 144),
    "Blue Diamond": (56, 4, 116),
    "Blue Dianne": (32, 72, 82),
    "Blue Gem": (44, 14, 140),
    "Blue Haze": (191, 190, 216),
    "Blue Lagoon": (1, 121, 135),
    "Blue Marguerite": (118, 102, 198),
    "Blue Ribbon": (0, 102, 255),
    "Blue Romance": (210, 246, 222),
    "Blue Smoke": (116, 136, 129),
    "Blue Stone": (1, 97, 98),
    "Blue Violet": (100, 86, 183),
    "Blue Whale": (4, 46, 76),
    "Blue Zodiac": (19, 38, 77),
    "Blumine": (24, 88, 122),
    "Blush": (180, 70, 104),
    "Blush Pink": (255, 111, 255),
    "Bombay": (175, 177, 184),
    "Bon Jour": (229, 224, 225),
    "Bondi Blue": (0, 149, 182),
    "Bone": (228, 209, 192),
    "Bordeaux": (92, 1, 32),
    "Bossanova": (78, 42, 90),
    "Boston Blue": (59, 145, 180),
    "Botticelli": (199, 221, 229),
    "Bottle Green": (9, 54, 36),
    "Boulder": (122, 122, 122),
    "Bouquet": (174, 128, 158),
    "Bourbon": (186, 111, 30),
    "Bracken": (74, 42, 4),
    "Brandy": (222, 193, 150),
    "Brandy Punch": (205, 132, 41),
    "Brandy Rose": (187, 137, 131),
    "Breaker Bay": (93, 161, 159),
    "Brick Red": (198, 45, 66),
    "Bridal Heath": (255, 250, 244),
    "Bridesmaid": (254, 240, 236),
    "Bright Gray": (60, 65, 81),
    "Bright Green": (102, 255, 0),
    "Bright Red": (177, 0, 0),
    "Bright Sun": (254, 211, 60),
    "Bright Turquoise": (8, 232, 222),
    "Brilliant Rose": (246, 83, 166),
    "Brink Pink": (251, 96, 127),
    "Bronco": (171, 161, 150),
    "Bronze": (63, 33, 9),
    "Bronze Olive": (78, 66, 12),
    "Bronzetone": (77, 64, 15),
    "Broom": (255, 236, 19),
    "Brown": (150, 75, 0),
    "Brown Bramble": (89, 40, 4),
    "Brown Derby": (73, 38, 21),
    "Brown Pod": (64, 24, 1),
    "Brown Rust": (175, 89, 62),
    "Brown Tumbleweed": (55, 41, 14),
    "Bubbles": (231, 254, 255),
    "Buccaneer": (98, 47, 48),
    "Bud": (168, 174, 156),
    "Buddha Gold": (193, 160, 4),
    "Buff": (240, 220, 130),
    "Bulgarian Rose": (72, 6, 7),
    "Bull Shot": (134, 77, 30),
    "Bunker": (13, 17, 23),
    "Bunting": (21, 31, 76),
    "Burgundy": (144, 0, 32),
    "Burnham": (0, 46, 32),
    "Burning Orange": (255, 112, 52),
    "Burning Sand": (217, 147, 118),
    "Burnt Maroon": (66, 3, 3),
    "Burnt Orange": (204, 85, 0),
    "Burnt Sienna": (233, 116, 81),
    "Burnt Umber": (138, 51, 36),
    "Bush": (13, 46, 28),
    "Buttercup": (243, 173, 22),
    "Buttered Rum": (161, 117, 13),
    "Butterfly Bush": (98, 78, 154),
    "Buttermilk": (255, 241, 181),
    "Buttery White": (255, 252, 234),
    "Cab Sav": (77, 10, 24),
    "Cabaret": (217, 73, 114),
    "Cabbage Pont": (63, 76, 58),
    "Cactus": (88, 113, 86),
    "Cadet Blue": (169, 178, 195),
    "Cadillac": (176, 76, 106),
    "Cafe Royale": (111, 68, 12),
    "Calico": (224, 192, 149),
    "California": (254, 157, 4),
    "Calypso": (49, 114, 141),
    "Camarone": (0, 88, 26),
    "Camelot": (137, 52, 86),
    "Cameo": (217, 185, 155),
    "Camouflage": (60, 57, 16),
    "Camouflage Green": (120, 134, 107),
    "Can Can": (213, 145, 164),
    "Canary": (243, 251, 98),
    "Candlelight": (252, 217, 23),
    "Candy Corn": (251, 236, 93),
    "Cannon Black": (37, 23, 6),
    "Cannon Pink": (137, 67, 103),
    "Cape Cod": (60, 68, 67),
    "Cape Honey": (254, 229, 172),
    "Cape Palliser": (162, 102, 69),
    "Caper": (220, 237, 180),
    "Caramel": (255, 221, 175),
    "Cararra": (238, 238, 232),
    "Cardin Green": (1, 54, 28),
    "Cardinal": (196, 30, 58),
    "Cardinal Pink": (140, 5, 94),
    "Careys Pink": (210, 158, 170),
    "Caribbean Green": (0, 204, 153),
    "Carissma": (234, 136, 168),
    "Carla": (243, 255, 216),
    "Carmine": (150, 0, 24),
    "Carnaby Tan": (92, 46, 1),
    "Carnation": (249, 90, 97),
    "Carnation Pink": (255, 166, 201),
    "Carousel Pink": (249, 224, 237),
    "Carrot Orange": (237, 145, 33),
    "Casablanca": (248, 184, 83),
    "Casal": (47, 97, 104),
    "Cascade": (139, 169, 165),
    "Cashmere": (230, 190, 165),
    "Casper": (173, 190, 209),
    "Castro": (82, 0, 31),
    "Catalina Blue": (6, 42, 120),
    "Catskill White": (238, 246, 247),
    "Cavern Pink": (227, 190, 190),
    "Cedar": (62, 28, 20),
    "Cedar Wood Finish": (113, 26, 0),
    "Celadon": (172, 225, 175),
    "Celery": (184, 194, 93),
    "Celeste": (209, 210, 202),
    "Cello": (30, 56, 91),
    "Celtic": (22, 50, 34),
    "Cement": (141, 118, 98),
    "Ceramic": (252, 255, 249),
    "Cerise": (218, 50, 135),
    "Cerise Red": (222, 49, 99),
    "Cerulean": (2, 164, 211),
    "Cerulean Blue": (42, 82, 190),
    "Chablis": (255, 244, 243),
    "Chalet Green": (81, 110, 61),
    "Chalky": (238, 215, 148),
    "Chambray": (53, 78, 140),
    "Chamois": (237, 220, 177),
    "Champagne": (250, 236, 204),
    "Chantilly": (248, 195, 223),
    "Charade": (41, 41, 55),
    "Chardon": (255, 243, 241),
    "Chardonnay": (255, 205, 140),
    "Charlotte": (186, 238, 249),
    "Charm": (212, 116, 148),
    "Chartreuse": (127, 255, 0),
    "Chartreuse Yellow": (223, 255, 0),
    "Chateau Green": (64, 168, 96),
    "Chatelle": (189, 179, 199),
    "Chathams Blue": (23, 85, 121),
    "Chelsea Cucumber": (131, 170, 93),
    "Chelsea Gem": (158, 83, 2),
    "Chenin": (223, 205, 111),
    "Cherokee": (252, 218, 152),
    "Cherry Pie": (42, 3, 89),
    "Cherrywood": (101, 26, 20),
    "Cherub": (248, 217, 233),
    "Chestnut": (185, 78, 72),
    "Chestnut Rose": (205, 92, 92),
    "Chetwode Blue": (133, 129, 217),
    "Chicago": (93, 92, 88),
    "Chiffon": (241, 255, 200),
    "Chilean Fire": (247, 119, 3),
    "Chilean Heath": (255, 253, 230),
    "China Ivory": (252, 255, 231),
    "Chino": (206, 199, 167),
    "Chinook": (168, 227, 189),
    "Chocolate": (55, 2, 2),
    "Christalle": (51, 3, 107),
    "Christi": (103, 167, 18),
    "Christine": (231, 115, 10),
    "Chrome White": (232, 241, 212),
    "Cinder": (14, 14, 24),
    "Cinderella": (253, 225, 220),
    "Cinnabar": (227, 66, 52),
    "Cinnamon": (123, 63, 0),
    "Cioccolato": (85, 40, 12),
    "Citrine White": (250, 247, 214),
    "Citron": (158, 169, 31),
    "Citrus": (161, 197, 10),
    "Clairvoyant": (72, 6, 86),
    "Clam Shell": (212, 182, 175),
    "Claret": (127, 23, 52),
    "Classic Rose": (251, 204, 231),
    "Clay Ash": (189, 200, 179),
    "Clay Creek": (138, 131, 96),
    "Clear Day": (233, 255, 253),
    "Clementine": (233, 110, 0),
    "Clinker": (55, 29, 9),
    "Cloud": (199, 196, 191),
    "Cloud Burst": (32, 46, 84),
    "Cloudy": (172, 165, 159),
    "Clover": (56, 73, 16),
    "Cobalt": (0, 71, 171),
    "Cocoa Bean": (72, 28, 28),
    "Cocoa Brown": (48, 31, 30),
    "Coconut Cream": (248, 247, 220),
    "Cod Gray": (11, 11, 11),
    "Coffee": (112, 101, 85),
    "Coffee Bean": (42, 20, 14),
    "Cognac": (159, 56, 29),
    "Cola": (63, 37, 0),
    "Cold Purple": (171, 160, 217),
    "Cold Turkey": (206, 186, 186),
    "Colonial White": (255, 237, 188),
    "Comet": (92, 93, 117),
    "Como": (81, 124, 102),
    "Conch": (201, 217, 210),
    "Concord": (124, 123, 122),
    "Concrete": (242, 242, 242),
    "Confetti": (233, 215, 90),
    "Congo Brown": (89, 55, 55),
    "Congress Blue": (2, 71, 142),
    "Conifer": (172, 221, 77),
    "Contessa": (198, 114, 107),
    "Copper": (184, 115, 51),
    "Copper Canyon": (126, 58, 21),
    "Copper Rose": (153, 102, 102),
    "Copper Rust": (148, 71, 71),
    "Copperfield": (218, 138, 103),
    "Coral": (255, 127, 80),
    "Coral Red": (255, 64, 64),
    "Coral Reef": (199, 188, 162),
    "Coral Tree": (168, 107, 107),
    "Corduroy": (96, 110, 104),
    "Coriander": (196, 208, 176),
    "Cork": (64, 41, 29),
    "Corn": (231, 191, 5),
    "Corn Field": (248, 250, 205),
    "Corn Harvest": (139, 107, 11),
    "Cornflower": (147, 204, 234),
    "Cornflower Blue": (100, 149, 237),
    "Cornflower Lilac": (255, 176, 172),
    "Corvette": (250, 211, 162),
    "Cosmic": (118, 57, 93),
    "Cosmos": (255, 216, 217),
    "Costa Del Sol": (97, 93, 48),
    "Cotton Candy": (255, 183, 213),
    "Cotton Seed": (194, 189, 182),
    "County Green": (1, 55, 26),
    "Cowboy": (77, 40, 45),
    "Crail": (185, 81, 64),
    "Cranberry": (219, 80, 121),
    "Crater Brown": (70, 36, 37),
    "Cream": (255, 253, 208),
    "Cream Brulee": (255, 229, 160),
    "Cream Can": (245, 200, 92),
    "Creole": (30, 15, 4),
    "Crete": (115, 120, 41),
    "Crimson": (220, 20, 60),
    "Crocodile": (115, 109, 88),
    "Crown of Thorns": (119, 31, 31),
    "Crowshead": (28, 18, 8),
    "Cruise": (181, 236, 223),
    "Crusoe": (0, 72, 22),
    "Crusta": (253, 123, 51),
    "Cumin": (146, 67, 33),
    "Cumulus": (253, 255, 213),
    "Cupid": (251, 190, 218),
    "Curious Blue": (37, 150, 209),
    "Cutty Sark": (80, 118, 114),
    "Cyan / Aqua": (0, 255, 255),
    "Cyprus": (0, 62, 64),
    "Daintree": (1, 39, 49),
    "Dairy Cream": (249, 228, 188),
    "Daisy Bush": (79, 35, 152),
    "Dallas": (110, 75, 38),
    "Dandelion": (254, 216, 93),
    "Danube": (96, 147, 209),
    "Dark Blue": (0, 0, 200),
    "Dark Burgundy": (119, 15, 5),
    "Dark Ebony": (60, 32, 5),
    "Dark Fern": (10, 72, 13),
    "Dark Tan": (102, 16, 16),
    "Dawn": (166, 162, 154),
    "Dawn Pink": (243, 233, 229),
    "De York": (122, 196, 136),
    "Deco": (210, 218, 151),
    "Deep Blue": (34, 8, 120),
    "Deep Blush": (228, 118, 152),
    "Deep Bronze": (74, 48, 4),
    "Deep Cerulean": (0, 123, 167),
    "Deep Cove": (5, 16, 64),
    "Deep Fir": (0, 41, 0),
    "Deep Forest Green": (24, 45, 9),
    "Deep Koamaru": (27, 18, 123),
    "Deep Oak": (65, 32, 16),
    "Deep Sapphire": (8, 37, 103),
    "Deep Sea": (1, 130, 107),
    "Deep Sea Green": (9, 88, 89),
    "Deep Teal": (0, 53, 50),
    "Del Rio": (176, 154, 149),
    "Dell": (57, 100, 19),
    "Delta": (164, 164, 157),
    "Deluge": (117, 99, 168),
    "Denim": (21, 96, 189),
    "Derby": (255, 238, 216),
    "Desert": (174, 96, 32),
    "Desert Sand": (237, 201, 175),
    "Desert Storm": (248, 248, 247),
    "Dew": (234, 255, 254),
    "Di Serria": (219, 153, 94),
    "Diesel": (19, 0, 0),
    "Dingley": (93, 119, 71),
    "Disco": (135, 21, 80),
    "Dixie": (226, 148, 24),
    "Dodger Blue": (30, 144, 255),
    "Dolly": (249, 255, 139),
    "Dolphin": (100, 96, 119),
    "Domino": (142, 119, 94),
    "Don Juan": (93, 76, 81),
    "Donkey Brown": (166, 146, 121),
    "Dorado": (107, 87, 85),
    "Double Colonial White": (238, 227, 173),
    "Double Pearl Lusta": (252, 244, 208),
    "Double Spanish White": (230, 215, 185),
    "Dove Gray": (109, 108, 108),
    "Downriver": (9, 34, 86),
    "Downy": (111, 208, 197),
    "Driftwood": (175, 135, 81),
    "Drover": (253, 247, 173),
    "Dull Lavender": (168, 153, 230),
    "Dune": (56, 53, 51),
    "Dust Storm": (229, 204, 201),
    "Dusty Gray": (168, 152, 155),
    "Eagle": (182, 186, 164),
    "Earls Green": (201, 185, 59),
    "Early Dawn": (255, 249, 230),
    "East Bay": (65, 76, 125),
    "East Side": (172, 145, 206),
    "Eastern Blue": (30, 154, 176),
    "Ebb": (233, 227, 227),
    "Ebony": (12, 11, 29),
    "Ebony Clay": (38, 40, 59),
    "Eclipse": (49, 28, 23),
    "Ecru White": (245, 243, 229),
    "Ecstasy": (250, 120, 20),
    "Eden": (16, 88, 82),
    "Edgewater": (200, 227, 215),
    "Edward": (162, 174, 171),
    "Egg Sour": (255, 244, 221),
    "Egg White": (255, 239, 193),
    "Eggplant": (97, 64, 81),
    "El Paso": (30, 23, 8),
    "El Salva": (143, 62, 51),
    "Electric Lime": (204, 255, 0),
    "Electric Violet": (139, 0, 255),
    "Elephant": (18, 52, 71),
    "Elf Green": (8, 131, 112),
    "Elm": (28, 124, 125),
    "Emerald": (80, 200, 120),
    "Eminence": (108, 48, 130),
    "Emperor": (81, 70, 73),
    "Empress": (129, 115, 119),
    "Endeavour": (0, 86, 167),
    "Energy Yellow": (248, 221, 92),
    "English Holly": (2, 45, 21),
    "English Walnut": (62, 43, 35),
    "Envy": (139, 166, 144),
    "Equator": (225, 188, 100),
    "Espresso": (97, 39, 24),
    "Eternity": (33, 26, 14),
    "Eucalyptus": (39, 138, 91),
    "Eunry": (207, 163, 157),
    "Evening Sea": (2, 78, 70),
    "Everglade": (28, 64, 46),
    "Faded Jade": (66, 121, 119),
    "Fair Pink": (255, 239, 236),
    "Falcon": (127, 98, 109),
    "Fall Green": (236, 235, 189),
    "Falu Red": (128, 24, 24),
    "Fantasy": (250, 243, 240),
    "Fedora": (121, 106, 120),
    "Feijoa": (159, 221, 140),
    "Fern": (99, 183, 108),
    "Fern Frond": (101, 114, 32),
    "Fern Green": (79, 121, 66),
    "Ferra": (112, 79, 80),
    "Festival": (251, 233, 108),
    "Feta": (240, 252, 234),
    "Fiery Orange": (179, 82, 19),
    "Finch": (98, 102, 73),
    "Finlandia": (85, 109, 86),
    "Finn": (105, 45, 84),
    "Fiord": (64, 81, 105),
    "Fire": (170, 66, 3),
    "Fire Bush": (232, 153, 40),
    "Firefly": (14, 42, 48),
    "Flame Pea": (218, 91, 56),
    "Flamenco": (255, 125, 7),
    "Flamingo": (242, 85, 42),
    "Flax": (238, 220, 130),
    "Flax Smoke": (123, 130, 101),
    "Flesh": (255, 203, 164),
    "Flint": (111, 106, 97),
    "Flirt": (162, 0, 109),
    "Flush Mahogany": (202, 52, 53),
    "Flush Orange": (255, 127, 0),
    "Foam": (216, 252, 250),
    "Fog": (215, 208, 255),
    "Foggy Gray": (203, 202, 182),
    "Forest Green": (34, 139, 34),
    "Forget Me Not": (255, 241, 238),
    "Fountain Blue": (86, 180, 190),
    "Frangipani": (255, 222, 179),
    "French Gray": (189, 189, 198),
    "French Lilac": (236, 199, 238),
    "French Pass": (189, 237, 253),
    "French Rose": (246, 74, 138),
    "Fresh Eggplant": (153, 0, 102),
    "Friar Gray": (128, 126, 121),
    "Fringy Flower": (177, 226, 193),
    "Froly": (245, 117, 132),
    "Frost": (237, 245, 221),
    "Frosted Mint": (219, 255, 248),
    "Frostee": (228, 246, 231),
    "Fruit Salad": (79, 157, 93),
    "Fuchsia Blue": (122, 88, 193),
    "Fuchsia Pink": (193, 84, 193),
    "Fuego": (190, 222, 13),
    "Fuel Yellow": (236, 169, 39),
    "Fun Blue": (25, 89, 168),
    "Fun Green": (1, 109, 57),
    "Fuscous Gray": (84, 83, 77),
    "Fuzzy Wuzzy Brown": (196, 86, 85),
    "Gable Green": (22, 53, 49),
    "Gallery": (239, 239, 239),
    "Galliano": (220, 178, 12),
    "Gamboge": (228, 155, 15),
    "Geebung": (209, 143, 27),
    "Genoa": (21, 115, 107),
    "Geraldine": (251, 137, 137),
    "Geyser": (212, 223, 226),
    "Ghost": (199, 201, 213),
    "Gigas": (82, 60, 148),
    "Gimblet": (184, 181, 106),
    "Gin": (232, 242, 235),
    "Gin Fizz": (255, 249, 226),
    "Givry": (248, 228, 191),
    "Glacier": (128, 179, 196),
    "Glade Green": (97, 132, 95),
    "Go Ben": (114, 109, 78),
    "Goblin": (61, 125, 82),
    "Gold": (255, 215, 0),
    "Gold Drop": (241, 130, 0),
    "Gold Sand": (230, 190, 138),
    "Gold Tips": (222, 186, 19),
    "Golden Bell": (226, 137, 19),
    "Golden Dream": (240, 213, 45),
    "Golden Fizz": (245, 251, 61),
    "Golden Glow": (253, 226, 149),
    "Golden Grass": (218, 165, 32),
    "Golden Sand": (240, 219, 125),
    "Golden Tainoi": (255, 204, 92),
    "Goldenrod": (252, 214, 103),
    "Gondola": (38, 20, 20),
    "Gordons Green": (11, 17, 7),
    "Gorse": (255, 241, 79),
    "Gossamer": (6, 155, 129),
    "Gossip": (210, 248, 176),
    "Gothic": (109, 146, 161),
    "Governor Bay": (47, 60, 179),
    "Grain Brown": (228, 213, 183),
    "Grandis": (255, 211, 140),
    "Granite Green": (141, 137, 116),
    "Granny Apple": (213, 246, 227),
    "Granny Smith": (132, 160, 160),
    "Granny Smith Apple": (157, 224, 147),
    "Grape": (56, 26, 81),
    "Graphite": (37, 22, 7),
    "Gravel": (74, 68, 75),
    "Gray": (128, 128, 128),
    "Gray Asparagus": (70, 89, 69),
    "Gray Chateau": (162, 170, 179),
    "Gray Nickel": (195, 195, 189),
    "Gray Nurse": (231, 236, 230),
    "Gray Olive": (169, 164, 145),
    "Gray Suit": (193, 190, 205),
    "Green": (0, 255, 0),
    "Green Haze": (1, 163, 104),
    "Green House": (36, 80, 15),
    "Green Kelp": (37, 49, 28),
    "Green Leaf": (67, 106, 13),
    "Green Mist": (203, 211, 176),
    "Green Pea": (29, 97, 66),
    "Green Smoke": (164, 175, 110),
    "Green Spring": (184, 193, 177),
    "Green Vogue": (3, 43, 82),
    "Green Waterloo": (16, 20, 5),
    "Green White": (232, 235, 224),
    "Green Yellow": (173, 255, 47),
    "Grenadier": (213, 70, 0),
    "Guardsman Red": (186, 1, 1),
    "Gulf Blue": (5, 22, 87),
    "Gulf Stream": (128, 179, 174),
    "Gull Gray": (157, 172, 183),
    "Gum Leaf": (182, 211, 191),
    "Gumbo": (124, 161, 166),
    "Gun Powder": (65, 66, 87),
    "Gunsmoke": (130, 134, 133),
    "Gurkha": (154, 149, 119),
    "Hacienda": (152, 129, 27),
    "Hairy Heath": (107, 42, 20),
    "Haiti": (27, 16, 53),
    "Half Baked": (133, 196, 204),
    "Half Colonial White": (253, 246, 211),
    "Half Dutch White": (254, 247, 222),
    "Half Spanish White": (254, 244, 219),
    "Half and Half": (255, 254, 225),
    "Hampton": (229, 216, 175),
    "Harlequin": (63, 255, 0),
    "Harp": (230, 242, 234),
    "Harvest Gold": (224, 185, 116),
    "Havelock Blue": (85, 144, 217),
    "Hawaiian Tan": (157, 86, 22),
    "Hawkes Blue": (212, 226, 252),
    "Heath": (84, 16, 18),
    "Heather": (183, 195, 208),
    "Heathered Gray": (182, 176, 149),
    "Heavy Metal": (43, 50, 40),
    "Heliotrope": (223, 115, 255),
    "Hemlock": (94, 93, 59),
    "Hemp": (144, 120, 116),
    "Hibiscus": (182, 49, 108),
    "Highland": (111, 142, 99),
    "Hillary": (172, 165, 134),
    "Himalaya": (106, 93, 27),
    "Hint of Green": (230, 255, 233),
    "Hint of Red": (251, 249, 249),
    "Hint of Yellow": (250, 253, 228),
    "Hippie Blue": (88, 154, 175),
    "Hippie Green": (83, 130, 75),
    "Hippie Pink": (174, 69, 96),
    "Hit Gray": (161, 173, 181),
    "Hit Pink": (255, 171, 129),
    "Hokey Pokey": (200, 165, 40),
    "Hoki": (101, 134, 159),
    "Holly": (1, 29, 19),
    "Hollywood Cerise": (244, 0, 161),
    "Honey Flower": (79, 28, 112),
    "Honeysuckle": (237, 252, 132),
    "Hopbush": (208, 109, 161),
    "Horizon": (90, 135, 160),
    "Horses Neck": (96, 73, 19),
    "Hot Cinnamon": (210, 105, 30),
    "Hot Pink": (255, 105, 180),
    "Hot Toddy": (179, 128, 7),
    "Humming Bird": (207, 249, 243),
    "Hunter Green": (22, 29, 16),
    "Hurricane": (135, 124, 123),
    "Husk": (183, 164, 88),
    "Ice Cold": (177, 244, 231),
    "Iceberg": (218, 244, 240),
    "Illusion": (246, 164, 201),
    "Inch Worm": (176, 227, 19),
    "Indian Khaki": (195, 176, 145),
    "Indian Tan": (77, 30, 1),
    "Indigo": (79, 105, 198),
    "Indochine": (194, 107, 3),
    "International Klein Blue": (0, 47, 167),
    "International Orange": (255, 79, 0),
    "Irish Coffee": (95, 61, 38),
    "Iroko": (67, 49, 32),
    "Iron": (212, 215, 217),
    "Ironside Gray": (103, 102, 98),
    "Ironstone": (134, 72, 60),
    "Island Spice": (255, 252, 238),
    "Ivory": (255, 255, 240),
    "Jacaranda": (46, 3, 41),
    "Jacarta": (58, 42, 106),
    "Jacko Bean": (46, 25, 5),
    "Jacksons Purple": (32, 32, 141),
    "Jade": (0, 168, 107),
    "Jaffa": (239, 134, 63),
    "Jagged Ice": (194, 232, 229),
    "Jagger": (53, 14, 87),
    "Jaguar": (8, 1, 16),
    "Jambalaya": (91, 48, 19),
    "Janna": (244, 235, 211),
    "Japanese Laurel": (10, 105, 6),
    "Japanese Maple": (120, 1, 9),
    "Japonica": (216, 124, 99),
    "Java": (31, 194, 194),
    "Jazzberry Jam": (165, 11, 94),
    "Jelly Bean": (41, 123, 154),
    "Jet Stream": (181, 210, 206),
    "Jewel": (18, 107, 64),
    "Jon": (59, 31, 31),
    "Jonquil": (238, 255, 154),
    "Jordy Blue": (138, 185, 241),
    "Judge Gray": (84, 67, 51),
    "Jumbo": (124, 123, 130),
    "Jungle Green": (41, 171, 135),
    "Jungle Mist": (180, 207, 211),
    "Juniper": (109, 146, 146),
    "Just Right": (236, 205, 185),
    "Kabul": (94, 72, 62),
    "Kaitoke Green": (0, 70, 32),
    "Kangaroo": (198, 200, 189),
    "Karaka": (30, 22, 9),
    "Karry": (255, 234, 212),
    "Kashmir Blue": (80, 112, 150),
    "Kelp": (69, 73, 54),
    "Kenyan Copper": (124, 28, 5),
    "Keppel": (58, 176, 158),
    "Key Lime Pie": (191, 201, 33),
    "Khaki": (240, 230, 140),
    "Kidnapper": (225, 234, 212),
    "Kilamanjaro": (36, 12, 2),
    "Killarney": (58, 106, 71),
    "Kimberly": (115, 108, 159),
    "Kingfisher Daisy": (62, 4, 128),
    "Kobi": (231, 159, 196),
    "Kokoda": (110, 109, 87),
    "Korma": (143, 75, 14),
    "Koromiko": (255, 189, 95),
    "Kournikova": (255, 231, 114),
    "Kumera": (136, 98, 33),
    "La Palma": (54, 135, 22),
    "La Rioja": (179, 193, 16),
    "Las Palmas": (198, 230, 16),
    "Laser": (200, 181, 104),
    "Laser Lemon": (255, 255, 102),
    "Laurel": (116, 147, 120),
    "Lavender": (181, 126, 220),
    "Lavender Gray": (189, 187, 215),
    "Lavender Magenta": (238, 130, 238),
    "Lavender Pink": (251, 174, 210),
    "Lavender Purple": (150, 123, 182),
    "Lavender Rose": (251, 160, 227),
    "Lavender blush": (255, 240, 245),
    "Leather": (150, 112, 89),
    "Lemon": (253, 233, 16),
    "Lemon Chiffon": (255, 250, 205),
    "Lemon Ginger": (172, 158, 34),
    "Lemon Grass": (155, 158, 143),
    "Light Apricot": (253, 213, 177),
    "Light Orchid": (226, 156, 210),
    "Light Wisteria": (201, 160, 220),
    "Lightning Yellow": (252, 192, 30),
    "Lilac": (200, 162, 200),
    "Lilac Bush": (152, 116, 211),
    "Lily": (200, 170, 191),
    "Lily White": (231, 248, 255),
    "Lima": (118, 189, 23),
    "Lime": (191, 255, 0),
    "Limeade": (111, 157, 2),
    "Limed Ash": (116, 125, 99),
    "Limed Oak": (172, 138, 86),
    "Limed Spruce": (57, 72, 81),
    "Linen": (250, 240, 230),
    "Link Water": (217, 228, 245),
    "Lipstick": (171, 5, 99),
    "Lisbon Brown": (66, 57, 33),
    "Livid Brown": (77, 40, 46),
    "Loafer": (238, 244, 222),
    "Loblolly": (189, 201, 206),
    "Lochinvar": (44, 140, 132),
    "Lochmara": (0, 126, 199),
    "Locust": (168, 175, 142),
    "Log Cabin": (36, 42, 29),
    "Logan": (170, 169, 205),
    "Lola": (223, 207, 219),
    "London Hue": (190, 166, 195),
    "Lonestar": (109, 1, 1),
    "Lotus": (134, 60, 60),
    "Loulou": (70, 11, 65),
    "Lucky": (175, 159, 28),
    "Lucky Point": (26, 26, 104),
    "Lunar Green": (60, 73, 58),
    "Luxor Gold": (167, 136, 44),
    "Lynch": (105, 126, 154),
    "Mabel": (217, 247, 255),
    "Macaroni and Cheese": (255, 185, 123),
    "Madang": (183, 240, 190),
    "Madison": (9, 37, 93),
    "Madras": (63, 48, 2),
    "Magenta / Fuchsia": (255, 0, 255),
    "Magic Mint": (170, 240, 209),
    "Magnolia": (248, 244, 255),
    "Mahogany": (78, 6, 6),
    "Mai Tai": (176, 102, 8),
    "Maize": (245, 213, 160),
    "Makara": (137, 125, 109),
    "Mako": (68, 73, 84),
    "Malachite": (11, 218, 81),
    "Malibu": (125, 200, 247),
    "Mallard": (35, 52, 24),
    "Malta": (189, 178, 161),
    "Mamba": (142, 129, 144),
    "Manatee": (141, 144, 161),
    "Mandalay": (173, 120, 27),
    "Mandy": (226, 84, 101),
    "Mandys Pink": (242, 195, 178),
    "Mango Tango": (231, 114, 0),
    "Manhattan": (245, 201, 153),
    "Mantis": (116, 195, 101),
    "Mantle": (139, 156, 144),
    "Manz": (238, 239, 120),
    "Mardi Gras": (53, 0, 54),
    "Marigold": (185, 141, 40),
    "Marigold Yellow": (251, 232, 112),
    "Mariner": (40, 106, 205),
    "Maroon": (128, 0, 0),
    "Maroon Flush": (195, 33, 72),
    "Maroon Oak": (82, 12, 23),
    "Marshland": (11, 15, 8),
    "Martini": (175, 160, 158),
    "Martinique": (54, 48, 80),
    "Marzipan": (248, 219, 157),
    "Masala": (64, 59, 56),
    "Matisse": (27, 101, 157),
    "Matrix": (176, 93, 84),
    "Matterhorn": (78, 59, 65),
    "Mauve": (224, 176, 255),
    "Mauvelous": (240, 145, 169),
    "Maverick": (216, 194, 213),
    "Medium Carmine": (175, 64, 53),
    "Medium Purple": (147, 112, 219),
    "Medium Red Violet": (187, 51, 133),
    "Melanie": (228, 194, 213),
    "Melanzane": (48, 5, 41),
    "Melon": (254, 186, 173),
    "Melrose": (199, 193, 255),
    "Mercury": (229, 229, 229),
    "Merino": (246, 240, 230),
    "Merlin": (65, 60, 55),
    "Merlot": (131, 25, 35),
    "Metallic Bronze": (73, 55, 27),
    "Metallic Copper": (113, 41, 29),
    "Meteor": (208, 125, 18),
    "Meteorite": (60, 31, 118),
    "Mexican Red": (167, 37, 37),
    "Mid Gray": (95, 95, 110),
    "Midnight": (1, 22, 53),
    "Midnight Blue": (0, 51, 102),
    "Midnight Moss": (4, 16, 4),
    "Mikado": (45, 37, 16),
    "Milan": (250, 255, 164),
    "Milano Red": (184, 17, 4),
    "Milk Punch": (255, 246, 212),
    "Millbrook": (89, 68, 51),
    "Mimosa": (248, 253, 211),
    "Mindaro": (227, 249, 136),
    "Mine Shaft": (50, 50, 50),
    "Mineral Green": (63, 93, 83),
    "Ming": (54, 116, 125),
    "Minsk": (63, 48, 127),
    "Mint Green": (152, 255, 152),
    "Mint Julep": (241, 238, 193),
    "Mint Tulip": (196, 244, 235),
    "Mirage": (22, 25, 40),
    "Mischka": (209, 210, 221),
    "Mist Gray": (196, 196, 188),
    "Mobster": (127, 117, 137),
    "Moccaccino": (110, 29, 20),
    "Mocha": (120, 45, 25),
    "Mojo": (192, 71, 55),
    "Mona Lisa": (255, 161, 148),
    "Monarch": (139, 7, 35),
    "Mondo": (74, 60, 48),
    "Mongoose": (181, 162, 127),
    "Monsoon": (138, 131, 137),
    "Monte Carlo": (131, 208, 198),
    "Monza": (199, 3, 30),
    "Moody Blue": (127, 118, 211),
    "Moon Glow": (252, 254, 218),
    "Moon Mist": (220, 221, 204),
    "Moon Raker": (214, 206, 246),
    "Morning Glory": (158, 222, 224),
    "Morocco Brown": (68, 29, 0),
    "Mortar": (80, 67, 81),
    "Mosque": (3, 106, 110),
    "Moss Green": (173, 223, 173),
    "Mountain Meadow": (26, 179, 133),
    "Mountain Mist": (149, 147, 150),
    "Mountbatten Pink": (153, 122, 141),
    "Muddy Waters": (183, 142, 92),
    "Muesli": (170, 139, 91),
    "Mulberry": (197, 75, 140),
    "Mulberry Wood": (92, 5, 54),
    "Mule Fawn": (140, 71, 47),
    "Mulled Wine": (78, 69, 98),
    "Mustard": (255, 219, 88),
    "My Pink": (214, 145, 136),
    "My Sin": (255, 179, 31),
    "Mystic": (226, 235, 237),
    "Nandor": (75, 93, 82),
    "Napa": (172, 164, 148),
    "Narvik": (237, 249, 241),
    "Natural Gray": (139, 134, 128),
    "Navajo White": (255, 222, 173),
    "Navy Blue": (0, 0, 128),
    "Nebula": (203, 219, 214),
    "Negroni": (255, 226, 197),
    "Neon Carrot": (255, 153, 51),
    "Nepal": (142, 171, 193),
    "Neptune": (124, 183, 187),
    "Nero": (20, 6, 0),
    "Nevada": (100, 110, 117),
    "New Orleans": (243, 214, 157),
    "New York Pink": (215, 131, 127),
    "Niagara": (6, 161, 137),
    "Night Rider": (31, 18, 15),
    "Night Shadz": (170, 55, 90),
    "Nile Blue": (25, 55, 81),
    "Nobel": (183, 177, 177),
    "Nomad": (186, 177, 162),
    "Norway": (168, 189, 159),
    "Nugget": (197, 153, 34),
    "Nutmeg": (129, 66, 44),
    "Nutmeg Wood Finish": (104, 54, 0),
    "Oasis": (254, 239, 206),
    "Observatory": (2, 134, 111),
    "Ocean Green": (65, 170, 120),
    "Ochre": (204, 119, 34),
    "Off Green": (230, 248, 243),
    "Off Yellow": (254, 249, 227),
    "Oil": (40, 30, 21),
    "Old Brick": (144, 30, 30),
    "Old Copper": (114, 74, 47),
    "Old Gold": (207, 181, 59),
    "Old Lace": (253, 245, 230),
    "Old Lavender": (121, 104, 120),
    "Old Rose": (192, 128, 129),
    "Olive": (128, 128, 0),
    "Olive Drab": (107, 142, 35),
    "Olive Green": (181, 179, 92),
    "Olive Haze": (139, 132, 112),
    "Olivetone": (113, 110, 16),
    "Olivine": (154, 185, 115),
    "Onahau": (205, 244, 255),
    "Onion": (47, 39, 14),
    "Opal": (169, 198, 194),
    "Opium": (142, 111, 112),
    "Oracle": (55, 116, 117),
    "Orange": (255, 104, 31),
    "Orange Peel": (255, 160, 0),
    "Orange Roughy": (196, 87, 25),
    "Orange White": (254, 252, 237),
    "Orchid": (218, 112, 214),
    "Orchid White": (255, 253, 243),
    "Oregon": (155, 71, 3),
    "Orient": (1, 94, 133),
    "Oriental Pink": (198, 145, 145),
    "Orinoco": (243, 251, 212),
    "Oslo Gray": (135, 141, 145),
    "Ottoman": (233, 248, 237),
    "Outer Space": (45, 56, 58),
    "Outrageous Orange": (255, 96, 55),
    "Oxford Blue": (56, 69, 85),
    "Oxley": (119, 158, 134),
    "Oyster Bay": (218, 250, 255),
    "Oyster Pink": (233, 206, 205),
    "Paarl": (166, 85, 41),
    "Pablo": (119, 111, 97),
    "Pacific Blue": (0, 157, 196),
    "Pacifika": (119, 129, 32),
    "Paco": (65, 31, 16),
    "Padua": (173, 230, 196),
    "Pale Canary": (255, 255, 153),
    "Pale Leaf": (192, 211, 185),
    "Pale Oyster": (152, 141, 119),
    "Pale Prim": (253, 254, 184),
    "Pale Rose": (255, 225, 242),
    "Pale Sky": (110, 119, 131),
    "Pale Slate": (195, 191, 193),
    "Palm Green": (9, 35, 15),
    "Palm Leaf": (25, 51, 14),
    "Pampas": (244, 242, 238),
    "Panache": (234, 246, 238),
    "Pancho": (237, 205, 171),
    "Papaya Whip": (255, 239, 213),
    "Paprika": (141, 2, 38),
    "Paradiso": (49, 125, 130),
    "Parchment": (241, 233, 210),
    "Paris Daisy": (255, 244, 110),
    "Paris M": (38, 5, 106),
    "Paris White": (202, 220, 212),
    "Parsley": (19, 79, 25),
    "Pastel Green": (119, 221, 119),
    "Pastel Pink": (255, 209, 220),
    "Patina": (99, 154, 143),
    "Pattens Blue": (222, 245, 255),
    "Paua": (38, 3, 104),
    "Pavlova": (215, 196, 152),
    "Peach": (255, 229, 180),
    "Peach Cream": (255, 240, 219),
    "Peach Orange": (255, 204, 153),
    "Peach Schnapps": (255, 220, 214),
    "Peach Yellow": (250, 223, 173),
    "Peanut": (120, 47, 22),
    "Pear": (209, 226, 49),
    "Pearl Bush": (232, 224, 213),
    "Pearl Lusta": (252, 244, 220),
    "Peat": (113, 107, 86),
    "Pelorous": (62, 171, 191),
    "Peppermint": (227, 245, 225),
    "Perano": (169, 190, 242),
    "Perfume": (208, 190, 248),
    "Periglacial Blue": (225, 230, 214),
    "Periwinkle": (204, 204, 255),
    "Periwinkle Gray": (195, 205, 230),
    "Persian Blue": (28, 57, 187),
    "Persian Green": (0, 166, 147),
    "Persian Indigo": (50, 18, 122),
    "Persian Pink": (247, 127, 190),
    "Persian Plum": (112, 28, 28),
    "Persian Red": (204, 51, 51),
    "Persian Rose": (254, 40, 162),
    "Persimmon": (255, 107, 83),
    "Peru Tan": (127, 58, 2),
    "Pesto": (124, 118, 49),
    "Petite Orchid": (219, 150, 144),
    "Pewter": (150, 168, 161),
    "Pharlap": (163, 128, 123),
    "Picasso": (255, 243, 157),
    "Pickled Bean": (110, 72, 38),
    "Pickled Bluewood": (49, 68, 89),
    "Picton Blue": (69, 177, 232),
    "Pig Pink": (253, 215, 228),
    "Pigeon Post": (175, 189, 217),
    "Pigment Indigo": (75, 0, 130),
    "Pine Cone": (109, 94, 84),
    "Pine Glade": (199, 205, 144),
    "Pine Green": (1, 121, 111),
    "Pine Tree": (23, 31, 4),
    "Pink": (255, 192, 203),
    "Pink Flamingo": (255, 102, 255),
    "Pink Flare": (225, 192, 200),
    "Pink Lace": (255, 221, 244),
    "Pink Lady": (255, 241, 216),
    "Pink Salmon": (255, 145, 164),
    "Pink Swan": (190, 181, 183),
    "Piper": (201, 99, 35),
    "Pipi": (254, 244, 204),
    "Pippin": (255, 225, 223),
    "Pirate Gold": (186, 127, 3),
    "Pistachio": (157, 194, 9),
    "Pixie Green": (192, 216, 182),
    "Pizazz": (255, 144, 0),
    "Pizza": (201, 148, 21),
    "Plantation": (39, 80, 75),
    "Plum": (132, 49, 121),
    "Pohutukawa": (143, 2, 28),
    "Polar": (229, 249, 246),
    "Polo Blue": (141, 168, 204),
    "Pomegranate": (243, 71, 35),
    "Pompadour": (102, 0, 69),
    "Porcelain": (239, 242, 243),
    "Porsche": (234, 174, 105),
    "Port Gore": (37, 31, 79),
    "Portafino": (255, 255, 180),
    "Portage": (139, 159, 238),
    "Portica": (249, 230, 99),
    "Pot Pourri": (245, 231, 226),
    "Potters Clay": (140, 87, 56),
    "Powder Ash": (188, 201, 194),
    "Powder Blue": (176, 224, 230),
    "Prairie Sand": (154, 56, 32),
    "Prelude": (208, 192, 229),
    "Prim": (240, 226, 236),
    "Primrose": (237, 234, 153),
    "Provincial Pink": (254, 245, 241),
    "Prussian Blue": (0, 49, 83),
    "Puce": (204, 136, 153),
    "Pueblo": (125, 44, 20),
    "Puerto Rico": (63, 193, 170),
    "Pumice": (194, 202, 196),
    "Pumpkin": (255, 117, 24),
    "Pumpkin Skin": (177, 97, 11),
    "Punch": (220, 67, 51),
    "Punga": (77, 61, 20),
    "Purple": (102, 0, 153),
    "Purple Heart": (101, 45, 193),
    "Purple Mountain's Majesty": (150, 120, 182),
    "Purple Pizzazz": (255, 0, 204),
    "Putty": (231, 205, 140),
    "Quarter Pearl Lusta": (255, 253, 244),
    "Quarter Spanish White": (247, 242, 225),
    "Quicksand": (189, 151, 142),
    "Quill Gray": (214, 214, 209),
    "Quincy": (98, 63, 45),
    "Racing Green": (12, 25, 17),
    "Radical Red": (255, 53, 94),
    "Raffia": (234, 218, 184),
    "Rainee": (185, 200, 172),
    "Rajah": (247, 182, 104),
    "Rangitoto": (46, 50, 34),
    "Rangoon Green": (28, 30, 19),
    "Raven": (114, 123, 137),
    "Raw Sienna": (210, 125, 70),
    "Raw Umber": (115, 74, 18),
    "Razzle Dazzle Rose": (255, 51, 204),
    "Razzmatazz": (227, 11, 92),
    "Rebel": (60, 18, 6),
    "Red": (255, 0, 0),
    "Red Beech": (123, 56, 1),
    "Red Berry": (142, 0, 0),
    "Red Damask": (218, 106, 65),
    "Red Devil": (134, 1, 17),
    "Red Orange": (255, 63, 52),
    "Red Oxide": (110, 9, 2),
    "Red Ribbon": (237, 10, 63),
    "Red Robin": (128, 52, 31),
    "Red Stage": (208, 95, 4),
    "Red Violet": (199, 21, 133),
    "Redwood": (93, 30, 15),
    "Reef": (201, 255, 162),
    "Reef Gold": (159, 130, 28),
    "Regal Blue": (1, 63, 106),
    "Regent Gray": (134, 148, 159),
    "Regent St Blue": (170, 214, 230),
    "Remy": (254, 235, 243),
    "Reno Sand": (168, 101, 21),
    "Resolution Blue": (0, 35, 135),
    "Revolver": (44, 22, 50),
    "Rhino": (46, 63, 98),
    "Rice Cake": (255, 254, 240),
    "Rice Flower": (238, 255, 226),
    "Rich Gold": (168, 83, 7),
    "Rio Grande": (187, 208, 9),
    "Ripe Lemon": (244, 216, 28),
    "Ripe Plum": (65, 0, 86),
    "Riptide": (139, 230, 216),
    "River Bed": (67, 76, 89),
    "Rob Roy": (234, 198, 116),
    "Robin's Egg Blue": (0, 204, 204),
    "Rock": (77, 56, 51),
    "Rock Blue": (158, 177, 205),
    "Rock Spray": (186, 69, 12),
    "Rodeo Dust": (201, 178, 155),
    "Rolling Stone": (116, 125, 131),
    "Roman": (222, 99, 96),
    "Roman Coffee": (121, 93, 76),
    "Romance": (255, 254, 253),
    "Romantic": (255, 210, 183),
    "Ronchi": (236, 197, 78),
    "Roof Terracotta": (166, 47, 32),
    "Rope": (142, 77, 30),
    "Rose": (255, 0, 127),
    "Rose Bud": (251, 178, 163),
    "Rose Bud Cherry": (128, 11, 71),
    "Rose Fog": (231, 188, 180),
    "Rose White": (255, 246, 245),
    "Rose of Sharon": (191, 85, 0),
    "Rosewood": (101, 0, 11),
    "Roti": (198, 168, 75),
    "Rouge": (162, 59, 108),
    "Royal Blue": (65, 105, 225),
    "Royal Heath": (171, 52, 114),
    "Royal Purple": (107, 63, 160),
    "Rum": (121, 105, 137),
    "Rum Swizzle": (249, 248, 228),
    "Russet": (128, 70, 27),
    "Russett": (117, 90, 87),
    "Rust": (183, 65, 14),
    "Rustic Red": (72, 4, 4),
    "Rusty Nail": (134, 86, 10),
    "Saddle": (76, 48, 36),
    "Saddle Brown": (88, 52, 1),
    "Saffron": (244, 196, 48),
    "Saffron Mango": (249, 191, 88),
    "Sage": (158, 165, 135),
    "Sahara": (183, 162, 20),
    "Sahara Sand": (241, 231, 136),
    "Sail": (184, 224, 249),
    "Salem": (9, 127, 75),
    "Salmon": (255, 140, 105),
    "Salomie": (254, 219, 141),
    "Salt Box": (104, 94, 110),
    "Saltpan": (241, 247, 242),
    "Sambuca": (58, 32, 16),
    "San Felix": (11, 98, 7),
    "San Juan": (48, 75, 106),
    "San Marino": (69, 108, 172),
    "Sand Dune": (130, 111, 101),
    "Sandal": (170, 141, 111),
    "Sandrift": (171, 145, 122),
    "Sandstone": (121, 109, 98),
    "Sandwisp": (245, 231, 162),
    "Sandy Beach": (255, 234, 200),
    "Sandy brown": (244, 164, 96),
    "Sangria": (146, 0, 10),
    "Sanguine Brown": (141, 61, 56),
    "Santa Fe": (177, 109, 82),
    "Santas Gray": (159, 160, 177),
    "Sapling": (222, 212, 164),
    "Sapphire": (47, 81, 158),
    "Saratoga": (85, 91, 16),
    "Satin Linen": (230, 228, 212),
    "Sauvignon": (255, 245, 243),
    "Sazerac": (255, 244, 224),
    "Scampi": (103, 95, 166),
    "Scandal": (207, 250, 244),
    "Scarlet": (255, 36, 0),
    "Scarlet Gum": (67, 21, 96),
    "Scarlett": (149, 0, 21),
    "Scarpa Flow": (88, 85, 98),
    "Schist": (169, 180, 151),
    "School bus Yellow": (255, 216, 0),
    "Schooner": (139, 132, 126),
    "Science Blue": (0, 102, 204),
    "Scooter": (46, 191, 212),
    "Scorpion": (105, 95, 98),
    "Scotch Mist": (255, 251, 220),
    "Screamin' Green": (102, 255, 102),
    "Sea Buckthorn": (251, 161, 41),
    "Sea Green": (46, 139, 87),
    "Sea Mist": (197, 219, 202),
    "Sea Nymph": (120, 163, 156),
    "Sea Pink": (237, 152, 158),
    "Seagull": (128, 204, 234),
    "Seance": (115, 30, 143),
    "Seashell": (241, 241, 241),
    "Seashell Peach": (255, 245, 238),
    "Seaweed": (27, 47, 17),
    "Selago": (240, 238, 253),
    "Selective Yellow": (255, 186, 0),
    "Sepia": (112, 66, 20),
    "Sepia Black": (43, 2, 2),
    "Sepia Skin": (158, 91, 64),
    "Serenade": (255, 244, 232),
    "Shadow": (131, 112, 80),
    "Shadow Green": (154, 194, 184),
    "Shady Lady": (170, 165, 169),
    "Shakespeare": (78, 171, 209),
    "Shalimar": (251, 255, 186),
    "Shamrock": (51, 204, 153),
    "Shark": (37, 39, 44),
    "Sherpa Blue": (0, 73, 80),
    "Sherwood Green": (2, 64, 44),
    "Shilo": (232, 185, 179),
    "Shingle Fawn": (107, 78, 49),
    "Ship Cove": (120, 139, 186),
    "Ship Gray": (62, 58, 68),
    "Shiraz": (178, 9, 49),
    "Shocking": (226, 146, 192),
    "Shocking Pink": (252, 15, 192),
    "Shuttle Gray": (95, 102, 114),
    "Siam": (100, 106, 84),
    "Sidecar": (243, 231, 187),
    "Silk": (189, 177, 168),
    "Silver": (192, 192, 192),
    "Silver Chalice": (172, 172, 172),
    "Silver Rust": (201, 192, 187),
    "Silver Sand": (191, 193, 194),
    "Silver Tree": (102, 181, 143),
    "Sinbad": (159, 215, 211),
    "Siren": (122, 1, 58),
    "Sirocco": (113, 128, 128),
    "Sisal": (211, 203, 186),
    "Skeptic": (202, 230, 218),
    "Sky Blue": (118, 215, 234),
    "Slate Gray": (112, 128, 144),
    "Smalt": (0, 51, 153),
    "Smalt Blue": (81, 128, 143),
    "Smoky": (96, 91, 115),
    "Snow Drift": (247, 250, 247),
    "Snow Flurry": (228, 255, 209),
    "Snowy Mint": (214, 255, 219),
    "Snuff": (226, 216, 237),
    "Soapstone": (255, 251, 249),
    "Soft Amber": (209, 198, 180),
    "Soft Peach": (245, 237, 239),
    "Solid Pink": (137, 56, 67),
    "Solitaire": (254, 248, 226),
    "Solitude": (234, 246, 255),
    "Sorbus": (253, 124, 7),
    "Sorrell Brown": (206, 185, 143),
    "Soya Bean": (106, 96, 81),
    "Spanish Green": (129, 152, 133),
    "Spectra": (47, 90, 87),
    "Spice": (106, 68, 46),
    "Spicy Mix": (136, 83, 66),
    "Spicy Mustard": (116, 100, 13),
    "Spicy Pink": (129, 110, 113),
    "Spindle": (182, 209, 234),
    "Spray": (121, 222, 236),
    "Spring Green": (0, 255, 127),
    "Spring Leaves": (87, 131, 99),
    "Spring Rain": (172, 203, 177),
    "Spring Sun": (246, 255, 220),
    "Spring Wood": (248, 246, 241),
    "Sprout": (193, 215, 176),
    "Spun Pearl": (170, 171, 183),
    "Squirrel": (143, 129, 118),
    "St Tropaz": (45, 86, 155),
    "Stack": (138, 143, 138),
    "Star Dust": (159, 159, 156),
    "Stark White": (229, 215, 189),
    "Starship": (236, 242, 69),
    "Steel Blue": (70, 130, 180),
    "Steel Gray": (38, 35, 53),
    "Stiletto": (156, 51, 54),
    "Stonewall": (146, 133, 115),
    "Storm Dust": (100, 100, 99),
    "Storm Gray": (113, 116, 134),
    "Stratos": (0, 7, 65),
    "Straw": (212, 191, 141),
    "Strikemaster": (149, 99, 135),
    "Stromboli": (50, 93, 82),
    "Studio": (113, 74, 178),
    "Submarine": (186, 199, 201),
    "Sugar Cane": (249, 255, 246),
    "Sulu": (193, 240, 124),
    "Summer Green": (150, 187, 171),
    "Sun": (251, 172, 19),
    "Sundance": (201, 179, 91),
    "Sundown": (255, 177, 179),
    "Sunflower": (228, 212, 34),
    "Sunglo": (225, 104, 101),
    "Sunglow": (255, 204, 51),
    "Sunset Orange": (254, 76, 64),
    "Sunshade": (255, 158, 44),
    "Supernova": (255, 201, 1),
    "Surf": (187, 215, 193),
    "Surf Crest": (207, 229, 210),
    "Surfie Green": (12, 122, 121),
    "Sushi": (135, 171, 57),
    "Suva Gray": (136, 131, 135),
    "Swamp": (0, 27, 28),
    "Swamp Green": (172, 183, 142),
    "Swans Down": (220, 240, 234),
    "Sweet Corn": (251, 234, 140),
    "Sweet Pink": (253, 159, 162),
    "Swirl": (211, 205, 197),
    "Swiss Coffee": (221, 214, 213),
    "Sycamore": (144, 141, 57),
    "Tabasco": (160, 39, 18),
    "Tacao": (237, 179, 129),
    "Tacha": (214, 197, 98),
    "Tahiti Gold": (233, 124, 7),
    "Tahuna Sands": (238, 240, 200),
    "Tall Poppy": (179, 45, 41),
    "Tallow": (168, 165, 137),
    "Tamarillo": (153, 22, 19),
    "Tamarind": (52, 21, 21),
    "Tan": (210, 180, 140),
    "Tan Hide": (250, 157, 90),
    "Tana": (217, 220, 193),
    "Tangaroa": (3, 22, 60),
    "Tangerine": (242, 133, 0),
    "Tango": (237, 122, 28),
    "Tapa": (123, 120, 116),
    "Tapestry": (176, 94, 129),
    "Tara": (225, 246, 232),
    "Tarawera": (7, 58, 80),
    "Tasman": (207, 220, 207),
    "Taupe": (72, 60, 50),
    "Taupe Gray": (179, 175, 149),
    "Tawny Port": (105, 37, 69),
    "Te Papa Green": (30, 67, 60),
    "Tea": (193, 186, 176),
    "Tea Green": (208, 240, 192),
    "Teak": (177, 148, 97),
    "Teal": (0, 128, 128),
    "Teal Blue": (4, 66, 89),
    "Temptress": (59, 0, 11),
    "Tenn": (205, 87, 0),
    "Tequila": (255, 230, 199),
    "Terracotta": (226, 114, 91),
    "Texas": (248, 249, 156),
    "Texas Rose": (255, 181, 85),
    "Thatch": (182, 157, 152),
    "Thatch Green": (64, 61, 25),
    "Thistle": (216, 191, 216),
    "Thistle Green": (204, 202, 168),
    "Thunder": (51, 41, 47),
    "Thunderbird": (192, 43, 24),
    "Tia Maria": (193, 68, 14),
    "Tiara": (195, 209, 209),
    "Tiber": (6, 53, 55),
    "Tickle Me Pink": (252, 128, 165),
    "Tidal": (241, 255, 173),
    "Tide": (191, 184, 176),
    "Timber Green": (22, 50, 44),
    "Timberwolf": (217, 214, 207),
    "Titan White": (240, 238, 255),
    "Toast": (154, 110, 97),
    "Tobacco Brown": (113, 93, 71),
    "Toledo": (58, 0, 32),
    "Tolopea": (27, 2, 69),
    "Tom Thumb": (63, 88, 59),
    "Tonys Pink": (231, 159, 140),
    "Topaz": (124, 119, 138),
    "Torch Red": (253, 14, 53),
    "Torea Bay": (15, 45, 158),
    "Tory Blue": (20, 80, 170),
    "Tosca": (141, 63, 63),
    "Totem Pole": (153, 27, 7),
    "Tower Gray": (169, 189, 191),
    "Tradewind": (95, 179, 172),
    "Tranquil": (230, 255, 255),
    "Travertine": (255, 253, 232),
    "Tree Poppy": (252, 156, 29),
    "Treehouse": (59, 40, 32),
    "Trendy Green": (124, 136, 26),
    "Trendy Pink": (140, 100, 149),
    "Trinidad": (230, 78, 3),
    "Tropical Blue": (195, 221, 249),
    "Tropical Rain Forest": (0, 117, 94),
    "Trout": (74, 78, 90),
    "True V": (138, 115, 214),
    "Tuatara": (54, 53, 52),
    "Tuft Bush": (255, 221, 205),
    "Tulip Tree": (234, 179, 59),
    "Tumbleweed": (222, 166, 129),
    "Tuna": (53, 53, 66),
    "Tundora": (74, 66, 68),
    "Turbo": (250, 230, 0),
    "Turkish Rose": (181, 114, 129),
    "Turmeric": (202, 187, 72),
    "Turquoise": (48, 213, 200),
    "Turquoise Blue": (108, 218, 231),
    "Turtle Green": (42, 56, 11),
    "Tuscany": (189, 94, 46),
    "Tusk": (238, 243, 195),
    "Tussock": (197, 153, 75),
    "Tutu": (255, 241, 249),
    "Twilight": (228, 207, 222),
    "Twilight Blue": (238, 253, 255),
    "Twine": (194, 149, 93),
    "Tyrian Purple": (102, 2, 60),
    "Ultramarine": (18, 10, 143),
    "Valencia": (216, 68, 55),
    "Valentino": (53, 14, 66),
    "Valhalla": (43, 25, 79),
    "Van Cleef": (73, 23, 12),
    "Vanilla": (209, 190, 168),
    "Vanilla Ice": (243, 217, 223),
    "Varden": (255, 246, 223),
    "Venetian Red": (114, 1, 15),
    "Venice Blue": (5, 89, 137),
    "Venus": (146, 133, 144),
    "Verdigris": (93, 94, 55),
    "Verdun Green": (73, 84, 0),
    "Vermilion": (255, 77, 0),
    "Vesuvius": (177, 74, 11),
    "Victoria": (83, 68, 145),
    "Vida Loca": (84, 144, 25),
    "Viking": (100, 204, 219),
    "Vin Rouge": (152, 61, 97),
    "Viola": (203, 143, 169),
    "Violent Violet": (41, 12, 94),
    "Violet": (36, 10, 64),
    "Violet Eggplant": (153, 17, 153),
    "Violet Red": (247, 70, 138),
    "Viridian": (64, 130, 109),
    "Viridian Green": (103, 137, 117),
    "Vis Vis": (255, 239, 161),
    "Vista Blue": (143, 214, 180),
    "Vista White": (252, 248, 247),
    "Vivid Tangerine": (255, 153, 128),
    "Vivid Violet": (128, 55, 144),
    "Voodoo": (83, 52, 85),
    "Vulcan": (16, 18, 29),
    "Wafer": (222, 203, 198),
    "Waikawa Gray": (90, 110, 156),
    "Waiouru": (54, 60, 13),
    "Walnut": (119, 63, 26),
    "Wasabi": (120, 138, 37),
    "Water Leaf": (161, 233, 222),
    "Watercourse": (5, 111, 87),
    "Waterloo ": (123, 124, 148),
    "Wattle": (220, 215, 71),
    "Watusi": (255, 221, 207),
    "Wax Flower": (255, 192, 168),
    "We Peep": (247, 219, 230),
    "Web Orange": (255, 165, 0),
    "Wedgewood": (78, 127, 158),
    "Well Read": (180, 51, 50),
    "West Coast": (98, 81, 25),
    "West Side": (255, 145, 15),
    "Westar": (220, 217, 210),
    "Wewak": (241, 155, 171),
    "Wheat": (245, 222, 179),
    "Wheatfield": (243, 237, 207),
    "Whiskey": (213, 154, 111),
    "Whisper": (247, 245, 250),
    "White": (255, 255, 255),
    "White Ice": (221, 249, 241),
    "White Lilac": (248, 247, 252),
    "White Linen": (248, 240, 232),
    "White Pointer": (254, 248, 255),
    "White Rock": (234, 232, 212),
    "Wild Blue Yonder": (122, 137, 184),
    "Wild Rice": (236, 224, 144),
    "Wild Sand": (244, 244, 244),
    "Wild Strawberry": (255, 51, 153),
    "Wild Watermelon": (253, 91, 120),
    "Wild Willow": (185, 196, 106),
    "William": (58, 104, 108),
    "Willow Brook": (223, 236, 218),
    "Willow Grove": (101, 116, 93),
    "Windsor": (60, 8, 120),
    "Wine Berry": (89, 29, 53),
    "Winter Hazel": (213, 209, 149),
    "Wisp Pink": (254, 244, 248),
    "Wisteria": (151, 113, 181),
    "Wistful": (164, 166, 211),
    "Witch Haze": (255, 252, 153),
    "Wood Bark": (38, 17, 5),
    "Woodland": (77, 83, 40),
    "Woodrush": (48, 42, 15),
    "Woodsmoke": (12, 13, 15),
    "Woody Brown": (72, 49, 49),
    "Xanadu": (115, 134, 120),
    "Yellow": (255, 255, 0),
    "Yellow Green": (197, 225, 122),
    "Yellow Metal": (113, 99, 56),
    "Yellow Orange": (255, 174, 66),
    "Yellow Sea": (254, 169, 4),
    "Your Pink": (255, 195, 192),
    "Yukon Gold": (123, 102, 8),
    "Yuma": (206, 194, 145),
    "Zambezi": (104, 85, 88),
    "Zanah": (218, 236, 214),
    "Zest": (229, 132, 27),
    "Zeus": (41, 35, 25),
    "Ziggurat": (191, 219, 226),
    "Zinnwaldite": (235, 194, 175),
    "Zircon": (244, 248, 255),
    "Zombie": (228, 214, 155),
    "Zorba": (165, 155, 145),
    "Zuccini": (4, 64, 34),
    "Zumthor": (237, 246, 255)
}
_searchtree = {
    0: {
        0: {
            0: {
                0: {
                    0: 'Black',
                    7: {
                        0: 'Cod Gray',
                        2: 'Marshland',
                        7: 'Woodsmoke'
                    }
                },
                1: {
                    3: 'Blue Charcoal',
                    4: 'Jaguar',
                    5: 'Black Russian',
                    7: {
                        5: 'Ebony',
                        6: 'Cinder'
                    }
                },
                2: {
                    0: 'Midnight Moss',
                    4: {
                        1: {
                            5: 'Gordons Green',
                            6: 'Black Forest'
                        }
                    }
                },
                3: {
                    2: 'Holly',
                    3: 'Swamp',
                    4: 'Bunker',
                    6: {
                        0: 'Black Bean',
                        4: 'Racing Green'
                    },
                    7: 'Aztec'
                },
                4: {
                    0: {
                        0: 'Diesel',
                        6: 'Nero'
                    },
                    2: 'Asphalt',
                    6: 'Creole'
                },
                6: {
                    0: 'Green Waterloo',
                    2: 'Pine Tree',
                    4: 'Acadia',
                    5: {
                        4: 'Crowshead',
                        5: 'Night Rider',
                        6: {
                            6: {
                                1: 'Karaka',
                                2: 'El Paso'
                            }
                        }
                    }
                },
                7: {
                    1: 'Vulcan',
                    2: 'Hunter Green',
                    6: 'Rangoon Green'
                }
            },
            1: {
                1: 'Black Rock',
                2: 'Black Pearl',
                3: {
                    0: 'Midnight',
                    1: 'Tangaroa'
                },
                6: 'Mirage',
                7: 'Haiti'
            },
            2: {
                0: {
                    2: 'Deep Fir',
                    5: 'Palm Green'
                },
                1: {
                    2: 'English Holly',
                    7: 'Bush'
                },
                3: {
                    1: {
                        2: 'County Green',
                        3: 'Cardin Green'
                    }
                },
                4: 'Deep Forest Green',
                5: 'Seaweed',
                6: 'Palm Leaf'
            },
            3: {
                0: 'Burnham',
                1: {
                    0: 'Daintree',
                    6: 'Firefly'
                },
                2: 'Bottle Green',
                3: {
                    0: {
                        2: 'Deep Teal',
                        7: 'Tiber'
                    }
                },
                6: {
                    0: 'Celtic',
                    1: 'Timber Green'
                },
                7: 'Gable Green'
            },
            4: {
                0: {
                    2: 'Kilamanjaro',
                    4: 'Sepia Black'
                },
                2: {
                    0: {
                        5: 'Wood Bark',
                        7: {
                            3: {
                                5: 'Graphite',
                                6: 'Cannon Black'
                            }
                        }
                    },
                    3: 'Eternity',
                    5: 'Coffee Bean',
                    6: 'Jacko Bean'
                },
                3: {
                    0: 'Gondola',
                    6: 'Oil'
                },
                4: {
                    0: 'Chocolate',
                    5: 'Temptress',
                    6: 'Bean  '
                },
                5: 'Aubergine',
                6: {
                    3: 'Clinker',
                    4: 'Rebel'
                },
                7: {
                    0: 'Tamarind',
                    2: 'Eclipse',
                    3: 'Cocoa Brown',
                    6: 'Cedar',
                    7: 'Jon'
                }
            },
            5: {
                0: 'Jacaranda',
                3: 'Revolver',
                4: {
                    1: 'Melanzane',
                    4: 'Toledo'
                },
                5: 'Mardi Gras'
            },
            6: {
                0: 'Onion',
                1: {
                    2: 'Black Olive',
                    3: 'Log Cabin',
                    4: 'Mikado',
                    5: 'Zeus'
                },
                2: 'Turtle Green',
                3: {
                    1: {
                        2: 'Mallard',
                        5: 'Green Kelp'
                    }
                },
                4: {
                    3: {
                        1: 'Woodrush',
                        5: 'Brown Tumbleweed'
                    },
                    4: {
                        5: 'Dark Ebony',
                        6: 'Cola'
                    },
                    5: 'Bronze'
                },
                5: {
                    4: 'Sambuca',
                    7: {
                        5: 'Bistre',
                        7: 'Black Marlin'
                    }
                },
                6: {
                    3: 'Waiouru',
                    4: 'Madras'
                },
                7: 'Camouflage'
            },
            7: {
                0: 'Shark',
                1: {
                    0: 'Steel Gray',
                    3: 'Ebony Clay',
                    4: {
                        0: 'Bastille',
                        2: 'Baltic Sea',
                        4: 'Bleached Cedar'
                    },
                    6: 'Charade'
                },
                2: {
                    4: 'Rangitoto',
                    5: 'Heavy Metal'
                },
                3: 'Outer Space',
                4: {
                    3: 'Thunder',
                    6: {
                        0: 'Treehouse',
                        4: 'English Walnut'
                    }
                },
                5: 'Blackcurrant',
                6: 'Birch',
                7: {
                    0: {
                        0: 'Mine Shaft',
                        7: 'Tuatara'
                    },
                    4: 'Dune'
                }
            }
        },
        1: {
            0: {
                0: 'Stratos',
                2: 'Deep Cove',
                3: 'Gulf Blue',
                4: 'Tolopea',
                6: 'Bunting'
            },
            1: {
                4: 'Arapawa',
                6: 'Lucky Point',
                7: 'Deep Koamaru'
            },
            2: {
                0: 'Blue Whale',
                1: {
                    2: 'Green Vogue',
                    4: 'Downriver',
                    5: 'Madison'
                },
                2: 'Cyprus',
                3: {
                    0: 'Prussian Blue',
                    2: 'Tarawera'
                },
                4: {
                    1: 'Blue Zodiac',
                    2: 'Big Stone'
                },
                6: 'Elephant',
                7: {
                    4: 'Nile Blue',
                    7: 'Cello'
                }
            },
            3: {
                0: 'Deep Sapphire',
                1: 'Catalina Blue',
                2: {
                    0: 'Midnight Blue',
                    2: 'Astronaut Blue',
                    3: 'Regal Blue'
                },
                6: 'Biscay'
            },
            4: {
                0: 'Violet',
                1: {
                    5: 'Cherry Pie',
                    7: 'Violent Violet'
                },
                2: {
                    3: 'Port Gore',
                    7: 'Valhalla'
                },
                4: 'Valentino',
                5: 'Jagger',
                7: 'Grape'
            },
            5: {
                0: {
                    1: {
                        4: 'Paua',
                        6: 'Paris M'
                    }
                },
                1: 'Deep Blue',
                4: 'Christalle',
                5: {
                    4: 'Blue Diamond',
                    7: 'Windsor'
                },
                7: {
                    1: 'Persian Indigo',
                    6: 'Meteorite'
                }
            },
            6: {
                1: 'Cloud Burst',
                6: {
                    0: 'Tuna',
                    6: 'Ship Gray'
                },
                7: 'Martinique'
            },
            7: {
                2: 'Rhino',
                3: 'Astronaut',
                4: 'Jacarta',
                7: 'Minsk'
            }
        },
        2: {
            0: {
                0: 'Dark Fern',
                1: 'Crusoe',
                3: 'Camarone',
                5: 'Parsley'
            },
            1: {
                0: {
                    0: {
                        2: 'Kaitoke Green',
                        4: 'Zuccini'
                    },
                    1: 'Sherwood Green'
                },
                4: 'Everglade',
                5: 'Te Papa Green'
            },
            2: {
                0: {
                    4: 'San Felix',
                    6: 'Japanese Laurel'
                }
            },
            3: 'Fun Green',
            4: {
                2: 'Green House',
                5: 'Clover'
            },
            5: {
                5: {
                    7: {
                        4: 'Lunar Green',
                        6: 'Cabbage Pont'
                    }
                },
                7: 'Tom Thumb'
            },
            6: {
                5: 'Dell',
                7: 'Bilbao'
            }
        },
        3: {
            0: {
                0: {
                    2: {
                        0: 'Aqua Deep',
                        3: 'Evening Sea'
                    }
                },
                1: {
                    1: 'Teal Blue',
                    2: 'Sherpa Blue'
                },
                3: 'Deep Sea Green',
                7: 'Eden'
            },
            1: {
                7: {
                    1: 'Chathams Blue',
                    7: 'Blumine'
                }
            },
            2: {
                1: 'Watercourse',
                2: 'Salem',
                3: 'Tropical Rain Forest',
                4: {
                    2: 'Jewel',
                    4: 'Green Pea'
                }
            },
            3: {
                0: {
                    0: 'Blue Stone',
                    3: 'Mosque'
                },
                1: 'Atoll',
                2: 'Pine Green',
                3: 'Surfie Green',
                6: 'Genoa',
                7: 'Elm'
            },
            4: {
                1: 'Blue Dianne',
                2: 'Plantation',
                3: 'Spectra',
                4: 'Cape Cod',
                5: {
                    1: 'Pickled Bluewood',
                    4: {
                        3: 'Oxford Blue',
                        4: 'Bright Gray'
                    },
                    6: 'Limed Spruce'
                },
                7: {
                    2: 'Stromboli',
                    6: 'Mineral Green'
                }
            },
            5: 'San Juan',
            6: {
                4: 'Killarney',
                7: {
                    6: {
                        1: 'Amazon',
                        6: 'Goblin'
                    }
                }
            },
            7: {
                0: 'Casal',
                4: 'William',
                7: {
                    0: 'Oracle',
                    1: 'Ming'
                }
            }
        },
        4: {
            0: {
                0: {
                    0: 'Burnt Maroon',
                    4: {
                        3: {
                            0: 'Rustic Red',
                            3: 'Bulgarian Rose'
                        },
                        7: 'Mahogany'
                    }
                },
                1: 'Cab Sav',
                2: {
                    2: {
                        0: 'Brown Pod',
                        6: 'Morocco Brown'
                    },
                    5: 'Van Cleef',
                    6: 'Indian Tan'
                },
                3: {
                    2: 'Paco',
                    7: 'Cocoa Bean'
                },
                5: {
                    1: 'Castro',
                    2: 'Maroon Oak'
                },
                6: 'Redwood',
                7: 'Heath'
            },
            1: {
                0: 'Barossa',
                1: 'Blackberry',
                4: 'Bordeaux',
                5: 'Mulberry Wood',
                7: 'Wine Berry'
            },
            2: {
                0: 'Bracken',
                1: {
                    0: 'Deep Oak',
                    3: 'Cork',
                    4: 'Brown Derby'
                },
                2: 'Deep Bronze',
                3: {
                    3: 'Thatch Green',
                    5: 'Metallic Bronze',
                    6: 'Punga'
                },
                4: {
                    3: 'Cioccolato',
                    6: {
                        1: 'Brown Bramble',
                        6: 'Carnaby Tan'
                    }
                },
                6: 'Saddle Brown',
                7: 'Jambalaya'
            },
            3: {
                0: {
                    0: 'Crater Brown',
                    7: {
                        5: {
                            0: 'Cowboy',
                            1: 'Livid Brown'
                        }
                    }
                },
                2: {
                    0: 'Iroko',
                    2: 'Lisbon Brown',
                    4: 'Saddle'
                },
                3: {
                    2: {
                        3: {
                            1: 'Merlin',
                            7: 'Armadillo'
                        }
                    },
                    3: 'Masala',
                    4: 'Woody Brown',
                    6: {
                        2: {
                            1: 'Taupe',
                            4: 'Mondo'
                        },
                        4: 'Rock'
                    }
                },
                6: 'Irish Coffee',
                7: 'Congo Brown'
            },
            4: {
                0: {
                    1: 'Rosewood',
                    4: 'Lonestar',
                    6: 'Red Oxide'
                },
                3: {
                    0: 'Dark Tan',
                    2: 'Cherrywood',
                    6: 'Moccaccino'
                },
                4: {
                    1: 'Venetian Red',
                    2: 'Dark Burgundy',
                    5: 'Japanese Maple'
                },
                6: {
                    2: 'Cedar Wood Finish',
                    6: 'Kenyan Copper'
                },
                7: {
                    3: {
                        3: 'Persian Plum',
                        7: 'Crown of Thorns'
                    }
                }
            },
            5: {
                0: 'Black Rose',
                1: 'Tyrian Purple',
                5: 'Siren',
                7: 'Claret'
            },
            6: {
                1: {
                    1: 'Espresso',
                    6: 'Hairy Heath'
                },
                2: 'Nutmeg Wood Finish',
                5: {
                    3: 'Metallic Copper',
                    6: {
                        3: 'Peanut',
                        7: 'Pueblo'
                    },
                    7: 'Mocha'
                },
                6: {
                    6: {
                        0: 'Red Beech',
                        2: 'Cinnamon',
                        4: 'Peru Tan'
                    }
                },
                7: {
                    3: 'Walnut',
                    6: 'Copper Canyon'
                }
            },
            7: {
                1: 'Buccaneer',
                2: 'Quincy'
            }
        },
        5: {
            0: {
                0: 'Loulou',
                1: {
                    0: 'Ripe Plum',
                    4: 'Clairvoyant'
                }
            },
            1: {
                2: 'Scarlet Gum',
                3: 'Honey Flower'
            },
            2: {
                1: 'Bossanova',
                2: 'Matterhorn',
                7: 'Voodoo'
            },
            4: 'Pompadour',
            6: {
                0: 'Tawny Port',
                1: 'Finn',
                7: 'Cosmic'
            }
        },
        6: {
            0: {
                0: {
                    5: {
                        5: {
                            1: 'Bronzetone',
                            6: 'Bronze Olive'
                        }
                    }
                },
                2: 'Verdun Green',
                7: 'Saratoga'
            },
            1: {
                1: 'Kelp',
                2: 'Woodland',
                5: {
                    0: 'Judge Gray',
                    4: 'Millbrook',
                    7: 'Kabul'
                },
                7: {
                    6: 'Verdigris',
                    7: 'Hemlock'
                }
            },
            2: 'Green Leaf',
            3: 'Chalet Green',
            4: {
                0: 'Cafe Royale',
                1: 'Horses Neck',
                3: {
                    1: 'West Coast',
                    7: 'Himalaya'
                },
                4: 'Antique Bronze',
                5: {
                    0: 'Sepia',
                    2: 'Raw Umber'
                }
            },
            5: {
                0: {
                    5: 'Spice',
                    6: {
                        5: {
                            5: 'Pickled Bean',
                            7: 'Dallas'
                        }
                    }
                },
                1: 'Shingle Fawn',
                3: 'Costa Del Sol',
                4: 'Old Copper'
            },
            6: {
                4: {
                    1: 'Spicy Mustard',
                    5: 'Yukon Gold'
                },
                5: 'Olivetone'
            },
            7: {
                2: 'Fern Frond',
                5: 'Yellow Metal',
                6: 'Crete',
                7: 'Pesto'
            }
        },
        7: {
            0: {
                0: {
                    4: 'Tundora',
                    5: 'Gravel'
                },
                1: {
                    0: 'Gun Powder',
                    2: 'Mako',
                    3: 'River Bed',
                    6: 'Abbey',
                    7: 'Trout'
                },
                2: 'Gray Asparagus',
                3: 'Nandor',
                4: 'Emperor',
                5: {
                    0: 'Mortar',
                    6: 'Don Juan'
                },
                6: 'Fuscous Gray',
                7: 'Chicago'
            },
            1: {
                0: 'Mulled Wine',
                1: 'East Bay',
                2: 'Fiord',
                6: {
                    4: 'Scarpa Flow',
                    7: 'Mid Gray'
                },
                7: 'Comet'
            },
            2: {
                0: 'Axolotl',
                2: 'Fern Green',
                5: 'Finlandia',
                6: 'Dingley',
                7: 'Cactus'
            },
            3: {
                1: 'Blue Bayoux',
                3: 'Faded Jade',
                5: 'Shuttle Gray',
                6: 'Como',
                7: 'Cutty Sark'
            },
            4: {
                1: 'Eggplant',
                3: {
                    4: 'Dorado',
                    5: 'Zambezi',
                    6: 'Pine Cone'
                },
                5: 'Ferra',
                6: {
                    2: 'Tobacco Brown',
                    7: 'Roman Coffee'
                },
                7: 'Russett'
            },
            5: {
                2: {
                    6: 'Scorpion',
                    7: 'Salt Box'
                },
                3: 'Smoky'
            },
            6: {
                0: 'Finch',
                1: {
                    2: 'Siam',
                    4: 'Soya Bean',
                    6: 'Kokoda'
                },
                3: 'Willow Grove',
                4: 'Go Ben',
                5: {
                    0: 'Coffee',
                    2: 'Peat',
                    3: 'Crocodile'
                }
            },
            7: {
                0: {
                    0: {
                        6: {
                            1: 'Storm Dust',
                            7: 'Ironside Gray'
                        }
                    },
                    3: 'Corduroy',
                    6: 'Flint',
                    7: 'Dove Gray'
                },
                1: {
                    0: 'Dolphin',
                    2: 'Nevada'
                },
                4: {
                    2: 'Pablo',
                    5: 'Falcon',
                    6: 'Sandstone'
                },
                5: {
                    7: {
                        0: {
                            0: 'Old Lavender',
                            2: 'Fedora'
                        }
                    }
                },
                6: 'Limed Ash',
                7: {
                    6: 'Tapa',
                    7: {
                        0: 'Boulder',
                        4: 'Concord'
                    }
                }
            }
        }
    },
    1: {
        0: {
            0: {
                0: 'Navy Blue',
                4: 'Ultramarine'
            },
            2: {
                0: 'Resolution Blue',
                1: 'Torea Bay',
                3: 'Smalt'
            },
            3: {
                0: 'International Klein Blue',
                7: 'Persian Blue'
            },
            4: {
                0: 'Blue Gem',
                4: 'Kingfisher Daisy'
            },
            6: {
                0: 'Jacksons Purple',
                2: 'Bay of Many'
            },
            7: 'Governor Bay'
        },
        1: {
            0: 'Dark Blue',
            1: 'Blue'
        },
        2: {
            0: {
                0: 'Congress Blue',
                2: {
                    2: 'Orient',
                    3: 'Venice Blue'
                }
            },
            1: {
                0: 'Cobalt',
                2: 'Endeavour',
                6: {
                    1: 'Tory Blue',
                    7: 'Fun Blue'
                }
            },
            2: {
                1: 'Bahama Blue',
                2: 'Blue Lagoon',
                5: 'Matisse'
            },
            3: {
                2: {
                    0: 'Allports',
                    2: 'Deep Cerulean'
                },
                5: 'Denim'
            },
            4: {
                3: {
                    5: {
                        5: 'Sapphire',
                        6: 'St Tropaz'
                    }
                },
                4: 'Chambray'
            },
            5: {
                3: 'Cerulean Blue',
                6: 'Azure'
            },
            6: {
                3: 'Jelly Bean',
                6: {
                    1: 'Calypso',
                    2: 'Paradiso'
                }
            },
            7: 'Astral'
        },
        3: {
            2: {
                0: 'Science Blue',
                2: 'Lochmara'
            },
            3: {
                1: 'Blue Ribbon',
                3: 'Azure Radiance'
            },
            6: 'Mariner'
        },
        4: {
            0: 'Pigment Indigo',
            2: {
                1: 'Daisy Bush',
                7: 'Gigas'
            },
            4: {
                1: 'Purple',
                6: 'Seance'
            },
            6: 'Eminence',
            7: 'Royal Purple'
        },
        5: 'Purple Heart',
        6: {
            0: 'Victoria',
            2: {
                2: 'Bismark',
                3: 'Wedgewood',
                5: 'Waikawa Gray',
                7: 'Kashmir Blue'
            },
            3: 'San Marino',
            4: {
                1: 'Butterfly Bush',
                5: 'Affair'
            },
            5: {
                2: 'Scampi',
                3: 'Blue Violet',
                5: 'Studio'
            },
            6: {
                2: 'Pale Sky',
                3: 'Lynch',
                4: 'Rum',
                5: 'Kimberly',
                6: {
                    0: 'Storm Gray',
                    2: 'Rolling Stone',
                    3: 'Raven',
                    5: {
                        6: {
                            3: 'Topaz',
                            4: 'Mobster'
                        }
                    },
                    6: 'Jumbo'
                },
                7: 'Waterloo '
            },
            7: 'Deluge'
        },
        7: {
            2: 'Indigo',
            3: 'Royal Blue',
            4: 'Fuchsia Blue',
            6: {
                4: 'Blue Marguerite',
                7: 'Moody Blue'
            }
        }
    },
    2: {
        0: {
            4: 'La Palma',
            5: 'Forest Green'
        },
        1: {
            1: {
                0: {
                    1: {
                        0: 'Deep Sea',
                        3: 'Observatory'
                    }
                },
                1: 'Elf Green'
            },
            3: {
                0: {
                    1: 'Green Haze',
                    3: 'Jade'
                }
            },
            4: {
                1: {
                    3: 'Eucalyptus',
                    6: 'Sea Green'
                }
            }
        },
        2: {
            2: 'Green',
            6: 'Harlequin'
        },
        3: {
            0: 'Malachite',
            3: 'Spring Green'
        },
        4: {
            0: 'Vida Loca',
            3: 'Apple',
            4: {
                2: 'Limeade',
                5: 'Trendy Green'
            },
            5: {
                0: 'Olive Drab',
                4: {
                    0: 'Pacifika',
                    6: 'Wasabi'
                }
            },
            6: {
                1: 'Christi',
                7: 'Lima'
            }
        },
        5: {
            0: {
                3: 'Fruit Salad',
                4: 'Hippie Green'
            },
            1: {
                0: 'Viridian',
                4: 'Spring Leaves'
            },
            3: {
                0: 'Chateau Green',
                1: 'Ocean Green',
                5: 'Aqua Forest'
            },
            4: 'Glade Green',
            5: {
                0: 'Highland',
                1: 'Viridian Green',
                4: {
                    4: 'Flax Smoke',
                    5: 'Camouflage Green'
                },
                5: 'Xanadu',
                7: 'Laurel'
            },
            6: 'Asparagus',
            7: 'Fern'
        },
        6: {
            6: {
                2: 'Bright Green',
                6: 'Chartreuse'
            }
        },
        7: {
            1: 'Emerald',
            5: {
                4: 'Mantis',
                7: 'Pastel Green'
            },
            7: "Screamin' Green"
        }
    },
    3: {
        0: {
            0: {
                0: 'Teal',
                1: 'Blue Chill',
                2: 'Gossamer'
            },
            1: {
                3: 'Bondi Blue',
                7: 'Eastern Blue'
            },
            2: {
                0: 'Niagara',
                1: 'Persian Green',
                6: 'Mountain Meadow'
            },
            4: 'Lochinvar',
            5: 'Boston Blue',
            6: {
                0: 'Jungle Green',
                7: 'Keppel'
            },
            7: 'Pelorous'
        },
        1: {
            0: 'Pacific Blue',
            1: 'Dodger Blue',
            2: 'Cerulean',
            4: 'Curious Blue',
            6: 'Scooter'
        },
        2: {
            0: 'Caribbean Green',
            4: 'Shamrock',
            5: 'Puerto Rico'
        },
        3: {
            0: {
                0: "Robin's Egg Blue",
                4: 'Java'
            },
            2: 'Bright Turquoise',
            3: 'Cyan / Aqua',
            4: 'Turquoise'
        },
        4: {
            0: 'Smalt Blue',
            1: {
                1: 'Steel Blue',
                4: 'Horizon',
                6: 'Hippie Blue'
            },
            2: 'Breaker Bay',
            3: {
                6: 'Tradewind',
                7: 'Fountain Blue'
            },
            4: {
                1: 'Hoki',
                2: 'Patina',
                3: 'Juniper',
                4: {
                    0: 'Sirocco',
                    2: 'Blue Smoke'
                },
                5: 'Slate Gray',
                6: {
                    2: 'Oxley',
                    6: 'Amulet'
                }
            },
            5: {
                0: 'Bermuda Gray',
                2: 'Gothic',
                5: {
                    7: {
                        0: {
                            3: 'Ship Cove',
                            4: 'Wild Blue Yonder'
                        }
                    }
                }
            },
            6: {
                2: 'Silver Tree',
                4: 'Bay Leaf',
                5: 'Sea Nymph'
            },
            7: {
                4: 'Gumbo',
                6: 'Acapulco',
                7: 'Neptune'
            }
        },
        5: {
            0: 'Havelock Blue',
            2: 'Shakespeare',
            3: 'Picton Blue',
            4: 'Danube',
            5: 'Cornflower Blue'
        },
        6: 'De York',
        7: {
            4: {
                1: 'Viking',
                2: 'Downy',
                6: 'Bermuda'
            },
            5: {
                2: 'Turquoise Blue',
                5: 'Malibu',
                6: {
                    1: 'Sky Blue',
                    2: 'Aquamarine Blue',
                    7: 'Spray'
                }
            },
            6: 'Aquamarine'
        }
    },
    4: {
        0: {
            0: {
                0: {
                    0: 'Maroon',
                    4: 'Red Berry'
                },
                1: {
                    0: 'Red Devil',
                    5: 'Pohutukawa'
                },
                3: 'Falu Red',
                4: 'Sangria',
                5: {
                    0: 'Scarlett',
                    1: 'Carmine'
                },
                6: 'Totem Pole',
                7: {
                    3: 'Old Brick',
                    4: 'Tamarillo'
                }
            },
            1: {
                0: {
                    4: {
                        2: 'Monarch',
                        5: 'Paprika'
                    }
                },
                2: 'Merlot',
                4: 'Burgundy'
            },
            2: {
                3: 'Red Robin',
                7: 'Cognac'
            },
            3: {
                2: 'Burnt Umber',
                3: {
                    3: 'Lotus',
                    6: 'El Salva',
                    7: {
                        6: 'Sanguine Brown',
                        7: 'Tosca'
                    }
                },
                6: 'Prairie Sand',
                7: 'Stiletto'
            },
            4: {
                4: {
                    0: 'Bright Red',
                    4: 'Guardsman Red'
                },
                6: 'Milano Red'
            },
            5: 'Shiraz',
            6: 'Tabasco',
            7: {
                0: {
                    0: 'Mexican Red',
                    2: 'Roof Terracotta'
                },
                4: 'Tall Poppy',
                7: 'Well Read'
            }
        },
        1: {
            0: {
                0: 'Rose Bud Cherry',
                1: 'Cardinal Pink',
                3: 'Disco'
            },
            1: 'Fresh Eggplant',
            2: {
                2: 'Solid Pink',
                3: 'Camelot'
            },
            3: {
                3: 'Plum',
                6: 'Vin Rouge'
            },
            4: 'Jazzberry Jam',
            5: {
                0: {
                    1: 'Flirt',
                    4: 'Lipstick'
                }
            },
            6: 'Night Shadz',
            7: {
                2: 'Rouge',
                3: 'Royal Heath',
                6: 'Hibiscus'
            }
        },
        2: {
            0: {
                0: 'Korma',
                1: {
                    1: 'Russet',
                    3: 'Bull Shot',
                    7: 'Rope'
                },
                2: 'Rusty Nail',
                4: {
                    2: 'Brown',
                    4: 'Oregon'
                },
                6: 'Chelsea Gem',
                7: 'Hawaiian Tan'
            },
            1: {
                0: {
                    1: 'Nutmeg',
                    5: 'Mule Fawn'
                },
                1: 'Ironstone',
                3: 'Potters Clay',
                4: 'Cumin'
            },
            2: 'Corn Harvest',
            3: 'Kumera',
            4: {
                0: 'Fire',
                2: 'Rich Gold',
                4: {
                    1: 'Rust',
                    3: 'Vesuvius',
                    5: 'Rock Spray'
                },
                6: 'Rose of Sharon',
                7: 'Fiery Orange'
            },
            5: {
                1: 'Medium Carmine',
                2: 'Paarl',
                3: 'Brown Rust',
                6: 'Tuscany'
            },
            6: {
                1: 'Reno Sand',
                2: 'Buttered Rum',
                3: 'Mandalay',
                4: {
                    1: {
                        0: 'Pumpkin Skin',
                        2: 'Mai Tai'
                    }
                },
                5: 'Bourbon',
                6: 'Pirate Gold'
            },
            7: {
                0: 'Desert',
                7: 'Copper'
            }
        },
        3: {
            0: {
                2: 'Spicy Mix',
                4: 'Copper Rust',
                6: 'Sepia Skin'
            },
            1: 'Cannon Pink',
            2: {
                3: {
                    0: 'Shadow',
                    5: 'Domino'
                },
                5: {
                    1: 'Au Chico',
                    3: 'Beaver'
                },
                7: 'Leather'
            },
            3: {
                0: 'Sand Dune',
                1: {
                    2: 'Spicy Pink',
                    6: 'Opium'
                },
                2: {
                    1: 'Americano',
                    4: 'Cement',
                    7: 'Makara'
                },
                3: {
                    0: 'Empress',
                    3: {
                        2: 'Friar Gray',
                        6: 'Hurricane'
                    }
                },
                4: {
                    4: 'Copper Rose',
                    6: 'Toast'
                },
                7: {
                    2: {
                        0: 'Almond Frost',
                        1: 'Hemp'
                    },
                    5: 'Bazaar'
                }
            },
            4: {
                0: 'Apple Blossom',
                4: 'Chestnut',
                6: 'Crail',
                7: 'Matrix'
            },
            5: {
                0: 'Hippie Pink',
                4: {
                    1: 'Blush',
                    3: 'Cadillac'
                }
            },
            6: {
                0: 'Cape Palliser',
                5: 'Santa Fe'
            },
            7: 'Coral Tree'
        },
        4: {
            0: 'Monza',
            1: {
                3: 'Cardinal',
                7: 'Crimson'
            },
            2: 'Thunderbird',
            3: {
                3: {
                    4: {
                        3: 'Flush Mahogany',
                        4: 'Persian Red'
                    }
                }
            },
            4: 'Red',
            5: {
                1: 'Red Ribbon',
                5: 'Torch Red'
            },
            6: 'Scarlet',
            7: {
                1: 'Alizarin Crimson',
                7: 'Red Orange'
            }
        },
        5: {
            2: {
                0: {
                    1: 'Maroon Flush',
                    2: 'Brick Red'
                }
            },
            3: 'Cerise Red',
            4: 'Razzmatazz',
            5: 'Rose',
            6: {
                1: 'Amaranth',
                7: 'Radical Red'
            }
        },
        6: {
            0: {
                0: 'Tia Maria',
                2: {
                    4: {
                        6: {
                            0: 'Burnt Orange',
                            2: 'Tenn'
                        }
                    }
                },
                3: 'Orange Roughy',
                4: 'Grenadier',
                6: 'Red Stage'
            },
            1: {
                1: 'Mojo',
                5: {
                    4: {
                        3: 'Valencia',
                        4: 'Punch'
                    }
                },
                7: 'Flame Pea'
            },
            2: {
                0: 'Indochine',
                4: 'Bamboo',
                5: 'Hot Cinnamon',
                7: 'Meteor'
            },
            3: {
                0: 'Piper',
                2: 'Ochre'
            },
            4: {
                0: 'Trinidad',
                4: {
                    6: {
                        6: {
                            4: 'Vermilion',
                            6: 'International Orange'
                        }
                    }
                }
            },
            5: {
                1: 'Cinnabar',
                4: 'Pomegranate',
                6: 'Flamingo'
            },
            6: {
                0: 'Clementine',
                2: {
                    0: 'Mango Tango',
                    1: 'Christine',
                    6: 'Tahiti Gold'
                },
                3: 'Tango',
                4: 'Blaze Orange',
                5: 'Orange',
                6: {
                    0: 'Chilean Fire',
                    6: {
                        6: 'Flush Orange',
                        7: {
                            1: 'Sorbus',
                            5: 'Flamenco'
                        }
                    }
                },
                7: {
                    5: 'Pumpkin',
                    6: 'Ecstasy'
                }
            },
            7: {
                5: 'Outrageous Orange',
                7: {
                    4: 'Burning Orange',
                    6: 'Crusta'
                }
            }
        },
        7: {
            0: {
                3: {
                    0: 'Fuzzy Wuzzy Brown',
                    7: 'Chestnut Rose'
                }
            },
            1: {
                5: 'Cabaret',
                7: 'Cranberry'
            },
            2: {
                4: 'Red Damask',
                6: 'Raw Sienna'
            },
            3: {
                2: 'Contessa',
                4: 'Roman',
                6: 'Japonica'
            },
            4: {
                4: {
                    4: 'Coral Red',
                    6: 'Sunset Orange'
                }
            },
            5: {
                2: 'Mandy',
                6: 'Carnation',
                7: 'Wild Watermelon'
            },
            6: {
                3: {
                    1: 'Terracotta',
                    4: 'Burnt Sienna'
                },
                5: {
                    6: 'Persimmon',
                    7: 'Bittersweet'
                },
                7: 'Coral'
            },
            7: {
                0: 'Sunglo',
                5: 'Brink Pink'
            }
        }
    },
    5: {
        0: {
            0: 'Violet Eggplant',
            2: 'Vivid Violet',
            6: 'Medium Red Violet'
        },
        1: 'Electric Violet',
        2: {
            2: {
                1: 'Trendy Pink',
                4: 'Strikemaster',
                6: 'Mountbatten Pink'
            },
            3: {
                7: {
                    0: 'Wisteria',
                    2: {
                        5: {
                            5: "Purple Mountain's Majesty",
                            7: 'Lavender Purple'
                        }
                    }
                }
            },
            4: 'Tapestry',
            6: 'Turkish Rose'
        },
        3: {
            2: {
                3: 'True V',
                4: 'Amethyst',
                7: {
                    1: 'Medium Purple',
                    4: 'Lilac Bush'
                }
            },
            6: 'Lavender'
        },
        4: {
            0: 'Red Violet',
            2: 'Cerise',
            5: 'Hollywood Cerise',
            6: 'Wild Strawberry',
            7: 'Persian Rose'
        },
        5: {
            4: {
                4: {
                    5: 'Purple Pizzazz',
                    6: 'Shocking Pink'
                }
            },
            5: 'Magenta / Fuchsia',
            6: 'Razzle Dazzle Rose'
        },
        6: {
            0: 'Mulberry',
            2: 'Charm',
            3: 'Hopbush',
            4: {
                4: {
                    1: 'Violet Red',
                    3: 'French Rose'
                }
            },
            5: 'Brilliant Rose',
            6: {
                3: 'Deep Blush',
                6: 'Froly'
            },
            7: {
                5: 'Hot Pink',
                7: 'Persian Pink'
            }
        },
        7: {
            0: 'Fuchsia Pink',
            2: 'Orchid',
            3: 'Heliotrope',
            7: {
                5: {
                    5: 'Pink Flamingo',
                    7: 'Blush Pink'
                }
            }
        }
    },
    6: {
        0: {
            0: {
                0: 'Olive',
                5: {
                    5: {
                        0: 'Hacienda',
                        5: 'Reef Gold'
                    }
                }
            },
            1: 'Sycamore',
            2: 'Citron',
            3: 'Sushi',
            4: {
                3: 'Lucky',
                4: 'Hot Toddy'
            },
            5: {
                0: {
                    3: 'Luxor Gold',
                    7: 'Alpine'
                },
                2: 'Lemon Ginger',
                4: 'Marigold'
            },
            6: 'Sahara'
        },
        1: {
            1: {
                0: {
                    4: 'Clay Creek',
                    6: 'Avocado'
                },
                1: {
                    0: 'Bandicoot',
                    2: {
                        2: 'Battleship Gray',
                        5: 'Bitter'
                    },
                    4: {
                        2: 'Olive Haze',
                        5: 'Squirrel'
                    },
                    5: 'Schooner',
                    6: 'Granite Green'
                },
                5: {
                    0: {
                        2: 'Stonewall',
                        6: 'Arrowtown'
                    },
                    6: 'Pale Oyster'
                },
                7: 'Gurkha'
            },
            2: 'Chelsea Cucumber',
            3: 'Olivine',
            4: {
                1: {
                    3: 'Barley Corn',
                    4: 'Driftwood',
                    6: 'Limed Oak',
                    7: 'Muesli'
                },
                5: 'Muddy Waters'
            },
            5: {
                0: 'Sandal',
                1: 'Pharlap',
                3: {
                    1: 'Donkey Brown',
                    5: 'Sandrift'
                },
                6: 'Teak'
            },
            6: {
                5: 'Husk',
                7: 'Olive Green'
            },
            7: {
                0: 'Green Smoke',
                5: 'Mongoose',
                6: 'Gimblet'
            }
        },
        2: {
            0: 'Pistachio',
            1: 'Atlantis',
            4: {
                0: {
                    1: 'Citrus',
                    3: 'Bahia'
                },
                5: 'La Rioja',
                6: {
                    5: 'Rio Grande',
                    7: 'Fuego'
                }
            },
            5: 'Key Lime Pie',
            6: {
                5: 'Inch Worm',
                6: 'Lime'
            },
            7: 'Green Yellow'
        },
        3: {
            4: {
                2: 'Conifer',
                5: 'Celery'
            },
            5: 'Wild Willow'
        },
        4: {
            0: {
                3: 'Pizza',
                5: 'Geebung'
            },
            1: {
                0: 'Brandy Punch',
                2: 'Nugget'
            },
            2: {
                0: 'Buddha Gold',
                6: 'Galliano',
                7: 'Gold Tips'
            },
            3: {
                0: 'Hokey Pokey',
                3: {
                    5: 'Old Gold',
                    7: 'Earls Green'
                },
                4: 'Golden Grass'
            },
            4: {
                1: {
                    1: 'Zest',
                    2: 'Golden Bell'
                },
                2: 'Gamboge',
                3: 'Dixie',
                4: {
                    0: {
                        0: 'Gold Drop',
                        2: 'Tangerine'
                    }
                },
                6: {
                    4: 'Pizazz',
                    5: 'West Side',
                    6: 'California'
                },
                7: 'Tree Poppy'
            },
            5: {
                1: 'Jaffa',
                2: {
                    4: 'Carrot Orange',
                    7: 'Fire Bush'
                },
                6: 'Sunshade',
                7: 'Neon Carrot'
            },
            6: {
                2: 'Corn',
                4: {
                    4: {
                        4: 'Orange Peel',
                        6: 'Web Orange'
                    },
                    6: 'Yellow Sea'
                },
                5: {
                    2: 'Buttercup',
                    6: 'Sun'
                },
                6: {
                    6: {
                        4: 'Selective Yellow',
                        6: 'Amber'
                    }
                },
                7: 'My Sin'
            },
            7: {
                0: 'Fuel Yellow',
                3: 'Tulip Tree',
                4: 'Sea Buckthorn'
            }
        },
        5: {
            0: {
                2: 'Tussock',
                3: 'Twine',
                7: 'Di Serria'
            },
            1: {
                0: 'Antique Brass',
                4: 'Copperfield',
                5: 'New York Pink',
                6: 'Whiskey',
                7: 'Burning Sand'
            },
            2: {
                0: 'Roti',
                2: 'Turmeric',
                3: 'Sundance'
            },
            3: {
                2: 'Laser',
                6: 'Apache'
            },
            4: 'Tan Hide',
            5: {
                3: 'Apricot',
                4: 'Salmon',
                6: 'Atomic Tangerine'
            },
            6: {
                2: 'Anzac',
                4: 'Yellow Orange',
                7: {
                    4: 'Texas Rose',
                    6: 'Casablanca',
                    7: {
                        2: 'Saffron Mango',
                        7: 'Koromiko'
                    }
                }
            },
            7: {
                0: 'Porsche',
                2: 'Equator',
                3: 'Harvest Gold',
                4: 'Sandy brown',
                6: 'Rajah',
                7: 'Macaroni and Cheese'
            }
        },
        6: {
            0: {
                5: 'Bird Flower',
                7: 'Barberry'
            },
            2: {
                0: 'Bitter Lemon',
                1: 'Las Palmas',
                2: 'Electric Lime',
                6: 'Chartreuse Yellow'
            },
            3: 'Pear',
            4: {
                4: 'Supernova',
                5: 'Lightning Yellow',
                6: {
                    4: 'Gold',
                    6: 'School bus Yellow'
                },
                7: {
                    3: 'Ripe Lemon',
                    6: 'Candlelight'
                }
            },
            5: {
                2: 'Sunflower',
                5: {
                    0: 'Saffron',
                    6: 'Sunglow'
                },
                6: 'Golden Dream',
                7: 'Bright Sun'
            },
            6: {
                4: 'Turbo',
                5: {
                    6: {
                        4: 'Lemon',
                        6: 'Broom'
                    }
                },
                6: 'Yellow'
            },
            7: 'Golden Fizz'
        },
        7: {
            0: 'Wattle',
            1: {
                4: {
                    0: 'Tacha',
                    7: 'Chenin'
                }
            },
            3: {
                1: 'Yellow Green',
                3: 'Sulu'
            },
            4: {
                0: 'Ronchi',
                3: 'Confetti',
                5: {
                    3: 'Cream Can',
                    7: 'Golden Tainoi'
                },
                7: {
                    7: {
                        3: 'Energy Yellow',
                        4: 'Mustard',
                        5: 'Dandelion'
                    }
                }
            },
            5: {
                1: 'Rob Roy',
                6: 'Goldenrod',
                7: 'Golden Sand'
            },
            6: {
                2: 'Starship',
                5: 'Candy Corn',
                6: 'Gorse'
            },
            7: {
                1: 'Manz',
                4: {
                    4: 'Portica',
                    7: 'Festival'
                },
                5: {
                    4: 'Kournikova',
                    6: 'Marigold Yellow'
                },
                6: {
                    2: 'Canary',
                    5: 'Paris Daisy',
                    6: 'Laser Lemon'
                }
            }
        }
    },
    7: {
        0: {
            0: {
                0: {
                    0: {
                        0: 'Gray',
                        3: 'Gunsmoke'
                    },
                    4: {
                        1: 'Suva Gray',
                        2: 'Natural Gray'
                    },
                    5: 'Monsoon',
                    7: 'Stack'
                },
                1: {
                    2: 'Oslo Gray',
                    4: 'Mamba'
                },
                2: 'Spanish Green',
                3: {
                    1: 'Regent Gray',
                    6: 'Mantle'
                },
                5: 'Venus',
                6: 'Lemon Grass',
                7: {
                    0: 'Mountain Mist',
                    7: 'Star Dust'
                }
            },
            1: {
                2: {
                    3: 'Bali Hai',
                    4: 'Manatee'
                }
            },
            2: {
                1: 'Envy',
                4: 'Sage'
            },
            3: {
                0: {
                    0: 'Granny Smith',
                    6: 'Cascade'
                },
                2: 'Gulf Stream',
                4: 'Pewter',
                5: {
                    4: 'Santas Gray',
                    6: 'Gull Gray'
                },
                6: 'Summer Green'
            },
            4: {
                1: 'Bouquet',
                3: {
                    2: 'Zorba',
                    7: 'Dusty Gray'
                },
                4: 'Brandy Rose',
                6: 'Quicksand',
                7: {
                    2: 'Del Rio',
                    3: 'Thatch'
                }
            },
            5: 'Amethyst Smoke',
            6: {
                0: {
                    4: 'Hillary',
                    5: 'Tallow',
                    7: 'Locust'
                },
                1: {
                    1: {
                        4: 'Dawn',
                        7: 'Delta'
                    },
                    4: {
                        1: 'Bronco',
                        2: 'Gray Olive',
                        7: 'Napa'
                    },
                    5: {
                        5: 'Martini',
                        7: 'Cloudy'
                    },
                    7: 'Bud'
                },
                2: 'Swamp Green',
                3: {
                    4: 'Schist',
                    7: 'Norway'
                },
                5: 'Taupe Gray',
                7: 'Heathered Gray'
            },
            7: {
                0: {
                    3: 'Edward',
                    5: 'Shady Lady',
                    7: 'Silver Chalice'
                },
                1: {
                    2: {
                        0: 'Gray Chateau',
                        3: 'Hit Gray'
                    },
                    6: {
                        1: 'Spun Pearl',
                        3: 'Aluminium'
                    }
                },
                3: {
                    5: 'Bombay',
                    7: 'Tower Gray'
                },
                6: {
                    2: 'Eagle',
                    4: {
                        0: 'Nomad',
                        4: 'Malta'
                    },
                    5: 'Silk'
                },
                7: {
                    0: 'Nobel',
                    4: 'Pink Swan',
                    6: 'Tide'
                }
            }
        },
        1: {
            0: {
                1: 'Chetwode Blue',
                6: 'Blue Bell'
            },
            1: 'Portage',
            2: {
                0: {
                    6: 'Nepal',
                    7: 'Polo Blue'
                },
                2: 'Glacier',
                6: 'Rock Blue'
            },
            3: 'Jordy Blue',
            4: 'East Side',
            5: 'Dull Lavender',
            6: {
                0: 'Logan',
                1: {
                    0: 'Wistful',
                    5: 'Cold Purple'
                },
                2: 'Cadet Blue',
                3: {
                    6: 'Casper',
                    7: 'Pigeon Post'
                },
                4: 'London Hue',
                6: {
                    4: 'Chatelle',
                    6: 'French Gray'
                },
                7: {
                    6: 'Lavender Gray',
                    7: 'Blue Haze'
                }
            },
            7: {
                3: 'Perano',
                4: 'Biloba Flower'
            }
        },
        2: {
            0: 'Feijoa',
            1: {
                3: 'Vista Blue',
                5: 'Shadow Green',
                7: 'Algae Green'
            },
            2: {
                5: 'Granny Smith Apple',
                7: 'Mint Green'
            },
            5: {
                1: 'Spring Rain',
                2: 'Moss Green',
                4: 'Rainee',
                5: {
                    4: 'Green Spring',
                    6: 'Clay Ash'
                },
                7: 'Gum Leaf'
            },
            7: {
                0: 'Celadon',
                1: 'Chinook',
                7: 'Madang'
            }
        },
        3: {
            0: {
                0: 'Half Baked',
                2: 'Monte Carlo',
                7: 'Sinbad'
            },
            1: {
                0: 'Seagull',
                4: 'Cornflower',
                6: 'Morning Glory'
            },
            2: 'Riptide',
            3: 'Anakiwa',
            4: {
                0: 'Opal',
                3: 'Aqua Island',
                4: {
                    4: 'Silver Sand',
                    5: 'Submarine',
                    6: 'Powder Ash',
                    7: 'Loblolly'
                },
                5: {
                    0: 'Heather',
                    2: 'Jungle Mist'
                },
                6: {
                    1: 'Jet Stream',
                    4: 'Surf'
                }
            },
            5: {
                2: 'Regent St Blue',
                6: {
                    1: 'Spindle',
                    6: 'Ziggurat'
                }
            },
            6: {
                0: 'Padua',
                1: 'Water Leaf',
                3: 'Magic Mint',
                4: 'Fringy Flower',
                5: 'Cruise'
            },
            7: {
                0: 'Blizzard Blue',
                4: 'Powder Blue',
                5: {
                    5: 'Sail',
                    7: {
                        2: 'Charlotte',
                        7: 'French Pass'
                    }
                },
                6: 'Ice Cold'
            }
        },
        4: {
            0: {
                0: 'Old Rose',
                1: 'Puce',
                3: 'Oriental Pink',
                6: 'My Pink',
                7: 'Petite Orchid'
            },
            1: {
                0: 'Viola',
                6: {
                    0: 'Can Can',
                    3: 'Careys Pink'
                }
            },
            2: {
                1: 'Eunry',
                2: 'Sorrell Brown',
                3: {
                    0: 'Indian Khaki',
                    5: 'Rodeo Dust'
                },
                4: 'Tumbleweed',
                6: {
                    1: 'Tan',
                    3: 'Straw'
                },
                7: 'Cameo'
            },
            3: {
                1: 'Lily',
                2: {
                    0: 'Bison Hide',
                    2: 'Coral Reef'
                },
                3: {
                    2: {
                        0: 'Tea',
                        3: 'Cotton Seed'
                    },
                    7: 'Cold Turkey'
                },
                6: {
                    1: 'Clam Shell',
                    3: 'Vanilla'
                },
                7: 'Blossom'
            },
            4: {
                2: 'Tonys Pink',
                3: 'Sea Pink',
                4: 'Geraldine',
                6: 'Vivid Tangerine'
            },
            5: {
                0: 'Carissma',
                4: 'Tickle Me Pink',
                6: {
                    1: 'Mauvelous',
                    3: 'Wewak',
                    4: 'Pink Salmon',
                    6: 'Sweet Pink'
                }
            },
            6: {
                2: {
                    3: 'Gold Sand',
                    4: 'Tacao'
                },
                4: 'Hit Pink',
                5: 'Mona Lisa'
            },
            7: {
                2: 'Cashmere',
                3: {
                    2: 'Rose Fog',
                    3: 'Cavern Pink',
                    6: 'Shilo'
                },
                6: {
                    4: 'Rose Bud',
                    5: 'Cornflower Lilac',
                    7: 'Melon'
                },
                7: 'Sundown'
            }
        },
        5: {
            2: {
                0: 'Lilac',
                1: 'Light Wisteria',
                2: {
                    2: 'Pale Slate',
                    3: 'Gray Suit'
                },
                7: 'Thistle'
            },
            3: 'Perfume',
            4: {
                2: {
                    0: 'Shocking',
                    2: 'Kobi'
                },
                3: 'Light Orchid'
            },
            5: 'Lavender Magenta',
            6: {
                4: {
                    1: 'Illusion',
                    5: 'Carnation Pink'
                },
                5: 'Lavender Pink',
                7: {
                    4: 'Cotton Candy',
                    7: 'Cupid'
                }
            },
            7: {
                3: 'Mauve',
                4: 'Lavender Rose'
            }
        },
        6: {
            0: {
                1: {
                    2: 'Pine Glade',
                    4: 'Yuma'
                },
                5: {
                    1: 'Pavlova',
                    4: 'Brandy'
                },
                7: {
                    0: 'Winter Hazel',
                    2: 'Deco'
                }
            },
            1: {
                0: {
                    4: 'Chino',
                    7: 'Thistle Green'
                },
                1: {
                    0: 'Ash',
                    1: {
                        1: 'Gray Nickel',
                        7: {
                            0: 'Mist Gray',
                            5: 'Cloud'
                        }
                    },
                    3: 'Kangaroo',
                    5: 'Silver Rust',
                    6: 'Foggy Gray'
                },
                3: {
                    0: {
                        2: 'Sprout',
                        4: 'Coriander'
                    },
                    1: 'Pale Leaf',
                    2: 'Pixie Green',
                    4: 'Green Mist'
                },
                4: 'Akaroa',
                5: {
                    0: 'Soft Amber',
                    3: 'Sisal'
                },
                6: 'Sapling'
            },
            3: {
                2: 'Reef',
                5: 'Caper',
                7: 'Gossip'
            },
            4: {
                0: 'Putty',
                1: 'Calico',
                2: 'Flax',
                3: {
                    1: 'Zombie',
                    4: 'Chalky'
                },
                4: 'Chardonnay',
                5: {
                    3: 'Manhattan',
                    7: 'Peach Orange'
                },
                6: {
                    2: 'Buff',
                    5: 'Grandis',
                    7: 'Salomie'
                },
                7: {
                    1: 'New Orleans',
                    7: {
                        1: 'Marzipan',
                        4: 'Cherokee'
                    }
                }
            },
            5: {
                0: {
                    5: 'Zinnwaldite',
                    7: {
                        5: 'Desert Sand',
                        6: 'Pancho'
                    }
                },
                1: {
                    5: 'Beauty Bush',
                    7: 'Just Right'
                },
                2: 'Hampton',
                3: {
                    0: 'Grain Brown',
                    1: {
                        6: 'Double Spanish White',
                        7: 'Stark White'
                    },
                    6: 'Chamois',
                    7: 'Raffia'
                },
                4: {
                    5: 'Wax Flower',
                    6: 'Flesh'
                },
                5: {
                    0: 'Mandys Pink',
                    6: 'Apricot Peach'
                },
                6: {
                    0: 'Maize',
                    4: 'Corvette',
                    7: {
                        3: 'Peach Yellow',
                        7: {
                            5: 'Caramel',
                            6: 'Navajo White'
                        }
                    }
                },
                7: {
                    2: 'Wheat',
                    4: {
                        5: 'Romantic',
                        6: 'Light Apricot'
                    },
                    6: 'Frangipani'
                }
            },
            6: {
                1: {
                    4: 'Wild Rice',
                    7: 'Primrose'
                },
                2: {
                    3: 'Mindaro',
                    6: 'Honeysuckle'
                },
                3: 'Jonquil',
                4: {
                    1: {
                        2: 'Sahara Sand',
                        3: 'Khaki'
                    },
                    7: 'Sweet Corn'
                },
                5: 'Golden Glow',
                6: 'Dolly',
                7: {
                    5: 'Picasso',
                    7: {
                        1: 'Texas',
                        6: {
                            4: 'Witch Haze',
                            6: 'Pale Canary'
                        }
                    }
                }
            },
            7: {
                0: 'Double Colonial White',
                1: 'Fall Green',
                4: {
                    0: 'Sandwisp',
                    4: 'Cream Brulee',
                    5: 'Cape Honey',
                    6: 'Vis Vis'
                },
                5: {
                    1: 'Sidecar',
                    4: {
                        2: 'Banana Mania',
                        7: 'Peach'
                    },
                    5: {
                        3: {
                            0: 'Dairy Cream',
                            1: 'Givry'
                        }
                    },
                    7: {
                        0: 'Astra',
                        7: 'Colonial White'
                    }
                },
                6: {
                    3: 'Tidal',
                    5: 'Drover',
                    6: 'Milan'
                },
                7: {
                    3: 'Australian Mint',
                    4: 'Buttermilk',
                    6: 'Portafino',
                    7: {
                        2: 'Shalimar',
                        6: 'Pale Prim'
                    }
                }
            }
        },
        7: {
            0: {
                0: {
                    0: 'Silver',
                    2: 'Pumice'
                },
                1: 'Ghost',
                2: {
                    3: 'Sea Mist',
                    7: 'Tasman'
                },
                3: {
                    0: 'Tiara',
                    6: {
                        0: 'Conch',
                        1: 'Nebula',
                        3: 'Paris White'
                    }
                },
                4: {
                    2: 'Swirl',
                    6: 'Wafer'
                },
                5: {
                    4: 'Maverick',
                    7: 'Lola'
                },
                6: {
                    1: 'Celeste',
                    5: 'Timberwolf',
                    6: 'Tana',
                    7: 'Moon Mist'
                },
                7: {
                    0: 'Quill Gray',
                    1: {
                        1: 'Mischka',
                        6: 'Iron'
                    },
                    4: 'Swiss Coffee',
                    6: 'Westar',
                    7: 'Alto'
                }
            },
            1: {
                0: 'Periwinkle Gray',
                1: {
                    1: 'Melrose',
                    7: 'Periwinkle'
                },
                2: 'Botticelli',
                3: 'Tropical Blue',
                4: 'Prelude',
                5: 'Moon Raker',
                6: 'Geyser',
                7: 'Fog'
            },
            2: {
                1: {
                    4: {
                        1: 'Edgewater',
                        6: 'Surf Crest'
                    },
                    5: 'Skeptic'
                },
                4: 'Beryl Green',
                5: {
                    6: 'Zanah',
                    7: 'Willow Brook'
                },
                6: 'Tea Green',
                7: {
                    1: 'Blue Romance',
                    3: 'Snowy Mint'
                }
            },
            3: {
                0: 'Jagged Ice',
                2: {
                    1: 'Mint Tulip',
                    6: 'Aero Blue'
                },
                3: {
                    5: 'Onahau',
                    6: {
                        4: 'Humming Bird',
                        5: 'Scandal'
                    }
                },
                5: {
                    1: 'Hawkes Blue',
                    4: 'Link Water'
                },
                6: {
                    0: 'Granny Apple',
                    5: 'Swans Down'
                },
                7: {
                    4: 'Iceberg',
                    5: {
                        3: 'Mabel',
                        7: 'Pattens Blue'
                    },
                    6: 'White Ice',
                    7: {
                        1: 'Oyster Bay',
                        2: {
                            1: 'Foam',
                            6: 'Frosted Mint'
                        }
                    }
                }
            },
            4: {
                0: {
                    1: 'Pink Flare',
                    3: 'Dust Storm',
                    7: 'Oyster Pink'
                },
                1: {
                    0: 'Melanie',
                    3: 'Twilight'
                },
                2: {
                    0: 'Bone',
                    6: 'Almond'
                },
                3: 'Bizarre',
                4: {
                    4: 'Your Pink',
                    5: 'Pink'
                },
                5: {
                    3: 'Azalea',
                    5: 'Chantilly'
                },
                6: {
                    7: {
                        7: {
                            4: 'Tuft Bush',
                            5: 'Watusi'
                        }
                    }
                },
                7: {
                    3: 'Vanilla Ice',
                    5: 'Pastel Pink',
                    6: 'Peach Schnapps',
                    7: 'Cosmos'
                }
            },
            5: {
                0: 'French Lilac',
                2: 'Snuff',
                4: 'Classic Rose',
                6: {
                    2: 'We Peep',
                    4: 'Pig Pink',
                    7: 'Cherub'
                },
                7: 'Pink Lace'
            },
            6: {
                0: 'Aths Special',
                1: {
                    0: {
                        3: 'Periglacial Blue',
                        7: 'Satin Linen'
                    },
                    2: 'Kidnapper',
                    4: 'Pearl Bush',
                    6: 'White Rock'
                },
                2: {
                    4: 'Tusk',
                    5: 'Tahuna Sands'
                },
                3: {
                    2: 'Snow Flurry',
                    4: 'Chrome White',
                    5: {
                        7: {
                            0: 'Frost',
                            5: 'Loafer'
                        }
                    }
                },
                4: {
                    2: 'Mint Julep',
                    3: 'Wheatfield',
                    4: {
                        5: 'Negroni',
                        7: 'Tequila'
                    },
                    6: 'Egg White',
                    7: {
                        3: 'Champagne',
                        4: 'Sandy Beach',
                        7: 'Oasis'
                    }
                },
                5: {
                    2: {
                        0: 'Parchment',
                        4: {
                            1: 'Albescent White',
                            3: 'Janna'
                        }
                    },
                    5: {
                        5: {
                            0: 'Cinderella',
                            5: 'Pippin'
                        }
                    },
                    6: {
                        5: 'Karry',
                        7: 'Papaya Whip'
                    },
                    7: 'Derby'
                },
                6: {
                    3: 'Chiffon',
                    4: 'Beeswax',
                    5: {
                        7: {
                            4: 'Pipi',
                            5: 'Barley White'
                        }
                    },
                    7: {
                        1: 'Corn Field',
                        5: 'Lemon Chiffon'
                    }
                },
                7: {
                    1: 'Beige',
                    2: 'Orinoco',
                    3: {
                        2: 'Carla',
                        7: 'Spring Sun'
                    },
                    4: {
                        3: 'Citrine White',
                        6: {
                            0: 'Double Pearl Lusta',
                            3: 'Half Colonial White'
                        },
                        7: 'Milk Punch'
                    },
                    5: {
                        3: 'Coconut Cream',
                        4: {
                            4: 'Pink Lady',
                            5: 'Peach Cream',
                            6: 'Bleach White'
                        },
                        6: 'Half Spanish White',
                        7: {
                            0: 'Pearl Lusta',
                            4: 'Egg Sour',
                            7: {
                                2: 'Half Dutch White',
                                5: 'Varden'
                            }
                        }
                    },
                    6: {
                        2: 'Mimosa',
                        4: 'Baja White',
                        6: 'Cream',
                        7: 'Cumulus'
                    },
                    7: {
                        5: 'Scotch Mist',
                        6: 'Moon Glow'
                    }
                }
            },
            7: {
                0: {
                    0: {
                        4: 'Bon Jour',
                        7: 'Mercury'
                    },
                    2: 'Gray Nurse',
                    3: 'Mystic',
                    4: 'Ebb',
                    6: 'Green White',
                    7: {
                        6: 'Cararra',
                        7: 'Gallery'
                    }
                },
                2: {
                    0: {
                        2: 'Peppermint',
                        7: 'Frostee'
                    },
                    1: {
                        1: 'Apple Green',
                        2: 'Tara',
                        4: 'Harp'
                    },
                    3: 'Hint of Green',
                    5: {
                        0: 'Gin',
                        3: 'Panache'
                    },
                    6: 'Rice Flower',
                    7: 'Ottoman'
                },
                3: {
                    2: {
                        4: 'Off Green',
                        5: 'Polar'
                    },
                    3: {
                        3: 'Baby Blue',
                        5: 'Lily White',
                        7: {
                            7: {
                                3: 'Tranquil',
                                5: 'Bubbles'
                            }
                        }
                    },
                    4: {
                        2: 'Aqua Squeeze',
                        4: {
                            5: 'Athens Gray',
                            7: 'Porcelain'
                        },
                        7: {
                            0: 'Aqua Haze',
                            7: 'Catskill White'
                        }
                    },
                    5: {
                        3: 'Solitude',
                        7: 'Zumthor'
                    },
                    6: {
                        1: 'Aqua Spring',
                        4: 'Narvik'
                    },
                    7: {
                        3: {
                            2: 'Clear Day',
                            7: 'Dew'
                        },
                        7: 'Twilight Blue'
                    }
                },
                4: {
                    0: 'Pot Pourri',
                    1: 'Prim',
                    2: 'Dawn Pink',
                    3: 'Soft Peach',
                    5: 'Carousel Pink',
                    7: 'Fair Pink'
                },
                5: {
                    3: {
                        1: 'Blue Chalk',
                        3: {
                            2: 'Selago',
                            3: 'Titan White'
                        }
                    },
                    4: 'Pale Rose',
                    6: {
                        0: 'Amour',
                        4: 'Remy'
                    }
                },
                6: {
                    0: {
                        4: 'Quarter Spanish White',
                        5: {
                            2: 'Ecru White',
                            5: 'Merino'
                        }
                    },
                    1: 'Pampas',
                    3: 'Feta',
                    4: {
                        1: 'Linen',
                        6: 'Sazerac',
                        7: 'Old Lace'
                    },
                    5: {
                        0: 'White Linen',
                        5: {
                            4: 'Bridesmaid',
                            5: 'Forget Me Not'
                        },
                        6: 'Serenade',
                        7: 'Seashell Peach'
                    },
                    6: {
                        1: 'Rum Swizzle',
                        3: 'Hint of Yellow',
                        4: {
                            5: {
                                0: 'Solitaire',
                                3: 'Off Yellow',
                                6: 'Gin Fizz'
                            }
                        },
                        5: 'Early Dawn',
                        6: 'Half and Half',
                        7: {
                            3: 'China Ivory',
                            5: 'Chilean Heath'
                        }
                    },
                    7: {
                        6: {
                            4: 'Travertine',
                            5: 'Buttery White'
                        },
                        7: {
                            4: 'Orange White',
                            5: 'Island Spice',
                            6: 'Apricot White'
                        }
                    }
                },
                7: {
                    0: {
                        0: {
                            0: 'Seashell',
                            7: 'Concrete'
                        },
                        2: 'Saltpan',
                        7: {
                            0: 'Wild Sand',
                            7: 'Black Haze'
                        }
                    },
                    1: 'Whisper',
                    2: 'Snow Drift',
                    3: {
                        0: 'Black Squeeze',
                        1: 'Alice Blue',
                        5: 'Zircon'
                    },
                    4: {
                        0: 'Fantasy',
                        2: 'Spring Wood',
                        4: 'Chardon',
                        5: 'Lavender blush',
                        6: {
                            4: 'Provincial Pink',
                            5: {
                                5: 'Chablis',
                                7: 'Sauvignon'
                            }
                        },
                        7: 'Rose White'
                    },
                    5: {
                        3: {
                            1: 'Magnolia',
                            2: 'White Lilac'
                        },
                        4: 'Tutu',
                        6: 'Wisp Pink'
                    },
                    6: {
                        1: 'Desert Storm',
                        3: 'Sugar Cane',
                        4: 'Bianca',
                        5: {
                            1: 'Vista White',
                            6: 'Bridal Heath'
                        },
                        6: {
                            5: 'Orchid White',
                            6: {
                                4: 'Rice Cake',
                                6: 'Ivory'
                            }
                        },
                        7: {
                            4: 'Quarter Pearl Lusta',
                            7: 'Black White'
                        }
                    },
                    7: {
                        0: {
                            4: 'Hint of Red',
                            7: 'Alabaster'
                        },
                        4: 'Soapstone',
                        5: 'White Pointer',
                        6: 'Ceramic',
                        7: {
                            6: 'Romance',
                            7: 'White'
                        }
                    }
                }
            }
        }
    }
}

if __name__ == "__main__":
    exact = [("Amaranth", (229, 43, 80)), ("Bamboo", (218, 99, 4)), ("Camelot", (137, 52, 86)), ("Denim", (21, 96, 189)), ("Elephant", (18, 52, 71))]
    approximate = [("Black", (1, 3, 2)), ("White", (254, 255, 255))]
    print("Exact matches:")
    for name, color in exact:
        result = find(color)
        print("  {:16} Expected: {:9} Actual: {}".format(str(color), name, result))
    print("Approximate matches:")
    for name, color in approximate:
        result = find(color)
        print("  {:16} Expected: {:9} Actual: {}".format(str(color), name, result))
