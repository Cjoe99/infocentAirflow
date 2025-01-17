from _typeshed import Incomplete

class CredentialsParser:
    client_id: Incomplete
    client_secret: Incomplete
    access_token: Incomplete
    def __init__(
        self, client_id: Incomplete | None = None, client_secret: Incomplete | None = None, access_token: Incomplete | None = None
    ) -> None: ...
    environment: Incomplete
    def parse_client_credentials(self) -> None: ...
    merchant_id: Incomplete
    def parse_access_token(self) -> None: ...
    def get_environment(self, credential): ...
    def get_merchant_id(self, credential): ...
