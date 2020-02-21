
from flask_restful import Resource, Api
from flask import request
from .model import db, ExpenseModel, ExpenseSchema



def init_routes(app):
    api = Api(app)

    # Schema instantiation
    expense_single_schema = ExpenseSchema()
    expense_list_schema = ExpenseSchema(many=True)

    @app.route('/expenses/dummy', methods=['GET'])
    def dummy():
        return {'message': 'Working'}, 200

    # Api Routes
    class ExpenseList(Resource):
        def get(self):
            task_ids = request.json['task_ids']
            expenses = ExpenseModel.query.filter(ExpenseModel.task_id.in_(task_ids)).all() # Get Expenses of user
            return expense_list_schema.dump(expenses)
        
        def post(self):
            expense = {
                'amount': request.json['amount'],
                'title': request.json['title'] if 'title' in request.json else None,
                'comment': request.json['comment'] if 'comment' in request.json else None,
                'date': request.json['date'] if 'date' in request.json else None,
                'category': request.json['category'] if 'category' in request.json else None,
                'task_id': request.json['task_id']
            }
            validation_errors = expense_single_schema.validate(expense)
            if validation_errors:
                return {'errors': validation_errors}, '400'
            expense = expense_single_schema.load(expense)
            new_expense = ExpenseModel(
                amount=expense['amount'],
                task_id=expense['task_id'],
                title=expense['title'],
                comment=expense['comment'],
                category=expense['category'],
                date=expense['date']
            )
            db.session.add(new_expense)
            db.session.commit()
            return expense_single_schema.dump(new_expense), '201'


    class ExpenseSingle(Resource):
        def get(self, expense_id):
            expense = ExpenseModel.query.get_or_404(expense_id)
            return expense_single_schema.dump(expense), '200'

        def patch(self, expense_id):
            expense = ExpenseModel.query.get_or_404(expense_id)

            request_expense = {
                'amount': request.json['amount'],
                'title': request.json['title'] if 'title' in request.json else None,
                'comment': request.json['comment'] if 'comment' in request.json else None,
                'date': request.json['date'] if 'date' in request.json else None,
                'category': request.json['category'] if 'category' in request.json else None,
                'task_id': request.json['task_id']
            }
            validation_errors = expense_single_schema.validate(request_expense)
            if validation_errors:
                return {'errors': validation_errors}, '400'
            request_expense = expense_single_schema.load(request_expense)
            expense.amount = request_expense['amount']
            expense.category = request_expense['category']
            expense.title = request_expense['title']
            expense.comment = request_expense['comment']
            expense.date = request_expense['date']
            expense.task_id = request_expense['task_id']
            db.session.commit()
            return expense_single_schema.dump(expense), '200'

        def delete(self, expense_id):
            expense = ExpenseModel.query.get_or_404(expense_id)
            db.session.delete(expense)
            db.session.commit()
            return '', '204'

    api.add_resource(ExpenseList, '/expenses')
    api.add_resource(ExpenseSingle,'/expenses/<string:expense_id>/')
