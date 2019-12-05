from flask import current_app


class Reports:
    @classmethod
    def monthly_spending(cls, portfolio):
        return current_app.csp.reports.get_portfolio_monthly_spending(portfolio)

    @classmethod
    def expired_task_orders(cls, portfolio):
        return current_app.csp.reports.get_expired_task_orders(portfolio)

    @classmethod
    def obligated_funds_by_JEDI_clin(cls, portfolio):
        return current_app.csp.reports.get_spending_by_JEDI_clin(portfolio)
