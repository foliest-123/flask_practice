from flask import Flask , render_template , request , jsonify
import psycopg2 
from sqlalchemy import create_engine


app = Flask(__name__)

@app.route("/")
def index():
    return ("hello world")

conn = psycopg2.connect(database="sample_test",  
                        user="postgres", 
                    password="1234",  
                    host="localhost", port="5432") 
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
    


@app.route('/addemployees' , methods = ["POST" , "GET"])
def addemployees():
   
    engine = create_engine('postgresql+psycopg2://postgres:1234@localhost/sample_test')
    cur = engine.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS testing (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    department VARCHAR(50),
    salary NUMERIC(10, 2),
    hire_date DATE
);
                              ''')
    conn.commit()

    first_name = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    department = request.form.get('department')
    salary = request.form.get('salary')
    hire_date = request.form.get('hiredate')

    cur.execute('''
    INSERT INTO Employee (first_name, last_name, email, department, salary, hire_date)
    VALUES (%s, %s, %s, %s, %s, %s)
''', (first_name, lastname, email, department, salary, hire_date))
    

    alldetails = cur.execute('''select * from Employee''')
    return render_template('addemployees.html' , data = alldetails)
    cur.close()
    conn.close()



















app.run(host="0.0.0.0", port="5000", debug=True)