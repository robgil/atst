from wtforms.fields import (
    SelectMultipleField,
    StringField,
    TextAreaField,
)
from wtforms.validators import Length, InputRequired
from wtforms.widgets import ListWidget, CheckboxInput

from .forms import BaseForm
from atst.utils.localization import translate

from .data import SERVICE_BRANCHES


class PortfolioForm(BaseForm):
    name = StringField(
        translate("forms.portfolio.name.label"),
        validators=[
            Length(
                min=4,
                max=100,
                message=translate("forms.portfolio.name.length_validation_message"),
            )
        ],
    )


class PortfolioCreationForm(BaseForm):
    name = StringField(
        translate("forms.portfolio.name.label"),
        validators=[
            Length(
                min=4,
                max=100,
                message=translate("forms.portfolio.name.length_validation_message"),
            )
        ],
    )
    description = TextAreaField(translate("forms.portfolio.description.label"),)
    defense_component = SelectMultipleField(
        choices=SERVICE_BRANCHES,
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
        validators=[
            InputRequired(message="You must select at least one defense component.")
        ],
    )
