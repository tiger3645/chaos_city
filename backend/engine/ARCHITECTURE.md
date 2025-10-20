# Arquitectura del Sistema de Efectos

```
┌─────────────────────────────────────────────────────────────────┐
│                         CHAOS CITY GAME                          │
│                      Sistema de Efectos v1.0                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          GAME ENGINE                             │
│  (base.py - Motor principal del juego)                          │
│                                                                  │
│  • create_game()        • play_card()                           │
│  • join_game()          • attack()                              │
│  • draw_card()          • next_phase()                          │
│                                                                  │
│  ┌──────────────────────────────────────────────┐              │
│  │         Integración con Efectos               │              │
│  │  play_card_with_effects()                     │              │
│  │  attack_with_effects()                        │              │
│  │  start_turn_with_effects()                    │              │
│  │  end_turn_with_effects()                      │              │
│  └──────────────────────────────────────────────┘              │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ usa
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EFFECT MANAGER                              │
│  (effects.py - Gestor centralizado)                             │
│                                                                  │
│  • registered_effects: Dict[str, Effect]                        │
│  • active_passive_effects: Dict[str, List[PassiveEffect]]      │
│  • active_async_effects: Dict[str, List[AsyncEffect]]          │
│                                                                  │
│  Métodos:                                                        │
│  ├─ register_effect(effect)                                     │
│  ├─ execute_immediate_effect(effect_id, context)                │
│  ├─ add_passive_effect(game_id, effect)                         │
│  ├─ add_async_effect(game_id, effect)                           │
│  ├─ trigger_effects(game_id, trigger, context)                  │
│  ├─ get_stat_modifiers(game_id, card)                           │
│  └─ clear_game_effects(game_id)                                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ gestiona
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TIPOS DE EFECTOS                             │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │ ImmediateEffect │  │ PassiveEffect   │  │ AsyncEffect    │ │
│  │                 │  │                 │  │                │ │
│  │ • Ejecución     │  │ • Modificadores │  │ • Temporales   │ │
│  │   única         │  │   continuos     │  │ • Retardados   │ │
│  │ • Inmediata     │  │ • Triggers      │  │ • Auto-expiran │ │
│  │ • Puede requerir│  │ • Reactivos     │  │ • Una ejecución│ │
│  │   objetivo      │  │                 │  │                │ │
│  │ • Multi-paso    │  │                 │  │                │ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ implementados en
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EFECTOS CONCRETOS                              │
│  (card_effects.py - Implementaciones específicas)               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │             EFECTOS INMEDIATOS                        │      │
│  │  • DrawCardsEffect         • DestroyCardEffect       │      │
│  │  • DealDamageEffect        • ReturnToHandEffect      │      │
│  │  • HealReputationEffect    • DiscardRandomEffect     │      │
│  │  • RevealOpponentHandEffect                          │      │
│  │  • SwapRandomHandCardEffect                          │      │
│  │  • DestroyAllCardsEffect                             │      │
│  │  • PlayCardFreeEffect                                │      │
│  │  ... y más                                           │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │             EFECTOS PASIVOS                           │      │
│  │  • StatModifierEffect                                │      │
│  │  • OnAllyDestroyEffect                               │      │
│  │  • OnTurnStartEffect                                 │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │             EFECTOS ASÍNCRONOS                        │      │
│  │  • DelayedStatModifierEffect                         │      │
│  │  • PreventNextAttackEffect                           │      │
│  │  • PreventAttackEffect                               │      │
│  │  • IgnoreDefenseEffect                               │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
│  Mapeos:                                                         │
│  ├─ get_card_effect(card_id) → Effect                          │
│  ├─ get_environment_effect(card_id) → PassiveEffect            │
│  └─ get_leader_passive_effect(card_id) → PassiveEffect         │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ usa
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MODELOS DE DATOS                              │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ EffectContext    │  │ EffectResult     │  │EffectTrigger │ │
│  │                  │  │                  │  │              │ │
│  │ • game_state     │  │ • success        │  │ • ON_PLAY    │ │
│  │ • source_player  │  │ • message        │  │ • ON_DESTROY │ │
│  │ • source_card    │  │ • requires_choice│  │ • ON_ATTACK  │ │
│  │ • target_card    │  │ • choices        │  │ • ON_TURN_*  │ │
│  │ • target_player  │  │ • revealed_info  │  │ • ALWAYS     │ │
│  │ • trigger        │  │ • next_step      │  │ • ...        │ │
│  │ • additional_data│  │ • data           │  │              │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     FLUJO DE EJECUCIÓN                           │
│                                                                  │
│  1. JUGAR CARTA DE EFECTO                                       │
│     ┌─────────────┐                                             │
│     │ Jugador     │ juega carta                                 │
│     └──────┬──────┘                                             │
│            │                                                     │
│            ▼                                                     │
│     ┌─────────────┐                                             │
│     │ GameEngine  │ verifica costo, deduce monedas             │
│     └──────┬──────┘                                             │
│            │                                                     │
│            ▼                                                     │
│     ┌─────────────────┐                                         │
│     │ get_card_effect │ obtiene efecto por ID                  │
│     └──────┬──────────┘                                         │
│            │                                                     │
│            ▼                                                     │
│     ┌─────────────────────┐                                     │
│     │ EffectManager       │ ejecuta efecto inmediato           │
│     │ execute_immediate   │                                     │
│     └──────┬──────────────┘                                     │
│            │                                                     │
│            ▼                                                     │
│     ┌─────────────┐                                             │
│     │ Effect      │ can_execute() → execute()                  │
│     └──────┬──────┘                                             │
│            │                                                     │
│            ▼                                                     │
│     ┌─────────────┐                                             │
│     │ EffectResult│ retorna resultado                          │
│     └──────┬──────┘                                             │
│            │                                                     │
│            ▼                                                     │
│     Si requires_choice = True:                                  │
│            │                                                     │
│            ▼                                                     │
│     ┌─────────────┐                                             │
│     │   Cliente   │ muestra opciones                           │
│     └──────┬──────┘                                             │
│            │                                                     │
│            ▼                                                     │
│     ┌─────────────┐                                             │
│     │   Jugador   │ elige opción                               │
│     └──────┬──────┘                                             │
│            │                                                     │
│            ▼                                                     │
│     ┌─────────────────────────┐                                 │
│     │ continue_multi_step     │ continúa con elección          │
│     │ _effect()               │                                 │
│     └─────────────────────────┘                                 │
│                                                                  │
│  2. CALCULAR ATAQUE CON MODIFICADORES                           │
│     ┌─────────────┐                                             │
│     │ attack()    │                                             │
│     └──────┬──────┘                                             │
│            │                                                     │
│            ▼                                                     │
│     ┌─────────────────────┐                                     │
│     │ get_stat_modifiers  │ obtiene mods activos               │
│     └──────┬──────────────┘                                     │
│            │                                                     │
│            ▼                                                     │
│     ┌─────────────────────┐                                     │
│     │ trigger_effects     │ ON_ATTACK                          │
│     └──────┬──────────────┘                                     │
│            │                                                     │
│            ▼                                                     │
│     Calcula daño con modificadores                              │
│            │                                                     │
│            ▼                                                     │
│     Si carta destruida:                                         │
│            │                                                     │
│            ▼                                                     │
│     ┌─────────────────────┐                                     │
│     │ trigger_effects     │ ON_DESTROY                         │
│     └─────────────────────┘                                     │
│                                                                  │
│  3. INICIO/FIN DE TURNO                                         │
│     ┌─────────────┐                                             │
│     │ next_phase()│                                             │
│     └──────┬──────┘                                             │
│            │                                                     │
│            ▼                                                     │
│     ┌─────────────────────┐                                     │
│     │ trigger_effects     │ ON_TURN_START / ON_TURN_END        │
│     └──────┬──────────────┘                                     │
│            │                                                     │
│            ▼                                                     │
│     Ejecuta todos los efectos pasivos/asíncronos               │
│     que respondan al trigger                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   EFECTOS POR FACCIÓN                            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   POLICE     │  │    MAFIA     │  │  DETECTIVE   │         │
│  │   8 efectos  │  │   9 efectos  │  │   9 efectos  │         │
│  │              │  │              │  │              │         │
│  │ • Control    │  │ • Extorsión  │  │ • Interrogar │         │
│  │ • Defensa    │  │ • Soborno    │  │ • Emboscada  │         │
│  │ • Bloqueos   │  │ • Influencia │  │ • Vigilancia │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │    THIEF     │  │  WILDCARD    │                            │
│  │   8 efectos  │  │   8 efectos  │                            │
│  │              │  │              │                            │
│  │ • Robo       │  │ • Caos       │                            │
│  │ • Evasión    │  │ • Destrucción│                            │
│  │ • Oscuridad  │  │ • Locura     │                            │
│  └──────────────┘  └──────────────┘                            │
│                                                                  │
│  TOTAL: 42 EFECTOS ÚNICOS IMPLEMENTADOS                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    ESTADÍSTICAS DEL SISTEMA                      │
│                                                                  │
│  Archivos principales:           5                              │
│  Líneas de código:               ~3,000                         │
│  Efectos implementados:          42                             │
│  Tipos de efectos diferentes:    ~25                            │
│  Triggers disponibles:           10                             │
│  Cartas con efectos:             42/75 (56%)                    │
│                                                                  │
│  Cobertura por tipo:                                            │
│  ├─ Cartas de efecto:           100% (todas mapeadas)          │
│  ├─ Cartas de ambiente:         100% (todas implementadas)     │
│  ├─ Líderes con pasivas:        20%  (2/10 implementados)      │
│  └─ Personajes especiales:      10%  (casos especiales)        │
└─────────────────────────────────────────────────────────────────┘
```
