from io.swagger.v3.oas.annotations.enums import SecuritySchemeIn, SecuritySchemeType
from io.swagger.v3.oas.annotations.info import Info
from io.swagger.v3.oas.annotations import OpenAPIDefinition
from io.swagger.v3.oas.annotations.security import SecurityScheme


@OpenAPIDefinition(info=Info(title="FIDE ratings", version="1.0", description="FIDE rating lists stored per month."))
@SecurityScheme(
    name="apiKey",
    type=SecuritySchemeType.APIKEY,
    in_=SecuritySchemeIn.HEADER,
    paramName="X-API-KEY",
    description="API key sent in the X-API-KEY header. Required to import ratings.",
)
class ApiDocumentation:
    pass
