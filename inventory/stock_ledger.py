from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from core.exceptions import ValidationError


QTY = Decimal("0.000001")
MONEY = Decimal("0.01")


def dec(value, quantum=QTY):
    return Decimal(str(value or 0)).quantize(quantum, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class StockLayer:
    quantity: Decimal
    unit_cost: Decimal


@dataclass(frozen=True)
class StockIssue:
    quantity: Decimal
    cost: Decimal


class StockLedger:
    def __init__(self, layers: list[StockLayer] | None = None):
        self.layers = list(layers or [])

    @property
    def quantity(self) -> Decimal:
        return dec(sum((x.quantity for x in self.layers), Decimal("0")))

    @property
    def value(self) -> Decimal:
        return dec(sum((x.quantity * x.unit_cost for x in self.layers), Decimal("0")), MONEY)

    def receive(self, quantity, unit_cost) -> None:
        quantity = dec(quantity)
        unit_cost = dec(unit_cost, MONEY)
        if quantity <= 0 or unit_cost < 0:
            raise ValidationError("كمية أو تكلفة الاستلام غير صالحة.")
        self.layers.append(StockLayer(quantity, unit_cost))

    def fifo_issue(self, quantity) -> StockIssue:
        remaining = dec(quantity)
        if remaining <= 0:
            raise ValidationError("كمية الصرف يجب أن تكون أكبر من صفر.")
        if remaining > self.quantity:
            raise ValidationError("الرصيد المخزني غير كافٍ.")
        cost = Decimal("0")
        new_layers: list[StockLayer] = []
        for layer in self.layers:
            if remaining <= 0:
                new_layers.append(layer)
                continue
            used = min(layer.quantity, remaining)
            cost += used * layer.unit_cost
            left = layer.quantity - used
            remaining -= used
            if left > 0:
                new_layers.append(StockLayer(left, layer.unit_cost))
        self.layers = new_layers
        return StockIssue(dec(quantity), dec(cost, MONEY))

    def weighted_average_cost(self) -> Decimal:
        if self.quantity <= 0:
            return Decimal("0.00")
        return dec(self.value / self.quantity, MONEY)

    def average_issue(self, quantity) -> StockIssue:
        quantity = dec(quantity)
        if quantity <= 0 or quantity > self.quantity:
            raise ValidationError("كمية الصرف غير صالحة.")
        unit_cost = self.weighted_average_cost()
        remaining = quantity
        new_layers: list[StockLayer] = []
        for layer in self.layers:
            if remaining <= 0:
                new_layers.append(layer)
                continue
            used = min(layer.quantity, remaining)
            left = layer.quantity - used
            remaining -= used
            if left > 0:
                new_layers.append(StockLayer(left, layer.unit_cost))
        self.layers = new_layers
        return StockIssue(quantity, dec(quantity * unit_cost, MONEY))
