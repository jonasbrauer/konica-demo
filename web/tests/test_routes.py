import random

import mock
import pytest

from app import app


@pytest.fixture
def mock_computations(monkeypatch):
    mocked_computations = {
        "id123": mock.MagicMock(),
        "id345": mock.MagicMock(),
    }
    monkeypatch.setattr("app.ACTIVE_COMPUTATIONS", mocked_computations)
    return mocked_computations


@pytest.fixture
def mock_render_template():
    with mock.patch("app.render_template") as mocked_render:
        yield mocked_render


def test_home_get(mock_render_template, mock_computations):
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
    mock_render_template.assert_called_once()
    mock_call = mock_render_template.call_args_list.pop()
    assert mock_call.args == ("home.html",)
    assert list(mock_call.kwargs.get("computations")) == list(mock_computations.values())


@mock.patch("app.base64.b64encode")
def test_status(mock_base64, mock_computations, mock_render_template):
    c_id = random.choice(list(mock_computations.keys()))
    mock_base64.return_value = "some_bytes_as_b_64".encode()

    with app.test_client() as client:
        response = client.get(f"/{c_id}")
        assert response._status_code == 200

    mock_render_template.assert_called_once()
    mock_render_template.assert_called_with(
        "status.html", computation=mock_computations[c_id], image_bytes="some_bytes_as_b_64"
    )


def test_status_404():
    with app.test_client() as client:
        response = client.get("/non_existant_id}")
        assert response._status_code == 404
