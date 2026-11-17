import numpy as np
from pathlib import Path
import trimesh
import os

# Ustawienie katalogu dla wygenerowanych plików
GENERATED_DIR = Path('generated_files')
GENERATED_DIR.mkdir(exist_ok=True)

def generate_hollow_plate_3mf(length=100, width=80, height=35, hole_length=90, hole_width=70, thickness=10):
    """
    Generuje plik 3MF płyty z wycięciem w środku
    
    Args:
        length (float): Długość płyty [mm]
        width (float): Szerokość płyty [mm]
        height (float): Wysokość płyty [mm]
        hole_length (float): Długość wycięcia [mm]
        hole_width (float): Szerokość wycięcia [mm]
        thickness (float): Grubość płyty [mm]
    """
    # Tworzenie bryły płyty
    plate = trimesh.creation.box([length, width, height])
    
    # Tworzenie wycięcia (mniejszego prostokąta)
    hole = trimesh.creation.box([hole_length, hole_width, thickness])
    
    # Przesunięcie wycięcia do środka
    hole.apply_translation([0, 0, height/2 - thickness/2])
    
    # Wykonanie operacji wycięcia
    result = plate.difference(hole)
    
    # Zapis do pliku 3MF
    file_path = GENERATED_DIR / 'hollow_plate.3mf'
    result.export(file_path)
    print(f'Plik 3MF wygenerowany: {file_path}')
    return file_path

def generate_hollow_plate_stl(length=100, width=80, height=35, hole_length=90, hole_width=70, thickness=10):
    """
    Generuje plik STL płyty z wycięciem w środku
    
    Args:
        length (float): Długość płyty [mm]
        width (float): Szerokość płyty [mm]
        height (float): Wysokość płyty [mm]
        hole_length (float): Długość wycięcia [mm]
        hole_width (float): Szerokość wycięcia [mm]
        thickness (float): Grubość płyty [mm]
    """
    # Tworzenie bryły płyty
    plate = trimesh.creation.box([length, width, height])
    
    # Tworzenie wycięcia (mniejszego prostokąta)
    hole = trimesh.creation.box([hole_length, hole_width, thickness])
    
    # Przesunięcie wycięcia do środka
    hole.apply_translation([0, 0, height/2 - thickness/2])
    
    # Wykonanie operacji wycięcia
    result = plate.difference(hole)
    
    # Zapis do pliku STL
    file_path = GENERATED_DIR / 'hollow_plate.stl'
    result.export(file_path)
    print(f'Plik STL wygenerowany: {file_path}')
    return file_path

if __name__ == '__main__':
    # Generowanie plików
    print('Generowanie plików 3D...')
    generate_hollow_plate_3mf()
    generate_hollow_plate_stl()
    print('Generowanie zakończone.')