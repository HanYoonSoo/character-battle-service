from __future__ import annotations


class ApplicationError(Exception):
    status_code = 400

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class BadRequestError(ApplicationError):
    status_code = 400


class UnauthorizedError(ApplicationError):
    status_code = 401


class NotFoundError(ApplicationError):
    status_code = 404


class ConflictError(ApplicationError):
    status_code = 409


class ExternalServiceError(ApplicationError):
    status_code = 502


class ServiceUnavailableError(ApplicationError):
    status_code = 503

