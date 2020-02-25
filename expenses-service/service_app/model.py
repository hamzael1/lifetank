
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema, validates, ValidationError

from datetime import datetime, timedelta

from random import random as rand, randrange, choice


db = SQLAlchemy()

####### MODEL ########

class ExpenseModel(db.Model):
    __tablename__ = 'expenses'

    EXPENSE_CATEGORIES = ['RESTAURANT', 'CAFE', 'STUDY', 'ENTERTAINMENT', 'FOOD', 'MATERIAL', 'WORK']

    id = db.Column(db.Integer, primary_key=True)
    owner_user_id = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer, nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    comment = db.Column(db.String(255), default='')
    date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(64), default='OTHER')
    created = db.Column(db.DateTime, default=datetime.today())

    def __repr__(self):
        return '<Expense (%s) %s>' % (self.amount, self.title)

####### SCHEMA ########

class ExpenseSchema(Schema):
    id = fields.Integer(dump_only=True)
    owner_user_id = fields.Integer(required=True)
    task_id = fields.Integer(required=True)
    amount = fields.Integer(required=True)
    title = fields.Str(required=True)
    comment = fields.Str(required=False)
    date = fields.DateTime(required=True, format='iso')
    category = fields.Str(required=True)
    created = fields.DateTime(dump_only=True, format='iso')

    @validates("owner_user_id")
    def validate_owner_user_id(self, value):
        if value < 1:
            raise ValidationError('owner_user_id cant be less than 1')

    @validates("task_id")
    def validate_task_id(self, value):
        if value < 1:
            raise ValidationError('task_id cant be less than 1')

    @validates("amount")
    def validate_amount(self, value):
        if value  <= 0:
            raise ValidationError('Amount must be bigger than 0')

    @validates("title")
    def validate_title(self, value):
        if len(value) == 0:
            raise ValidationError('title cant be empty')


####### FUNCTIONS ########

def init_db(app):
    db.init_app(app)


def populate_db(app, expenses_to_add=[]):
    """
        Populate DB with "nbr_expenses" expenses
    """
    print('Populating ...')
    with app.app_context():
        db.drop_all()
        db.create_all()
        today = datetime.today()
        for e in expenses_to_add:
            #print(str(e))
            t =  ExpenseModel( 
                owner_user_id=e['owner_user_id'],
                task_id=e['task_id'],
                amount=e['amount'],
                title=e['title'],
                comment=e['comment'],
                category=e['category'],
                date=e['date'],
                )
            db.session.add(t)
        db.session.commit()