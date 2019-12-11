from flask import (
    g,
    redirect,
    render_template,
    request as http_request,
    url_for,
    current_app as app,
    jsonify,
)

from .blueprint import task_orders_bp
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.exceptions import AlreadyExistsError, NoAccessError
from atst.domain.task_orders import TaskOrders
from atst.forms.task_order import TaskOrderForm, SignatureForm
from atst.models.permissions import Permissions
from atst.utils.flash import formatted_flash as flash


def render_task_orders_edit(
    template, portfolio_id=None, task_order_id=None, form=None, extra_args=None
):
    render_args = extra_args or {}

    render_args["contract_start"] = app.config.get("CONTRACT_START_DATE")
    render_args["contract_end"] = app.config.get("CONTRACT_END_DATE")

    if task_order_id:
        task_order = TaskOrders.get(task_order_id)
        portfolio_id = task_order.portfolio_id
        render_args["form"] = form or TaskOrderForm(obj=task_order)
        render_args["task_order_id"] = task_order_id
        render_args["task_order"] = task_order
    else:
        render_args["form"] = form or TaskOrderForm()

    render_args["cancel_save_url"] = url_for(
        "task_orders.cancel_edit",
        task_order_id=task_order_id,
        portfolio_id=portfolio_id,
        save=True,
    )
    render_args["cancel_discard_url"] = url_for(
        "task_orders.cancel_edit",
        task_order_id=task_order_id,
        portfolio_id=portfolio_id,
        save=False,
    )

    return render_template(template, **render_args)


def update_task_order(
    form_data, next_page, current_template, portfolio_id=None, task_order_id=None
):
    form = None
    if task_order_id:
        task_order = TaskOrders.get(task_order_id)
        form = TaskOrderForm(form_data, obj=task_order)
    else:
        form = TaskOrderForm(form_data)

    if form.validate():
        task_order = None
        if task_order_id:
            try:
                task_order = TaskOrders.update(task_order_id, **form.data)
                portfolio_id = task_order.portfolio_id
            except AlreadyExistsError:
                return (
                    render_task_orders_edit(
                        current_template, portfolio_id, task_order_id, form
                    ),
                    400,
                )
        else:
            try:
                task_order = TaskOrders.create(portfolio_id, **form.data)
            except AlreadyExistsError:
                return (
                    render_task_orders_edit(
                        current_template, portfolio_id, task_order_id, form
                    ),
                    400,
                )

        return redirect(url_for(next_page, task_order_id=task_order.id))
    else:
        return (
            render_task_orders_edit(
                current_template, portfolio_id, task_order_id, form
            ),
            400,
        )


@task_orders_bp.route("/task_orders/<portfolio_id>/upload_token")
@user_can(Permissions.CREATE_TASK_ORDER, message="edit task order form")
def upload_token(portfolio_id):
    (token, object_name) = app.csp.files.get_token()
    render_args = {"token": token, "objectName": object_name}

    return jsonify(render_args)


@task_orders_bp.route("/task_orders/<portfolio_id>/download_link")
@user_can(Permissions.VIEW_TASK_ORDER_DETAILS, message="view task order download link")
def download_link(portfolio_id):
    filename = http_request.args.get("filename")
    object_name = http_request.args.get("objectName")
    render_args = {
        "downloadLink": app.csp.files.generate_download_link(object_name, filename)
    }

    return jsonify(render_args)


@task_orders_bp.route("/task_orders/<task_order_id>/edit")
@user_can(Permissions.CREATE_TASK_ORDER, message="edit task order form")
def edit(task_order_id):
    task_order = TaskOrders.get(task_order_id)

    if not task_order.pdf:
        return redirect(
            url_for("task_orders.form_step_one_add_pdf", task_order_id=task_order_id)
        )
    elif not task_order.number:
        return redirect(
            url_for("task_orders.form_step_two_add_number", task_order_id=task_order_id)
        )
    elif not task_order.clins_are_completed:
        return redirect(
            url_for(
                "task_orders.form_step_three_add_clins", task_order_id=task_order_id
            )
        )
    elif task_order.is_completed:
        return redirect(
            url_for("task_orders.form_step_four_review", task_order_id=task_order_id)
        )
    else:
        return redirect(
            url_for("task_orders.form_step_one_add_pdf", task_order_id=task_order_id)
        )


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders/form/step_1")
@task_orders_bp.route("/task_orders/<task_order_id>/form/step_1")
@user_can(Permissions.CREATE_TASK_ORDER, message="view task order form")
def form_step_one_add_pdf(portfolio_id=None, task_order_id=None):
    return render_task_orders_edit(
        "task_orders/step_1.html",
        portfolio_id=portfolio_id,
        task_order_id=task_order_id,
    )


