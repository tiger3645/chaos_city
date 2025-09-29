from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from enum import Enum

class Faction(Enum):
    POLICE = "police"
    MAFIA = "mafia"
    DETECTIVE = "detective"
    THIEF = "thief"
    WILDCARD = "wildcard"

class CardType(Enum):
    LEADER = "leader"
    CHARACTER = "character"
    EFFECT = "effect"
    ENVIRONMENT = "environment"

class Zone(Enum):
    BRUTES = "brutes"
    SHOOTERS = "shooters"
    TALKERS = "talkers"

@dataclass
class Card:
    id: str
    name: str
    faction: Faction
    card_type: CardType
    zone: Optional[Zone]
    attack: int = 0
    defense: int = 0
    cost: int = 0
    description: str = ""
    ability: Optional[str] = None
    is_unique: bool = False

@dataclass
class Player:
    id: str
    name: str
    reputation: int = 20
    hand: List[Card] = field(default_factory=list)
    deck: List[Card] = field(default_factory=list)
    field: Dict[Zone, List[Card]] = field(default_factory=lambda: {zone: [] for zone in Zone})
    leader: Optional[Card] = None

Phase = Literal["draw", "deploy", "action", "resolution"]

@dataclass
class GameState:
    game_id: str
    players: List[Player]
    current_player: int = 0
    turn: int = 1
    phase: Phase = "draw"
    winner: Optional[str] = None
    active_environments: Dict[Zone, Optional[Card]] = field(default_factory=lambda: {zone: None for zone in Zone})

