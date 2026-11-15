# Dlaczego GoodFix używa teraz podejścia z `chappie`

## Co zostało zmienione

GoodFix korzysta teraz z bezpośredniego serwera `llama.cpp`, tak jak projekt
`chappie`. Model GGUF jest ładowany przez `llama-server`, a nie przez
`llama-cpp-python` uruchamiane z własnego pliku Python.

W [docker-compose.yml](./docker-compose.yml) model ma teraz następujące
ważne parametry:

```yaml
--n-gpu-layers all
--tensor-split 0.5,0.5
--split-mode layer
--ctx-size 32768
--parallel 1
```

Wartości można zmienić w [.env](./.env). Model nadal znajduje się na hoście
w katalogu `E:/GoodFix/model` i jest montowany do kontenera tylko do odczytu.

## Jak było wcześniej w GoodFix

Pierwsza wersja korzystała z własnego [model-server/app.py](./model-server/app.py)
oraz biblioteki `llama-cpp-python`. Python tworzył obiekt ustawień modelu i
przekazywał go do serwera.

To podejście było wygodne do napisania, ale przy tym konkretnym modelu pojawiły
się problemy:

- część parametrów podziału GPU zachowywała się inaczej niż oczekiwaliśmy,
- tryb podziału był łatwy do pomylenia z inną wartością liczbową,
- próba załadowania modelu kończyła się próbą alokacji około 30 GiB na GPU 0,
- serwer nie uruchamiał endpointu API, więc agent zwracał błąd połączenia.

To nie oznacza, że Python jest zły. Oznacza tylko, że w tym miejscu dodawał
warstwę pośrednią, która nie była nam potrzebna.

## Co robi `chappie` inaczej

`chappie` uruchamia gotowy binarny serwer `llama-server` z obrazu:

```dockerfile
FROM ghcr.io/ggml-org/llama.cpp:server-cuda-b9544
```

W jego konfiguracji model główny używa obu GPU i jednego slotu rozmowy. Dzięki
temu pamięć przeznaczona na KV cache nie jest mnożona przez kilka równoległych
sesji.

W GoodFix zastosowaliśmy ten sam wzorzec, ale zachowaliśmy montowanie modelu z
hosta. `chappie` kopiuje model do obrazu podczas budowy, natomiast GoodFix
montuje go jako wolumen. Dla pliku wielkości około 32,5 GB montowanie jest
praktyczniejsze: nie tworzy kolejnej kopii modelu w warstwach obrazu i pozwala
zmienić plik bez przebudowywania całego obrazu.

## Dlaczego większy kontekst

Wcześniej GoodFix miał:

```env
N_CTX=4096
```

Agent wysłał żądanie o długości około 5030 tokenów, więc model odrzucił je
komunikatem o przekroczeniu kontekstu.

Teraz ustawiliśmy:

```env
N_CTX=32768
```

Pozwala to pomieścić kontekst projektu, zawartość `.vader`, wyniki RAG,
historię sesji i bieżące pytanie. Cena jest taka, że większy KV cache zajmuje
więcej VRAM. Dlatego pozostaje `--parallel 1`: jedna rozmowa dostaje cały
przydzielony kontekst, zamiast dzielić pamięć między cztery sloty.

## Dlaczego to podejście jest lepsze tutaj

Nie dlatego, że jest zawsze lepsze. Jest lepsze dla GoodFix, ponieważ:

1. używa tego samego sprawdzonego backendu co `chappie`,
2. bezpośrednio wystawia kompatybilne API `/v1/chat/completions`,
3. pozwala `llama.cpp` samodzielnie wykryć oba GPU,
4. ogranicza liczbę warstw pośrednich między agentem a modelem,
5. daje większy kontekst potrzebny do pracy z plikami projektu,
6. utrzymuje model poza obrazem Dockera, więc nie kopiuje 32,5 GB przy buildzie.

## Czego nie kopiowaliśmy bez potrzeby

`chappie` ma również drugi model `vision_model` — Qwen2.5-VL z projektorem
`mmproj`. Ten model służy do obrazów i kamer. GoodFix obecnie nie ma funkcji
analizy obrazu, więc nie dodaliśmy go tylko dlatego, że istnieje w drugim
projekcie. Dodanie go zwiększyłoby zużycie VRAM i skomplikowałoby uruchamianie,
ale nie poprawiłoby tekstowego agenta programistycznego.

## Stan decyzji

Decyzja brzmi: używamy architektury serwera z `chappie`, ale zachowujemy
specyfikę GoodFix — bezpośredni dostęp do workspace, `.vader`, RAG, sesje i
montowanie modelu z `E:/GoodFix/model`.

To jest świadome połączenie dwóch podejść, a nie kopiowanie całego projektu
`chappie`.
