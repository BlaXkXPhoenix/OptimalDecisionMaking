from otree.api import *
import random

doc = """
Experiment zu Framing- und Aesthetic-Usability-Effekten bei Preisschätzungen
"""

class C(BaseConstants):
    NAME_IN_URL = 'framing_experiment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10
    
    # Wahre Werte der Gegenstände (in CHF)
    TRUE_VALUES = [390, 210, 280, 180, 520, 450, 150, 450, 680, 280]
    
    # Gegenstandsnamen
    ITEMS = ['Sessel', 'Couchtisch', 'Pfannen-Set', 'Rennvelo', 
             'Esstisch', 'Sofa', 'Stehlampe', 'Strickpullover',
             'Thermomix', 'KitchenAid']
    
    # Bildpfade (müssen im _static/framing_experiment/ Ordner liegen)
    IMAGES_FRAMED = [
        'framing_experiment/armchair_beautiful.png',
        'framing_experiment/coffee_table_beautiful.png',
        'framing_experiment/pans_beautiful.png',
        'framing_experiment/racebike_beautiful.png',
        'framing_experiment/table_beautiful.png',
        'framing_experiment/sofa_beautiful.png',
        'framing_experiment/lamp_beautiful.png',
        'framing_experiment/Strickpullover_ästhetisch.png',
        'framing_experiment/Thermomix_pretty.png',
        'framing_experiment/KitchenAid_pretty.png'
    ]
    
    IMAGES_UNFRAMED = [
        'framing_experiment/armchair_plain.png',
        'framing_experiment/coffee_table_plain.png',
        'framing_experiment/pans_plain.png',
        'framing_experiment/racebike_plain.png',
        'framing_experiment/table_plain.png',
        'framing_experiment/sofa_plain.png',
        'framing_experiment/lamp_plain.png',
        'framing_experiment/Strickpullover_unästhetisch.png',
        'framing_experiment/Thermomix_ugly.png',
        'framing_experiment/KitchenAid_ugly.png'
    ]


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    """
    Hardcoded Rotation: Jede Gruppe hat eine feste Sequenz über 10 Runden
    """
    
    # Hardcoded Sequenzen: [Framing, Usability] für jede Runde
    # Jede Gruppe erlebt alle 4 Kombinationen mehrfach
    GROUP_SEQUENCES = {
        1: [  # Gruppe 1: Rotiert durch alle 4 Kombinationen
            (False, False),  # R1: Ugly + Low
            (False, True),   # R2: Ugly + High
            (True, False),   # R3: Beautiful + Low
            (True, True),    # R4: Beautiful + High
            (False, False),  # R5: Ugly + Low
            (False, True),   # R6: Ugly + High
            (True, False),   # R7: Beautiful + Low
            (True, True),    # R8: Beautiful + High
            (False, False),  # R9: Ugly + Low
            (False, True),   # R10: Ugly + High
        ],
        2: [  # Gruppe 2: Startet anders
            (False, True),   # R1: Ugly + High
            (True, False),   # R2: Beautiful + Low
            (True, True),    # R3: Beautiful + High
            (False, False),  # R4: Ugly + Low
            (False, True),   # R5: Ugly + High
            (True, False),   # R6: Beautiful + Low
            (True, True),    # R7: Beautiful + High
            (False, False),  # R8: Ugly + Low
            (False, True),   # R9: Ugly + High
            (True, False),   # R10: Beautiful + Low
        ],
        3: [  # Gruppe 3: Startet anders
            (True, False),   # R1: Beautiful + Low
            (True, True),    # R2: Beautiful + High
            (False, False),  # R3: Ugly + Low
            (False, True),   # R4: Ugly + High
            (True, False),   # R5: Beautiful + Low
            (True, True),    # R6: Beautiful + High
            (False, False),  # R7: Ugly + Low
            (False, True),   # R8: Ugly + High
            (True, False),   # R9: Beautiful + Low
            (True, True),    # R10: Beautiful + High
        ],
        4: [  # Gruppe 4: Startet anders
            (True, True),    # R1: Beautiful + High
            (False, False),  # R2: Ugly + Low
            (False, True),   # R3: Ugly + High
            (True, False),   # R4: Beautiful + Low
            (True, True),    # R5: Beautiful + High
            (False, False),  # R6: Ugly + Low
            (False, True),   # R7: Ugly + High
            (True, False),   # R8: Beautiful + Low
            (True, True),    # R9: Beautiful + High
            (False, False),  # R10: Ugly + Low
        ]
    }
    
    if subsession.round_number == 1:
        # Weise jedem Spieler eine permanente Gruppe zu (1-4)
        for player in subsession.get_players():
            group_num = ((player.id_in_subsession - 1) % 4) + 1
            player.participant.vars['experiment_group'] = group_num
            print(f"\n{'='*60}")
            print(f"🎯 SESSION SETUP: Player {player.id_in_subsession} → Gruppe {group_num}")
            print(f"{'='*60}\n")
    
    # WICHTIG: Setze die Bedingungen DIREKT im Player-Objekt für diese Runde!
    for player in subsession.get_players():
        group_num = player.participant.vars['experiment_group']
        round_num = subsession.round_number
        
        # Hole Bedingungen aus der hardcoded Sequenz
        framing, usability = GROUP_SEQUENCES[group_num][round_num - 1]
        
        # Speichere DIREKT im Player-Objekt (nicht in participant.vars!)
        player.framing_condition = framing
        player.usability_condition = usability
        player.experiment_group = group_num
        
        # Debug Output
        print(f"ROUND {round_num}: Player {player.id_in_subsession} (Gruppe {group_num}) → "
              f"Framing={'Beautiful ✨' if framing else 'Ugly 📦'}, "
              f"Usability={'High ⭐' if usability else 'Low ⬇️'} "
              f"[DIREKT in player.framing_condition={framing}, player.usability_condition={usability}]")


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Speichert die Preisschätzung des Spielers
    price_estimate = models.IntegerField(
        min=0,
        max=10000,
        label="Ihre Preisschätzung (in CHF):"
    )
    
    # Score für diese Runde
    round_score = models.IntegerField(initial=0)
    
    # Wahre Wert für diese Runde
    true_value = models.IntegerField()
    
    # Item Name für diese Runde
    item_name = models.StringField()
    
    # Experimentbedingungen für diese Runde (für Datenanalyse)
    framing_condition = models.BooleanField()  # True = Beautiful, False = Ugly
    usability_condition = models.BooleanField()  # True = High, False = Low
    experiment_group = models.IntegerField()  # 1-4


# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            high_usability=player.usability_condition
        )


class Estimate(Page):
    form_model = 'player'
    form_fields = ['price_estimate']
    
    @staticmethod
    def vars_for_template(player: Player):
        round_num = player.round_number - 1
        
        # LESE DIREKT AUS DEM PLAYER-OBJEKT (wurde in creating_session gesetzt!)
        framing = player.framing_condition
        usability = player.usability_condition
        
        # Bestimme das richtige Bild
        if framing:
            image_path = C.IMAGES_FRAMED[round_num]
        else:
            image_path = C.IMAGES_UNFRAMED[round_num]
        
        # Speichere andere Werte
        player.true_value = C.TRUE_VALUES[round_num]
        player.item_name = C.ITEMS[round_num]
        
        # DEBUG
        print(f"\n{'='*70}")
        print(f"🎮 ESTIMATE PAGE - PLAYER {player.id_in_subsession} | RUNDE {player.round_number}")
        print(f"{'='*70}")
        print(f"📋 Gruppe: {player.experiment_group}")
        print(f"")
        print(f"🖼️  FRAMING (Bilder):")
        print(f"     player.framing_condition = {framing}")
        print(f"     → Zeigt: {'✨ BEAUTIFUL Bild' if framing else '📦 UGLY Bild'}")
        print(f"     → Datei: {image_path}")
        print(f"")
        print(f"🎨 AESTHETIC USABILITY (Interface):")
        print(f"     player.usability_condition = {usability}")
        print(f"     → Zeigt: {'⭐ HIGH (goldenes Design)' if usability else '⬇️  LOW (graues Design)'}")
        print(f"     → Template bekommt: high_usability={usability}")
        print(f"")
        if framing == usability:
            print(f"⚠️  WARNUNG: Beide gleich! (sollte bei Gruppe 2 & 4 gemischt sein)")
        else:
            print(f"✅ GEMISCHT: Bild und Interface unterschiedlich!")
        print(f"{'='*70}\n")
        
        return dict(
            image_path=image_path,
            item_name=C.ITEMS[round_num],
            round_number=player.round_number,
            high_usability=usability  # DIREKT aus player-Objekt!
        )
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Berechne Score basierend auf Abweichung vom wahren Wert
        difference = abs(player.price_estimate - player.true_value)

        # Score: Je kleiner die Abweichung, desto mehr Punkte
        # Max 100 Punkte wenn perfekt, 0 Punkte bei >500 CHF Abweichung
        if difference == 0:
            player.round_score = 100
        elif difference <= 50:
            player.round_score = 90
        elif difference <= 100:
            player.round_score = 70
        elif difference <= 200:
            player.round_score = 50
        elif difference <= 300:
            player.round_score = 30
        elif difference <= 500:
            player.round_score = 10
        else:
            player.round_score = 0

        player.payoff = player.round_score


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    
    @staticmethod
    def vars_for_template(player: Player):
        all_players = player.in_all_rounds()
        
        total_score = sum([p.round_score for p in all_players])
        
        estimates = []
        for p in all_players:
            estimates.append({
                'item': p.item_name,
                'estimate': p.price_estimate,
                'true_value': p.true_value,
                'difference': abs(p.price_estimate - p.true_value),
                'score': p.round_score
            })
        
        return dict(
            estimates=estimates,
            total_score=total_score,
            high_usability=player.usability_condition,
            framing=player.framing_condition
        )


page_sequence = [Instructions, Estimate, Results]