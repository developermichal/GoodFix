# GoodFix Agent

Uruchamianie z katalogu `E:\GoodFix`:

```powershell
docker compose build
docker compose up
```

Parametry Compose są w pliku `.env`. Możesz tam zmienić ścieżki, porty,
nazwę modelu, autosave, kontekst, podział GPU, offload KV-cache i pamięć.

Projekt nie wymaga Condy. Zależności usług są instalowane przez `pip` z plików
`agent/requirements.txt` oraz obrazu `model-server`; Dockerfile nie tworzy
środowiska Conda.

Plik GGUF ma około 30,25 GiB, a na uruchomienie modelu przewidziano około
40 GiB pamięci. Dostępne jest 44 GB VRAM, więc serwer używa obu GPU
(`CUDA_VISIBLE_DEVICES=0,1`, `tensor_split=1,1`) i pełnego offloadu warstw
(`N_GPU_LAYERS=-1`). KV-cache również jest kierowany do VRAM
(`OFFLOAD_KQV=1`), a `FLASH_ATTN=1` ogranicza zużycie pamięci. Domyślny
kontekst to 4096 tokenów, aby zostawić zapas pamięci.

Jeżeli chcesz uruchomić samą funkcję z `figury.py`, wykonaj ją wewnątrz
FreeCAD, ponieważ moduły `FreeCAD`, `Part` i `Mesh` są dostarczane przez
FreeCAD, a nie przez Condę.

UI: `http://localhost:5173`  
Agent API: `http://localhost:8001/docs`  
Model API: `http://localhost:8002/docs`  
Chroma: `http://localhost:8003`

Agent działa wyłącznie w katalogu zamontowanym jako `/workspace`. Każde wejście do katalogu tworzy albo odczytuje `.vader`, zapisuje strukturę i aktualizuje kontekst. Sesje są zapisywane w `.agent_sessions`, a autosave działa co 120 sekund.
