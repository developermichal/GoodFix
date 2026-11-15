FROM ghcr.io/ggml-org/llama.cpp:server-cuda-b9544

# The GGUF stays mounted read-only from the host instead of being copied into
# every image build.
EXPOSE 8000
ENTRYPOINT ["/app/llama-server"]
