from dataclasses import dataclass

from jakarta.inject import Singleton
from micronaut.context.annotation import EachProperty
from micronaut.core.async_.publisher import Publishers
from micronaut.http import HttpRequest
from micronaut.security.authentication import Authentication
from micronaut.security.token.reader import TokenReader
from micronaut.security.token.validator import TokenValidator
from micronaut.serde.annotation import Serdeable
from org.reactivestreams import Publisher


@Serdeable
@EachProperty("api-keys")
@dataclass
class ApiKeyConfiguration:
    name: str
    key: str


@Singleton
class ApiKeyTokenReader(TokenReader):
    def findToken(self, request: HttpRequest):
        return request.getHeaders().findFirst("X-API-KEY")


@Singleton
class ApiKeyTokenValidator(TokenValidator):
    def __init__(self, api_keys: list[ApiKeyConfiguration]):
        self.names = {configuration.key: configuration.name for configuration in api_keys}

    def validateToken(self, token: str, request) -> Publisher:
        name = self.names.get(token)
        if name is None:
            return Publishers.empty()
        return Publishers.just(Authentication.build(name))
