from itertools import groupby
import pendulum
from decimal import Decimal
from collections import OrderedDict


class ReportingInterface:
    def monthly_totals_for_environment(environment):
        """Return the monthly totals for the specified environment.

        Data should be in the format of a dictionary with the month as the key
        and the spend in that month as the value. For example:

            { "01/2018": 79.85, "02/2018": 86.54 }

        """
        raise NotImplementedError()


class MockEnvironment:
    def __init__(self, id_, env_name):
        self.id = id_
        self.name = env_name


class MockApplication:
    def __init__(self, application_name, envs):
        def make_env(name):
            return MockEnvironment("{}_{}".format(application_name, name), name)

        self.name = application_name
        self.environments = [make_env(env_name) for env_name in envs]


def generate_sample_dates(_max=8):
    current = pendulum.now()
    sample_dates = []
    for _i in range(_max):
        sample_dates.append(current.strftime("%m/%Y"))
        current = current.subtract(months=1)

    reversed(sample_dates)
    return sample_dates


class MockReportingProvider(ReportingInterface):
    MOCK_PERCENT_INVOICED_EXPENDED_FUNDS = 0.60
    MOCK_PERCENT_ESTIMATED_EXPENDED_FUNDS = 0.15

    FIXTURE_MONTHS = generate_sample_dates()

    MONTHLY_SPEND_BY_ENVIRONMENT = {
        "LC04_Integ": {
            FIXTURE_MONTHS[7]: 284,
            FIXTURE_MONTHS[6]: 1210,
            FIXTURE_MONTHS[5]: 1430,
            FIXTURE_MONTHS[4]: 1366,
            FIXTURE_MONTHS[3]: 1169,
            FIXTURE_MONTHS[2]: 991,
            FIXTURE_MONTHS[1]: 978,
            FIXTURE_MONTHS[0]: 737,
        },
        "LC04_PreProd": {
            FIXTURE_MONTHS[7]: 812,
            FIXTURE_MONTHS[6]: 1389,
            FIXTURE_MONTHS[5]: 1425,
            FIXTURE_MONTHS[4]: 1306,
            FIXTURE_MONTHS[3]: 1112,
            FIXTURE_MONTHS[2]: 936,
            FIXTURE_MONTHS[1]: 921,
            FIXTURE_MONTHS[0]: 694,
        },
        "LC04_Prod": {
            FIXTURE_MONTHS[7]: 1742,
            FIXTURE_MONTHS[6]: 1716,
            FIXTURE_MONTHS[5]: 1866,
            FIXTURE_MONTHS[4]: 1809,
            FIXTURE_MONTHS[3]: 1839,
            FIXTURE_MONTHS[2]: 1633,
            FIXTURE_MONTHS[1]: 1654,
            FIXTURE_MONTHS[0]: 1103,
        },
        "SF18_Integ": {
            FIXTURE_MONTHS[5]: 1498,
            FIXTURE_MONTHS[4]: 1400,
            FIXTURE_MONTHS[3]: 1394,
            FIXTURE_MONTHS[2]: 1171,
            FIXTURE_MONTHS[1]: 1200,
            FIXTURE_MONTHS[0]: 963,
        },
        "SF18_PreProd": {
            FIXTURE_MONTHS[5]: 1780,
            FIXTURE_MONTHS[4]: 1667,
            FIXTURE_MONTHS[3]: 1703,
            FIXTURE_MONTHS[2]: 1474,
            FIXTURE_MONTHS[1]: 1441,
            FIXTURE_MONTHS[0]: 933,
        },
        "SF18_Prod": {
            FIXTURE_MONTHS[5]: 1686,
            FIXTURE_MONTHS[4]: 1779,
            FIXTURE_MONTHS[3]: 1792,
            FIXTURE_MONTHS[2]: 1570,
            FIXTURE_MONTHS[1]: 1539,
            FIXTURE_MONTHS[0]: 986,
        },
        "Canton_Prod": {
            FIXTURE_MONTHS[4]: 28699,
            FIXTURE_MONTHS[3]: 26766,
            FIXTURE_MONTHS[2]: 22619,
            FIXTURE_MONTHS[1]: 24090,
            FIXTURE_MONTHS[0]: 16719,
        },
        "BD04_Integ": {},
        "BD04_PreProd": {
            FIXTURE_MONTHS[7]: 7019,
            FIXTURE_MONTHS[6]: 3004,
            FIXTURE_MONTHS[5]: 2691,
            FIXTURE_MONTHS[4]: 2901,
            FIXTURE_MONTHS[3]: 3463,
            FIXTURE_MONTHS[2]: 3314,
            FIXTURE_MONTHS[1]: 3432,
            FIXTURE_MONTHS[0]: 723,
        },
        "SCV18_Dev": {FIXTURE_MONTHS[1]: 9797},
        "Crown_CR Portal Dev": {
            FIXTURE_MONTHS[6]: 208,
            FIXTURE_MONTHS[5]: 457,
            FIXTURE_MONTHS[4]: 671,
            FIXTURE_MONTHS[3]: 136,
            FIXTURE_MONTHS[2]: 1524,
            FIXTURE_MONTHS[1]: 2077,
            FIXTURE_MONTHS[0]: 1858,
        },
        "Crown_CR Staging": {
            FIXTURE_MONTHS[6]: 208,
            FIXTURE_MONTHS[5]: 457,
            FIXTURE_MONTHS[4]: 671,
            FIXTURE_MONTHS[3]: 136,
            FIXTURE_MONTHS[2]: 1524,
            FIXTURE_MONTHS[1]: 2077,
            FIXTURE_MONTHS[0]: 1858,
        },
        "Crown_CR Portal Test 1": {
            FIXTURE_MONTHS[2]: 806,
            FIXTURE_MONTHS[1]: 1966,
            FIXTURE_MONTHS[0]: 2597,
        },
        "Crown_Jewels Prod": {
            FIXTURE_MONTHS[2]: 806,
            FIXTURE_MONTHS[1]: 1966,
            FIXTURE_MONTHS[0]: 2597,
        },
        "Crown_Jewels Dev": {
            FIXTURE_MONTHS[6]: 145,
            FIXTURE_MONTHS[5]: 719,
            FIXTURE_MONTHS[4]: 1243,
            FIXTURE_MONTHS[3]: 2214,
            FIXTURE_MONTHS[2]: 2959,
            FIXTURE_MONTHS[1]: 4151,
            FIXTURE_MONTHS[0]: 4260,
        },
        "NP02_Integ": {FIXTURE_MONTHS[1]: 284, FIXTURE_MONTHS[0]: 1210},
        "NP02_PreProd": {FIXTURE_MONTHS[1]: 812, FIXTURE_MONTHS[0]: 1389},
        "NP02_Prod": {FIXTURE_MONTHS[1]: 3742, FIXTURE_MONTHS[0]: 4716},
        "FM_Integ": {FIXTURE_MONTHS[1]: 1498},
        "FM_Prod": {FIXTURE_MONTHS[0]: 5686},
    }

    REPORT_FIXTURE_MAP = {
        "A-Wing": {
            "applications": [
                MockApplication("LC04", ["Integ", "PreProd", "Prod"]),
                MockApplication("SF18", ["Integ", "PreProd", "Prod"]),
                MockApplication("Canton", ["Prod"]),
                MockApplication("BD04", ["Integ", "PreProd"]),
                MockApplication("SCV18", ["Dev"]),
                MockApplication(
                    "Crown",
                    [
                        "CR Portal Dev",
                        "CR Staging",
                        "CR Portal Test 1",
                        "Jewels Prod",
                        "Jewels Dev",
                    ],
                ),
            ],
            "budget": 500_000,
        },
        "B-Wing": {
            "applications": [
                MockApplication("NP02", ["Integ", "PreProd", "Prod"]),
                MockApplication("FM", ["Integ", "Prod"]),
            ],
            "budget": 70000,
        },
    }

    def _rollup_application_totals(self, data):
        application_totals = {}
        for application, environments in data.items():
            application_spend = [
                (month, spend)
                for env in environments.values()
                if env
                for month, spend in env.items()
            ]
            application_totals[application] = {
                month: sum([spend[1] for spend in spends])
                for month, spends in groupby(sorted(application_spend), lambda x: x[0])
            }

        return application_totals

    def _rollup_portfolio_totals(self, application_totals):
        monthly_spend = [
            (month, spend)
            for application in application_totals.values()
            for month, spend in application.items()
        ]
        portfolio_totals = {}
        for month, spends in groupby(sorted(monthly_spend), lambda m: m[0]):
            portfolio_totals[month] = sum([spend[1] for spend in spends])

        return portfolio_totals

    def monthly_totals_for_environment(self, environment_id):
        """Return the monthly totals for the specified environment.

        Data should be in the format of a dictionary with the month as the key
        and the spend in that month as the value. For example:

            { "01/2018": 79.85, "02/2018": 86.54 }

        """
        environment_monthly_totals = self.MONTHLY_SPEND_BY_ENVIRONMENT.get(
            environment_id, {}
        ).copy()

        environment_monthly_totals["total_spend_to_date"] = sum(
            monthly_total for monthly_total in environment_monthly_totals.values()
        )
        return environment_monthly_totals

    def monthly_totals(self, portfolio):
        """Return month totals rolled up by environment, application, and portfolio.

        Data should returned with three top level keys, "portfolio", "applications",
        and "environments".
        The "applications" key will have budget data per month for each application,
        The "environments" key will have budget data for each environment.
        The "portfolio" key will be total monthly spending for the portfolio.
        For example:

            {
                "environments": { "X-Wing": { "Prod": { "01/2018": 75.42 } } },
                "applications": { "X-Wing": { "01/2018": 75.42 } },
                "portfolio": { "01/2018": 75.42 },
            }

        """
        applications = portfolio.applications
        if portfolio.name in self.REPORT_FIXTURE_MAP:
            applications = self.REPORT_FIXTURE_MAP[portfolio.name]["applications"]
        environments = {
            application.name: {
                env.name: self.monthly_totals_for_environment(env.id)
                for env in application.environments
            }
            for application in applications
        }

        application_totals = self._rollup_application_totals(environments)
        portfolio_totals = self._rollup_portfolio_totals(application_totals)

        return {
            "environments": environments,
            "applications": application_totals,
            "portfolio": portfolio_totals,
        }

    def get_obligated_funds_by_JEDI_clin(self, portfolio):
        """
        Returns a dictionary of obligated funds and spending per JEDI CLIN
        {
            JEDI_CLIN: {
                obligated_funds,
                expended_funds
            }
        }
        """
        if portfolio.name in self.REPORT_FIXTURE_MAP:
            return_dict = {}
            for jedi_clin, clins in groupby(
                portfolio.active_clins, lambda clin: clin.jedi_clin_type
            ):
                obligated_funds = sum(clin.obligated_amount for clin in clins)
                return_dict[jedi_clin.value] = {
                    "obligated_funds": obligated_funds,
                    "expended_funds": (
                        obligated_funds
                        * Decimal(self.MOCK_PERCENT_INVOICED_EXPENDED_FUNDS)
                    ),
                    "estimated_expended_funds": (
                        obligated_funds
                        * Decimal(self.MOCK_PERCENT_ESTIMATED_EXPENDED_FUNDS)
                    ),
                }
            return OrderedDict(
                # 0 index for dict item, -1 for last digit of 4 digit CLIN, e.g. 0001
                sorted(return_dict.items(), key=lambda clin: clin[0][-1])
            )
        return {}

    def get_expired_task_orders(self, portfolio):
        def sorted_task_orders(to_list):
            return sorted(to_list, key=lambda to: to["number"])

        def sorted_clins(clin_list):
            return sorted(clin_list, key=lambda clin: clin["number"])

        def serialize_clin(clin):
            return {
                "number": clin.number,
                "jedi_clin_type": clin.jedi_clin_type,
                "period_of_performance": {
                    "start_date": clin.start_date,
                    "end_date": clin.end_date,
                },
                "total_value": clin.total_amount,
                "total_obligated_funds": clin.obligated_amount,
                "expended_funds": (
                    clin.obligated_amount
                    * Decimal(self.MOCK_PERCENT_INVOICED_EXPENDED_FUNDS)
                ),
            }

        return sorted_task_orders(
            [
                {
                    "id": task_order.id,
                    "number": task_order.number,
                    "clins": sorted_clins(
                        [serialize_clin(clin) for clin in task_order.clins]
                    ),
                }
                for task_order in portfolio.task_orders
                if task_order.is_expired
            ]
        )
