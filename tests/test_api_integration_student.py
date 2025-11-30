import sys
from pathlib import Path
import importlib
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import app as app_module 

@pytest.fixture
def client():
    importlib.reload(app_module)
    flask_app = app_module.app
    flask_app.config["TESTING"] = True

    with flask_app.test_client() as client:
        yield client


BASE_URL = "/todo/api/v1.0/tasks"


def test_get_all_tasks_returns_list(client):

    resp = client.get(BASE_URL)

    assert resp.status_code == 200
    data = resp.get_json()
    assert "tasks" in data
    assert isinstance(data["tasks"], list)
    assert len(data["tasks"]) > 0
    first = data["tasks"][0]
    for key in ("id", "title", "done"):
        assert key in first


def test_get_single_task_success(client):

    resp = client.get(f"{BASE_URL}/1")

    assert resp.status_code == 200
    data = resp.get_json()
    assert "task" in data
    assert data["task"]["id"] == 1


def test_get_single_task_not_found_returns_404(client):

    resp = client.get(f"{BASE_URL}/9999")

    assert resp.status_code == 404

    assert resp.is_json


def test_create_task_success(client):

    payload = {
        "title": "Write integration tests",
        "description": "Lab 2",
        "done": False,
    }

    resp = client.post(BASE_URL, json=payload)

    assert resp.status_code in (200, 201)
    data = resp.get_json()
    assert "task" in data
    task = data["task"]
    assert task["title"] == payload["title"]
    assert task["description"] == payload["description"]
    assert task["done"] is False


def test_create_task_without_title_returns_400(client):

    bad_payload = {"description": "no title here"}

    resp = client.post(BASE_URL, json=bad_payload)

    assert resp.status_code == 400


def test_update_task_sets_done_true(client):

    update_payload = {"done": True}

    resp = client.put(f"{BASE_URL}/1", json=update_payload)

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["task"]["done"] is True


def test_delete_task_then_404_on_get(client):

    delete_resp = client.delete(f"{BASE_URL}/1")

    assert delete_resp.status_code == 200
    delete_data = delete_resp.get_json()

    assert delete_data.get("result") in (True, 1)

    get_resp = client.get(f"{BASE_URL}/1")

    assert get_resp.status_code == 404
