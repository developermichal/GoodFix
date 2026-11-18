import json
from functools import wraps

def cuboid_decorator(func):
    """
    Dekorator do generowania danych dla graniastosłupa z możliwością wycięcia.
    Obsługuje różne ściany i możliwość podania grubości ścianki.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Pobranie argumentów
        width = kwargs.get('width', 10)
        height = kwargs.get('height', 10)
        depth = kwargs.get('depth', 10)
        cut_location = kwargs.get('cut_location', None)
        cut_dimensions = kwargs.get('cut_dimensions', None)
        wall_thickness = kwargs.get('wall_thickness', 0)
        
        # Walidacja danych
        if width <= 0 or height <= 0 or depth <= 0:
            raise ValueError("Wymiary muszą być dodatnie")
        
        if cut_location and cut_dimensions:
            cut_x, cut_y, cut_z = cut_dimensions
            if cut_x <= 0 or cut_y <= 0 or cut_z <= 0:
                raise ValueError("Wymiary wycięcia muszą być dodatnie")
            
            # Walidacja lokalizacji wycięcia
            if cut_location not in ['front', 'back', 'left', 'right', 'top', 'bottom']:
                raise ValueError("Nieprawidłowa lokalizacja wycięcia")
            
            # Walidacja wymiarów wycięcia względem graniastosłupa
            if cut_location in ['front', 'back']:
                if cut_x > width or cut_z > depth:
                    raise ValueError("Wymiary wycięcia przekraczają rozmiary graniastosłupa")
            elif cut_location in ['left', 'right']:
                if cut_y > height or cut_z > depth:
                    raise ValueError("Wymiary wycięcia przekraczają rozmiary graniastosłupa")
            elif cut_location in ['top', 'bottom']:
                if cut_x > width or cut_y > height:
                    raise ValueError("Wymiary wycięcia przekraczają rozmiary graniastosłupa")
        
        # Wywołanie oryginalnej funkcji
        result = func(*args, **kwargs)
        
        # Dodanie danych do wyniku
        data = {
            "cuboid": {
                "width": width,
                "height": height,
                "depth": depth,
                "wall_thickness": wall_thickness
            }
        }
        
        if cut_location and cut_dimensions:
            data["cut"] = {
                "location": cut_location,
                "dimensions": cut_dimensions
            }
        
        # Zapis do pliku JSON
        with open('cuboid_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        
        return data
    
    return wrapper

# Przykład użycia
@cuboid_decorator
def generate_cuboid_data(**kwargs):
    # Funkcja generująca dane
    return kwargs

# Przykład użycia
if __name__ == "__main__":
    # Przykład 1: Graniastosłup bez wycięcia
    try:
        result1 = generate_cuboid_data(width=20, height=15, depth=10)
        print("Graniastosłup bez wycięcia:", result1)
    except Exception as e:
        print("Błąd:", e)
    
    # Przykład 2: Graniastosłup z wycięciem
    try:
        result2 = generate_cuboid_data(
            width=20,
            height=15,
            depth=10,
            cut_location='front',
            cut_dimensions=(5, 5, 2)
        )
        print("Graniastosłup z wycięciem:", result2)
    except Exception as e:
        print("Błąd:", e)
    
    # Przykład 3: Graniastosłup z grubością ścianki
    try:
        result3 = generate_cuboid_data(
            width=20,
            height=15,
            depth=10,
            wall_thickness=1
        )
        print("Graniastosłup z grubością ścianki:", result3)
    except Exception as e:
        print("Błąd:", e)
