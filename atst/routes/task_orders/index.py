from flask import g, render_template, url_for, redirect

from .blueprint import task_orders_bp
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.portfolios import Portfolios
from atst.domain.task_orders import TaskOrders
from atst.forms.task_order import SignatureForm
from atst.models import Permissions


@task_orders_bp.route("/task_orders/<task_order_id>/review")
@user_can(Permissions.VIEW_TASK_ORDER_DETAILS, message="review task order details")
def review_task_order(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    if task_order.is_draft:
        return redirect(url_for("task_orders.edit", task_order_id=task_order.id))
    else:
        signature_form = SignatureForm()
        return render_template(
            "task_orders/review.html",
            task_order=task_order,
            signature_form=signature_form,
        )


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders")
@user_can(Permissions.VIEW_PORTFOLIO_FUNDING, message="view portfolio funding")
def portfolio_funding(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_orders = TaskOrders.sort_by_status(portfolio.task_orders)
    # TODO: Get expended amount from the CSP
    return render_template("task_orders/index.html", task_orders=task_orders)
