"""
Pytest configuration and fixtures for AI Calling Agent tests.
"""
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import get_settings
from app.core.database import Base, get_async_session
from app.main import app


# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    settings = get_settings()
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        echo=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    TestSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def override_get_async_session(test_session):
    """Override database session dependency."""
    async def _override_get_async_session():
        yield test_session
    
    app.dependency_overrides[get_async_session] = _override_get_async_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_async_session) -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_twilio_request():
    """Mock Twilio webhook request data."""
    return {
        "From": "+1234567890",
        "CallSid": "test-call-sid-123",
        "To": "+1987654321",
        "CallStatus": "in-progress"
    }


@pytest.fixture
def mock_salesforce_lead():
    """Mock Salesforce lead data."""
    return {
        "Id": "00Q123456789ABC",
        "Name": "John Doe",
        "Phone": "+1234567890",
        "Email": "john.doe@example.com",
        "Company": "Test Company",
        "LeadSource": "AI_Calling_Agent",
        "Status": "Open - Not Contacted"
    }