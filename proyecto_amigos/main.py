"""Programa principal con menú interactivo para gestionar amigos."""

from amigos import GestorAmigos, Amigo


def mostrar_menu():
    print("\n" + "=" * 40)
    print("   GESTOR DE AMIGOS")
    print("=" * 40)
    print("1. Agregar amigo")
    print("2. Listar amigos")
    print("3. Buscar amigo")
    print("4. Cumpleaños próximos")
    print("5. Registrar evento/salida")
    print("6. Ver eventos de un amigo")
    print("7. Editar amigo")
    print("8. Eliminar amigo")
    print("9. Exportar a CSV")
    print("0. Salir")
    print("-" * 40)


def agregar_amigo(gestor):
    print("\n--- Agregar nuevo amigo ---")
    nombre = input("Nombre: ").strip()
    if not nombre:
        print("El nombre es obligatorio.")
        return
    telefono = input("Teléfono (opcional): ").strip()
    email = input("Email (opcional): ").strip()
    cumpleaños = input("Cumpleaños DD/MM/AAAA (opcional): ").strip()
    notas = input("Notas (opcional): ").strip()

    amigo = Amigo(nombre, telefono, email, cumpleaños, notas)
    gestor.agregar(amigo)
    print(f"'{nombre}' agregado correctamente.")


def listar_amigos(gestor):
    amigos = gestor.listar()
    if not amigos:
        print("\nNo hay amigos registrados.")
        return
    print(f"\n--- Lista de amigos ({len(amigos)}) ---")
    for i, a in enumerate(amigos, 1):
        print(f"\n{i}.")
        print(a)


def buscar_amigo(gestor):
    texto = input("\nBuscar: ").strip()
    if not texto:
        return
    resultados = gestor.buscar(texto)
    if not resultados:
        print("No se encontraron resultados.")
        return
    print(f"\n--- Resultados ({len(resultados)}) ---")
    for a in resultados:
        print()
        print(a)


def cumpleaños_proximos(gestor):
    dias = input("Días a consultar (default 30): ").strip()
    dias = int(dias) if dias.isdigit() else 30
    proximos = gestor.cumpleaños_proximos(dias)
    if not proximos:
        print(f"\nNo hay cumpleaños en los próximos {dias} días.")
        return
    print(f"\n--- Cumpleaños próximos ({dias} días) ---")
    for a in proximos:
        d = a.dias_para_cumpleaños()
        print(f"  {a.nombre} - {a.cumpleaños} (faltan {d} días)")


def registrar_evento(gestor):
    nombre = input("\nNombre del amigo: ").strip()
    if not nombre:
        return
    evento = input("Descripción del evento: ").strip()
    if not evento:
        return
    if gestor.agregar_evento(nombre, evento):
        print("Evento registrado.")
    else:
        print(f"No se encontró a '{nombre}'.")


def ver_eventos(gestor):
    nombre = input("\nNombre del amigo: ").strip()
    resultados = gestor.buscar(nombre)
    if not resultados:
        print(f"No se encontró a '{nombre}'.")
        return
    amigo = resultados[0]
    if not amigo.eventos:
        print(f"{amigo.nombre} no tiene eventos registrados.")
        return
    print(f"\n--- Eventos de {amigo.nombre} ---")
    for e in amigo.eventos:
        print(f"  [{e['fecha']}] {e['descripcion']}")


def editar_amigo(gestor):
    nombre = input("\nNombre del amigo a editar: ").strip()
    resultados = gestor.buscar(nombre)
    if not resultados:
        print(f"No se encontró a '{nombre}'.")
        return
    amigo = resultados[0]
    print(f"\nEditando a {amigo.nombre} (dejar vacío para no cambiar):")
    nuevo_nombre = input(f"  Nombre [{amigo.nombre}]: ").strip()
    nuevo_tel = input(f"  Teléfono [{amigo.telefono}]: ").strip()
    nuevo_email = input(f"  Email [{amigo.email}]: ").strip()
    nuevo_cumple = input(f"  Cumpleaños [{amigo.cumpleaños}]: ").strip()
    nuevas_notas = input(f"  Notas [{amigo.notas}]: ").strip()

    if nuevo_nombre:
        amigo.nombre = nuevo_nombre
    if nuevo_tel:
        amigo.telefono = nuevo_tel
    if nuevo_email:
        amigo.email = nuevo_email
    if nuevo_cumple:
        amigo.cumpleaños = nuevo_cumple
    if nuevas_notas:
        amigo.notas = nuevas_notas

    gestor.guardar()
    print("Amigo actualizado.")


def eliminar_amigo(gestor):
    nombre = input("\nNombre del amigo a eliminar: ").strip()
    if not nombre:
        return
    confirmar = input(f"¿Seguro que quieres eliminar a '{nombre}'? (s/n): ").strip().lower()
    if confirmar == "s":
        if gestor.eliminar(nombre):
            print(f"'{nombre}' eliminado.")
        else:
            print(f"No se encontró a '{nombre}'.")


def exportar_csv(gestor):
    ruta = input("Nombre del archivo (default: amigos.csv): ").strip()
    if not ruta:
        ruta = "amigos.csv"
    gestor.exportar_csv(ruta)
    print(f"Datos exportados a '{ruta}'.")


def main():
    gestor = GestorAmigos()
    acciones = {
        "1": agregar_amigo,
        "2": listar_amigos,
        "3": buscar_amigo,
        "4": cumpleaños_proximos,
        "5": registrar_evento,
        "6": ver_eventos,
        "7": editar_amigo,
        "8": eliminar_amigo,
        "9": exportar_csv,
    }

    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()
        if opcion == "0":
            print("\n¡Hasta luego!")
            break
        accion = acciones.get(opcion)
        if accion:
            accion(gestor)
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
