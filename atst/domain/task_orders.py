import datetime
from sqlalchemy.exc import IntegrityError

from atst.database import db
from atst.models.clin import CLIN
from atst.models.task_order import TaskOrder, SORT_ORDERING
from . import BaseDomainClass
from .exceptions import AlreadyExistsError


class TaskOrders(BaseDomainClass):
    model = TaskOrder
    resource_name = "task_order"

    @classmethod
    def create(cls, portfolio_id, number, clins, pdf):
        try:
            task_order = TaskOrder(portfolio_id=portfolio_id, number=number, pdf=pdf)
            db.session.add(task_order)
            db.session.commit()
        except IntegrityError:
            raise AlreadyExistsError("task_order")

        TaskOrders.create_clins(task_order.id, clins)

        return task_order

    @classmethod
    def update(cls, task_order_id, number, clins, pdf):
        task_order = TaskOrders.get(task_order_id)
        task_order.pdf = pdf

        if len(clins) > 0:
            for clin in task_order.clins:
                db.session.delete(clin)

            TaskOrders.create_clins(task_order_id, clins)

        if number != task_order.number:
            task_order.number = number
            db.session.add(task_order)

        try:
            db.session.commit()
        except IntegrityError:
            raise AlreadyExistsError("task_order")

        return task_order

    @classmethod
    def sign(cls, task_order, signer_dod_id):
        task_order.signer_dod_id = signer_dod_id
        task_order.signed_at = datetime.datetime.now()

        db.session.add(task_order)
        db.session.commit()

        return task_order

    @classmethod
    def create_clins(cls, task_order_id, clin_list):
        for clin_data in clin_list:
            clin = CLIN(
                task_order_id=task_order_id,
                number=clin_data["number"],
                start_date=clin_data["start_date"],
                end_date=clin_data["end_date"],
                total_amount=clin_data["total_amount"],
                obligated_amount=clin_data["obligated_amount"],
                jedi_clin_type=clin_data["jedi_clin_type"],
            )
            db.session.add(clin)
            db.session.commit()

    @classmethod
    def sort(cls, task_orders: [TaskOrder]) -> [TaskOrder]:
        # Sorts a list of task orders on two keys: status (primary) and time_created (secondary)
        by_time_created = sorted(task_orders, key=lambda to: to.time_created)
        by_status = sorted(by_time_created, key=lambda to: SORT_ORDERING.get(to.status))
        return by_status

    @classmethod
    def delete(cls, task_order_id):
        task_order = TaskOrders.get(task_order_id)
        db.session.delete(task_order)
        db.session.commit()
