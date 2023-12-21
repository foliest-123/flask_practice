from flask import Flask , render_template , request , jsonify, redirect , url_for
import psycopg2 
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.exc import SQLAlchemyError
import os

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

app.config['SQLALCHEMY_DATABASE_URI'] =f'postgresql+psycopg2://{username}:{password}@localhost/{db}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional but recommended for performance

db = SQLAlchemy(app)


@app.route("/connect_psql" , methods =["POST" , "GET"])
def sql_connection():
    cur = conn.cursor() 
    cur.execute('''select * from students''')
    data = cur.fetchall()   
    conn.commit() 
    cur.close() 
    conn.close()
    return render_template('index.html' , data=data)


@app.route("/addnumber")
def add_number():
    return render_template('add.html')

@app.route("/addnumber", methods=["POST"])
def calculate_sum():
    num1 = request.form.get('num1')
    num2 = request.form.get('num2')
    try:
        result = int(num1) + int(num2)
        return render_template('add.html',add=result)
    except ValueError:
        return 'Please enter valid numbers'

@app.route('/bankdata' , methods = ["POST" , "GET"])
def bankdata():
    if request.method == 'POST':
        data = request.get_json()  
        compute_value = 0
        if data[0]['mode'] == 'deposit':
            compute_value = data[0]['net_amount'] + data[0]['amount']
        else:
            compute_value = data[0]['net_amount'] - data[0]['amount']

        return jsonify({"net_amount": compute_value})
    else:
        return jsonify({"error": "Invalid JSON format or net_amount not found"})
    

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
def get_employees():
    try:
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
    except SQLAlchemyError as e:
        error_message = f"Error retrieving employees: {str(e)}"
        return (error_message)
@app.route('/add_employee', methods=["GET"])
def add_employee():
    values = request.get_json()
    try:
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
    except Exception as e:
        # Handle the exception here
        error_message = "An error occurred: {}".format(str(e))
        # You can log the error or handle it in a way suitable for your application
        return (error_message)

@app.route('/update_employee', methods=["GET"])
def update_employee():

    form_data = request.get_json() 
    employee = Employee.query.filter(Employee.employee_id == form_data['id']).first()
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
 
    update_data = {key: value for key, value in form_data.items()}
    for key, value in update_data.items():
     setattr(employee, key, value)
    db.session.commit()
    
    return jsonify({'success': 'data updated successfully'})


@app.route('/delete_employee', methods=["GET"])
def delete_employee():
    try:
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

    except SQLAlchemyError as e:
        # Handle the SQLAlchemyError exception here
        db.session.rollback()  # Roll back changes in case of an error
        error_message = "An error occurred: {}".format(str(e))
        # You can log the error or handle it in a way suitable for your application
        return (error_message)


if __name__ == "__main__":
    app.run()

