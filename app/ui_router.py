from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any


@dataclass(frozen=True)
class Screen:
    key: str
    title: str
    factory: Callable[..., Any]


class UIRouter:
    def __init__(self):
        self._screens: dict[str, Screen] = {}
        self.current: str | None = None

    def register(self, key: str, title: str, factory: Callable[..., Any]):
        if not key or key in self._screens:
            raise ValueError("واجهة غير صالحة أو مكررة")
        self._screens[key] = Screen(key, title, factory)

    def register_defaults(self, factories: dict[str, Callable[..., Any]]):
        titles = {
            'dashboard':'الرئيسية', 'pos':'الكاشير والمبيعات', 'purchases':'المشتريات',
            'inventory':'المخزون', 'customers':'العملاء والديون', 'suppliers':'الموردون',
            'returns':'المرتجعات', 'cash':'الصندوق', 'accounting':'المحاسبة',
            'reports':'التقارير', 'settings':'الإعدادات', 'audit':'الأرشيف والمراجعة'
        }
        for key, factory in factories.items():
            if key in titles and key not in self._screens:
                self.register(key, titles[key], factory)

    def open(self, key: str, **kwargs):
        screen = self._screens[key]
        self.current = key
        return screen.factory(**kwargs)

    def menu(self):
        return [{'key': s.key, 'title': s.title} for s in self._screens.values()]
