import pytest
import redis
from agent.app.redis_context_manager import RedisContextManager

def test_redis_context_manager_init():
    # Testowanie inicjalizacji menedżera kontekstu Redis
    manager = RedisContextManager()
    assert manager is not None
    
    # Sprawdzenie połączenia z Redis
    try:
        manager.redis_client.ping()
        assert True
    except redis.ConnectionError:
        pytest.fail("Nie można połączyć się z Redisem")

def test_redis_context_operations():
    # Testowanie operacji na kontekście
    manager = RedisContextManager()
    
    # Testowanie zapisu i odczytu danych
    key = 'test_key'
    value = 'test_value'
    
    manager.set(key, value)
    retrieved_value = manager.get(key)
    
    assert retrieved_value == value
    
    # Testowanie usuwania danych
    manager.delete(key)
    assert manager.get(key) is None