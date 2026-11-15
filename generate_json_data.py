import json
import random

def generate_json_data(min_size=10, max_size=100, num_items=10):
    """
    Generuje dane w formacie JSON z elementami o rozmiarach w określonym zakresie.
    
    :param min_size: Minimalny dozwolony rozmiar
    :param max_size: Maksymalny dozwolony rozmiar
    :param num_items: Liczba generowanych elementów
    :return: Lista słowników z danymi
    """
    data = []
    for i in range(num_items):
        # Generowanie losowego rozmiaru w zakresie
        size = random.randint(min_size, max_size)
        item = {
            "id": i + 1,
            "size": size
        }
        data.append(item)
    
    return data


def save_to_json(data, filename="model_data.json"):
    """
    Zapisuje dane do pliku JSON.
    
    :param data: Lista słowników z danymi
    :param filename: Nazwa pliku do zapisu
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Dane zapisano do pliku: {filename}")


if __name__ == "__main__":
    # Generowanie danych
    generated_data = generate_json_data(min_size=10, max_size=100, num_items=10)
    
    # Zapis do pliku JSON
    save_to_json(generated_data)
