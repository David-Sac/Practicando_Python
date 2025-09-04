# SISTEMA DE GESTION ESCOLAR

import json
import csv
import os

DATA_JSON = "alumnos.json"
DATA_CSV = "alumnos.csv"


# Tupla para cursos fijos
CURSOS_DISPONIBLES = (
    "Matemática",
    "Lenguaje",
    "Ciencia"
) 

def leer_float(mensaje: str, minimo: float = None, maximo: float = None):
    """Lee un número float con validación opcional de rango"""
    while True:
        try:
            val = float(input(mensaje))
            if minimo is not None and val < minimo:
                print(f"* Debe ser >= {minimo}")
                continue
            if maximo is not None and val > maximo:
                print(f"* Debe ser <= {maximo}")
                continue
            return val
        except ValueError:
            print("* Ingrese un número válido")
            
def leer_int(mensaje: str, minimo: int = None, maximo: int = None):
    """Lee un entero con validación opcional de rango."""
    while True:
        try:
            val = int(input(mensaje))
            if minimo is not None and val<minimo:
                print(f"* Debe ser >= {minimo}")
                continue
            if maximo is not None and val>maximo:
                print(f"* Debe ser <= {maximo}")
                continue
            return val
        except ValueError:
            print("* Ingrese un número entero válido")

def pausar():
    input("\nPresiona ENTER para continuar...")
            
class Persona:
    def __init__(self, nombre: str, edad: int, dni: str):
        self.nombre = nombre
        self.edad = edad
        self.__dni = dni
    
    @property
    def dni(self) -> str:
        return self.__dni
    
    def info(self) -> str:
        return f"{self.nombre} (Edad: {self.edad} , DNI: {self.__dni})"

class Alumno(Persona):
    def __init__(self, nombre: str, edad: int, dni: str):
        super().__init__(nombre, edad, dni)
        self.notas: dict[str, float] = {}
        
    def set_nota(self, curso: str, nota: float):
        self.notas[curso] = nota
        
    def promedio(self) -> float:
        if not self.notas:
            return 0.0
        return sum(self.notas.values())/len(self.notas)

    def aprobado(self) -> bool:
        return self.promedio() >= 11.0
    
    def info(self) -> str: #polimorfismo: sobreescribimos   
        base = super().info()
        prom = self.promedio()
        estado = "APROBADO" if self.aprobado() else "DESAPROBADO"
        return f"{base} | Promedio: {prom:.2f} -> {estado}"
        
class Profesor(Persona):
    def __init__(self, nombre: str, edad: int, dni: str, cursos_asignados: tuple[str,...] = CURSOS_DISPONIBLES):
        super().__init__(nombre, edad, dni)
        self.cursos_asignados = cursos_asignados
        
    def info(self) -> str:
        base = super().info()
        cursos = ", ".join(self.cursos_asignados)
        return f"{base} | Profesor de: {cursos}"

class Escuela:
    def __init__(self):
        self.alumnos: dict[str, Alumno] = {}
        self._dni_registrados : set[str] = set()
        
    # CRUD Alumnos
    def registrar_alumno(self, nombre: str, edad: int, dni: str) -> bool:
        if dni in self._dni_registrados:
            return False
        alumno = Alumno(nombre, edad, dni)
        self.alumnos[dni] = alumno
        self._dni_registrados.add(dni)
        return True
    
    def eliminar_alumno(self, dni: str) -> bool:
        if dni not in self._dni_registrados:
            return False
        self._dni_registrados.remove(dni)
        self.alumnos.pop(dni, None)
        return True
    
    def obtener_alumno(self, dni: str) -> Alumno | None:
        return self.alumnos.get(dni)
    
    def listar_alumnos(self) -> list[Alumno]:
        return list(self.alumnos.values())    
    
    # Notas
    
    def asignar_nota(self, dni:str, curso:str, nota:float) -> bool:
        alumno = self.obtener_alumno(dni)
        if not alumno:
            return False
        if curso not in CURSOS_DISPONIBLES:
            return False
        alumno.set_nota(curso, nota)
        return True
    
    # Persistencia (JSON & CSV)
    def guardar_json(self, ruta:str = DATA_JSON) -> None:
        data = []
        for a in self.alumnos.values():
            data.append({
                "nombre": a.nombre,
                "edad": a.edad,
                "dni": a.dni,
                "notas": a.notas 
            })
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def cargar_json(self, ruta:str = DATA_JSON) -> None:
        if not os.path.exists(ruta):
            return
        with open(ruta, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print("* Archivo JSON corrupto o vvacio. Se ignorará la carga.")
                return
            
        # Reconstruccion de objetos
        self.alumnos.clear()
        self._dni_registrados.clear()
        for item in data: 
            a = Alumno(item["nombre"], int(item["edad"]), item["dni"])
            # valudar que las notas sean floats
            notas_limpias = {}
            for curso, n in item.get("notas", {}).items():
                try:
                    notas_limpias[curso] = float(n)
                except (TypeError, ValueError):
                    pass
            a.notas = notas_limpias
            self.alumnos[a.dni] = a
            self._dni_registrados.add(a.dni)
            
    
    def exportar_csv(self, ruta: str = DATA_CSV) -> None:
        """
        Exporta a CSV con columnas: DNI, Nombre, Edad, Curso, Nota, Promedio
        """
        
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["DNI", "Nombre", "Edad", "Curso", "Nota", "Promedio"])
            for a in self.alumnos.values():
                prom = f"{a.promedio():.2f}"
                if a.notas:
                    for curso, nota in a.notas.items():
                        writer.writerow(a.dni, a.nombre, a.edad, curso, nota, prom)
                else:
                    writer.writerow([a.dni, a.nombre, a.edad, "", "", prom])

