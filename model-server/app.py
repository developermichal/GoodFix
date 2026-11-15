import os
import subprocess

from llama_cpp.server.app import create_app
from llama_cpp.server.settings import Settings

settings = Settings(
    model=os.environ["MODEL_PATH"],
    n_gpu_layers=int(os.getenv("N_GPU_LAYERS", "-1")),
    tensor_split=[float(x) for x in os.getenv("TENSOR_SPLIT", "1,1").split(",")],
    split_mode=int(os.getenv("SPLIT_MODE", "0")),
    offload_kqv=os.getenv("OFFLOAD_KQV", "1") == "1",
    flash_attn=os.getenv("FLASH_ATTN", "1") == "1",
    n_ctx=int(os.getenv("N_CTX", "8192")),
)
expected_gb = float(os.getenv("MODEL_EXPECTED_MEMORY_GB", "40"))
configured_vram_gb = float(os.getenv("AVAILABLE_VRAM_GB", "0"))
gpu_memory: list[float] = []
try:
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
        check=True,
        capture_output=True,
        text=True,
    )
    gpu_memory = [float(line.strip()) / 1024 for line in result.stdout.splitlines() if line.strip()]
except (FileNotFoundError, subprocess.CalledProcessError):
    pass
available_vram_gb = sum(gpu_memory) if gpu_memory else configured_vram_gb
available_gb = 0.0
try:
    with open("/proc/meminfo", encoding="utf-8") as memory_info:
        available_kb = next(
            int(line.split()[1])
            for line in memory_info
            if line.startswith("MemAvailable:")
        )
    available_gb = available_kb / (1024**2)
except (FileNotFoundError, StopIteration):
    pass
print(
    f"Model wymaga około {expected_gb:.0f} GB pamięci runtime; "
    f"VRAM kart: {[round(value, 1) for value in gpu_memory]} GB "
    f"(suma: {available_vram_gb:.1f} GB); "
    f"dostępne MemAvailable VM: {available_gb:.1f} GB",
    flush=True,
)
app = create_app(settings=settings)
