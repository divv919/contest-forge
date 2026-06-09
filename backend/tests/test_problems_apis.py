import pytest


def test_get_problems_list(client):
    response = client.get("/problems/all")
    assert response.status_code == 200
    value = response.json()
    assert value is not None
    assert isinstance(value, list)
    assert len(value) > 0


@pytest.mark.parametrize("slug", ["two_sum", "three_sum"])
def test_get_specific_problem(client, slug):
    response = client.get(f"/problems/{slug}")
    assert response.status_code == 200
    value = response.json()
    assert value is not None
    assert isinstance(value, dict)
    assert value["slug"] == slug


def test_get_wrong_problem(client):
    response = client.get("/problems/wrong_slug")
    assert response.status_code == 404
