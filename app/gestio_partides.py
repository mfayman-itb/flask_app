import json
import gestio_participants as gp
import puntuacions as p
import random
import os
# Modul per gestionar partides

# TODO: Afegir funcions per generar partides i avançar jornades

FITXER_PARTIDES_LLIGA = 'partides_lliga.json'
FITXER_ELIMINATORIES = 'partides_eliminatories.json'

def generar_partides_auto(modalitat):
    participants = gp.carregar_participants_de_fitxer("participants.txt")
    print(f'participants: {participants}')
    # TODO: Implementar lògica per generar partides automàtiques
    # Generar partides automàtiques
    if modalitat == 'lliga':
        partides = []
        for i in range(len(participants)):
            for j in range(i + 1, len(participants)):
                partides.append((participants[i], participants[j]))
        return partides
    elif modalitat == 'eliminatories':
        num_participants = len(participants)
        if (num_participants & (num_participants - 1)) != 0:
            raise ValueError("El nombre de participants ha de ser una potència de dos")
        rondes = []
        actuals = [(participants[i], participants[i + 1]) for i in range(0, num_participants, 2)]
        ronda = 1
        while len(actuals) > 1:
            rondes.append((f'Ronda {ronda}', actuals))
            ronda += 1
            guanyadors = [f'Guanyador {i + 1}' for i in range(len(actuals))]
            actuals = [(guanyadors[i], guanyadors[i + 1]) for i in range(0, len(guanyadors), 2)]
        rondes.append((f'Ronda {ronda}', actuals))
        return rondes
# Generar partides manualment

def generar_partides_manual_lliga(p1, p2):
    partides = [{'player1':'a', 'player2':'b'}, {'player1':'a', 'player2':'c'}]#carregar_partides_de_fitxer(FITXER_PARTIDES)
    participants = gp.carregar_participants_de_fitxer("participants.txt")
    if {'player1':p1, 'player2':p2} not in partides:
        partides.append({'player1':p1, 'player2':p2})
        return partides

def simular_lliga(partides, mode):
    participants = gp.carregar_participants_de_fitxer('participants.txt')
    puntuacions = p.carregar_puntuacions(participants)
    if mode == 'auto':
        for partida in partides:
            guanyador = partida[random.randint(0, 1)]
            puntuacions = p.actualitzar_puntuacions(puntuacions, guanyador)
    p.guardar_puntuacions(puntuacions)
    return puntuacions

def load_matches_lliga():
    """Load matches with proper empty structure"""
    default_data = {
        "current_round": 1,
        "rounds": []
    }

    if not os.path.exists(FITXER_PARTIDES_LLIGA):
        return default_data

    try:
        with open(FITXER_PARTIDES_LLIGA, 'r') as f:
            if os.stat(FITXER_PARTIDES_LLIGA).st_size == 0:
                return default_data
            data = json.load(f)
            # Ensure required fields exist
            data.setdefault('current_round', 1)
            data.setdefault('rounds', [])
            return data
    except Exception as e:
        print(f"Error loading matches: {str(e)}")
        return default_data

def save_match_lliga(match):
    """Save match with improved duplicate check"""
    data = load_matches_lliga()
    sorted_match = sorted(match)

    # Check across all rounds for existing match
    match_exists = any(
        sorted(m['participants']) == sorted_match
        for rnd in data['rounds']
        for m in rnd['matches']
    )

    if not match_exists:
        # Find or create appropriate round
        round_added = False
        for rnd in data['rounds']:
            if all(p not in get_players_in_round(rnd) for p in match):
                rnd['matches'].append({
                    "participants": list(match),
                    "winner": None
                })
                round_added = True
                break

        if not round_added:
            new_round = {
                "round_number": len(data['rounds']) + 1,
                "matches": [{
                    "participants": list(match),
                    "winner": None
                }]
            }
            data['rounds'].append(new_round)

        with open(FITXER_PARTIDES_LLIGA, 'w') as f:
            json.dump(data, f, indent=2)

    return data

def group_matches_into_rounds(matches):
    """Organize matches into rounds ensuring no player appears twice per round"""
    rounds = []
    for match in matches:
        match_added = False
        # Check existing rounds
        for rnd in rounds:
            players_in_round = set()
            for m in rnd:
                players_in_round.update(m)
            # Check if both players are available in this round
            if match[0] not in players_in_round and match[1] not in players_in_round:
                rnd.append(match)
                match_added = True
                break
        # Create new round if needed
        if not match_added:
            rounds.append([match])
    return rounds

def get_players_in_round(round_data):
    """Get all players in a round"""
    players = set()
    for match in round_data['matches']:
        players.update(match['participants'])
    return players

