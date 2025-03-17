from flask import Flask, render_template, request, redirect, url_for, session
from itertools import combinations
import json
import gestio_participants as gp
import gestio_partides as gg
import puntuacions as p
import utils

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_FOLDER'] = 'templates'

def get_available_players(all_players):
    """Return players with remaining possible matches"""
    try:
        data = gg.load_matches_lliga()
        scheduled_pairs = set(
            tuple(sorted(match['participants']))
            for rnd in data.get('rounds', [])
            for match in rnd.get('matches', [])
        )
    except Exception as e:
        print(f"Error loading matches: {str(e)}")
        scheduled_pairs = set()

    available = []
    for player in all_players:
        possible_opponents = [
            p for p in all_players
            if p != player and tuple(sorted((player, p))) not in scheduled_pairs
        ]
        if possible_opponents:
            available.append(player)

    return sorted(available)
    

@app.route('/')
def index():
    
    return render_template('index.html')

@app.template_filter('is_power_of_two')
def is_power_of_two_filter(n):
    return n >= 2 and (n & (n - 1)) == 0

@app.template_filter('next_power_of_two')
def next_power_of_two_filter(n):
    if n < 1: return 2
    return 2**((n-1).bit_length())

@app.route('/participants', methods=["POST", "GET"])
def participants():
    if request.method == "POST":
        nom = request.form["nom"]
        if utils.validar_nom(nom):
            if gp.afegir_participant(nom):
                return redirect(url_for('participants'))
            else:
                error = "El participant ja existeix"
        else:
            error = "El nom no és vàlid"
        participants = gp.carregar_participants_de_fitxer("participants.txt")
        print(f"Loaded participants: {participants}")  # Debug output
        return render_template('participants.html', participants=participants, error=error)
    participants = gp.carregar_participants_de_fitxer("participants.txt")
    return render_template('participants.html', participants=participants)

@app.route('/partides/lliga', methods=["GET"])
def matchup_form():
    all_players = gp.carregar_participants_de_fitxer("participants.txt")
    data = gg.load_matches_lliga()

    # Get existing matches for availability check
    existing_matches = [
        match
        for rnd in data.get('rounds', [])
        for match in rnd.get('matches', [])
    ]

    return render_template('partides.html',
                         available_players=get_available_players(all_players),
                         existing_matches=existing_matches,
                         rounds=data.get('rounds', []),
                         all_players=all_players)

@app.route('/partides', methods=["POST"])
def partides():
    if request.form.get("manual"):
        player1 = request.form.get("player1")
        player2 = request.form.get("player2")

        if not player1 or not player2 or player1 == player2:
            return redirect(url_for('matchup_form'))

        match = tuple(sorted([player1, player2]))
        gg.save_match_lliga(match)

    return redirect(url_for('matchup_form'))

@app.route('/play/round')
def play_round():
    data = gg.load_matches_lliga()
    current_round_num = data['current_round']

    try:
        current_round = data['rounds'][current_round_num - 1]
    except IndexError:
        return redirect(url_for('matchup_form'))

    return render_template('play_round.html',
                         current_round=current_round,
                         current_round_num=current_round_num,
                         total_rounds=len(data['rounds']))

@app.route('/submit_result', methods=['POST'])
def submit_result():
    round_num = int(request.form.get('round_num'))
    match_index = int(request.form.get('match_index'))
    winner = request.form.get('winner')

    if winner:
        gg.update_match_result(round_num, match_index, winner)
        # Update tournament state after result submission
        data = gg.load_matches_lliga()
        current_round = data['rounds'][data['current_round'] - 1]
        if all(m.get('winner') for m in current_round['matches']):
            gg.advance_round()

    return redirect(url_for('play_round'))

