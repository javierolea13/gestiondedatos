"""Modelos de datos para el registro de Mario Kart."""

import json
from datetime import datetime
from pathlib import Path

DATOS_PATH = Path(__file__).parent / "datos" / "registro.json"

# Todas las pistas de Mario Kart 8 Deluxe organizadas por Copa
COPAS = {
    "Copa Champiñón": ["Circuito de Mario", "Parque Acuático", "Pista Dulce Dulce", "Ruinas Thwomp"],
    "Copa Flor": ["Circuito de Mario (GCN)", "Autopista Toad", "Montaña Rocosa", "Estación Marios"],
    "Copa Estrella": ["Aeropuerto Sol Sol", "Delfino Plaza", "Circuito Electro", "Carretera Arco Iris (N64)"],
    "Copa Especial": ["Mina de Wario", "Carretera Arco Iris", "Castillo de Bowser", "Circuito Arco Iris"],
    "Copa Huevo": ["Yoshi Circuit (GCN)", "Excitebike Arena", "Dragon Driftway", "Mute City"],
    "Copa Triforce": ["Hyrule Circuit", "Wild Woods", "Animal Crossing", "Neo Bowser City"],
    "Copa Campana": ["Baby Park (GCN)", "Cheese Land (GBA)", "Ribbon Road (GBA)", "Super Bell Subway"],
    "Copa Hoja": ["Koopa City", "Wario Stadium (DS)", "Sherbet Land (GCN)", "Music Park (3DS)"],
}

POSICIONES_PUNTOS = {
    1: 15,
    2: 12,
    3: 10,
    4: 8,
    5: 7,
    6: 6,
    7: 5,
    8: 4,
    9: 3,
    10: 2,
    11: 1,
    12: 0,
}


def cargar_datos() -> dict:
    """Carga los datos del archivo JSON."""
    if DATOS_PATH.exists():
        with open(DATOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"jugadores": [], "torneos": []}


def guardar_datos(datos: dict):
    """Guarda los datos en el archivo JSON."""
    DATOS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATOS_PATH, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def agregar_jugador(datos: dict, nombre: str) -> bool:
    """Agrega un jugador nuevo. Retorna False si ya existe."""
    if nombre.lower() in [j.lower() for j in datos["jugadores"]]:
        return False
    datos["jugadores"].append(nombre)
    guardar_datos(datos)
    return True


def crear_torneo(datos: dict, nombre_torneo: str, copa: str, jugadores: list[str]) -> dict:
    """Crea un nuevo torneo (Grand Prix) con 4 carreras."""
    pistas = COPAS.get(copa, [])
    torneo = {
        "id": len(datos["torneos"]) + 1,
        "nombre": nombre_torneo,
        "copa": copa,
        "jugadores": jugadores,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "carreras": [],
        "completado": False,
    }
    # Pre-crear las 4 carreras con las pistas de la copa
    for i, pista in enumerate(pistas[:4]):
        torneo["carreras"].append({
            "numero": i + 1,
            "pista": pista,
            "resultados": {},  # {jugador: posicion}
        })
    datos["torneos"].append(torneo)
    guardar_datos(datos)
    return torneo


def crear_torneo_personalizado(datos: dict, nombre_torneo: str, pistas: list[str], jugadores: list[str]) -> dict:
    """Crea un torneo con pistas personalizadas."""
    torneo = {
        "id": len(datos["torneos"]) + 1,
        "nombre": nombre_torneo,
        "copa": "Personalizada",
        "jugadores": jugadores,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "carreras": [],
        "completado": False,
    }
    for i, pista in enumerate(pistas[:4]):
        torneo["carreras"].append({
            "numero": i + 1,
            "pista": pista,
            "resultados": {},
        })
    datos["torneos"].append(torneo)
    guardar_datos(datos)
    return torneo


def registrar_resultado(datos: dict, torneo_id: int, num_carrera: int, resultados: dict[str, int]) -> bool:
    """Registra los resultados de una carrera. resultados = {jugador: posicion}"""
    for torneo in datos["torneos"]:
        if torneo["id"] == torneo_id:
            for carrera in torneo["carreras"]:
                if carrera["numero"] == num_carrera:
                    carrera["resultados"] = resultados
                    # Verificar si el torneo está completo
                    todas = all(c["resultados"] for c in torneo["carreras"])
                    torneo["completado"] = todas
                    guardar_datos(datos)
                    return True
    return False


def puntos_por_posicion(posicion: int) -> int:
    """Retorna los puntos según la posición (sistema Mario Kart)."""
    return POSICIONES_PUNTOS.get(posicion, 0)


def calcular_ranking_torneo(torneo: dict) -> list[tuple[str, int]]:
    """Calcula el ranking de un torneo sumando puntos de las 4 carreras."""
    puntos = {}
    for jugador in torneo["jugadores"]:
        puntos[jugador] = 0
    for carrera in torneo["carreras"]:
        for jugador, posicion in carrera["resultados"].items():
            puntos[jugador] = puntos.get(jugador, 0) + puntos_por_posicion(posicion)
    return sorted(puntos.items(), key=lambda x: x[1], reverse=True)


