from typing import List, Optional

from pydantic import BaseModel


class search_match_info(BaseModel):
    ID: str
    activity: str
    party_members: str
    isPrivate: bool
    experience: str
    split_type: str
    accounts: str
    regions: str
    player_count: str
    party_leader: str
    match_version: str
    notes: Optional[str]


class location(BaseModel):
    """location model"""

    x: int
    y: int
    regionX: int
    regionY: int
    regionID: int
    plane: int
    world: int


class all_search_match_info(BaseModel):
    search_matches: List[search_match_info]


class stats(BaseModel):
    """player skills"""

    attack: int
    strength: int
    defense: int
    ranged: int
    prayer: int
    magic: int
    runecraft: int
    construction: int
    hitpoints: int
    agility: int
    herblore: int
    thieving: int
    crafting: int
    fletching: int
    slayer: int
    hunter: int
    mining: int
    smithing: int
    fishing: int
    cooking: int
    firemaking: int
    woodcutting: int
    farming: int


class status(BaseModel):
    """player status"""

    hp: int
    base_hp: int
    prayer: int
    base_prayer: int
    run_energy: int


class player(BaseModel):
    """player model"""

    discord: str
    stats: Optional[stats]
    status: Optional[status]
    location: Optional[location]
    runewatch: Optional[str]
    wdr: Optional[str]
    verified: Optional[bool]
    rating: Optional[int]
    kick_list: Optional[list[int]]
    promote_list: Optional[list[int]]
    user_id: int
    login: str
    isPartyLeader: Optional[bool] = False


class requirement(BaseModel):
    """match requirements"""

    experience: str
    split_type: str
    accounts: str
    regions: str


class match(BaseModel):
    """match model"""

    discord_invite: Optional[str]
    ID: str
    activity: str
    party_members: str
    group_passcode: str
    isPrivate: bool
    match_version: str
    notes: Optional[str]
    ban_list: Optional[list[int]]
    requirement: requirement
    players: list[player]


class ping(BaseModel):
    """ping model"""

    username: str
    x: int
    y: int
    regionX: int
    regionY: int
    regionID: int
    plane: int
    color_r: int
    color_g: int
    color_b: int
    color_alpha: int
    isAlert: bool


class active_match_discord(BaseModel):
    """active match model"""

    discord_invite: Optional[str]
    player_count: Optional[int]
    ID: str
