import requests

BASE_URL = "http://127.0.0.1:5000/todo/api/v1.0/tasks"


def _create_task(title="Новый год", description="Купить подарки"):
    payload = {
        "title": title,
        "description": description,
    }
    resp = requests.post(BASE_URL, json=payload)
    assert resp.status_code == 201
    return resp.json()["task"]


def test_get_all_tasks_returns_list_e2e():

    resp = requests.get(BASE_URL)

    assert resp.status_code == 200

    data = resp.json()
    assert "tasks" in data

    tasks = data["tasks"]
    assert isinstance(tasks, list)
    assert len(tasks) >= 1 

    for task in tasks:
        assert "id" in task
        assert "title" in task
        assert "description" in task
        assert "done" in task


def test_create_task_and_get_by_id_e2e():

    created = _create_task(
        title="Позвонить врачу",
        description="Записаться на приём на следующую неделю",
    )
    task_id = created["id"]

    get_resp = requests.get(f"{BASE_URL}/{task_id}")

    assert get_resp.status_code == 200
    data = get_resp.json()
    assert "task" in data
    task = data["task"]

    assert task["id"] == task_id
    assert task["title"] == "Позвонить врачу"
    assert task["description"] == "Записаться на приём на следующую неделю"
    assert task["done"] is False


def test_update_task_mark_done_e2e():

    created = _create_task(
        title="E2E: mark done",
        description="should become done=True",
    )
    task_id = created["id"]

    update_payload = {"done": True}
    update_resp = requests.put(f"{BASE_URL}/{task_id}", json=update_payload)

    assert update_resp.status_code == 200
    updated = update_resp.json()["task"]
    assert updated["id"] == task_id
    assert updated["done"] is True

    get_resp = requests.get(f"{BASE_URL}/{task_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["task"]["done"] is True


def test_delete_task_and_then_404_on_get_e2e():

    created = _create_task(title="E2E: to be deleted")
    task_id = created["id"]

    delete_resp = requests.delete(f"{BASE_URL}/{task_id}")

    assert delete_resp.status_code in (200, 204)
    delete_body = delete_resp.json()

    assert delete_body.get("result", True) is True

    get_resp = requests.get(f"{BASE_URL}/{task_id}")
    assert get_resp.status_code == 404

    err = get_resp.json()
    assert "error" in err


def test_get_nonexistent_task_returns_404_e2e():

    nonexistent_id = 99999

    resp = requests.get(f"{BASE_URL}/{nonexistent_id}")

    assert resp.status_code == 404
    body = resp.json()
    assert body.get("error") == "Not found"


def test_create_task_without_title_returns_400_e2e():

    bad_payload = {"description": "missing title field"}

    resp = requests.post(BASE_URL, json=bad_payload)

    assert resp.status_code == 400