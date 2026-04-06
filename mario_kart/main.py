"""Aplicación principal de registro de Mario Kart."""

from modelos import (
    cargar_datos,
    agregar_jugador,
    crear_torneo,
    crear_torneo_personalizado,
    registrar_resultado,
    calcular_ranking_torneo,
    calcular_ranking_global,
    stats_por_pista,
    mejor_y_peor_pista,
    historial_enfrentamientos,
    COPAS,
    puntos_por_posicion,
)


def mostrar_menu():
    print("\n" + "=" * 50)
    print("   🏎️  MARIO KART - REGISTRO DE CARRERAS  🏎️")
    print("=" * 50)
    print("  JUGADORES")
    print("    1. Agregar jugador")
    print("    2. Ver jugadores")
    print()
    print("  TORNEOS (Grand Prix)")
    print("    3. Nuevo torneo (Copa oficial)")
    print("    4. Nuevo torneo (Pistas personalizadas)")
    print("    5. Registrar resultados de carrera")
    print("    6. Ver torneos")
    print()
    print("  RANKINGS Y ESTADÍSTICAS")
    print("    7. Ranking global")
    print("    8. Ranking por pista")
    print("    9. Mejor/peor pista de un jugador")
    print("   10. Enfrentamiento directo (1 vs 1)")
    print()
    print("    0. Salir")
    print("-" * 50)


def menu_agregar_jugador(datos):
    print("\n--- Agregar Jugador ---")
    nombre = input("Nombre del jugador: ").strip()
    if not nombre:
        print("Nombre vacío.")
        return
    if agregar_jugador(datos, nombre):
        print(f"'{nombre}' agregado.")
    else:
        print(f"'{nombre}' ya existe.")


def menu_ver_jugadores(datos):
    if not datos["jugadores"]:
        print("\nNo hay jugadores registrados.")
        return
    print(f"\n--- Jugadores ({len(datos['jugadores'])}) ---")
    for i, j in enumerate(sorted(datos["jugadores"]), 1):
        print(f"  {i}. {j}")


def seleccionar_jugadores(datos) -> list[str]:
    """Permite seleccionar entre 2 y 4 jugadores para un torneo."""
    print("\nJugadores disponibles:")
    for i, j in enumerate(datos["jugadores"], 1):
        print(f"  {i}. {j}")
    print("\nSelecciona entre 2 y 4 jugadores (números separados por coma):")
    seleccion = input("> ").strip()
    try:
        indices = [int(x.strip()) for x in seleccion.split(",")]
        jugadores = []
        for idx in indices:
            if 1 <= idx <= len(datos["jugadores"]):
                jugadores.append(datos["jugadores"][idx - 1])
        if len(jugadores) < 2:
            print("Se necesitan al menos 2 jugadores.")
            return []
        if len(jugadores) > 4:
            print("Máximo 4 jugadores.")
            return []
        return jugadores
    except ValueError:
        print("Entrada no válida.")
        return []


def menu_nuevo_torneo_copa(datos):
    print("\n--- Nuevo Torneo (Copa Oficial) ---")
    if len(datos["jugadores"]) < 2:
        print("Necesitas al menos 2 jugadores registrados.")
        return

    print("\nCopas disponibles:")
    copas_lista = list(COPAS.keys())
    for i, copa in enumerate(copas_lista, 1):
        pistas = ", ".join(COPAS[copa])
        print(f"  {i}. {copa}")
        print(f"     Pistas: {pistas}")

    try:
        opcion = int(input("\nElige una copa: ").strip())
        if opcion < 1 or opcion > len(copas_lista):
            print("Opción no válida.")
            return
        copa = copas_lista[opcion - 1]
    except ValueError:
        print("Entrada no válida.")
        return

    jugadores = seleccionar_jugadores(datos)
    if not jugadores:
        return

    nombre = input("Nombre del torneo (opcional, Enter para auto): ").strip()
    if not nombre:
        nombre = f"{copa} - {len(datos['torneos']) + 1}"

    torneo = crear_torneo(datos, nombre, copa, jugadores)
    print(f"\nTorneo '{torneo['nombre']}' creado con {len(jugadores)} jugadores.")
    print("Pistas:")
    for c in torneo["carreras"]:
        print(f"  Carrera {c['numero']}: {c['pista']}")
    print("\nUsa la opción 5 para registrar los resultados de cada carrera.")


def menu_nuevo_torneo_personalizado(datos):
    print("\n--- Nuevo Torneo (Pistas Personalizadas) ---")
    if len(datos["jugadores"]) < 2:
        print("Necesitas al menos 2 jugadores registrados.")
        return

    print("Ingresa 4 nombres de pista:")
    pistas = []
    for i in range(1, 5):
        pista = input(f"  Pista {i}: ").strip()
        if not pista:
            print("Nombre vacío, cancelando.")
            return
        pistas.append(pista)

    jugadores = seleccionar_jugadores(datos)
    if not jugadores:
        return

    nombre = input("Nombre del torneo (opcional): ").strip()
    if not nombre:
        nombre = f"Torneo Personalizado - {len(datos['torneos']) + 1}"

    torneo = crear_torneo_personalizado(datos, nombre, pistas, jugadores)
    print(f"\nTorneo '{torneo['nombre']}' creado.")
    print("\nUsa la opción 5 para registrar resultados.")


