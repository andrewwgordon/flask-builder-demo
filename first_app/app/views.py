
import calendar
import datetime
import logging
import random
from flask import redirect
from flask_appbuilder import ModelView
from flask_appbuilder.fieldwidgets import Select2Widget
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.views import MasterDetailView
from flask_appbuilder.charts.views import (
    DirectByChartView,
    DirectChartView,
    GroupByChartView,
)
from flask_babel import lazy_gettext as _
from flask_appbuilder.actions import action
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_appbuilder.widgets import ListBlock, ShowBlockWidget
from flask_appbuilder.models.group import aggregate_avg, aggregate_sum
from . import appbuilder, db
from .models import Contact, ContactGroup, Gender
from .models import Benefit, Department, Employee, EmployeeHistory, Function
from .models import Product, ProductType
from .models import Country, CountryStats, PoliticalType

def fill_gender():
    try:
        db.session.add(Gender(name="Male"))
        db.session.add(Gender(name="Female"))
        db.session.commit()
    except Exception:
        db.session.rollback()

def department_query():
    return db.session.query(Department)

log = logging.getLogger(__name__)


def fill_data():
    countries = [
        "Portugal",
        "Germany",
        "Spain",
        "France",
        "USA",
        "China",
        "Russia",
        "Japan",
    ]
    politicals = ["Democratic", "Authorative"]
    for country in countries:
        c = Country(name=country)
        try:
            db.session.add(c)
            db.session.commit()
        except Exception as e:
            log.error("Update ViewMenu error: {0}".format(str(e)))
            db.session.rollback()
    for political in politicals:
        c = PoliticalType(name=political)
        try:
            db.session.add(c)
            db.session.commit()
        except Exception as e:
            log.error("Update ViewMenu error: {0}".format(str(e)))
            db.session.rollback()
    try:
        for x in range(1, 20):
            cs = CountryStats()
            cs.population = random.randint(1, 100)
            cs.unemployed = random.randint(1, 100)
            cs.college = random.randint(1, 100)
            year = random.choice(range(1900, 2012))
            month = random.choice(range(1, 12))
            day = random.choice(range(1, 28))
            cs.stat_date = datetime.datetime(year, month, day)
            cs.country_id = random.randint(1, len(countries))
            cs.political_type_id = random.randint(1, len(politicals))
            db.session.add(cs)
            db.session.commit()
    except Exception as e:
        log.error("Update ViewMenu error: {0}".format(str(e)))
        db.session.rollback()


class CountryStatsModelView(ModelView):
    datamodel = SQLAInterface(CountryStats)
    list_columns = ["country", "stat_date", "population", "unemployed", "college"]


class CountryModelView(ModelView):
    datamodel = SQLAInterface(Country)


class PoliticalTypeModelView(ModelView):
    datamodel = SQLAInterface(PoliticalType)


class CountryStatsDirectChart(DirectChartView):
    datamodel = SQLAInterface(CountryStats)
    chart_title = "Statistics"
    chart_type = "LineChart"
    direct_columns = {
        "General Stats": ("stat_date", "population", "unemployed", "college")
    }
    base_order = ("stat_date", "asc")


def pretty_month_year(value):
    return calendar.month_name[value.month] + " " + str(value.year)


class CountryDirectChartView(DirectByChartView):
    datamodel = SQLAInterface(CountryStats)
    chart_title = "Direct Data"

    definitions = [
        {
            "group": "stat_date",
            "series": ["unemployed", "college"],
        }
    ]


class CountryGroupByChartView(GroupByChartView):
    datamodel = SQLAInterface(CountryStats)
    chart_title = "Statistics"

    definitions = [
        {
            "label": "Country Stat",
            "group": "country",
            "series": [
                (aggregate_avg, "unemployed"),
                (aggregate_avg, "population"),
                (aggregate_avg, "college"),
            ],
        },
        {
            "group": "month_year",
            "formatter": pretty_month_year,
            "series": [
                (aggregate_sum, "unemployed"),
                (aggregate_avg, "population"),
                (aggregate_avg, "college"),
            ],
        },
    ]
    """
        [{
            'label': 'String',
            'group': '<COLNAME>'|'<FUNCNAME>'
            'formatter: <FUNC>
            'series': [(<AGGR FUNC>, <COLNAME>|'<FUNCNAME>'),...]
            }
        ]
    """

    group_by_columns = ["country", "political_type", "country_political", "month_year"]
    aggregate_by_column = [
        (aggregate_avg, "unemployed"),
        (aggregate_avg, "population"),
        (aggregate_avg, "college"),
    ]
    # [{'aggr_func':<FUNC>,'column':'<COL NAME>'}]
    formatter_by_columns = {"month_year": pretty_month_year}

class ProductPubView(ModelView):
    datamodel = SQLAInterface(Product)
    base_permissions = ["can_list", "can_show"]
    list_widget = ListBlock
    show_widget = ShowBlockWidget

    label_columns = {"photo_img": "Photo"}

    list_columns = ["name", "photo_img", "price_label"]
    search_columns = ["name", "price", "product_type"]

    show_fieldsets = [
        ("Summary", {"fields": ["name", "price_label", "photo_img", "product_type"]}),
        ("Description", {"fields": ["description"], "expanded": True}),
    ]


