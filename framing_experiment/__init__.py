from otree.api import *
import random

doc = """
Experiment zu Framing- und Aesthetic-Usability-Effekten bei Preisschätzungen
"""

class C(BaseConstants):
    NAME_IN_URL = 'framing_experiment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 4
    
    # Wahre Werte der Gegenstände (in CHF)
    TRUE_VALUES = [450, 320, 280, 180]
    
    # Gegenstandsnamen
    ITEMS = ['Sofa', 'Schreibtisch', 'Fahrrad', 'Kommode']
    
    # Bildpfade (müssen im _static/framing_experiment/ Ordner liegen)
    IMAGES_FRAMED = [
        'framing_experiment/sofa_beautiful.png',
        'framing_experiment/desk_beautiful.jpeg',
        'framing_experiment/bike_beautiful.jpeg',
        'framing_experiment/dresser_beautiful.jpeg'
    ]
    
    IMAGES_UNFRAMED = [
        'framing_experiment/sofa_plain.png',
        'framing_experiment/desk_plain.jpeg',
        'framing_experiment/bike_plain.jpeg',
        'framing_experiment/dresser_plain.jpeg'
    ]


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    """Zufällige Zuweisung der Teilnehmer zu den 4 Experimentbedingungen"""
    if subsession.round_number == 1:
        # 4 Treatments: (framing, aesthetic_usability)
        treatments = [
            {'framing': True, 'high_usability': True},   # Gruppe 1
            {'framing': True, 'high_usability': False},  # Gruppe 2
            {'framing': False, 'high_usability': True},  # Gruppe 3
            {'framing': False, 'high_usability': False}, # Gruppe 4
        ]
        
        for player in subsession.get_players():
            # Zufällige Zuweisung
            treatment = random.choice(treatments)
            player.participant.vars['framing'] = treatment['framing']
            player.participant.vars['high_usability'] = treatment['high_usability']


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


# HELPER FUNCTIONS
def get_framing(player: Player):
    """Gibt den Framing-Status zurück"""
    return player.participant.vars.get('framing', True)


def get_high_usability(player: Player):
    """Gibt den Usability-Status zurück"""
    return player.participant.vars.get('high_usability', True)


# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            high_usability=get_high_usability(player)
        )


class Estimate(Page):
    form_model = 'player'
    form_fields = ['price_estimate']
    
    @staticmethod
    def vars_for_template(player: Player):
        round_num = player.round_number - 1
        
        # Bestimme das richtige Bild basierend auf Framing-Bedingung
        if get_framing(player):
            image_path = C.IMAGES_FRAMED[round_num]
        else:
            image_path = C.IMAGES_UNFRAMED[round_num]
        
        # Speichere Werte für die Auswertung
        player.true_value = C.TRUE_VALUES[round_num]
        player.item_name = C.ITEMS[round_num]
        
        return dict(
            image_path=image_path,
            item_name=C.ITEMS[round_num],
            round_number=player.round_number,
            high_usability=get_high_usability(player)
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
        else:
            player.round_score = max(0, 20 - (difference - 300) // 50)
        
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
            high_usability=get_high_usability(player)
        )


page_sequence = [Instructions, Estimate, Results]