"""Módulo para gestionar un grupo de amigos."""

import json
import csv
from datetime import datetime, date
from pathlib import Path

DATOS_PATH = Path(__file__).parent / "datos" / "amigos.json"


class Amigo:
    """Representa a un amigo con su información de contacto."""

    def __init__(self, nombre, telefono="", email="", cumpleaños="", notas=""):
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.cumpleaños = cumpleaños  # formato: DD/MM/AAAA
        self.notas = notas
        self.eventos = []

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "telefono": self.telefono,
            "email": self.email,
            "cumpleaños": self.cumpleaños,
            "notas": self.notas,
            "eventos": self.eventos,
        }

    @classmethod
    def from_dict(cls, data):
        amigo = cls(
            nombre=data["nombre"],
            telefono=data.get("telefono", ""),
            email=data.get("email", ""),
            cumpleaños=data.get("cumpleaños", ""),
            notas=data.get("notas", ""),
        )
        amigo.eventos = data.get("eventos", [])
        return amigo

    def dias_para_cumpleaños(self):
        """Calcula los días que faltan para el próximo cumpleaños."""
        if not self.cumpleaños:
            return None
        try:
            dia, mes, _ = self.cumpleaños.split("/")
            hoy = date.today()
            cumple_este_año = date(hoy.year, int(mes), int(dia))
            if cumple_este_año < hoy:
                cumple_este_año = date(hoy.year + 1, int(mes), int(dia))
            return (cumple_este_año - hoy).days
        except (ValueError, IndexError):
            return None

    def __str__(self):
        info = f"  Nombre: {self.nombre}"
        if self.telefono:
            info += f"\n  Teléfono: {self.telefono}"
        if self.email:
            info += f"\n  Email: {self.email}"
        if self.cumpleaños:
            dias = self.dias_para_cumpleaños()
            info += f"\n  Cumpleaños: {self.cumpleaños}"
            if dias is not None:
                info += f" (faltan {dias} días)"
        if self.notas:
            info += f"\n  Notas: {self.notas}"
        if self.eventos:
            info += f"\n  Eventos: {len(self.eventos)} registrados"
        return info


class GestorAmigos:
    """Gestiona la lista de amigos y operaciones sobre ella."""

    def __init__(self):
        self.amigos: list[Amigo] = []
        self.cargar()

    def cargar(self):
        """Carga los amigos desde el archivo JSON."""
        if DATOS_PATH.exists():
            with open(DATOS_PATH, "r", encoding="utf-8") as f:
                datos = json.load(f)
            self.amigos = [Amigo.from_dict(d) for d in datos]

    def guardar(self):
        """Guarda los amigos en el archivo JSON."""
        DATOS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DATOS_PATH, "w", encoding="utf-8") as f:
            json.dump([a.to_dict() for a in self.amigos], f, ensure_ascii=False, indent=2)

    def agregar(self, amigo: Amigo):
        """Agrega un nuevo amigo a la lista."""
        self.amigos.append(amigo)
        self.guardar()

    def eliminar(self, nombre: str) -> bool:
        """Elimina un amigo por nombre. Retorna True si se eliminó."""
        for i, a in enumerate(self.amigos):
            if a.nombre.lower() == nombre.lower():
                self.amigos.pop(i)
                self.guardar()
                return True
        return False

    def buscar(self, texto: str) -> list[Amigo]:
        """Busca amigos cuyo nombre contenga el texto dado."""
        texto = texto.lower()
        return [a for a in self.amigos if texto in a.nombre.lower()]

    def listar(self) -> list[Amigo]:
        """Retorna todos los amigos ordenados por nombre."""
        return sorted(self.amigos, key=lambda a: a.nombre.lower())

    def cumpleaños_proximos(self, dias: int = 30) -> list[Amigo]:
        """Retorna amigos con cumpleaños en los próximos N días."""
        resultado = []
        for a in self.amigos:
            d = a.dias_para_cumpleaños()
            if d is not None and d <= dias:
                resultado.append(a)
        return sorted(resultado, key=lambda a: a.dias_para_cumpleaños())

    def agregar_evento(self, nombre: str, evento: str) -> bool:
        """Registra un evento/salida con un amigo."""
        for a in self.amigos:
            if a.nombre.lower() == nombre.lower():
                a.eventos.append({
                    "fecha": datetime.now().strftime("%d/%m/%Y"),
                    "descripcion": evento,
                })
                self.guardar()
                return True
        return False

    def exportar_csv(self, ruta: str):
        """Exporta la lista de amigos a un archivo CSV."""
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Nombre", "Teléfono", "Email", "Cumpleaños", "Notas", "Num. Eventos"])
            for a in self.amigos:
                writer.writerow([a.nombre, a.telefono, a.email, a.cumpleaños, a.notas, len(a.eventos)])