def update_match_result(round_number, match_index, winner):
    data = load_matches_lliga()
    try:
        match = data['rounds'][round_number-1]['matches'][match_index]
        match['winner'] = winner

        # Actualizar puntuaciones
        puntuacions = p.carregar_puntuacions('puntuacions.json')
        puntuacions_actualitzades = p.actualitzar_puntuacions(puntuacions, winner)
        p.guardar_puntuacions(puntuacions_actualitzades)

        with open(FITXER_PARTIDES_LLIGA, 'w') as f:
            json.dump(data, f, indent=2)
    except (IndexError, KeyError):
        pass
    return data

def advance_round():
    """Move to next round only if current round is complete"""
    data = load_matches_lliga()
    current_round_num = data['current_round']

    if current_round_num <= len(data['rounds']):
        current_round = data['rounds'][current_round_num - 1]
        if all(m.get('winner') for m in current_round['matches']):
            data['current_round'] += 1
            with open(FITXER_PARTIDES_LLIGA, 'w') as f:
                json.dump(data, f, indent=2)
    return data

def previous_round():
    """Move to previous round"""
    data = load_matches_lliga()
    if data['current_round'] > 1:
        data['current_round'] -= 1
        with open(FITXER_PARTIDES_LLIGA, 'w') as f:
            json.dump(data, f, indent=2)
    return data

def reset_matches_file():
    """Reset matches to initial state with proper round structure"""
    initial_data = {
        "current_round": 1,
        "rounds": []
    }
    with open(FITXER_PARTIDES_LLIGA, 'w') as f:
        json.dump(initial_data, f, indent=2)

def load_eliminatories():
    try:
        with open(FITXER_ELIMINATORIES, 'r') as f:
            data = json.load(f)
            # Ensure required fields exist
            return {
                'current_round': data.get('current_round', 1),
                'participants': data.get('participants', []),
                'rounds': data.get('rounds', [])
            }
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            'current_round': 1,
            'participants': [],
            'rounds': []
        }

def save_elimination_match(match):
    """Save elimination tournament match"""
    data = load_eliminatories()

    # Initialize first round if empty
    if not data['rounds']:
        data['rounds'].append({'round_number': 1, 'matches': []})

    # Check if match already exists
    if not any(m['participants'] == sorted(match) for m in data['rounds'][0]['matches']):
        data['rounds'][0]['matches'].append({
            'participants': sorted(match),
            'winner': None
        })

    with open(FITXER_ELIMINATORIES, 'w') as f:
        json.dump(data, f, indent=2)
    return data

def create_elimination_bracket(participants):
    """Initialize tournament structure with validation"""
    if not is_power_of_two(len(participants)):
        raise ValueError("Nombre de participants ha de ser potència de 2")

    return {
        "current_round": 1,
        "participants": participants,
        "rounds": [{
            "round_number": 1,
            "matches": [{
                "participants": [participants[i], participants[i+1]],
                "winner": None
            } for i in range(0, len(participants), 2)]
        }]
    }

def update_elimination_round(data):
    """Progress to next round if current is complete"""
    current_round_num = data['current_round']
    current_round = next(r for r in data['rounds'] if r['round_number'] == current_round_num)

    if all(m['winner'] for m in current_round['matches']):
        next_round_num = current_round_num + 1
        winners = [m['winner'] for m in current_round['matches']]

        if len(winners) >= 2:
            data['rounds'].append({
                "round_number": next_round_num,
                "matches": [{
                    "participants": [winners[i], winners[i+1]],
                    "winner": None
                } for i in range(0, len(winners), 2)]
            })
            data['current_round'] = next_round_num

    return data

def is_power_of_two(n):
    return (n & (n-1) == 0) and n !=0

def save_elimination_result(round_num, match_index, winner):
    data = load_eliminatories()

    try:
        match = data['rounds'][round_num-1]['matches'][match_index]
        match['winner'] = winner

        # Registrar perdedor
        loser = [p for p in match['participants'] if p != winner][0]
        if 'losers' not in data:
            data['losers'] = []
        data['losers'].append({
            'round': round_num,
            'player': loser
        })

        # Actualizar rondas
        data = update_elimination_round(data)

        with open(FITXER_ELIMINATORIES, 'w') as f:
            json.dump(data, f, indent=2)

    except (IndexError, KeyError) as e:
        print(f"Error: {str(e)}")

    return data

def reset_eliminatories():
    """Reset elimination tournament data"""
    initial_data = {'rounds': []}
    with open(FITXER_ELIMINATORIES, 'w') as f:
        json.dump(initial_data, f, indent=2)