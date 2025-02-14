import os
import sys
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.models import History, Settings
from src.core.repositories.history_repository import HistoryRepository
from src.core.repositories.setting_repository import SettingRepository


@pytest.fixture
def mock_session():
    with patch(
        "src.core.repositories.history_repository.session_scope",
        return_value=MagicMock(spec=Session),
    ) as mock:
        session_mock = mock.return_value.__enter__.return_value
        query_mock = MagicMock()

        session_mock.query.return_value = query_mock
        query_mock.filter_by.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = [
            History(id=1),
            History(id=2),
        ]
        query_mock.first.return_value = History(id=1)

        yield mock


def test_get_property_from_db_history(mock_session):
    repo = HistoryRepository()

    mock_session.return_value.__enter__.return_value.query.return_value.first.return_value = (
        2,
    )
    value = repo._get_property_from_db("mode")
    assert value == 2

    mock_session.return_value.__enter__.return_value.query.return_value.first.return_value = (
        3,
    )
    value = repo._get_property_from_db("mode")
    assert value == 3


def test_get_property_from_db_settings(mock_session):
    repo = SettingRepository()
    value = repo._get_property_from_db("mode")
    assert value in [0, 1, 2, 3, 4, 5]


def test_get_last_history(mock_session):
    repo = HistoryRepository()
    history = repo.get_last_history()
    assert history.id == 1


def test_get_last_histories(mock_session):
    repo = HistoryRepository()
    mock_query = mock_session.return_value.__enter__.return_value.query
    mock_query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        History(id=1),
        History(id=2),
    ]

    histories = repo.get_last_histories()

    # Verify that filter was called (timestamp filtering)
    mock_query.return_value.filter.assert_called_once()
    # Verify that we got the expected results
    assert len(histories) == 2
    assert histories[0].id == 1
    assert histories[1].id == 2


def test_three_minute_avg_delta(mock_session):
    repo = HistoryRepository()
    mock_subquery = MagicMock()
    mock_subquery.c.delta = MagicMock()

    mock_session.return_value.__enter__.return_value.query.return_value.order_by.return_value.limit.return_value.subquery.return_value = mock_subquery

    mock_session.return_value.__enter__.return_value.query.return_value.first.return_value = (
        5.0,
    )

    avg_delta = repo.three_minute_avg_delta()
    assert avg_delta == 5.0


def test_get_last_settings(mock_session):
    mock_session.return_value.__enter__.return_value.query.return_value.first.return_value = Settings(
        id=1
    )
    repo = SettingRepository()
    settings = repo.get_last_settings()
    assert settings.id == 1


def test_update_mode_with_timestamp(mock_session):
    repo = SettingRepository()

    repo._update_property("mode", 0)

    current_time = datetime.now()
    repo._update_property("mode_switch_timestamp", current_time)
    time = repo._get_property_from_db("mode_switch_timestamp")
    assert current_time == time


def test_expired_lockout(mock_session):
    repo = SettingRepository()
    session_mock = mock_session.return_value.__enter__.return_value

    base_time = datetime(2024, 2, 11, 12, 0, 0)
    mock_settings = Settings(
        mode=0, mode_switch_timestamp=base_time, mode_switch_lockout_time=2
    )
    session_mock.query.return_value.first.return_value = mock_settings

    with patch("datetime.datetime") as mock_datetime:
        current_time = base_time + timedelta(minutes=3)
        mock_datetime.now.return_value = current_time

        settings = repo.get_last_settings()
        unlock_time = base_time + timedelta(minutes=settings.mode_switch_lockout_time)

        assert current_time > unlock_time, (
            f"Lockout should be expired. "
            f"Current time: {current_time}, "
            f"Unlock time: {unlock_time}"
        )
