from flask import redirect, render_template, request as http_request, url_for, g

from . import applications_bp
from atst.domain.exceptions import AlreadyExistsError
from atst.domain.environments import Environments
from atst.domain.applications import Applications
from atst.domain.application_roles import ApplicationRoles
from atst.domain.audit_log import AuditLog
from atst.domain.common import Paginator
from atst.domain.environment_roles import EnvironmentRoles
from atst.forms.application import ApplicationForm, EditEnvironmentForm
from atst.forms.application_member import NewForm as NewMemberForm, UpdateMemberForm
from atst.forms.data import ENV_ROLE_NO_ACCESS as NO_ACCESS
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions
from atst.domain.permission_sets import PermissionSets
from atst.utils.flash import formatted_flash as flash
from atst.utils.localization import translate
from atst.jobs import send_mail


def get_environments_obj_for_app(application):
    environments_obj = []
    for env in application.environments:
        env_data = {
            "id": env.id,
            "name": env.name,
            "edit_form": EditEnvironmentForm(obj=env),
            "member_count": len(env.roles),
            "members": [env_role.application_role.user_name for env_role in env.roles],
        }
        environments_obj.append(env_data)

    return environments_obj


def get_members_data(application):
    members_data = []
    for member in application.members:
        permission_sets = {
            "perms_team_mgmt": bool(
                member.has_permission_set(PermissionSets.EDIT_APPLICATION_TEAM)
            ),
            "perms_env_mgmt": bool(
                member.has_permission_set(PermissionSets.EDIT_APPLICATION_ENVIRONMENTS)
            ),
            "perms_del_env": bool(
                member.has_permission_set(
                    PermissionSets.DELETE_APPLICATION_ENVIRONMENTS
                )
            ),
        }
        roles = EnvironmentRoles.get_for_application_member(member.id)
        environment_roles = [
            {
                "environment_id": str(role.environment.id),
                "environment_name": role.environment.name,
                "role": role.role,
            }
            for role in roles
        ]

        env_roles_form_data = []
        for env in application.environments:
            env_data = {
                "environment_id": str(env.id),
                "environment_name": env.name,
                "role": NO_ACCESS,
            }
            env_role = EnvironmentRoles.get_by_user_and_environment(
                member.user_id, env.id
            )
            if env_role:
                env_data["role"] = env_role.role

            env_roles_form_data.append(env_data)

        form = UpdateMemberForm(
            environment_roles=env_roles_form_data, **permission_sets
        )
        members_data.append(
            {
                "role_id": member.id,
                "user_name": member.user_name,
                "permission_sets": permission_sets,
                "environment_roles": environment_roles,
                "role_status": member.status.value,
                "form": form,
            }
        )

    return members_data


def get_new_member_form(application):
    env_roles = [
        {"environment_id": e.id, "environment_name": e.name}
        for e in application.environments
    ]

    return NewMemberForm(data={"environment_roles": env_roles})


def render_settings_page(application, **kwargs):
    environments_obj = get_environments_obj_for_app(application=application)
    new_env_form = EditEnvironmentForm()
    pagination_opts = Paginator.get_pagination_opts(http_request)
    audit_events = AuditLog.get_application_events(application, pagination_opts)
    new_member_form = get_new_member_form(application)
    members = get_members_data(application)

    if "application_form" not in kwargs:
        kwargs["application_form"] = ApplicationForm(
            name=application.name, description=application.description
        )

    return render_template(
        "portfolios/applications/settings.html",
        application=application,
        environments_obj=environments_obj,
        new_env_form=new_env_form,
        audit_events=audit_events,
        new_member_form=new_member_form,
        members=members,
        **kwargs,
    )


def send_application_invitation(invitee_email, inviter_name, token):
    body = render_template(
        "emails/application/invitation.txt", owner=inviter_name, token=token
    )
    send_mail.delay(
        [invitee_email],
        translate("email.application_invite", {"inviter_name": inviter_name}),
        body,
    )


def perm_sets_obj_to_list(perms_obj):
    perm_sets = []

    if perms_obj["perms_env_mgmt"]:
        perm_sets.append(PermissionSets.EDIT_APPLICATION_ENVIRONMENTS)

    if perms_obj["perms_team_mgmt"]:
        perm_sets.append(PermissionSets.EDIT_APPLICATION_TEAM)

    if perms_obj["perms_del_env"]:
        perm_sets.append(PermissionSets.DELETE_APPLICATION_ENVIRONMENTS)

    return perm_sets


@applications_bp.route("/applications/<application_id>/settings")
@user_can(Permissions.VIEW_APPLICATION, message="view application edit form")
def settings(application_id):
    application = Applications.get(application_id)

    return render_settings_page(
        application=application,
        active_toggler=http_request.args.get("active_toggler"),
        active_toggler_section=http_request.args.get("active_toggler_section"),
    )


