
from flask_restful import Resource, Api
from flask import request
from .model import db, ExpenseModel, ExpenseSchema



def init_routes(app):
    api = Api(app)

    # Schema instantiation
    expense_single_schema = ExpenseSchema()
    expense_list_schema = ExpenseSchema(many=True)

    @app.route('/dummy', methods=['GET'])
    def dummy():
        return {'message': 'Working'}, 200

    # Api Routes
    class ExpenseList(Resource):

        def get(self):
            '''
                Get expenses of a specific task
            '''
            if 'task_id' in request.args:
                task_id = request.args.get('task_id')
                expenses = ExpenseModel.query.filter_by(task_id=task_id).all()
            elif 'owner' in request.args:
                task_id = request.args.get('owner')
                expenses = ExpenseModel.query.filter_by(owner_user_id=task_id).all()
            else:
                expenses = ExpenseModel.query.all()
            return expense_list_schema.dump(expenses)
        
        def post(self):
            request_expense = request.json.copy()
            validation_errors = expense_single_schema.validate(request_expense)
            if validation_errors:
                return {'errors': validation_errors}, '400'
            expense = expense_single_schema.load(request_expense)
            new_expense = ExpenseModel()
            for k, v in expense.items():
                setattr(new_expense, k, v)
            db.session.add(new_expense)
            db.session.commit()
            return expense_single_schema.dump(new_expense), '201'


    class ExpenseSingle(Resource):
        def get(self, expense_id):
            expense = ExpenseModel.query.get_or_404(expense_id)
            return expense_single_schema.dump(expense), '200'

        def patch(self, expense_id):
            expense = ExpenseModel.query.get_or_404(expense_id)

            request_expense = request.json.copy()
            validation_errors = expense_single_schema.validate(request_expense)
            if validation_errors:
                return {'errors': validation_errors}, '400'
            request_expense = expense_single_schema.load(request_expense)
            for k, v in request_expense.items():
                setattr(expense, k, v)
            db.session.commit()
            return expense_single_schema.dump(expense), '200'

        def delete(self, expense_id):
            expense = ExpenseModel.query.get_or_404(expense_id)
            db.session.delete(expense)
            db.session.commit()
            return '', '204'

    api.add_resource(ExpenseList, '/')
    api.add_resource(ExpenseSingle,'/<string:expense_id>')
