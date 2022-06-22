import pytest

from pact import Verifier

# For the purposes of this example, the Flask provider will be started up as part
# of run_pytest.sh when running the tests. Alternatives could be, for example
# running a Docker container with a database of test data configured.
# This is the "real" provider to verify against.
PROVIDER_HOST = "localhost"
PROVIDER_PORT = 5001
PROVIDER_URL = f"http://{PROVIDER_HOST}:{PROVIDER_PORT}"


def test_user_service_provider_against_pact():
    verifier = Verifier(provider="UserService", provider_base_url=PROVIDER_URL)

    # If the verification of an interaction fails then the output
    # result will be != 0, and so the test will FAIL.
    output, _ = verifier.verify_pacts(
        "../pacts/userserviceclient-userservice.json",
        provider_states_setup_url="{}/_pact/provider_states".format(
            PROVIDER_URL),
    )

    assert output == 0
