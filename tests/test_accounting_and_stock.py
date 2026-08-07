from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from accounting.journal import validate_lines
from core.exceptions import InsufficientStockError, UnbalancedEntryError
from inventory.stock import StockService
from models import Base if False else Product