@applications_bp.route("/environments/<environment_id>/edit", methods=["POST"])
@user_can(Permissions.EDIT_ENVIRONMENT, message="edit application environments")
def update_environment(environment_id):
    environment = Environments.get(environment_id)
    application = environment.application

    env_form = EditEnvironmentForm(obj=environment, formdata=http_request.form)

    if env_form.validate():
        Environments.update(environment=environment, name=env_form.name.data)

        flash("application_environments_updated")

        return redirect(
            url_for(
                "applications.settings",
                application_id=application.id,
                fragment="application-environments",
                _anchor="application-environments",
                active_toggler=environment.id,
                active_toggler_section="edit",
            )
        )
    else:
        return (
            render_settings_page(
                application=application,
                active_toggler=environment.id,
                active_toggler_section="edit",
            ),
            400,
        )


@applications_bp.route(
    "/applications/<application_id>/environments/new", methods=["POST"]
)
@user_can(Permissions.CREATE_ENVIRONMENT, message="create application environment")
def new_environment(application_id):
    application = Applications.get(application_id)
    env_form = EditEnvironmentForm(formdata=http_request.form)

    if env_form.validate():
        Environments.create(
            g.current_user, application=application, name=env_form.name.data
        )

        flash("environment_added", environment_name=env_form.data["name"])

        return redirect(
            url_for(
                "applications.settings",
                application_id=application.id,
                fragment="application-environments",
                _anchor="application-environments",
            )
        )
    else:
        return (render_settings_page(application=application), 400)


@applications_bp.route("/applications/<application_id>/edit", methods=["POST"])
@user_can(Permissions.EDIT_APPLICATION, message="update application")
def update(application_id):
    application = Applications.get(application_id)
    form = ApplicationForm(http_request.form)
    if form.validate():
        application_data = form.data
        Applications.update(application, application_data)

        return redirect(
            url_for(
                "applications.portfolio_applications",
                portfolio_id=application.portfolio_id,
            )
        )
    else:
        return render_settings_page(application=application, application_form=form)


@applications_bp.route("/applications/<application_id>/delete", methods=["POST"])
@user_can(Permissions.DELETE_APPLICATION, message="delete application")
def delete(application_id):
    application = Applications.get(application_id)
    Applications.delete(application)

    flash("application_deleted", application_name=application.name)

    return redirect(
        url_for(
            "applications.portfolio_applications", portfolio_id=application.portfolio_id
        )
    )


@applications_bp.route("/environments/<environment_id>/delete", methods=["POST"])
@user_can(Permissions.DELETE_ENVIRONMENT, message="delete environment")
def delete_environment(environment_id):
    environment = Environments.get(environment_id)
    Environments.delete(environment=environment, commit=True)

    flash("environment_deleted", environment_name=environment.name)

    return redirect(
        url_for(
            "applications.settings",
            application_id=environment.application_id,
            _anchor="application-environments",
            fragment="application-environments",
        )
    )


@applications_bp.route("/application/<application_id>/members/new", methods=["POST"])
@user_can(
    Permissions.CREATE_APPLICATION_MEMBER, message="create new application member"
)
def create_member(application_id):
    application = Applications.get(application_id)
    form = NewMemberForm(http_request.form)

    if form.validate():
        try:
            invite = Applications.invite(
                application=application,
                inviter=g.current_user,
                user_data=form.user_data.data,
                permission_sets_names=perm_sets_obj_to_list(form.permission_sets.data),
                environment_roles_data=form.environment_roles.data,
            )

            send_application_invitation(
                invitee_email=invite.email,
                inviter_name=g.current_user.full_name,
                token=invite.token,
            )

            flash("new_application_member", user_name=invite.user_name)

        except AlreadyExistsError:
            return render_template(
                "error.html", message="There was an error processing your request."
            )
    else:
        pass
        # TODO: flash error message

    return redirect(
        url_for(
            "applications.settings",
            application_id=application_id,
            fragment="application-members",
            _anchor="application-members",
        )
    )


@applications_bp.route(
    "/applications/<application_id>/members/<application_role_id>/delete",
    methods=["POST"],
)
@user_can(Permissions.DELETE_APPLICATION_MEMBER, message="remove application member")
def remove_member(application_id, application_role_id):
    application_role = ApplicationRoles.get_by_id(application_role_id)
    Applications.remove_member(application_role)

    flash(
        "application_member_removed",
        user_name=application_role.user_name,
        application_name=g.application.name,
    )

    return redirect(
        url_for(
            "applications.settings",
            _anchor="application-members",
            application_id=g.application.id,
            fragment="application-members",
        )
    )


@applications_bp.route(
    "/applications/<application_id>/members/<application_role_id>/update",
    methods=["POST"],
)
@user_can(Permissions.EDIT_APPLICATION_MEMBER, message="update application member")
def update_member(application_id, application_role_id):
    app_role = ApplicationRoles.get_by_id(application_role_id)
    form = UpdateMemberForm(http_request.form)

    if form.validate():
        perm_sets = {
            key: value for key, value in form.data.items() if key != "environment_roles"
        }
        new_perm_sets_names = perm_sets_obj_to_list(perm_sets)
        ApplicationRoles.update_permission_sets(app_role, new_perm_sets_names)

        for env_role in form.environment_roles:
            environment = Environments.get(env_role.environment_id.data)
            Environments.update_env_role(environment, app_role, env_role.data["role"])

        flash("application_member_updated", user_name=app_role.user_name)
    else:
        pass
        # TODO: flash error message

    return redirect(
        url_for(
            "applications.settings",
            application_id=application_id,
            fragment="application-members",
            _anchor="application-members",
        )
    )