class ProductView(ModelView):
    datamodel = SQLAInterface(Product)
    list_columns = ["name", "price_label"]

class ProductTypeView(ModelView):
    datamodel = SQLAInterface(ProductType)
    related_views = [ProductView]


class EmployeeHistoryView(ModelView):
    datamodel = SQLAInterface(EmployeeHistory)
    # base_permissions = ['can_add', 'can_show']
    list_columns = ["department", "begin_date", "end_date"]


class EmployeeView(ModelView):
    datamodel = SQLAInterface(Employee)

    list_columns = ["full_name", "department.name", "employee_number"]
    edit_form_extra_fields = {
        "department": QuerySelectField(
            "Department",
            query_factory=department_query,
            widget=Select2Widget(extra_classes="readonly"),
        )
    }

    related_views = [EmployeeHistoryView]
    show_template = "appbuilder/general/model/show_cascade.html"


class FunctionView(ModelView):
    datamodel = SQLAInterface(Function)
    related_views = [EmployeeView]


class DepartmentView(ModelView):
    datamodel = SQLAInterface(Department)
    related_views = [EmployeeView]


class BenefitView(ModelView):
    datamodel = SQLAInterface(Benefit)
    add_columns = ["name"]
    edit_columns = ["name"]
    show_columns = ["name"]
    list_columns = ["name"]


class ContactGeneralView(ModelView):
    datamodel = SQLAInterface(Contact)

    label_columns = {"contact_group": "Contacts Group"}
    list_columns = ["name", "personal_phone", "contact_group"]

    base_order = ("name", "asc")

    show_fieldsets = [
        ("Summary", {"fields": ["name", "gender", "contact_group"]}),
        (
            "Personal Info",
            {
                "fields": [
                    "address",
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                ],
                "expanded": False,
            },
        ),
    ]

    add_fieldsets = [
        ("Summary", {"fields": ["name", "gender", "contact_group"]}),
        (
            "Personal Info",
            {
                "fields": [
                    "address",
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                ],
                "expanded": False,
            },
        ),
    ]

    edit_fieldsets = [
        ("Summary", {"fields": ["name", "gender", "contact_group"]}),
        (
            "Personal Info",
            {
                "fields": [
                    "address",
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                ],
                "expanded": False,
            },
        ),
    ]


class GroupMasterView(MasterDetailView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactGeneralView]


class GroupGeneralView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactGeneralView]
    list_columns = ["name"]

    @action("Change Name", "Do something on this record", "Do you really want to?", "fa-rocket",False,True)
    def myaction(self, item):
        """
            do something with the item record
        """
        item.name = "Club Member"
        self.datamodel.edit(item)
        return redirect(self.get_redirect())

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


fixed_translations_import = [
    _("List Groups"),
    _("Manage Groups"),
    _("List Contacts"),
    _("Contacts Chart"),
    _("Contacts Birth Chart"),
]

db.create_all()
fill_gender()
# fill_data()

appbuilder.add_view(
    GroupMasterView, "List Groups", icon="fa-folder-open-o", category="Contacts"
)
appbuilder.add_separator("Contacts")
appbuilder.add_view(
    GroupGeneralView, "Manage Groups", icon="fa-folder-open-o", category="Contacts"
)
appbuilder.add_view(
    ContactGeneralView, "List Contacts", icon="fa-envelope", category="Contacts"
)
appbuilder.add_view_no_menu(EmployeeHistoryView, "EmployeeHistoryView")
appbuilder.add_view(
    EmployeeView, "Employees", icon="fa-folder-open-o", category="Company"
)
appbuilder.add_separator("Company")
appbuilder.add_view(
    DepartmentView, "Departments", icon="fa-folder-open-o", category="Company"
)
appbuilder.add_view(
    FunctionView, "Functions", icon="fa-folder-open-o", category="Company"
)
appbuilder.add_view(
    BenefitView, "Benefits", icon="fa-folder-open-o", category="Company"
)
appbuilder.add_view(ProductPubView, "Our Products", icon="fa-folder-open-o")
appbuilder.add_view(
    ProductView, "List Products", icon="fa-folder-open-o", category="Management"
)
appbuilder.add_separator("Management")
appbuilder.add_view(
    ProductTypeView, "List Product Types", icon="fa-envelope", category="Management"
)
appbuilder.add_view(
    CountryModelView, "List Countries", icon="fa-folder-open-o", category="Statistics"
)
appbuilder.add_view(
    PoliticalTypeModelView,
    "List Political Types",
    icon="fa-folder-open-o",
    category="Statistics",
)
appbuilder.add_view(
    CountryStatsModelView,
    "List Country Stats",
    icon="fa-folder-open-o",
    category="Statistics",
)
appbuilder.add_separator("Statistics")
appbuilder.add_view(
    CountryStatsDirectChart,
    "Show Country Chart",
    icon="fa-dashboard",
    category="Statistics",
)
appbuilder.add_view(
    CountryGroupByChartView,
    "Group Country Chart",
    icon="fa-dashboard",
    category="Statistics",
)
appbuilder.add_view(
    CountryDirectChartView,
    "Show Country Chart",
    icon="fa-dashboard",
    category="Statistics",
)