def menu_registrar_resultados(datos):
    print("\n--- Registrar Resultados ---")
    torneos_abiertos = [t for t in datos["torneos"] if not t["completado"]]
    if not torneos_abiertos:
        print("No hay torneos pendientes.")
        return

    print("Torneos en curso:")
    for t in torneos_abiertos:
        carreras_hechas = sum(1 for c in t["carreras"] if c["resultados"])
        print(f"  ID {t['id']}: {t['nombre']} ({carreras_hechas}/4 carreras)")

    try:
        tid = int(input("\nID del torneo: ").strip())
    except ValueError:
        print("ID no válido.")
        return

    torneo = None
    for t in datos["torneos"]:
        if t["id"] == tid:
            torneo = t
            break
    if not torneo:
        print("Torneo no encontrado.")
        return

    # Mostrar carreras pendientes
    print(f"\nTorneo: {torneo['nombre']}")
    print(f"Jugadores: {', '.join(torneo['jugadores'])}")
    print("\nCarreras:")
    for c in torneo["carreras"]:
        estado = "✅" if c["resultados"] else "⬜"
        print(f"  {estado} Carrera {c['numero']}: {c['pista']}")
        if c["resultados"]:
            for jugador, pos in sorted(c["resultados"].items(), key=lambda x: x[1]):
                print(f"      {pos}° - {jugador} ({puntos_por_posicion(pos)} pts)")

    # Seleccionar carrera
    pendientes = [c for c in torneo["carreras"] if not c["resultados"]]
    if not pendientes:
        print("\nTodas las carreras ya tienen resultados.")
        return

    try:
        num = int(input(f"\nNúmero de carrera a registrar ({pendientes[0]['numero']}-{pendientes[-1]['numero']}): ").strip())
    except ValueError:
        print("Número no válido.")
        return

    carrera = None
    for c in torneo["carreras"]:
        if c["numero"] == num:
            carrera = c
            break
    if not carrera:
        print("Carrera no encontrada.")
        return
    if carrera["resultados"]:
        print("Esta carrera ya tiene resultados.")
        return

    # Registrar posiciones
    print(f"\nCarrera {num}: {carrera['pista']}")
    print(f"Ingresa la posición de cada jugador (1-{len(torneo['jugadores'])}):")
    resultados = {}
    posiciones_usadas = set()
    for jugador in torneo["jugadores"]:
        while True:
            try:
                pos = int(input(f"  {jugador}: ").strip())
                if pos < 1 or pos > len(torneo["jugadores"]):
                    print(f"    Posición debe ser entre 1 y {len(torneo['jugadores'])}.")
                    continue
                if pos in posiciones_usadas:
                    print(f"    La posición {pos} ya fue asignada.")
                    continue
                resultados[jugador] = pos
                posiciones_usadas.add(pos)
                break
            except ValueError:
                print("    Número no válido.")

    registrar_resultado(datos, tid, num, resultados)
    print("\nResultados registrados:")
    for jugador, pos in sorted(resultados.items(), key=lambda x: x[1]):
        print(f"  {pos}° - {jugador} ({puntos_por_posicion(pos)} pts)")

    # Si se completó el torneo, mostrar ranking final
    torneo_actualizado = None
    for t in datos["torneos"]:
        if t["id"] == tid:
            torneo_actualizado = t
            break
    if torneo_actualizado and torneo_actualizado["completado"]:
        print("\n🏆 ¡TORNEO COMPLETADO! 🏆")
        ranking = calcular_ranking_torneo(torneo_actualizado)
        medallas = ["🥇", "🥈", "🥉", "  "]
        for i, (jugador, puntos) in enumerate(ranking):
            medalla = medallas[i] if i < len(medallas) else "  "
            print(f"  {medalla} {jugador}: {puntos} pts")


def menu_ver_torneos(datos):
    if not datos["torneos"]:
        print("\nNo hay torneos registrados.")
        return

    print(f"\n--- Torneos ({len(datos['torneos'])}) ---")
    for t in datos["torneos"]:
        estado = "✅ Completado" if t["completado"] else "🔄 En curso"
        print(f"\n  [{t['id']}] {t['nombre']} - {t['copa']}")
        print(f"      Fecha: {t['fecha']} | {estado}")
        print(f"      Jugadores: {', '.join(t['jugadores'])}")

        if t["completado"]:
            ranking = calcular_ranking_torneo(t)
            medallas = ["🥇", "🥈", "🥉", "  "]
            print("      Resultado:")
            for i, (jugador, puntos) in enumerate(ranking):
                medalla = medallas[i] if i < len(medallas) else "  "
                print(f"        {medalla} {jugador}: {puntos} pts")


