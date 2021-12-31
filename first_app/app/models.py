import datetime
from flask import Markup, url_for
from flask_appbuilder.filemanager import ImageManager
from flask_appbuilder.models.mixins import ImageColumn
from flask_appbuilder.security.sqla.models import User
from flask_appbuilder import Model
from sqlalchemy import Column, Float, Date, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship, backref

mindate = datetime.date(datetime.MINYEAR, 1, 1)

class Country(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class PoliticalType(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name

class CountryStats(Model):
    id = Column(Integer, primary_key=True)
    stat_date = Column(Date, nullable=True)
    population = Column(Float)
    unemployed = Column(Float)
    college = Column(Float)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)
    country = relationship("Country")
    political_type_id = Column(Integer, ForeignKey("political_type.id"), nullable=False)
    political_type = relationship("PoliticalType")

    def __repr__(self):
        return "{0}:{1}:{2}:{3}".format(
            self.country, self.political_type, self.population, self.college
        )

    def month_year(self):
        return datetime.datetime(self.stat_date.year, self.stat_date.month, 1)

    def country_political(self):
        return str(self.country) + " - " + str(self.political_type)

class ProductType(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name

class Product(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    photo = Column(ImageColumn)
    description = Column(Text())
    product_type_id = Column(Integer, ForeignKey("product_type.id"), nullable=False)
    product_type = relationship("ProductType")

    def photo_img(self):
        im = ImageManager()
        productPubViewUrl = url_for("ProductPubView.show", pk=str(self.id))
        if self.photo:
            photoUrl = im.get_url(self.photo)
            return Markup(
                f'<a href="{productPubViewUrl}" class="thumbnail"><img src="{photoUrl}" '
                f'alt="Photo" class="img-rounded img-responsive"></a>'
            )
        else:
            return Markup(
                f'<a href="{productPubViewUrl}"" class="thumbnail"><img src="//:0" '
                f'alt="Photo" class="img-responsive">' '</a>'
            )

    def price_label(self):
        return Markup("Price:<strong> {} </strong>".format(self.price))

    def __repr__(self):
        return self.name

class Client(User):
    __tablename__ = "ab_user"
    extra = Column(String(50), unique=True, nullable=False)

class Department(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Function(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Benefit(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


assoc_benefits_employee = Table(
    "benefits_employee",
    Model.metadata,
    Column("id", Integer, primary_key=True),
    Column("benefit_id", Integer, ForeignKey("benefit.id")),
    Column("employee_id", Integer, ForeignKey("employee.id")),
)


def today():
    return datetime.datetime.today().strftime("%Y-%m-%d")


class EmployeeHistory(Model):
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("department.id"), nullable=False)
    department = relationship("Department")
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)
    employee = relationship("Employee")
    begin_date = Column(Date, default=today)
    end_date = Column(Date)


class Employee(Model):
    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    address = Column(Text(250), nullable=False)
    fiscal_number = Column(Integer, nullable=False)
    employee_number = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"), nullable=False)
    department = relationship("Department")
    function_id = Column(Integer, ForeignKey("function.id"), nullable=False)
    function = relationship("Function")
    benefits = relationship(
        "Benefit", secondary=assoc_benefits_employee, backref="employee"
    )

    begin_date = Column(Date, default=datetime.date.today(), nullable=True)
    end_date = Column(Date, default=datetime.date.today(), nullable=True)

    def __repr__(self):
        return self.full_name

class ContactGroup(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Gender(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Contact(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    address = Column(String(564))
    birthday = Column(Date, nullable=True)
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    contact_group_id = Column(Integer, ForeignKey("contact_group.id"), nullable=False)
    contact_group = relationship("ContactGroup")
    gender_id = Column(Integer, ForeignKey("gender.id"), nullable=False)
    gender = relationship("Gender")

    def __repr__(self):
        return self.name

    def month_year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, date.month, 1) or mindate

    def year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, 1, 1)

class ModelOMParent(Model):
    __tablename__ = "model_om_parent"
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)


class ModelOMChild(Model):
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("model_om_parent.id"))
    parent = relationship(
        "ModelOMParent",
        backref=backref("children", cascade="all, delete-orphan"),
        foreign_keys=[parent_id],
    )