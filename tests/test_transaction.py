from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from core.transaction import transaction


def test_transaction_commits():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("create table t (value integer)"))

    with Session(engine) as session:
        with transaction(session):
            session.execute(text("insert into t(value) values (7)"))

        assert session.execute(text("select value from t")).scalar_one() == 7


def test_transaction_rolls_back():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("create table t (value integer)"))

    with Session(engine) as session:
        with pytest.raises(RuntimeError):
            with transaction(session):
                session.execute(text("insert into t(value) values (9)"))
                raise RuntimeError("boom")

        assert session.execute(text("select count(*) from t")).scalar_one() == 0


def test_nested_transaction_does_not_commit_early():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("create table t (value integer)"))

    with Session(engine) as session:
        with transaction(session):
            session.execute(text("insert into t(value) values (1)"))
            with transaction(session):
                session.execute(text("insert into t(value) values (2)"))
            raise RuntimeError("outer failure")

        
    with Session(engine) as check:
        assert check.execute(text("select count(*) from t")).scalar_one() == 0
