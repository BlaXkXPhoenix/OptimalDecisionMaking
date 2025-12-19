from otree.api import *
import random

doc = """
Experiment on framing and aesthetic usability effects in price estimation
"""

class C(BaseConstants):
    NAME_IN_URL = 'framing_experiment'
    PLAYERS_PER_GROUP = None  # No oTree grouping needed
    NUM_ROUNDS = 10
    
    # True values of items (in CHF)
    TRUE_VALUES = [390, 210, 280, 180, 520, 450, 150, 450, 680, 280]

    # Item names
    ITEMS = ['Armchair', 'Coffee Table', 'Pan Set', 'Racing Bike',
             'Dining Table', 'Sofa', 'Floor Lamp', 'Knit Sweater',
             'Thermomix', 'KitchenAid']

    # Image paths (must be in _static/framing_experiment/ folder)
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
    Hardcoded Rotation: Each experimental group has a fixed sequence across 10 rounds
    Players are assigned to experimental groups (1-4) based on their participant ID
    """

    # Hardcoded sequences: [Framing, Usability] for each round
    # Each experimental group experiences all 4 combinations multiple times
    GROUP_SEQUENCES = {
        1: [  # Group 1: Rotates through all 4 combinations
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
        2: [  # Group 2: Starts differently
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
        3: [  # Group 3: Starts differently
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
        4: [  # Group 4: Starts differently
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

    # Assign experimental group in round 1 and persist it
    if subsession.round_number == 1:
        for player in subsession.get_players():
            # Distribute players across 4 experimental groups using round-robin
            exp_group = ((player.participant.id_in_session - 1) % 4) + 1
            player.participant.vars['experiment_group'] = exp_group
            print(f"🎯 SESSION SETUP: Participant {player.participant.id_in_session} → Experimental Group {exp_group}")

    # Set conditions for this round based on assigned experimental group
    for player in subsession.get_players():
        exp_group = player.participant.vars['experiment_group']
        round_num = subsession.round_number

        # Get conditions from the hardcoded sequence
        framing, usability = GROUP_SEQUENCES[exp_group][round_num - 1]

        # Store conditions in player object for this round
        player.framing_condition = framing
        player.usability_condition = usability
        player.experiment_group = exp_group

        # Debug Output
        print(f"ROUND {round_num}: Participant {player.participant.id_in_session} → "
              f"Exp Group {exp_group} → "
              f"Framing={'Beautiful ✨' if framing else 'Ugly 📦'}, "
              f"Usability={'High ⭐' if usability else 'Low ⬇️'}")


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Stores the player's price estimate
    price_estimate = models.IntegerField(
        min=0,
        max=10000,
        label="Your price estimate (in CHF):"
    )

    # Score for this round
    round_score = models.IntegerField(initial=0)

    # True value for this round
    true_value = models.IntegerField()

    # Item name for this round
    item_name = models.StringField()

    # Experimental conditions for this round (for data analysis)
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

        # READ DIRECTLY FROM PLAYER OBJECT (was set in creating_session!)
        framing = player.framing_condition
        usability = player.usability_condition

        # Determine the correct image
        if framing:
            image_path = C.IMAGES_FRAMED[round_num]
        else:
            image_path = C.IMAGES_UNFRAMED[round_num]

        # Store other values
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
            high_usability=usability  # DIRECTLY from player object!
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Calculate score based on deviation from true value
        difference = abs(player.price_estimate - player.true_value)

        # Score: The smaller the deviation, the more points
        # Max 100 points if perfect, 0 points if >500 CHF deviation
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