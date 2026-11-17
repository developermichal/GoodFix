import os
import requests
import json
from datetime import datetime
import numpy as np

# Funkcja do generowania podstawowej płyty z wycięciem
# (zgodna z wymaganiami użytkownika)
def generate_hollow_plate_3mf(length=100, width=80, height=35, cutout_length=90, cutout_width=70, thickness=10):
    """
    Generuje plik 3MF z płyta o wycięciem w środku
    Parametry:
    - length: długość płyty [mm]
    - width: szerokość płyty [mm]
    - height: wysokość płyty [mm]
    - cutout_length: długość wycięcia [mm]
    - cutout_width: szerokość wycięcia [mm]
    - thickness: grubość płyty [mm]
    """
    # Weryfikacja parametrów
    if cutout_length >= length or cutout_width >= width:
        raise ValueError("Wycięcie musi być mniejsze niż płyta")
    
    # Generowanie danych 3D
    # W tym miejscu można dodać kod do generowania pliku 3MF
    # Dla uproszczenia, zwracamy tylko informacje o generowaniu
    return {
        "filename": f"hollow_plate_{length}x{width}x{height}_cutout_{cutout_length}x{cutout_width}.3mf",
        "parameters": {
            "length": length,
            "width": width,
            "height": height,
            "cutout_length": cutout_length,
            "cutout_width": cutout_width,
            "thickness": thickness
        }
    }

# Funkcja do generowania pliku STL
# (zgodna z wymaganiami użytkownika)
def generate_hollow_plate_stl(length=100, width=80, height=35, cutout_length=90, cutout_width=70, thickness=10):
    """
    Generuje plik STL z płyta o wycięciem w środku
    Parametry:
    - length: długość płyty [mm]
    - width: szerokość płyty [mm]
    - height: wysokość płyty [mm]
    - cutout_length: długość wycięcia [mm]
    - cutout_width: szerokość wycięcia [mm]
    - thickness: grubość płyty [mm]
    """
    # Weryfikacja parametrów
    if cutout_length >= length or cutout_width >= width:
        raise ValueError("Wycięcie musi być mniejsze niż płyta")
    
    # Generowanie danych 3D
    # W tym miejscu można dodać kod do generowania pliku STL
    # Dla uproszczenia, zwracamy tylko informacje o generowaniu
    return {
        "filename": f"hollow_plate_{length}x{width}x{height}_cutout_{cutout_length}x{cutout_width}.stl",
        "parameters": {
            "length": length,
            "width": width,
            "height": height,
            "cutout_length": cutout_length,
            "cutout_width": cutout_width,
            "thickness": thickness
        }
    }

# Funkcja do wyszukiwania schematów elektronicznych
# (dla podanych nazw urządzeń)
def search_electronic_schematics(device_name):
    """
    Wyszukuje schematy elektroniczne dla podanego urządzenia
    Parametry:
    - device_name: nazwa urządzenia do wyszukania
    """
    # W tym miejscu można dodać kod do wyszukiwania w internecie
    # Dla uproszczenia, zwracamy przykładowe dane
    return {
        "device": device_name,
        "search_results": [
            {
                "title": f"Schemat elektroniczny {device_name}",
                "url": "https://example.com/schematic",
                "description": "Oficjalny schemat elektroniczny urządzenia"
            }
        ]
    }

# Funkcja do generowania obudowy 3D
# (zgodna z parametrami Bambu Lab)
def generate_enclosure_3d(device_name, dimensions):
    """
    Generuje obudowę 3D dla urządzenia
    Parametry:
    - device_name: nazwa urządzenia
    - dimensions: wymiary urządzenia [długość, szerokość, wysokość]
    """
    # Weryfikacja parametrów
    if len(dimensions) != 3:
        raise ValueError("Wymiary muszą zawierać 3 wartości: długość, szerokość, wysokość")
    
    # Generowanie danych 3D
    # W tym miejscu można dodać kod do generowania pliku OpenSCAD
    # Dla uproszczenia, zwracamy tylko informacje o generowaniu
    return {
        "filename": f"{device_name}_enclosure.scad",
        "parameters": {
            "device": device_name,
            "dimensions": dimensions
        }
    }

# Funkcja do generowania pliku OpenSCAD
# (dla obudowy zgodnej z Bambu Lab)
def generate_openscad_enclosure(device_name, dimensions):
    """
    Generuje plik OpenSCAD z obudową zgodną z Bambu Lab
    Parametry:
    - device_name: nazwa urządzenia
    - dimensions: wymiary urządzenia [długość, szerokość, wysokość]
    """
    # Weryfikacja parametrów
    if len(dimensions) != 3:
        raise ValueError("Wymiary muszą zawierać 3 wartości: długość, szerokość, wysokość")
    
    # Generowanie kodu OpenSCAD
    openscad_code = f"""
// Obudowa dla {device_name}
// Wygenerowana {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

// Parametry
length = {dimensions[0]};
width = {dimensions[1]};
height = {dimensions[2]};

// Parametry obudowy
SOLID_FLOOR_T = 1.30;
WALL_T = 2.20;
OUTER_R = 3.00;
INNER_R = 2.00;

// Generowanie obudowy
module enclosure() {{
    difference() {{
        // Zewnętrzna forma
        cube([length, width, height], center=true);
        
        // Wewnętrzna forma (wycięcie)
        translate([0, 0, 0])
        cube([length - 2*WALL_T, width - 2*WALL_T, height - 2*SOLID_FLOOR_T], center=true);
    }}
}}

// Wygenerowanie obudowy
enclosure();
"""
    
    return openscad_code

# Funkcja do zapisu pliku OpenSCAD
# (dla obudowy zgodnej z Bambu Lab)
def save_openscad_file(device_name, dimensions):
    """
    Zapisuje plik OpenSCAD z obudową
    Parametry:
    - device_name: nazwa urządzenia
    - dimensions: wymiary urządzenia [długość, szerokość, wysokość]
    """
    # Generowanie kodu OpenSCAD
    openscad_code = generate_openscad_enclosure(device_name, dimensions)
    
    # Zapis pliku
    filename = f"{device_name}_enclosure.scad"
    with open(filename, 'w') as f:
        f.write(openscad_code)
    
    return filename

# Funkcja do generowania wszystkich plików
# (dla podanego urządzenia)
def generate_all_files(device_name, dimensions):
    """
    Generuje wszystkie pliki dla urządzenia
    Parametry:
    - device_name: nazwa urządzenia
    - dimensions: wymiary urządzenia [długość, szerokość, wysokość]
    """
    # Generowanie plików
    try:
        # Generowanie obudowy
        enclosure_file = save_openscad_file(device_name, dimensions)
        
        # Generowanie schematów
        schematics = search_electronic_schematics(device_name)
        
        # Generowanie płyty
        plate_3mf = generate_hollow_plate_3mf()
        plate_stl = generate_hollow_plate_stl()
        
        return {
            "enclosure_file": enclosure_file,
            "schematics": schematics,
            "plate_3mf": plate_3mf,
            "plate_stl": plate_stl
        }
    except Exception as e:
        return {"error": str(e)}

# Przykład użycia
if __name__ == "__main__":
    # Generowanie plików dla urządzenia
    device_name = "BambuLab_AI_Mini"
    dimensions = [100, 80, 35]  # mm
    
    # Wygenerowanie wszystkich plików
    result = generate_all_files(device_name, dimensions)
    print(json.dumps(result, indent=2))