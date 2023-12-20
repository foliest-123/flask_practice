from flask import Flask , render_template , request , jsonify, redirect , url_for
import psycopg2 
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy 
app = Flask(__name__)

@app.route("/")
def index():
    return ("hello world")

conn = psycopg2.connect(database="sample_test",  
                        user="postgres", 
                    password="1234",  
                    host="localhost", port="5432") 

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:1234@localhost/sample_test'
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
    return render_template('/addemployees.html' , result = result)

@app.route('/add_employee', methods=["POST"])
def add_employee():
        new_employee = Employee(
            first_name=request.form.get('firstname'),
            last_name=request.form.get('lastname'),
            email=request.form.get('email'),
            department=request.form.get('department'),
            salary=request.form.get('salary'),
            hire_date=request.form.get('hiredate')
        )
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for('get_employees'))

@app.route('/update_employee', methods=["POST"])
def update_employee():

    form_data = request.form.to_dict() 
    employee = Employee.query.filter(Employee.employee_id == form_data['id']).first()

    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
 
    # Filter out the keys that are not present or have empty values
    update_data = {key: value for key, value in form_data.items()}
    previous_value = Employee.query.get(Employee.employee_id == form_data['id']).first()
    # Update only the provided fields
    print(update_data)
    for key, value in update_data.items():
     setattr(employee, key, value)
    # Check for empty values in updated data and copy from employee if empty
    for key, value in update_data.items():
       if not value:
        setattr(employee, key, getattr(employee, key)) 
    print(previous_value) # Copy from employee if value is empty
    db.session.commit()
    
    return redirect(url_for('get_employees'))


@app.route('/delete_employee' , methods=["POST"])
def delete_employee():
    search_id = request.form.get('search_id')
    search_name = request.form.get('search_name')
    employee_to_delete = (
        Employee.query.filter(
            (Employee.employee_id == search_id) |
            (Employee.first_name == search_name) |
            (Employee.last_name == search_name)
        ).first()
    )
    if employee_to_delete:
        db.session.delete(employee_to_delete)
        db.session.commit()
    return redirect(url_for('get_employees'))



if __name__ == "__main__":
    app.run()