# Card database
CARDS_DB = {
    # Police faction
    "captain_oreilly": Card(
        id="captain_oreilly",
        name="Capitán O'Reilly",
        faction=Faction.POLICE,
        card_type=CardType.LEADER,
        zone=Zone.BRUTES,
        attack=3,
        defense=7,
        description="Habilidad única: 'Redada' – reduce -1 ATK a todos los Brutos enemigos este turno.",
        ability="raid",
        is_unique=True
    ),
    "patrol_agent": Card(
        id="patrol_agent",
        name="Agente de patrulla",
        faction=Faction.POLICE,
        card_type=CardType.CHARACTER,
        zone=Zone.BRUTES,
        attack=2,
        defense=3,
        description="Gana +1 DEF si hay otro Policía en la misma zona."
    ),
    "sergeant_shotgun": Card(
        id="sergeant_shotgun",
        name="Sargento con escopeta",
        faction=Faction.POLICE,
        card_type=CardType.CHARACTER,
        zone=Zone.SHOOTERS,
        attack=3,
        defense=2,
        description="Daño doble contra Mafiosos."
    ),
    "detective_on_duty": Card(
        id="detective_on_duty",
        name="Detective de turno",
        faction=Faction.POLICE,
        card_type=CardType.CHARACTER,
        zone=Zone.TALKERS,
        attack=2,
        defense=4,
        description="Al entrar, puedes ver la carta superior del mazo rival."
    ),
    "riot_guard": Card(
        id="riot_guard",
        name="Guardia antidisturbios",
        faction=Faction.POLICE,
        card_type=CardType.CHARACTER,
        zone=Zone.BRUTES,
        attack=3,
        defense=5,
        description="Si es destruido, evita el siguiente ataque directo al jugador."
    ),
    "rooftop_sniper_police": Card(
        id="rooftop_sniper_police",
        name="Francotirador del tejado",
        faction=Faction.POLICE,
        card_type=CardType.CHARACTER,
        zone=Zone.SHOOTERS,
        attack=4,
        defense=1,
        description="Ataca primero en su zona."
    ),
    
    # Mafia faction
    "don_moretti": Card(
        id="don_moretti",
        name="Don Moretti",
        faction=Faction.MAFIA,
        card_type=CardType.LEADER,
        zone=Zone.TALKERS,
        attack=5,
        defense=6,
        description="Habilidad única: 'Orden de ejecución' – elimina una unidad enemiga de fuerza 3 o menos.",
        ability="execution_order",
        is_unique=True
    ),
    "thug_with_bat": Card(
        id="thug_with_bat",
        name="Matón con bate",
        faction=Faction.MAFIA,
        card_type=CardType.CHARACTER,
        zone=Zone.BRUTES,
        attack=3,
        defense=3,
        description=""
    ),
    "trusted_man": Card(
        id="trusted_man",
        name="Hombre de confianza",
        faction=Faction.MAFIA,
        card_type=CardType.CHARACTER,
        zone=Zone.TALKERS,
        attack=2,
        defense=4,
        description="Mientras esté en juego, los Brutos ganan +1 DEF."
    ),
    "gangster_thompson": Card(
        id="gangster_thompson",
        name="Gánster con Thompson",
        faction=Faction.MAFIA,
        card_type=CardType.CHARACTER,
        zone=Zone.SHOOTERS,
        attack=4,
        defense=2,
        description=""
    ),
    "getaway_driver": Card(
        id="getaway_driver",
        name="Conductor de huida",
        faction=Faction.MAFIA,
        card_type=CardType.CHARACTER,
        zone=Zone.TALKERS,
        attack=1,
        defense=3,
        description="Puede mover un aliado a otra zona."
    ),
    
    # Detective faction
    "detective_sullivan": Card(
        id="detective_sullivan",
        name="Detective Sullivan",
        faction=Faction.DETECTIVE,
        card_type=CardType.LEADER,
        zone=Zone.TALKERS,
        attack=4,
        defense=5,
        description="Habilidad pasiva: 'Ojo clínico' – siempre que robes una carta, mira una del rival.",
        ability="keen_eye",
        is_unique=True
    ),
    "street_hound": Card(
        id="street_hound",
        name="Sabueso de la calle",
        faction=Faction.DETECTIVE,
        card_type=CardType.CHARACTER,
        zone=Zone.TALKERS,
        attack=2,
        defense=2,
        description="Al entrar, fuerza al rival a revelar una carta de su mano."
    ),
    
    # Thief faction
    "la_sombra": Card(
        id="la_sombra",
        name="La Sombra",
        faction=Faction.THIEF,
        card_type=CardType.LEADER,
        zone=Zone.TALKERS,
        attack=2,
        defense=4,
        description="Habilidad única: 'Golpe silencioso' – roba 2 de Reputación al enemigo directamente.",
        ability="silent_strike",
        is_unique=True
    ),
    "pickpocket": Card(
        id="pickpocket",
        name="Carterista",
        faction=Faction.THIEF,
        card_type=CardType.CHARACTER,
        zone=Zone.TALKERS,
        attack=1,
        defense=2,
        description="Roba 1 carta al entrar."
    ),
    
    # Wildcard faction
    "el_tahur": Card(
        id="el_tahur",
        name="El Tahúr",
        faction=Faction.WILDCARD,
        card_type=CardType.LEADER,
        zone=Zone.TALKERS,
        attack=3,
        defense=4,
        description="Habilidad condicional: Si ganas un duelo de Charlatanes, dobla tu ataque hasta el final del turno.",
        ability="gambler_luck",
        is_unique=True
    ),
    "street_boxer": Card(
        id="street_boxer",
        name="Boxeador callejero",
        faction=Faction.WILDCARD,
        card_type=CardType.CHARACTER,
        zone=Zone.BRUTES,
        attack=3,
        defense=3,
        description="Si pierde, inflige 1 daño al rival igual."
    )
}

def get_starter_deck(faction: Faction) -> List[str]:
    """Returns a list of card IDs for a starter deck of the given faction"""
    starter_decks = {
        Faction.POLICE: [
            "captain_oreilly", "patrol_agent", "patrol_agent", "sergeant_shotgun", 
            "detective_on_duty", "riot_guard", "rooftop_sniper_police"
        ],
        Faction.MAFIA: [
            "don_moretti", "thug_with_bat", "thug_with_bat", "trusted_man",
            "gangster_thompson", "getaway_driver"
        ],
        Faction.DETECTIVE: [
            "detective_sullivan", "street_hound", "street_hound"
        ],
        Faction.THIEF: [
            "la_sombra", "pickpocket", "pickpocket"
        ],
        Faction.WILDCARD: [
            "el_tahur", "street_boxer", "street_boxer"
        ]
    }
    return starter_decks.get(faction, [])