def calcular_ranking_global(datos: dict) -> list[dict]:
    """Calcula el ranking global de todos los jugadores."""
    stats = {}
    for jugador in datos["jugadores"]:
        stats[jugador] = {
            "nombre": jugador,
            "puntos_totales": 0,
            "torneos_jugados": 0,
            "torneos_ganados": 0,
            "carreras_jugadas": 0,
            "primer_lugar": 0,
            "segundo_lugar": 0,
            "tercer_lugar": 0,
            "posicion_promedio": 0,
            "posiciones": [],
        }

    for torneo in datos["torneos"]:
        if not torneo["completado"]:
            continue
        ranking = calcular_ranking_torneo(torneo)
        participantes = [j for j, _ in ranking]

        for jugador in participantes:
            if jugador not in stats:
                continue
            stats[jugador]["torneos_jugados"] += 1

        if ranking:
            ganador = ranking[0][0]
            if ganador in stats:
                stats[ganador]["torneos_ganados"] += 1

        for carrera in torneo["carreras"]:
            for jugador, posicion in carrera["resultados"].items():
                if jugador not in stats:
                    continue
                stats[jugador]["carreras_jugadas"] += 1
                stats[jugador]["puntos_totales"] += puntos_por_posicion(posicion)
                stats[jugador]["posiciones"].append(posicion)
                if posicion == 1:
                    stats[jugador]["primer_lugar"] += 1
                elif posicion == 2:
                    stats[jugador]["segundo_lugar"] += 1
                elif posicion == 3:
                    stats[jugador]["tercer_lugar"] += 1

    resultado = []
    for jugador, s in stats.items():
        if s["posiciones"]:
            s["posicion_promedio"] = round(sum(s["posiciones"]) / len(s["posiciones"]), 2)
        del s["posiciones"]
        resultado.append(s)

    return sorted(resultado, key=lambda x: x["puntos_totales"], reverse=True)


def stats_por_pista(datos: dict) -> dict[str, list[dict]]:
    """Calcula estadísticas de cada jugador en cada pista."""
    pista_stats = {}

    for torneo in datos["torneos"]:
        for carrera in torneo["carreras"]:
            pista = carrera["pista"]
            if pista not in pista_stats:
                pista_stats[pista] = {}
            for jugador, posicion in carrera["resultados"].items():
                if jugador not in pista_stats[pista]:
                    pista_stats[pista][jugador] = {"posiciones": [], "puntos": 0, "veces": 0}
                pista_stats[pista][jugador]["posiciones"].append(posicion)
                pista_stats[pista][jugador]["puntos"] += puntos_por_posicion(posicion)
                pista_stats[pista][jugador]["veces"] += 1

    # Calcular promedios y formatear
    resultado = {}
    for pista, jugadores in pista_stats.items():
        ranking_pista = []
        for jugador, s in jugadores.items():
            promedio = round(sum(s["posiciones"]) / len(s["posiciones"]), 2)
            ranking_pista.append({
                "jugador": jugador,
                "veces_jugada": s["veces"],
                "posicion_promedio": promedio,
                "puntos_totales": s["puntos"],
                "mejor_posicion": min(s["posiciones"]),
                "peor_posicion": max(s["posiciones"]),
            })
        resultado[pista] = sorted(ranking_pista, key=lambda x: x["posicion_promedio"])
    return resultado


def mejor_y_peor_pista(datos: dict, jugador: str) -> tuple[dict | None, dict | None]:
    """Encuentra la mejor y peor pista de un jugador."""
    pista_data = stats_por_pista(datos)
    mejor = None
    peor = None

    for pista, rankings in pista_data.items():
        for r in rankings:
            if r["jugador"].lower() == jugador.lower() and r["veces_jugada"] > 0:
                if mejor is None or r["posicion_promedio"] < mejor["posicion_promedio"]:
                    mejor = {**r, "pista": pista}
                if peor is None or r["posicion_promedio"] > peor["posicion_promedio"]:
                    peor = {**r, "pista": pista}
    return mejor, peor


def historial_enfrentamientos(datos: dict, jugador1: str, jugador2: str) -> dict:
    """Compara el historial entre dos jugadores."""
    victorias_j1 = 0
    victorias_j2 = 0
    empates = 0
    carreras = 0

    for torneo in datos["torneos"]:
        for carrera in torneo["carreras"]:
            res = carrera["resultados"]
            if jugador1 in res and jugador2 in res:
                carreras += 1
                if res[jugador1] < res[jugador2]:
                    victorias_j1 += 1
                elif res[jugador2] < res[jugador1]:
                    victorias_j2 += 1
                else:
                    empates += 1

    return {
        "jugador1": jugador1,
        "jugador2": jugador2,
        "carreras_juntos": carreras,
        "victorias_j1": victorias_j1,
        "victorias_j2": victorias_j2,
        "empates": empates,
    }
