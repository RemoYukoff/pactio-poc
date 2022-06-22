import pytest
import os
from pact import Consumer, Like, Provider, Term, Format
from src.consumer import UserConsumer

PACT_MOCK_HOST = "localhost"
PACT_MOCK_PORT = 1234
PACT_DIR = os.path.realpath("./../pacts")


@pytest.fixture
def consumer() -> UserConsumer:
    return UserConsumer(f"http://{PACT_MOCK_HOST}:{PACT_MOCK_PORT}")


@pytest.fixture(scope="session")
def pact(request):
    """Setup a Pact Consumer, which provides the Provider mock service. This
    will generate and optionally publish Pacts to the Pact Broker"""
    pact = Consumer("UserServiceClient").has_pact_with(
        Provider("UserService"),
        host_name=PACT_MOCK_HOST,
        port=PACT_MOCK_PORT,
        pact_dir=PACT_DIR
    )

    pact.start_service()

    yield pact

    pact.stop_service()


def test_get_user_non_admin(pact, consumer):
    # Define the Matcher
    expected = {
        "name": "UserA",
        "id": Format().uuid,
        "created_on": Term(r"\d+-\d+-\d+T\d+:\d+:\d+", "2016-12-15T20:16:01"),
        "ip_address": Format().ip_address,
        "admin": False,
    }

    # Define the expected behaviour of the Provider. This determines how the
    # Pact mock provider will behave. In this case, we expect a body which is
    # "Like" the structure defined above.
    (
        pact.given("UserA exists and is not an administrator")
        .upon_receiving("a request for UserA")
        .with_request("get", "/users/UserA")
        .will_respond_with(200, body=Like(expected))
    )

    with pact:
        # Perform the actual request
        user = consumer.get_user("UserA")

        # In this case the mock Provider will have returned a valid response
        assert user.name == "UserA"

        # Make sure that all interactions defined occurred
        pact.verify()


def test_get_non_existing_user(pact, consumer):
    # Define the expected behaviour of the Provider. This determines how the
    # Pact mock provider will behave. In this case, we expect a 404
    (
        pact.given("UserA does not exist")
        .upon_receiving("a request for UserA")
        .with_request("get", "/users/UserA")
        .will_respond_with(404)
    )

    with pact:
        # Perform the actual request
        user = consumer.get_user("UserA")

        # In this case, the mock Provider will have returned a 404 so the
        # consumer will have returned None
        assert user is None

        # Make sure that all interactions defined occurred
        pact.verify()
