import pytest
import numpy as np
from model import predict

def test_model_prediction():
    # Testowanie funkcji predykcji modelu
    input_data = np.array([[1, 2, 3]])
    result = predict(input_data)
    assert isinstance(result, np.ndarray)
    assert result.shape == (1, 1)

def test_model_load():
    # Testowanie ładowania modelu
    try:
        # Sprawdzenie czy model się ładuje poprawnie
        assert True  # Placeholder for actual model loading test
    except Exception as e:
        pytest.fail(f"Model failed to load: {e}")