from collections import defaultdict
import json
import os
import sys


class MockReportingProvider:
    with open(
        os.path.join(sys.path[0], "atst/domain/csp/fixture_spend_data.json")
    ) as json_file:
        FIXTURE_SPEND_DATA = json.load(json_file)

    @classmethod
    def get_portfolio_monthly_spending(cls, portfolio):
        """
        returns an array of application and enironment spending for the portfolio
        Applications and their nested environments are sorted in alphabetical order by name
        [
            {
                name
                this_month
                last_month
                total
                environments [
                    {
                        name
                        this_month
                        last_month
                        total
                    }
                ]
            }
        ]
        """
        if portfolio.name in FIXTURE_SPEND_DATA:
            applications = FIXTURE_SPEND_DATA["application"]
            return sorted(
                [
                    cls._get_application_monthly_totals(application)
                    for application in applications
                ],
                key=lambda app: app["name"],
            )
        return []

    @classmethod
    def _get_environment_monthly_totals(cls, environment):
        """
            create a dictionary that represents spending totals for an environment e.g. 
            {
                name
                this_month
                last_month
                total
            }
            """
        return {
            "name": environment["name"],
            "this_month": sum(environment["spending"]["this_month"].values()),
            "last_month": sum(environment["spending"]["last_month"].values()),
            "total": sum(environment["spending"]["total"].values()),
        }

    @classmethod
    def _get_application_monthly_totals(cls, application):
        """
        create a dictionary that represents spending totals for an environment e.g. 
            {
                name
                this_month
                last_month
                total
                environments: [
                    environment
                ]
            }
        """
        environments = sorted(
            [
                cls._get_environment_monthly_totals(env)
                for env in application["environments"]
            ],
            key=lambda env: env["name"],
        )

        application["this_month"] = sum(env["this_month"] for env in environments)
        application["last_month"] = sum(env["last_month"] for env in environments)
        application["total"] = sum(env["total"] for env in environments)
        application["environments"] = environments

        return application

    @classmethod
    def get_spending_by_JEDI_clin(cls, portfolio):
        """
        returns an array of spending per JEDI CLIN for a portfolio's applications
        [
            {
                name
                invoiced
                estimated
            }
        ]
        """
        return []

    @classmethod
    def _get_environment_JEDI_clin_totals(cls, environment):
        spend_dict = defaultdict(lambda: defaultdict(lambda: 0))
        for time_period, clin_spending in environment["spending"].items():
            for clin, spend in clin_spending.items():
                if time_period == "last_month" or time_period == "total":
                    spend_dict[clin]["invoiced"] += spend
                else:
                    spend_dict[clin]["estimated"] += spend
        return spend_dict

    @classmethod
    def _get_application_JEDI_clin_totals(cls, application):
        """
        create a dictionary that represents spending totals for an environment e.g. 
        {
            JEDI_CLIN_1:400
            JEDI_CLIN_2:500
        }
        """
        pass

