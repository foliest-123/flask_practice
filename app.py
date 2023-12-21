from flask import Flask , render_template , request , jsonify, redirect , url_for
import psycopg2 
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.exc import SQLAlchemyError
import os
from functools import wraps

db = os.getenv('DB')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

app = Flask(__name__)

@app.route("/")
def index():
    return ("hello world")

conn = psycopg2.connect(database="sample_test",  
                        user="postgres", 
                    password="1234",  
                    host="localhost", port="5432") 

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@localhost/{db}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional but recommended for performance

db = SQLAlchemy(app)

def handle_exceptions(route_function):
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        try:
            return route_function(*args, **kwargs)
        except SQLAlchemyError as e:
            error_message = f"Error retrieving employees: {str(e)}"
        return (error_message)
    return decorated_function


@app.route("/connect_psql" , methods =["POST" , "GET"])
@handle_exceptions
def sql_connection():
    cur = conn.cursor() 
    cur.execute('''select * from students''')
    data = cur.fetchall()   
    conn.commit() 
    cur.close() 
    conn.close()
    return data


@app.route("/addnumber", methods=["GET"])
@handle_exceptions
def calculate_sum():
        nums = request.get_json()
        result = int(nums['num1']) + int(nums['num2'])
        return f"{nums['num1']} + {nums['num1']} = {result}"

@app.route('/bankdata' , methods = ["GET"])
@handle_exceptions
def bankdata():
        data = request.get_json()      
        if 'mode' in data and 'net_amount' in data and 'amount' in data:
            compute_value = 0
            if data['mode'] == 'deposit':
                compute_value = data['net_amount'] + data['amount']
            else:
                compute_value = data['net_amount'] - data['amount']

            return jsonify({"net_amount": compute_value})
        else:
            return jsonify({"error": "Invalid JSON format or missing required fields"})

class Employee(db.Model):
    __table_name__ = 'employee'
    employee_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    department = db.Column(db.String(50))
    salary = db.Column(db.Numeric(10, 2))
    hire_date = db.Column(db.Date)
    def __init__(self, first_name, last_name, email, department, salary, hire_date):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.department = department
        self.salary = salary
        self.hire_date = hire_date


@app.route('/employees', methods=['GET'])
@handle_exceptions
def get_employees():
        employees = Employee.query.all()
        result = []
        for employee in employees:
            result.append({
                'id': employee.employee_id,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'email': employee.email,
                'department': employee.department,
                'salary': float(employee.salary),
                'hire_date': str(employee.hire_date)
            })
        return result
@app.route('/add_employee', methods=["GET"])
@handle_exceptions
def add_employee():
        values = request.get_json()
        new_employee = Employee(
            first_name=values['firstname'],
            last_name=values['lastname'],
            email=values['email'],
            department=values['department'],
            salary=values['salary'],
            hire_date=values['hiredate']
        )
        db.session.add(new_employee)
        db.session.commit()
        return jsonify("Data insert successfully")

@app.route('/update_employee', methods=["GET"])
@handle_exceptions
def update_employee():
        form_data = request.get_json() 
        employee_id  = form_data['id']
        employee_name = form_data['firstname']
        employee = Employee.query.filter_by(employee_id,employee_name).first()
        if not employee:
            return jsonify({'message': 'Employee not found'}), 404
        else:
            print(employee)
     
        update_data = {key: value for key, value in form_data.items() if value}
        for key, value in update_data.items():
            setattr(employee, key, value)
        
        db.session.commit()
        
        return update_data


@app.route('/delete_employee', methods=["GET"])
@handle_exceptions
def delete_employee():
        delete_values = request.get_json()

        employee_to_delete = (
            Employee.query.filter(
                (Employee.employee_id == delete_values['id']) &
                (Employee.email == delete_values['email'])
            ).first()
        )

        db.session.delete(employee_to_delete)
        db.session.commit()
        return "Data deleted successfully"


if __name__ == "__main__":
    app.run()

