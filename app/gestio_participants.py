# Modul per gestionar participants

fitxer = "participants.txt"
from utils import validar_nom

# TODO: Afegir funcions per afegir, validar i desar participants


def afegir_participant(nom):
  # TODO: Implementar validació i afegir el participant a la llista
  # Validació del nom
  if not validar_nom(nom):
    return False

  participants = carregar_participants_de_fitxer(fitxer)
  print(f'participants: {participants}')
  if not participants:
    participants = []
  # Evitar duplicats
  if nom in participants:
    return False
  else:
    participants.append(nom)

  desar_participants_a_fitxer(participants, fitxer)
  return True


def desar_participants_a_fitxer(participants, fitxer):
  # TODO: Implementar lògica per desar la llista de participants
  with open(fitxer, 'w') as f:
    for participant in participants:
      f.write(participant + '\n')


def carregar_participants_de_fitxer(fitxer):
  # TODO: Implementar lògica per carregar participants des del fitxer
  participants = []
  try:
    with open(fitxer, 'r') as file:
      lines = file.readlines()
      for line in lines:
        participants.append(line.strip())
    return participants
  except FileNotFoundError:
    return []
