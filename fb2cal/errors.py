"""Typed errors raised by the Facebook extraction pipeline."""


class FacebookError(Exception):
    """Base class for expected, user-facing fb2cal failures."""


class ConfigurationError(FacebookError):
    """The supplied configuration is missing or invalid."""


class CookieFileError(FacebookError):
    """The explicit cookie/session file cannot be loaded safely."""


class AuthenticationError(FacebookError):
    """Facebook rejected the supplied authentication state."""


class SessionExpiredError(AuthenticationError):
    """The session is no longer authenticated."""


class FacebookCheckpointError(AuthenticationError):
    """Facebook requires a checkpoint or additional verification."""


class TokenExtractionError(FacebookError):
    """The birthday page did not contain a usable ``fb_dtsg`` token."""


class GraphQLQueryError(FacebookError):
    """The birthday GraphQL request failed."""


class PersistedQueryError(GraphQLQueryError):
    """Facebook no longer recognises the persisted birthday query."""


class GraphQLSchemaError(FacebookError):
    """Facebook returned JSON whose birthday schema is not understood."""