# UI consola

def mostrar_cursos():
    print("\nCursos disponibles")
    for i, c in enumerate(CURSOS_DISPONIBLES, start=1):
        print(f" {i}. {c}")

def menu():
    print("\n","="*10," SISTEMA DE GESTION ESCOLAR ", "="*10)
    print("1. Registrar alumno")
    print("2. Asignar notas a alumno")
    print("3. Mostrar ionformacion a alumno")
    print("4. Listar todos los alumnos")
    print("5. Eliminar alumno")
    print("6. Guardar datos (JSON)")
    print("7. Cargar datos (JSON)")
    print("8. Exportar a CSV")
    print("9. Salir")
    
def registrar_alumno_ui(escuela: Escuela):
    print("\n--- Registrar alumno ---")
    nombre = input("Nombre: ").strip()
    edad = leer_int("Edad: ", minimo=0, maximo=120)
    dni = input("DNI: ").strip()
    if escuela.registrar_alumno(nombre,edad,dni):
        print("Alumno registrado")
    else:
        print("Ya existe un alumno con ese DNI")
        
def asignar_notas_ui(escuela: Escuela):
    print("\n--- Asignar notas ---")
    dni = input("DNI del alumno: ".strip())
    alumno = escuela.obtener_alumno(dni)
    if not alumno:
        print("No existe un alumno con ese dni")
        return
    mostrar_cursos()
    print("Ingrese notas de 0 al 20 (deje vacio para omitir un curso)")
    for curso in CURSOS_DISPONIBLES:
        entrada = input(f"Nota de {curso}: ").strip()
        if entrada == "":
            continue
        try:
            nota = float(entrada)
            if 0<=nota<=20:
                escuela.asignar_nota(dni, curso, nota)
            else:
                print("* La nota debe estar entre 0 y 20. Omitido")
        except ValueError:
            print("* Valor inválido. Omitido")
    print("Notas registradas/actualizadas")
    
def info_alumno_ui(escuela:Escuela):
    print("\n--- Informacion de alumno ---")
    dni = input("DNI del alumno: ").strip()
    a = escuela.obtener_alumno(dni)
    if not a:
        print("No existe un alumno con ese DNI")
        return
    print("\n"+ a.info())
    if a.notas:
        print("Notas:")
        for c,n in a.notas.items():
            print(f" - {c}: {n}")
    else:
        print("Sin notas registradas")

def listar_alumnos_ui(escuela:Escuela):
    print("\n--- Lista de alumnos ---")
    alumnos = escuela.listar_alumnos()
    if not alumnos:
        print("No hay alumnos registrados")
        return
    alumnos.sort(key=lambda x: x.nombre.lower())
    for a in alumnos:
        print(a.info())
        
def eliminar_alumno_ui(escuela:Escuela):
    print("\n--- Eliminar alumno ---")
    dni = input("DNI del alumno: ").strip()
    if escuela.eliminar_alumno(dni):
        print("Alumno eliminado.")
    else:
        print("No existe un alumno con ese DNI.")
        
def guardar_ui(escuela:Escuela):
    escuela.guardar_json(DATA_JSON)
    print(f"Datos guardados en {DATA_JSON}")
    
def cargar_ui(escuela:Escuela):
    escuela.cargar_json(DATA_JSON)
    print(f"Carga finalizada desde {DATA_JSON} (si existía)")
    
def exportar_csv_ui(escuela:Escuela):
    escuela.exportar_csv(DATA_CSV)
    print(f"Datos exportados a {DATA_JSON}")
    

def main():
    escuela = Escuela()
    if os.path.exists(DATA_JSON):
        escuela.cargar_json(DATA_JSON)
        print(" i Datos previos cargados automáticamente")
    
    while True:
        menu()
        op = input("Seleccione una opción: ").strip()
        if op == "1":
            registrar_alumno_ui(escuela)
            pausar()
        elif op == "2":
            asignar_notas_ui(escuela)
            pausar()
        elif op == "3":
            info_alumno_ui(escuela)
            pausar()
        elif op == "4":
            listar_alumnos_ui(escuela)
            pausar()
        elif op == "5":
            eliminar_alumno_ui(escuela)
            pausar()
        elif op == "6":
            guardar_ui(escuela)
            pausar()
        elif op == "7":
            cargar_ui(escuela)
            pausar()
        elif op == "8":
            exportar_csv_ui(escuela)
            pausar()
        elif op == "9":
            print("¡Hasta luego!")
            break
        else:
            print("✳ Opción inválida.")
            pausar()
    

if __name__ == "__main__":
    main()