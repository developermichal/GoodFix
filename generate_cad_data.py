# generate_cad_data.py

def generate_prism_data(length, width, height, position=(0, 0, 0), rotation_angle=0):
    """
    Generuje dane w formacie JSON do AutoCAD dla graniastosłupa.
    
    :param length: Długość graniastosłupa
    :param width: Szerokość graniastosłupa
    :param height: Wysokość graniastosłupa
    :param position: Pozycja graniastosłupa (x, y, z)
    :param rotation_angle: Kąt obrotu w stopniach
    :return: Słownik z danymi JSON
    """
    data = {
        "prism": {
            "dimensions": {
                "length": length,
                "width": width,
                "height": height
            },
            "position": {
                "x": position[0],
                "y": position[1],
                "z": position[2]
            },
            "rotation": {
                "angle": rotation_angle
            }
        }
    }
    return data

# Przykład użycia
if __name__ == "__main__":
    # Generowanie danych dla graniastosłupa o wymiarach 10x5x3 w pozycji (0,0,0) i obrocie 45 stopni
    prism_data = generate_prism_data(10, 5, 3, (0, 0, 0), 45)
    
    import json
    with open('prism_data.json', 'w') as f:
        json.dump(prism_data, f, indent=4)
    
    print("Dane zapisane do prism_data.json")
