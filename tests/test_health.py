def test_health_endpoint():

    from app import create_app

    app = create_app(testing=True)

    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "UP"
