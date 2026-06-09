from datetime import datetime, timedelta, timezone
from time import sleep


def test_create_and_verify_ongoing_contest(client, headers):
    endTime = datetime.now(tz=timezone.utc) + timedelta(hours=1)
    startTime = datetime.now(tz=timezone.utc) + timedelta(seconds=10)

    response = client.post(
        "/contests/create",
        json={
            "name": "Test contest by pytest",
            "endTime": endTime.isoformat(),
            "startTime": startTime.isoformat(),
            "problem_ids": [1, 2],
        },
        headers=headers,
    )
    assert response.status_code == 200
    created_contest = response.json()

    response = client.get("/contests/all_upcoming_contests")
    assert response.status_code == 200
    upcoming_contests = response.json()
    assert len(upcoming_contests) > 0 and upcoming_contests[-1]["id"] == created_contest["id"]
    print("start time is ", startTime.isoformat())
    print("Current time is ", datetime.now(tz=timezone.utc).isoformat())
    sleep(12)
    response = client.get("/contests/ongoing_contests")
    assert response.status_code == 200
    ongoing_contests = response.json()
    assert len(ongoing_contests) > 0 and ongoing_contests[-1]["id"] == created_contest["id"]

    response = client.post(
        "/contests/contest_info", headers=headers, json={"contest_slug": created_contest["slug"]}
    )
    assert response.status_code == 200
    created_contest_info = response.json()
    for problem in created_contest_info["problems"]:
        assert problem["id"] in [1, 2]
