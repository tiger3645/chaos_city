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
    FIGHTER = "fighter"
    GUNSLINGER = "gunslinger"
    TALKER = "talker"
    ENVIRONMENT = "environment"

@dataclass
class Card:
    id: int
    name: str
    faction: Faction
    type: CardType
    value: int
    zone: Optional[Zone] = None
    attack: int = 0
    defense: int = 0
    description: str = ""
    ability: Optional[str] = None

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
    # POLICE
    1: Card(
        id=1,
        name="Capitán O'Reilly",
        faction=Faction.POLICE,
        type=CardType.LEADER,
        zone=Zone.FIGHTER,
        value=8,
        attack=3,
        defense=7,
        description="Veterano endurecido, lidera con firmeza y no duda en ensuciarse las manos.",
        ability="'Redada': -1 ATK a todos los LUCHADORES enemigos este turno.",
    ),
    2: Card(
        id=2,
        name="Agentes de patrulla",
        faction=Faction.POLICE,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=2,
        attack=2,
        defense=3,
        description="Dos sombras azules recorren los callejones oscuros, buscando respuestas entre la lluvia y el humo. El brillo de sus linternas es la única certeza en la noche."
    ),
    3: Card(
        id=3,
        name="Sargento con escopeta",
        faction=Faction.POLICE,
        type=CardType.CHARACTER,
        zone=Zone.GUNSLINGER,
        value=3,
        attack=3,
        defense=2,
        description="Un guardián implacable de la ley, endurecido por años de patrullas en las calles más oscuras de Chicago. No retrocede ante la lluvia ni ante el delito; su sola presencia bajo la farola es una advertencia."
    ),
    4: Card(
        id=4,
        name="Detective de turno",
        faction=Faction.POLICE,
        type=CardType.CHARACTER,
        zone=Zone.TALKER,
        value=3,
        attack=2,
        defense=4,
        description="Un hombre endurecido por la ciudad, con paciencia corta y puños más duros que el asfalto. Cuando su voz no basta, la mesa tiembla."
    ),
    5: Card(
        id=5,
        name="Guardia antidisturbios",
        faction=Faction.POLICE,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=4,
        attack=3,
        defense=5,
        description="Si es destruido, evita el siguiente ataque directo al jugador."
    ),
    6: Card(
        id=6,
        name="Francotirador del tejado",
        faction=Faction.POLICE,
        type=CardType.CHARACTER,
        zone=Zone.GUNSLINGER,
        value=3,
        attack=4,
        defense=1,
        description="Un ojo fijo tras la mira en la lluvia. Acompañado solo por su paciencia, esperando el disparo perfecto."
    ),
    7: Card(
        id=7,
        name="Sirenas en la noche",
        faction=Faction.POLICE,
        type=CardType.EFFECT,
        value=3,
        description="Cancela la acción de un enemigo este turno."
    ),
    8: Card(
        id=8,
        name="Prisión preventiva",
        faction=Faction.POLICE,
        type=CardType.EFFECT,
        value=2,
        description="Devuelve una carta enemiga a la mano."
    ),
    9: Card(
        id=9,
        name="Sobrecarga de trabajo",
        faction=Faction.POLICE,
        type=CardType.EFFECT,
        value=2,
        description="El rival descarta una carta al azar."
    ),
    10: Card(
        id=10,
        name="Protección del Estado",
        faction=Faction.POLICE,
        type=CardType.EFFECT,
        value=4,
        description="Recupera 2 de Reputación."
    ),
    11: Card(
        id=11,
        name="Luz de patrulla",
        faction=Faction.POLICE,
        type=CardType.EFFECT,
        value=5,
        description="Impide que cualquier Ladrón use habilidades este turno."
    ),
    12: Card(
        id=12,
        name="Unidad canina",
        faction=Faction.POLICE,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=2,
        attack=3,
        defense=3,
        description="Un dúo inseparable, el oficial y su fiel compañero canino, patrullan las calles con un instinto agudo y una lealtad inquebrantable."
    ),
    13: Card(
        id=13,
        name="Barricadas improvisadas",
        faction=Faction.POLICE,
        type=CardType.ENVIRONMENT,
        zone=Zone.ENVIRONMENT,
        value=4,
        description="Todos los LUCHADORES aliados ganan +1 DEF mientras esta carta esté activa."
    ),
    14: Card(
        id=14,
        name="Pedir refuerzos",
        faction=Faction.POLICE,
        type=CardType.EFFECT,
        value=4,
        description="Roba 2 cartas."
    ),
    15: Card(
        id=15,
        name="Control de multitudes",
        faction=Faction.POLICE,
        type=CardType.EFFECT,
        value=3,
        description="El rival no puede atacar este turno."
    ),
    

    
    # MAFIA
    16: Card(
        id=16,
        name="Don Vito",
        faction=Faction.MAFIA,
        type=CardType.LEADER,
        zone=Zone.TALKER,
        value=9,
        attack=2,
        defense=8,
        description="El patriarca de la familia, cuya palabra es ley y cuyo poder se extiende en las sombras de la ciudad.",
        ability="Negociación: Gana 1 Reputación cada vez que un aliado es destruido.",
    ),
    17: Card(
        id=17,
        name="Matones a sueldo",
        faction=Faction.MAFIA,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=2,
        attack=3,
        defense=2,
        description="Tres figuras sombrías emergen de la niebla, sus miradas frías y calculadoras. En sus manos, la promesa de caos y control."
    ),
    18: Card(
        id=18,
        name="Pistolero de la familia",
        faction=Faction.MAFIA,
        type=CardType.CHARACTER,
        zone=Zone.GUNSLINGER,
        value=3,
        attack=4,
        defense=2,
        description="Un hombre con un pasado oscuro y una mira certera, siempre listo para defender el honor de la familia con un disparo rápido."
    ),
    19: Card(
        id=19,
        name="Consigliere astuto",
        faction=Faction.MAFIA,
        type=CardType.CHARACTER,
        zone=Zone.TALKER,
        value=3,
        attack=2,
        defense=4,
        description="Un hombre de palabras afiladas y mente aguda, siempre un paso adelante en el juego del poder y la traición."
    ),
    20: Card(
        id=20,
        name="Gangster con Tommy gun",
        faction=Faction.MAFIA,
        type=CardType.CHARACTER,
        zone=Zone.GUNSLINGER,
        value=4,
        attack=5,
        defense=1,
        description="Un hombre duro, con un cigarro perpetuamente encendido y una Thompson en mano, listo para sembrar el caos en las calles con ráfagas de balas."
    ),
    21: Card(
        id=21,
        name="Francotirador encubierto",
        faction=Faction.MAFIA,
        type=CardType.CHARACTER,
        zone=Zone.GUNSLINGER,
        value=3,
        attack=4,
        defense=1,
        description="Un asesino silencioso, moviéndose entre las sombras con una precisión mortal y un ojo para el blanco perfecto."
    ),
    22: Card(
        id=22,
        name="Soborno",
        faction=Faction.MAFIA,
        type=CardType.EFFECT,
        value=3,
        description="Roba una carta y gana 1 Reputación."
    ),
    23: Card(
        id=23,
        name="Amenaza velada",
        faction=Faction.MAFIA,
        type=CardType.EFFECT,
        value=2,
        description="Destruye una carta enemiga de valor 3 o menos."
    ),
    24: Card(
        id=24,
        name="Extorsión",
        faction=Faction.MAFIA,
        type=CardType.EFFECT,
        value=2,
        description="El rival pierde 2 de Reputación."
    ),
    25: Card(
        id=25,
        name="Red de influencias",
        faction=Faction.MAFIA,
        type=CardType.EFFECT,
        value=4,
        description="Roba 3 cartas."
    ),
    26: Card(
        id=26,
        name="Contrabando",
        faction=Faction.MAFIA,
        type=CardType.EFFECT,
        value=5,
        description="Gana 3 de Reputación."
    ),
    27: Card(
        id=27,
        name="Perro de pelea",
        faction=Faction.MAFIA,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=2,
        attack=4,
        defense=3,
        description="Un luchador feroz, entrenado en las calles y siempre listo para la próxima pelea, con cicatrices que cuentan historias de supervivencia y brutalidad."
    ),
    28: Card(
        id=28,
        name="Club nocturno",
        faction=Faction.MAFIA,
        type=CardType.ENVIRONMENT,
        zone=Zone.ENVIRONMENT,
        value=4,
        description="Todos los PERSUASORES aliados ganan +1 DEF mientras esta carta esté activa."
    ),
    29: Card(
        id=29,
        name="Lavado de dinero",
        faction=Faction.MAFIA,
        type=CardType.EFFECT,
        value=3,
        description="Reduce el coste de todas las cartas en tu mano en 1 este turno."
    ),
    30: Card(
        id=30,
        name="Ataque sorpresa",
        faction=Faction.MAFIA,
        type=CardType.EFFECT,
        value=3,
        description="Ignora la defensa de un enemigo este turno."
    ),



    # DETECTIVE
    31: Card(
        id=31,
        name="Detective Marlowe",
        faction=Faction.DETECTIVE,
        type=CardType.LEADER,
        zone=Zone.TALKER,
        value=8,
        attack=6,
        defense=4,
        description="Un investigador astuto y persistente, conocido por su habilidad para desentrañar los casos más complejos en las calles oscuras de la ciudad.",
        ability="Intuición: Mira la mano del rival al inicio de tu turno.",
    ),
    32: Card(
        id=32,
        name="Investigador privado",
        faction=Faction.DETECTIVE,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=3,
        attack=2,
        defense=3,
        description="Un investigador astuto y persistente, siempre en busca de la verdad."
    ),
    33: Card(
        id=33,
        name="Tirador experto",
        faction=Faction.DETECTIVE,
        type=CardType.CHARACTER,
        zone=Zone.GUNSLINGER,
        value=4,
        attack=5,
        defense=2,
        description="Un tirador con una puntería impecable, siempre listo para proteger a los inocentes con un disparo certero."
    ),
    34: Card(
        id=34,
        name="Informante callejero",
        faction=Faction.DETECTIVE,
        type=CardType.CHARACTER,
        zone=Zone.TALKER,
        value=2,
        attack=1,
        defense=2,
        description="Un informante anónimo que se mueve entre las sombras."
    ),
    35: Card(
        id=35,
        name="Oficial de policía encubierto",
        faction=Faction.DETECTIVE,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=6,
        attack=4,
        defense=4,
        description="Un oficial que ha dejado su placa para infiltrarse en las filas criminales, siempre vigilante y listo para actuar."
    ),
    36: Card(
        id=36,
        name="Tácticas de interrogatorio",
        faction=Faction.DETECTIVE,
        type=CardType.EFFECT,
        value=3,
        description="Mira la mano del rival y descarta una carta."
    ),
    37: Card(
        id=37,
        name="Orden de registro",
        faction=Faction.DETECTIVE,
        type=CardType.EFFECT,
        value=4,
        description="Destruye una carta enemiga de valor 4 o menos."
    ),
    38: Card(
        id=38,
        name="Informantes confiables",
        faction=Faction.DETECTIVE,
        type=CardType.EFFECT,
        value=4,
        description="Roba 2 cartas."
    ),
    39: Card(
        id=39,
        name="Evidencia incriminatoria",
        faction=Faction.DETECTIVE,
        type=CardType.EFFECT,
        value=3,
        description="El rival no puede atacar en su siguiente turno."
    ),
    40: Card(
        id=40,
        name="Mercenario",
        faction=Faction.DETECTIVE,
        type=CardType.CHARACTER,
        zone=Zone.GUNSLINGER,
        value=4,
        attack=5,
        defense=2,
        description="Un soldado de fortuna, contratado para proteger y servir a quien pague más, con habilidades letales y una moral flexible."
    ),
    41: Card(
        id=41,
        name="Bandolero",
        faction=Faction.DETECTIVE,
        type=CardType.CHARACTER,
        zone=Zone.GUNSLINGER,
        value=5,
        attack=6,
        defense=3,
        description="Un experto tirador que puede eliminar a sus objetivos desde la distancia con un solo disparo."
    ),
    42: Card(
        id=42,
        name="Refugio seguro",
        faction=Faction.DETECTIVE,
        type=CardType.ENVIRONMENT,
        zone=Zone.ENVIRONMENT,
        value=4,
        description="Todos los PERSUASORES aliados ganan +1 DEF mientras esta carta esté activa."
    ),
    43: Card(
        id=43,
        name="Red de vigilancia",
        faction=Faction.DETECTIVE,
        type=CardType.EFFECT,
        value=2,
        description="Mira la mano del rival."
    ),
    44: Card(
        id=44,
        name="Testigo protegido",
        faction=Faction.DETECTIVE,
        type=CardType.EFFECT,
        value=3,
        description="Recupera 2 de Reputación."
    ),
    45: Card(
        id=45,
        name="Emboscada",
        faction=Faction.DETECTIVE,
        type=CardType.EFFECT,
        value=5,
        description="Destruye una carta enemiga de valor 5 o menos."
    ),


    # THIEF
    46: Card(
        id=46,
        name="Sombra",
        faction=Faction.THIEF,
        type=CardType.LEADER,
        zone=Zone.FIGHTER,
        value=7,
        attack=8,
        defense=3,
        description="Un maestro del sigilo y la evasión, capaz de moverse sin ser detectado y atacar desde las sombras."
    ),
    47: Card(
        id=47,
        name="Ladrones callejeros",
        faction=Faction.THIEF,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=2,
        attack=3,
        defense=2,
        description="Un grupo de jóvenes astutos y ágiles, expertos en el arte del hurto y la evasión."
    ),
    48: Card(
        id=48,
        name="Secuestrador",
        faction=Faction.THIEF,
        type=CardType.CHARACTER,
        zone=Zone.GUNSLINGER,
        value=3,
        attack=4,
        defense=2,
        description="Armado y peligroso, siempre listo para tomar rehenes y exigir rescates."
    ),
    49: Card(
        id=49,
        name="Estafador",
        faction=Faction.THIEF,
        type=CardType.CHARACTER,
        zone=Zone.TALKER,
        value=2,
        attack=2,
        defense=3,
        description="Un maestro del engaño y la manipulación, capaz de convencer a cualquiera de cualquier cosa."
    ),
    50: Card(
        id=50,
        name="Ladrón de guante blanco",
        faction=Faction.THIEF,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=4,
        attack=5,
        defense=3,
        description="Un ladrón elegante y sofisticado, conocido por sus robos audaces y su estilo impecable."
    ),
    51: Card(
        id=51,
        name="Robo relámpago",
        faction=Faction.THIEF,
        type=CardType.EFFECT,
        value=3,
        description="Roba una carta y gana 1 Reputación."
    ),
    52: Card(
        id=52,
        name="Trampa para incautos",
        faction=Faction.THIEF,
        type=CardType.EFFECT,
        value=2,
        description="Destruye una carta enemiga de valor 3 o menos."
    ),
    53: Card(
        id=53,
        name="Callejones oscuros",
        faction=Faction.THIEF,
        type=CardType.ENVIRONMENT,
        zone=Zone.ENVIRONMENT,
        value=4,
        description="Todos los LUCHADORES aliados ganan +1 ATK mientras esta carta esté activa."
    ),
    54: Card(
        id=54,
        name="Escape audaz",
        faction=Faction.THIEF,
        type=CardType.EFFECT,
        value=4,
        description="Devuelve una carta descartada a tu mazo."
    ),
    55: Card(
        id=55,
        name="Red de contrabando",
        faction=Faction.THIEF,
        type=CardType.EFFECT,
        value=5,
        description="Gana 3 de Reputación."
    ),
    56: Card(
        id=56,
        name="Asaltante nocturno",
        faction=Faction.THIEF,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=3,
        attack=4,
        defense=2,
        description="Un ladrón que opera bajo el manto de la noche, sucio y astuto."
    ),
    57: Card(
        id=57,
        name="Maestro del disfraz",
        faction=Faction.THIEF,
        type=CardType.CHARACTER,
        zone=Zone.TALKER,
        value=3,
        attack=2,
        defense=4,
        description="Un experto en cambiar de identidad y mezclarse entre las multitudes."
    ),
    58: Card(
        id=58,
        name="Botín valioso",
        faction=Faction.THIEF,
        type=CardType.EFFECT,
        value=2,
        description="Roba 2 cartas."
    ),
    59: Card(
        id=59,
        name="Pacto oscuro",
        faction=Faction.THIEF,
        type=CardType.EFFECT,
        value=3,
        description="El rival pierde 2 de Reputación."
    ),
    60: Card(
        id=60,
        name="Golpe maestro",
        faction=Faction.THIEF,
        type=CardType.EFFECT,
        value=4,
        description="Destruye una carta enemiga de valor 4 o menos."
    ),


    # WILDCARD
    61: Card(
        id=61,
        name="Risas el payaso alegre",
        faction=Faction.WILDCARD,
        type=CardType.LEADER,
        zone=Zone.FIGHTER,
        value=10,
        attack=8,
        defense=3,
        description="Más que un bufón, un enigma de colores brillantes.",
        ability="Caos: Lanza una moneda, si sale cara, roba una carta, si sale cruz, devuelve una carta de tu mano al mazo."
    ),
    62: Card(
        id=62,
        name="La niña",
        faction=Faction.WILDCARD,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=5,
        attack=0,
        defense=0,
        description="Una niña pequeña. Destruirla cuesta 5 de Reputación.",
    ),
    63: Card(
        id=63,
        name="El mago",
        faction=Faction.WILDCARD,
        type=CardType.CHARACTER,
        zone=Zone.TALKER,
        value=6,
        attack=2,
        defense=5,
        description="Un ilusionista que juega con la mente y la realidad.",
    ),
    64: Card(
        id=64,
        name="El acróbata",
        faction=Faction.WILDCARD,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=4,
        attack=4,
        defense=2,
        description="Un maestro del equilibrio y la agilidad, capaz de hazañas impresionantes.",
    ),
    65: Card(
        id=65,
        name="El dentista",
        faction=Faction.WILDCARD,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=5,
        attack=5,
        defense=3,
        description="Un dentista. Terrible.",
    ),
    66: Card(
        id=66,
        name="El caballero",
        faction=Faction.WILDCARD,
        type=CardType.CHARACTER,
        zone=Zone.FIGHTER,
        value=7,
        attack=6,
        defense=4,
        description="Un noble guerrero con un fuerte sentido del honor.",
    ),
    67: Card(
        id=67,
        name="Una ardilla rabiosa",
        faction=Faction.WILDCARD,
        type=CardType.CHARACTER,
        zone=Zone.TALKER,
        value=2,
        attack=4,
        defense=0,
        description="Una ardilla. Rabiosa. Espuma, dientes, locura. Rabiosa.",
    ),
    68: Card(
        id=68,
        name="Electrocutar",
        faction=Faction.WILDCARD,
        type=CardType.EFFECT,
        value=3,
        description="Pierde 1 de Reputación para destruir una carta enemiga."
    ),
    69: Card(
        id=69,
        name="Cambio de identidad",
        faction=Faction.WILDCARD,
        type=CardType.EFFECT,
        value=2,
        description="Intercambia una carta aleatoria de tu mano con una carta aleatoria de la mano del rival."
    ),
    70: Card(
        id=70,
        name="Caos controlado",
        faction=Faction.WILDCARD,
        type=CardType.EFFECT,
        value=4,
        description="Roba 2 cartas y descarta 1 carta."
    ),
    71: Card(
        id=71,
        name="Mente maestra",
        faction=Faction.WILDCARD,
        type=CardType.EFFECT,
        value=5,
        description="Mira la mano del rival y roba una carta de su elección."
    ),
    72: Card(
        id=72,
        name="Muestra gratuita",
        faction=Faction.WILDCARD,
        type=CardType.EFFECT,
        value=2,
        description="Juega una carta de tu mano sin pagar su coste."
    ),
    73: Card(
        id=73,
        name="Bomba atómica",
        faction=Faction.WILDCARD,
        type=CardType.EFFECT,
        value=5,
        description="Destruye todas las cartas en juego."
    ),
    74: Card(
        id=74,
        name="Circo ambulante",
        faction=Faction.WILDCARD,
        type=CardType.ENVIRONMENT,
        zone=Zone.ENVIRONMENT,
        value=4,
        description="Todas las cartas aliadas ganan +1 ATK y +1 DEF."
    ),
    75: Card(
        id=75,
        name="Misterio",
        faction=Faction.WILDCARD,
        type=CardType.EFFECT,
        value=3,
        description="Toma la cantidad de monedas que quieras del pozo común y pierde 1 de Reputación por cada moneda tomada."
    ),
}


def get_starter_deck(faction: Faction) -> List[int]:
    """Returns a list of card IDs for a starter deck of the given faction"""
    starter_decks = {
        Faction.POLICE: [
            # una de cada efecto, una de lider, una de ambiente, y el resto de personajes
            1, 7, 8, 9, 10, 11, 13, 14, 15,
            2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 12, 12
        ],
        Faction.MAFIA: [
            16, 22, 23, 24, 25, 26, 28, 29, 30,
            17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 27, 27
        ],
        Faction.DETECTIVE: [
            31, 36, 37, 38, 39, 43, 44, 45, 42,
            32, 32, 33, 33, 34, 34, 35, 35, 40, 40, 41, 41
        ],
        Faction.THIEF: [
            46, 51, 52, 54, 55, 58, 59, 60, 53,
            47, 47, 48, 48, 49, 49, 50, 50, 56, 56, 57, 57
        ],
        Faction.WILDCARD: [
            61, 68, 69, 70, 71, 72, 73, 74, 75,
            62, 62, 63, 63, 64, 64, 65, 65, 66, 66, 67, 67
        ]
    }
    return starter_decks.get(faction, [])
