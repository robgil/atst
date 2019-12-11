from flask import url_for
import pytest

from tests.factories import (
    random_future_date,
    random_past_date,
    ApplicationFactory,
    PortfolioFactory,
    TaskOrderFactory,
    UserFactory,
)
from atst.utils.localization import translate
from atst.domain.portfolios import Portfolios, PortfolioDeletionApplicationsExistError
from atst.domain.portfolios.query import PortfoliosQuery


def test_new_portfolio(client, user_session):
    user = UserFactory.create()
    user_session(user)

    response = client.get(url_for("portfolios.new_portfolio_step_1"))

    assert response.status_code == 200


def test_create_portfolio_success(client, user_session):
    user = UserFactory.create()
    user_session(user)

    original_portfolio_count = len(PortfoliosQuery.get_all())

    response = client.post(
        url_for("portfolios.create_portfolio"),
        data={
            "name": "My project name",
            "description": "My project description",
            "defense_component": "army",
        },
    )

    assert response.status_code == 302
    assert len(PortfoliosQuery.get_all()) == original_portfolio_count + 1

    new_portfolio = Portfolios.for_user(user=user)[-1]

    assert (
        url_for("applications.portfolio_applications", portfolio_id=new_portfolio.id)
        in response.location
    )
    assert new_portfolio.owner == user


def test_create_portfolio_failure(client, user_session):
    user = UserFactory.create()
    user_session(user)

    original_portfolio_count = len(PortfoliosQuery.get_all())

    response = client.post(
        url_for("portfolios.create_portfolio"),
        data={"name": "My project name", "description": "My project description"},
    )

    assert response.status_code == 400
    assert len(PortfoliosQuery.get_all()) == original_portfolio_count


def test_portfolio_reports(client, user_session):
    portfolio = PortfolioFactory.create(
        applications=[
            {"name": "application1", "environments": [{"name": "application1 prod"}]}
        ]
    )
    task_order = TaskOrderFactory.create(number="42", portfolio=portfolio)
    user_session(portfolio.owner)
    response = client.get(url_for("portfolios.reports", portfolio_id=portfolio.id))
    assert response.status_code == 200
    assert portfolio.name in response.data.decode()


def test_portfolio_reports_with_mock_portfolio(client, user_session):
    portfolio = PortfolioFactory.create(name="A-Wing")
    user_session(portfolio.owner)
    response = client.get(url_for("portfolios.reports", portfolio_id=portfolio.id))
    assert response.status_code == 200
    assert portfolio.name in response.data.decode()


def test_delete_portfolio_success(client, user_session):
    portfolio = PortfolioFactory.create()
    owner = portfolio.owner
    user_session(owner)

    assert len(Portfolios.for_user(user=owner)) == 1

    response = client.post(
        url_for("portfolios.delete_portfolio", portfolio_id=portfolio.id)
    )

    assert response.status_code == 302
    assert url_for("atst.home") in response.location
    assert len(Portfolios.for_user(user=owner)) == 0


def test_delete_portfolio_failure(no_debug_client, user_session):
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)
    owner = portfolio.owner
    user_session(owner)

    assert len(Portfolios.for_user(user=owner)) == 1

    response = no_debug_client.post(
        url_for("portfolios.delete_portfolio", portfolio_id=portfolio.id)
    )

    assert response.status_code == 500
    assert len(Portfolios.for_user(user=owner)) == 1