@task_orders_bp.route(
    "/portfolios/<portfolio_id>/task_orders/form/step-1", methods=["POST"]
)
@task_orders_bp.route("/task_orders/<task_order_id>/form/step_1", methods=["POST"])
@user_can(Permissions.CREATE_TASK_ORDER, message="update task order form")
def submit_form_step_one_add_pdf(portfolio_id=None, task_order_id=None):
    form_data = {**http_request.form}
    next_page = "task_orders.form_step_two_add_number"
    current_template = "task_orders/step_1.html"

    return update_task_order(
        form_data,
        next_page,
        current_template,
        portfolio_id=portfolio_id,
        task_order_id=task_order_id,
    )


@task_orders_bp.route(
    "/portfolios/<portfolio_id>/task_orders/form/cancel", methods=["POST"]
)
@task_orders_bp.route("/task_orders/<task_order_id>/form/cancel", methods=["POST"])
@user_can(Permissions.CREATE_TASK_ORDER, message="cancel task order form")
def cancel_edit(task_order_id=None, portfolio_id=None):
    # Either save the currently entered data, or delete the TO
    save = http_request.args.get("save", "True").lower() == "true"

    if save:
        form_data = {**http_request.form}
        form = None
        if task_order_id:
            task_order = TaskOrders.get(task_order_id)
            form = TaskOrderForm(form_data, obj=task_order)
        else:
            form = TaskOrderForm(form_data)

        if form.validate(flash_invalid=False):
            task_order = None
            if task_order_id:
                task_order = TaskOrders.update(task_order_id, **form.data)
            else:
                task_order = TaskOrders.create(portfolio_id, **form.data)
    elif not save and task_order_id:
        TaskOrders.delete(task_order_id)

    return redirect(
        url_for("task_orders.portfolio_funding", portfolio_id=g.portfolio.id)
    )


@task_orders_bp.route("/task_orders/<task_order_id>/form/step_2")
@user_can(Permissions.CREATE_TASK_ORDER, message="view task order form")
def form_step_two_add_number(task_order_id):
    return render_task_orders_edit(
        "task_orders/step_2.html", task_order_id=task_order_id
    )


@task_orders_bp.route("/task_orders/<task_order_id>/form/step_2", methods=["POST"])
@user_can(Permissions.CREATE_TASK_ORDER, message="update task order form")
def submit_form_step_two_add_number(task_order_id):
    form_data = {**http_request.form}
    next_page = "task_orders.form_step_three_add_clins"
    current_template = "task_orders/step_2.html"

    return update_task_order(
        form_data, next_page, current_template, task_order_id=task_order_id
    )


@task_orders_bp.route("/task_orders/<task_order_id>/form/step_3")
@user_can(Permissions.CREATE_TASK_ORDER, message="view task order form")
def form_step_three_add_clins(task_order_id):
    return render_task_orders_edit(
        "task_orders/step_3.html", task_order_id=task_order_id
    )


@task_orders_bp.route("/task_orders/<task_order_id>/form/step_3", methods=["POST"])
@user_can(Permissions.CREATE_TASK_ORDER, message="update task order form")
def submit_form_step_three_add_clins(task_order_id):
    form_data = {**http_request.form}
    next_page = "task_orders.form_step_four_review"
    current_template = "task_orders/step_3.html"

    return update_task_order(
        form_data, next_page, current_template, task_order_id=task_order_id
    )


@task_orders_bp.route("/task_orders/<task_order_id>/form/step_4")
@user_can(Permissions.CREATE_TASK_ORDER, message="view task order form")
def form_step_four_review(task_order_id):
    task_order = TaskOrders.get(task_order_id)

    extra_args = {
        "pdf_download_url": app.csp.files.generate_download_link(
            task_order.pdf.object_name, task_order.pdf.filename
        )
    }

    if task_order.is_completed == False:
        raise NoAccessError("task order form review")

    return render_task_orders_edit(
        "task_orders/step_4.html", task_order_id=task_order_id, extra_args=extra_args
    )


@task_orders_bp.route("/task_orders/<task_order_id>/form/step_5")
@user_can(Permissions.CREATE_TASK_ORDER, message="view task order form")
def form_step_five_confirm_signature(task_order_id):
    task_order = TaskOrders.get(task_order_id)

    if task_order.is_completed == False:
        raise NoAccessError("task order form signature")

    return render_task_orders_edit(
        "task_orders/step_5.html", task_order_id=task_order_id, form=SignatureForm()
    )


@task_orders_bp.route("/task_orders/<task_order_id>/submit", methods=["POST"])
@user_can(Permissions.CREATE_TASK_ORDER, "submit task order")
def submit_task_order(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    TaskOrders.sign(task_order=task_order, signer_dod_id=g.current_user.dod_id)

    flash("task_order_submitted", task_order=task_order)

    return redirect(
        url_for("task_orders.portfolio_funding", portfolio_id=task_order.portfolio_id)
    )