@app.route('/partides/eliminatories', methods=['GET', 'POST'])
def elimination_form():
    all_players = gp.carregar_participants_de_fitxer("participants.txt")
    data = gg.load_eliminatories()
    participant_count = len(all_players)

    # Calculate tournament requirements
    is_valid = (participant_count >= 2) and ((participant_count & (participant_count - 1)) == 0)
    next_power = 2 ** ((participant_count - 1).bit_length()) if participant_count > 0 else 2

    if request.method == 'POST' and is_valid:
        try:
            bracket = gg.create_elimination_bracket(all_players)
            with open(gg.FITXER_ELIMINATORIES, 'w') as f:
                json.dump(bracket, f, indent=2)
        except ValueError as e:
            return render_template('error.html', error=str(e))
        return redirect(url_for('elimination_form'))

    return render_template('eliminatories.html',
                         all_players=all_players,
                         participant_count=participant_count,
                         is_valid=is_valid,
                         next_power=next_power,
                         bracket=data)

@app.route('/update_elimination', methods=['POST'])
def update_elimination():
    round_num = int(request.form.get('round_num'))
    match_index = int(request.form.get('match_index'))
    winner = request.form.get('winner')

    if winner:
        gg.save_elimination_result(round_num, match_index, winner)

    return redirect(url_for('elimination_form'))

@app.route('/eliminatories', methods=['POST'])
def save_elimination():
    if request.form.get("manual"):
        player1 = request.form.get("player1")
        player2 = request.form.get("player2")

        if not player1 or not player2 or player1 == player2:
            return redirect(url_for('elimination_form'))

        match = tuple(sorted([player1, player2]))
        gg.save_elimination_match(match)

    return redirect(url_for('elimination_form'))

@app.route('/next_round')
def next_round():
    gg.advance_round()
    return redirect(url_for('play_round'))

@app.route('/previous_round')
def previous_round():
    gg.previous_round()
    return redirect(url_for('play_round'))

@app.route('/partides/reset')
def reset_matches():
    gg.reset_matches_file()
    return redirect(url_for('matchup_form'))

@app.route('/eliminatories/reset')
def reset_eliminatories():
    gg.reset_eliminatories()
    return redirect(url_for('elimination_form'))
    
@app.route('/puntuacions')
def puntuacions():
    ranking = p.calcular_ranquing()
    return render_template('puntuacions.html', ranking=ranking)

@app.route('/ranking_eliminatories')
def ranking_eliminatories():
    data = gg.load_eliminatories()
    participants = gp.carregar_participants_de_fitxer("participants.txt")

    # Crear estructura para trackear progreso
    player_data = {player: {
        'position': None,
        'round_eliminated': 0,
        'is_winner': False
    } for player in participants}

    # Determinar última ronda jugada
    max_round = max([r['round_number'] for r in data['rounds']]) if data['rounds'] else 0

    # Analizar cada ronda para encontrar perdedores
    for ronda in data['rounds']:
        for match in ronda['matches']:
            if match['winner']:
                perdedor = [p for p in match['participants'] if p != match['winner']][0]
                player_data[perdedor]['round_eliminated'] = ronda['round_number']

                # Si es la última ronda, el perdedor es subcampeón
                if ronda['round_number'] == max_round:
                    player_data[perdedor]['position'] = 2

    # Encontrar al campeón
    if data['rounds']:
        final_match = data['rounds'][-1]['matches'][0]
        champion = final_match['winner']
        player_data[champion]['position'] = 1
        player_data[champion]['is_winner'] = True

    # Ordenar jugadores: 
    # 1. Posición asignada
    # 2. Ronda más avanzada alcanzada
    # 3. Orden alfabético
    sorted_players = sorted(
        player_data.items(),
        key=lambda x: (
            -x[1]['position'] if x[1]['position'] else 0,
            -x[1]['round_eliminated'],
            x[0]
        )
    )

    # Asignar posiciones definitivas
    position = 1
    last_round = None
    for i, (player, data) in enumerate(sorted_players):
        if i == 0:
            last_round = (data['position'], data['round_eliminated'])
        else:
            current_round = (data['position'], data['round_eliminated'])
            if current_round != last_round:
                position = i + 1
                last_round = current_round

        data['final_position'] = position

    return render_template('ranking.html', 
                         ranking=sorted_players, 
                         max_round=max_round)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
