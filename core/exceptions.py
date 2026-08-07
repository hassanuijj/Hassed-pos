class HassedERPError(Exception):
    pass


class ValidationError(HassedERPError):
    pass


class AccountingError(HassedERPError):
    pass


class UnbalancedEntryError(AccountingError):
    pass


class PermissionDeniedError(HassedERPError):
    pass


class InvalidStatusError(HassedERPError):
    pass


class InsufficientStockError(HassedERPError):
    pass


class NotFoundError(HassedERPError):
    pass


class CurrencyError(HassedERPError):
    pass


class FiscalPeriodClosedError(HassedERPError):
    pass
