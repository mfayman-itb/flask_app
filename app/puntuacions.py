import json
import gestio_participants as gp
# Modul per gestionar puntuacions

fitxer = 'puntuacions.txt'

# TODO: Afegir funcions per actualitzar puntuacions i generar rànquings

def inicialitzar_puntuacions(participants):
    puntuacions = dict.fromkeys(participants, 0)
    guardar_puntuacions(puntuacions)
    return puntuacions

def guardar_puntuacions(puntuacions):
    fitxer = 'puntuacions.json'
    with open(fitxer, 'w') as f:
        json.dump(puntuacions, f, indent=4)

def carregar_puntuacions(fitxer):
    puntuacions = {}
    try:
        with open(fitxer, 'r') as f:
            puntuacions = json.load(f)
        return puntuacions
    except FileNotFoundError:
        return {}

def actualitzar_puntuacions(puntuacions, guanyador):
    # TODO: Implementar lògica per actualitzar puntuacions
    if guanyador in puntuacions:
        puntuacions[guanyador] += 1
    else:
        puntuacions[guanyador] = 1

    print("Puntuacions actualitzades:", puntuacions)
    return puntuacions

def calcular_ranquing():
    # Obtener todos los participantes
    participants = gp.carregar_participants_de_fitxer("participants.txt")

    # Cargar puntuaciones existentes
    puntuacions = carregar_puntuacions('puntuacions.json')

    # Asegurar que todos los participantes están en el diccionario
    for participant in participants:
        if participant not in puntuacions:
            puntuacions[participant] = 0

    # Ordenar por puntuación descendente
    return sorted(puntuacions.items(), key=lambda x: x[1], reverse=True)
