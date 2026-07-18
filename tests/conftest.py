from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app import database, main


@pytest.fixture
def client(tmp_path) -> Generator[TestClient, None, None]:
    test_engine = database.create_engine_for_url(f"sqlite:///{tmp_path / 'patients.db'}")
    database.SessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    main.engine = test_engine
    database.Base.metadata.create_all(test_engine)
    with TestClient(main.create_app()) as test_client:
        yield test_client
    test_engine.dispose()