def menu_ranking_global(datos):
    ranking = calcular_ranking_global(datos)
    if not ranking or all(r["torneos_jugados"] == 0 for r in ranking):
        print("\nNo hay datos suficientes para el ranking.")
        return

    print("\n" + "=" * 55)
    print("          🏆 RANKING GLOBAL 🏆")
    print("=" * 55)
    medallas = ["🥇", "🥈", "🥉"]
    for i, r in enumerate(ranking):
        if r["torneos_jugados"] == 0:
            continue
        medalla = medallas[i] if i < len(medallas) else f"{i+1}."
        print(f"\n  {medalla} {r['nombre']}")
        print(f"      Puntos totales: {r['puntos_totales']}")
        print(f"      Torneos: {r['torneos_jugados']} jugados, {r['torneos_ganados']} ganados")
        print(f"      Carreras: {r['carreras_jugadas']} | Pos. promedio: {r['posicion_promedio']}")
        print(f"      Podios: 🥇{r['primer_lugar']} 🥈{r['segundo_lugar']} 🥉{r['tercer_lugar']}")


def menu_ranking_pista(datos):
    pista_data = stats_por_pista(datos)
    if not pista_data:
        print("\nNo hay datos de pistas todavía.")
        return

    pistas = sorted(pista_data.keys())
    print(f"\n--- Pistas jugadas ({len(pistas)}) ---")
    for i, pista in enumerate(pistas, 1):
        print(f"  {i}. {pista}")

    try:
        opcion = int(input("\nElige una pista (0 para ver todas): ").strip())
    except ValueError:
        print("Opción no válida.")
        return

    if opcion == 0:
        pistas_mostrar = pistas
    elif 1 <= opcion <= len(pistas):
        pistas_mostrar = [pistas[opcion - 1]]
    else:
        print("Opción no válida.")
        return

    for pista in pistas_mostrar:
        ranking = pista_data[pista]
        print(f"\n  📍 {pista}")
        for r in ranking:
            print(f"      {r['jugador']}: promedio {r['posicion_promedio']}° "
                  f"(mejor: {r['mejor_posicion']}°, peor: {r['peor_posicion']}°) "
                  f"- {r['veces_jugada']} veces - {r['puntos_totales']} pts")


def menu_mejor_peor_pista(datos):
    nombre = input("\nNombre del jugador: ").strip()
    if not nombre:
        return

    mejor, peor = mejor_y_peor_pista(datos, nombre)
    if not mejor:
        print(f"No hay datos para '{nombre}'.")
        return

    print(f"\n--- Estadísticas de pista para {nombre} ---")
    print(f"\n  ✅ MEJOR pista: {mejor['pista']}")
    print(f"      Posición promedio: {mejor['posicion_promedio']}°")
    print(f"      Mejor resultado: {mejor['mejor_posicion']}° | Jugada {mejor['veces_jugada']} veces")

    print(f"\n  ❌ PEOR pista: {peor['pista']}")
    print(f"      Posición promedio: {peor['posicion_promedio']}°")
    print(f"      Peor resultado: {peor['peor_posicion']}° | Jugada {peor['veces_jugada']} veces")


def menu_enfrentamiento(datos):
    print("\n--- Enfrentamiento Directo ---")
    j1 = input("Jugador 1: ").strip()
    j2 = input("Jugador 2: ").strip()
    if not j1 or not j2:
        return

    h = historial_enfrentamientos(datos, j1, j2)
    if h["carreras_juntos"] == 0:
        print(f"\n{j1} y {j2} no han corrido juntos.")
        return

    print(f"\n  ⚔️  {j1} vs {j2}  ⚔️")
    print(f"  Carreras juntos: {h['carreras_juntos']}")
    print(f"  {j1}: {h['victorias_j1']} victorias")
    print(f"  {j2}: {h['victorias_j2']} victorias")
    if h["empates"]:
        print(f"  Empates: {h['empates']}")

    if h["victorias_j1"] > h["victorias_j2"]:
        print(f"\n  👑 {j1} domina el enfrentamiento!")
    elif h["victorias_j2"] > h["victorias_j1"]:
        print(f"\n  👑 {j2} domina el enfrentamiento!")
    else:
        print(f"\n  🤝 ¡Están empatados!")


def main():
    datos = cargar_datos()

    acciones = {
        "1": menu_agregar_jugador,
        "2": menu_ver_jugadores,
        "3": menu_nuevo_torneo_copa,
        "4": menu_nuevo_torneo_personalizado,
        "5": menu_registrar_resultados,
        "6": menu_ver_torneos,
        "7": menu_ranking_global,
        "8": menu_ranking_pista,
        "9": menu_mejor_peor_pista,
        "10": menu_enfrentamiento,
    }

    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()
        if opcion == "0":
            print("\n¡Hasta la próxima carrera! 🏁")
            break
        accion = acciones.get(opcion)
        if accion:
            accion(datos)
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
