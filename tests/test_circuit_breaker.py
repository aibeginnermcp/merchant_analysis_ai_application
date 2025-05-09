"""断路器测试模块"""
import pytest
import asyncio
import time
from services.api_gateway.core.circuit_breaker import CircuitBreaker, CircuitState

pytestmark = pytest.mark.asyncio

async def test_circuit_breaker_initial_state():
    """测试断路器初始状态"""
    breaker = CircuitBreaker()
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0
    assert breaker.is_closed is True
    assert breaker.is_open is False
    assert breaker.is_half_open is False

async def test_circuit_breaker_success():
    """测试断路器成功请求"""
    breaker = CircuitBreaker()
    
    async with breaker():
        # 模拟成功请求
        pass
        
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0

async def test_circuit_breaker_failure():
    """测试断路器失败请求"""
    breaker = CircuitBreaker(failure_threshold=2)
    
    # 第一次失败
    with pytest.raises(Exception):
        async with breaker():
            raise Exception("Request failed")
            
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 1
    
    # 第二次失败，触发断路器打开
    with pytest.raises(Exception):
        async with breaker():
            raise Exception("Request failed")
            
    assert breaker.state == CircuitState.OPEN
    assert breaker.failure_count == 2

async def test_circuit_breaker_open_state():
    """测试断路器打开状态"""
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout=1
    )
    
    # 触发断路器打开
    with pytest.raises(Exception):
        async with breaker():
            raise Exception("Request failed")
            
    assert breaker.state == CircuitState.OPEN
    
    # 在恢复超时之前尝试请求
    with pytest.raises(Exception) as exc_info:
        async with breaker():
            pass
            
    assert "Circuit breaker is OPEN" in str(exc_info.value)
    
    # 等待恢复超时
    await asyncio.sleep(1)
    
    # 断路器应该进入半开状态
    async with breaker():
        pass
        
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0

async def test_circuit_breaker_half_open_state():
    """测试断路器半开状态"""
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout=1
    )
    
    # 触发断路器打开
    with pytest.raises(Exception):
        async with breaker():
            raise Exception("Request failed")
            
    assert breaker.state == CircuitState.OPEN
    
    # 等待恢复超时
    await asyncio.sleep(1)
    
    # 第一个请求应该被允许（半开状态）
    async with breaker():
        pass
        
    assert breaker.state == CircuitState.CLOSED
    
    # 如果在半开状态下失败，应该立即回到打开状态
    with pytest.raises(Exception):
        async with breaker():
            raise Exception("Request failed")
            
    assert breaker.state == CircuitState.OPEN

async def test_circuit_breaker_concurrent_requests():
    """测试断路器并发请求"""
    breaker = CircuitBreaker(failure_threshold=2)
    
    async def make_request(should_fail: bool):
        try:
            async with breaker():
                if should_fail:
                    raise Exception("Request failed")
        except Exception:
            pass
            
    # 并发发送多个请求
    await asyncio.gather(
        make_request(True),
        make_request(True),
        make_request(False)
    )
    
    assert breaker.state == CircuitState.OPEN
    assert breaker.failure_count == 2

async def test_circuit_breaker_recovery():
    """测试断路器恢复"""
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout=1
    )
    
    # 触发断路器打开
    with pytest.raises(Exception):
        async with breaker():
            raise Exception("Request failed")
            
    assert breaker.state == CircuitState.OPEN
    
    # 等待恢复超时
    await asyncio.sleep(1)
    
    # 成功请求应该重置断路器状态
    async with breaker():
        pass
        
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0

async def test_circuit_breaker_custom_settings():
    """测试断路器自定义设置"""
    breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=2,
        retry_timeout=1
    )
    
    # 验证自定义设置
    assert breaker.failure_threshold == 3
    assert breaker.recovery_timeout == 2
    assert breaker.retry_timeout == 1
    
    # 测试失败阈值
    for _ in range(2):
        with pytest.raises(Exception):
            async with breaker():
                raise Exception("Request failed")
                
    assert breaker.state == CircuitState.CLOSED
    
    # 第三次失败应该触发断路器
    with pytest.raises(Exception):
        async with breaker():
            raise Exception("Request failed")
            
    assert breaker.state == CircuitState.OPEN 