import pytest
from datetime import date, timedelta
from decimal import Decimal

from atst.domain.exceptions import AlreadyExistsError
from atst.domain.task_orders import TaskOrders
from atst.models import Attachment, TaskOrder
from tests.factories import TaskOrderFactory, CLINFactory, PortfolioFactory


def test_task_order_sorting():
    """
    Task orders should be listed first by status, and then by time_created.
    """

    today = date.today()
    yesterday = today - timedelta(days=1)
    future = today + timedelta(days=100)

    task_orders = [
        # Draft
        TaskOrderFactory.create(pdf=None),
        TaskOrderFactory.create(pdf=None),
        TaskOrderFactory.create(pdf=None),
        # Active
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=future)],
        ),
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=future)],
        ),
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=future)],
        ),
        # Upcoming
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=future, end_date=future)],
        ),
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=future, end_date=future)],
        ),
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
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=yesterday)],
        ),
        # Unsigned
        TaskOrderFactory.create(
            clins=[CLINFactory.create(start_date=today, end_date=today)]
        ),
        TaskOrderFactory.create(
            clins=[CLINFactory.create(start_date=today, end_date=today)]
        ),
        TaskOrderFactory.create(
            clins=[CLINFactory.create(start_date=today, end_date=today)]
        ),
    ]

    assert TaskOrders.sort(task_orders) == task_orders


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


def test_create_enforces_unique_number():
    portfolio = PortfolioFactory.create()
    number = "1234567890123"
    assert TaskOrders.create(portfolio.id, number, [], None)
    with pytest.raises(AlreadyExistsError):
        TaskOrders.create(portfolio.id, number, [], None)
    assert len(portfolio.task_orders) == 1


def test_update_enforces_unique_number():
    original_number = '1234567890123'
    task_order = TaskOrderFactory.create(number=original_number)

    dupe_number = '0987654321098'
    dupe_task_order = TaskOrderFactory.create(number=dupe_number)

    with pytest.raises(AlreadyExistsError):
        TaskOrders.update(dupe_task_order.id, original_number, [], None)

    assert TaskOrders.get(dupe_task_order.id)
