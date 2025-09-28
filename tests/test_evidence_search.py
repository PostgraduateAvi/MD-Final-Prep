import pytest
from fastapi.testclient import TestClient

from server import app


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def find_record(results, record_id):
    for record in results:
        if record["id"] == record_id:
            return record
    raise AssertionError(f"Record {record_id} not found in results")


def test_search_returns_results(client):
    response = client.get("/api/search")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 3
    first = results[0]
    assert {"id", "title", "identifier", "viva_prompt"} <= first.keys()


def test_verification_switch_controls_identifier(client):
    params = {"q": "metabolic", "verify": "true"}
    response = client.get("/api/search", params=params)
    assert response.status_code == 200
    verified = find_record(response.json(), "metabolic-syndrome-2019")
    assert verified["identifier"]["type"] == "pmid"
    assert verified["doi"] is None
    assert verified["doi_error"] is True

    params["verify"] = "false"
    response = client.get("/api/search", params=params)
    assert response.status_code == 200
    bypassed = find_record(response.json(), "metabolic-syndrome-2019")
    assert bypassed["identifier"]["type"] == "doi"
    assert bypassed["doi"] == "10.5555/invalid-metabolic-cohort"
    assert bypassed["doi_error"] is False


def test_topic_filter_limits_results(client):
    response = client.get("/api/search", params={"topic": "telemedicine"})
    assert response.status_code == 200
    results = response.json()
    assert all("telemedicine" in record["topics"] for record in results)


def test_topics_endpoint_returns_counts(client):
    response = client.get("/api/topics")
    assert response.status_code == 200
    topics = response.json()
    assert any(topic["name"] == "cardiology" for topic in topics)
    cardiology = next(topic for topic in topics if topic["name"] == "cardiology")
    assert cardiology["count"] >= 2
