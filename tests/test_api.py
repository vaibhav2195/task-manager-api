from fastapi.testclient import TestClient


def test_health_check_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data
    assert "version" in data
    assert data["database_status"] == "healthy"


def test_metrics_endpoint(client: TestClient):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text


def test_create_task_endpoint(client: TestClient):
    payload = {
        "title": "API Created Task",
        "description": "Created via HTTP POST",
        "priority": "high",
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["priority"] == payload["priority"]
    assert data["completed"] is False
    assert "id" in data


def test_create_task_invalid_title(client: TestClient):
    payload = {"title": "", "description": "Invalid empty title"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422 or response.status_code == 400


def test_list_tasks_endpoint(client: TestClient):
    client.post("/tasks", json={"title": "Task A", "priority": "low"})
    client.post("/tasks", json={"title": "Task B", "priority": "high"})

    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2


def test_get_task_by_id_endpoint(client: TestClient):
    res = client.post("/tasks", json={"title": "Single Task"})
    task_id = res.json()["id"]

    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == task_id


def test_get_task_not_found(client: TestClient):
    response = client.get("/tasks/non-existent-id-12345")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_task_endpoint(client: TestClient):
    res = client.post("/tasks", json={"title": "Before Update"})
    task_id = res.json()["id"]

    update_payload = {"title": "After Update", "completed": True}
    put_res = client.put(f"/tasks/{task_id}", json=update_payload)
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["title"] == "After Update"
    assert data["completed"] is True


def test_update_task_not_found(client: TestClient):
    put_res = client.put("/tasks/non-existent-id", json={"title": "Ghost"})
    assert put_res.status_code == 404


def test_delete_task_endpoint(client: TestClient):
    res = client.post("/tasks", json={"title": "To Delete"})
    task_id = res.json()["id"]

    del_res = client.delete(f"/tasks/{task_id}")
    assert del_res.status_code == 204

    # Verify deletion
    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 404


def test_delete_task_not_found(client: TestClient):
    del_res = client.delete("/tasks/non-existent-id")
    assert del_res.status_code == 404
