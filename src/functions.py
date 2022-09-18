import aiohttp
import json
import re


async def get_url(route):
    async with aiohttp.ClientSession() as session:
        async with session.get(route) as resp:
            response = await resp.text()
    response = json.loads(response)
    return response


async def post_url(route, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=route, json=data) as resp:
            response = await resp.text()


async def check_match_id(match_id: str) -> bool:
    if re.fullmatch("^[a-z]{2,7}-[a-z]{2,7}-[a-z]{2,7}", match_id):
        return True
    return False


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ActivityList:
    def __init__(self):
        self.activity_list = [
            "Random Activity",
            "Attack",
            "Strength",
            "Defence",
            "Hitpoints",
            "Ranged",
            "Prayer",
            "Magic",
            "Cooking",
            "Woodcutting",
            "Fletching",
            "Fishing",
            "Firemaking",
            "Crafting",
            "Smithing",
            "Mining",
            "Herblore",
            "Agility",
            "Thieving",
            "Slayer",
            "Farming",
            "Runecraft",
            "Hunter",
            "Construction",
            "All Skills",
            "Abyssal Sire",
            "Alchemical Hydra",
            "Crazy Archaeologist",
            "Deranged Archaeologist",
            "Bryophyta",
            "Barrows Brothers",
            "Callisto",
            "Cerberus",
            "Chaos Elemental",
            "Chaos Fanatic",
            "Commander Zilyana",
            "Corporeal Beast",
            "Dagannoth Prime",
            "Dagannoth Rex",
            "Dagannoth Supreme",
            "General Graardor",
            "Giant Mole",
            "Grotesque Guardians",
            "Hespori",
            "Kalphite Queen",
            "King Black Dragon",
            "Kraken",
            "Kreearra",
            "Kril Tsutsaroth",
            "Mimic",
            "Nex",
            "Nightmare",
            "Obor",
            "Phosani's Nightmare",
            "Sarachnis",
            "Scorpia",
            "Skotizo",
            "Gauntlet",
            "The Corrupted Gauntlet",
            "Thermonuclearsmokedevil",
            "The Inferno",
            "The Fight Caves",
            "Venenatis",
            "Vet'ion",
            "Vorkath",
            "Zalcano",
            "Zulrah",
            "Barbarian Assault",
            "Blast Furnace",
            "Blast Mine",
            "Brimhaven Agility Arena",
            "Bounty Hunter",
            "Camdozaal Vault",
            "Castle Wars",
            "Clan Wars",
            "Creature Creation",
            "PVP Arena",
            "Fishing Trawler",
            "Giants' Foundry",
            "Gnome Ball",
            "Gnome Restaurant",
            "Guardians of the Rift",
            "Hallowed Sepulchre",
            "Herbiboar",
            "Puro Puro",
            "Mage Arena",
            "Mahogany Homes",
            "Mage Training Arena",
            "Motherlode Mine",
            "Nightmare Zone",
            "Organized Crime",
            "Pest Control",
            "Pyramid Plunder",
            "Rogues Den",
            "Shades of Morton",
            "Shooting Stars",
            "Sorceress's Garden",
            "Tai Bwo Wannai",
            "Tithe Farm",
            "Trouble Brewing",
            "Underwater Agility and Thieving",
            "Volcanic Mine",
            "Last Man Standing",
            "Soul Wars",
            "Tempoross",
            "Wintertodt",
            "Chambers of Xeric",
            "Chambers of Xeric Challenge Mode",
            "Entry Theatre of Blood",
            "Theatre of Blood",
            "Theatre of Blood Hard Mode",
            "Entry Tombs of Amascut",
            "Tombs of Amascut",
            "Expert Tombs of Amascut",
            "Bankstanding",
            "Clues",
            "Falador Party Room",
            "PKing",
            "Chat and Relax",
            "All Quests",
            "All Diaries",
            "All Kourend Favors",
            "Combat Achievements (Easy)",
            "Combat Achievements (Medium)",
            "Combat Achievements (Hard)",
            "Combat Achievements (Elite)",
            "Combat Achievements (Master)",
            "Combat Achievements (Grandmaster)",
            "All Combat Achievements",
            "Money-making",
            "Free-to-Play",
        ]
