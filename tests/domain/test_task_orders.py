import pytest
from datetime import date, timedelta
from decimal import Decimal

from atst.domain.task_orders import TaskOrders
from atst.models import Attachment
from atst.models.task_order import TaskOrder, SORT_ORDERING, Status
from tests.factories import TaskOrderFactory, CLINFactory, PortfolioFactory


def test_create_adds_clins():
    portfolio = PortfolioFactory.create()
    clins = [
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
    ]
    task_order = TaskOrders.create(
        portfolio_id=portfolio.id,
        number="0123456789",
        clins=clins,
        pdf={"filename": "sample.pdf", "object_name": "1234567"},
    )
    assert len(task_order.clins) == 2


def test_update_adds_clins():
    task_order = TaskOrderFactory.create(number="1231231234")
    to_number = task_order.number
    clins = [
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
    ]
    task_order = TaskOrders.create(
        portfolio_id=task_order.portfolio_id,
        number="0000000000",
        clins=clins,
        pdf={"filename": "sample.pdf", "object_name": "1234567"},
    )
    assert task_order.number != to_number
    assert len(task_order.clins) == 2


def test_update_does_not_duplicate_clins():
    task_order = TaskOrderFactory.create(
        number="3453453456", create_clins=[{"number": "123"}, {"number": "456"}]
    )
    clins = [
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "123",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "111",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
    ]
    task_order = TaskOrders.update(
        task_order_id=task_order.id,
        number="0000000000",
        clins=clins,
        pdf={"filename": "sample.pdf", "object_name": "1234567"},
    )
    assert len(task_order.clins) == 2
    for clin in task_order.clins:
        assert clin.number != "456"


def test_delete_task_order_with_clins(session):
    task_order = TaskOrderFactory.create(
        create_clins=[{"number": 1}, {"number": 2}, {"number": 3}]
    )
    TaskOrders.delete(task_order.id)

    assert not session.query(
        session.query(TaskOrder).filter_by(id=task_order.id).exists()
    ).scalar()


def test_task_order_sort_by_status():
    today = date.today()
    yesterday = today - timedelta(days=1)
    future = today + timedelta(days=100)

    initial_to_list = [
        # Draft
        TaskOrderFactory.create(pdf=None),
        TaskOrderFactory.create(pdf=None),
        TaskOrderFactory.create(pdf=None),
        # Active
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=future)],
        ),
        # Upcoming
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=future, end_date=future)],
        ),
        # Expired
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=yesterday)],
        ),
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=yesterday)],
        ),
        # Unsigned
        TaskOrderFactory.create(
            clins=[CLINFactory.create(start_date=today, end_date=today)]
        ),
    ]

    sorted_by_status = TaskOrders.sort_by_status(initial_to_list)
    assert len(sorted_by_status[Status.DRAFT]) == 3
    assert len(sorted_by_status[Status.ACTIVE]) == 1
    assert len(sorted_by_status[Status.UPCOMING]) == 1
    assert len(sorted_by_status[Status.EXPIRED]) == 2
    assert len(sorted_by_status[Status.UNSIGNED]) == 1
    assert list(sorted_by_status.keys()) == SORT_ORDERING
