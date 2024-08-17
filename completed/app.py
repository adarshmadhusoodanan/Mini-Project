from flask import Flask, render_template, request, redirect, session, url_for, send_file
from flask_mysqldb import MySQL
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bus'

mysql = MySQL(app)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')  # Render registration form
    elif request.method == 'POST':
        # Get form data
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        branch_name = request.form['branch_name']
        semester = request.form['semester']
        phone_no = request.form['phone_no']
        password = request.form['password']  # Implement password hashing here!

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO bus_user (student_id, student_name, branch_name, phone_no, password, sem) VALUES (%s, %s, %s, %s, %s, %s)", (student_id, student_name, branch_name, phone_no, password, semester))
        mysql.connection.commit()
        cur.close()
    return render_template("login.html")

@app.route('/test_connection')
def test_connection():
    try:
        mysql.connection.ping()  # Check if connection is still alive
        return "Connection to database is active!"
    except Exception as e:
        return f"Error connecting to database: {e}"

@app.route('/')
def home():
    return render_template("homepage.html")

@app.route('/main')
def main():
    return render_template("main.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        password = request.form['password']
        
        try:
            cur = mysql.connection.cursor()
            
            cur.execute("SELECT student_id, password FROM bus_user WHERE student_id = %s", (student_id,))
            user = cur.fetchone()
            
            if user is not None and password == user[1]:
                session['student_id'] = user[0]
                cur.close() 
                return redirect(url_for('main'))
            
            if student_id == "admin" and password == "admin@123":
                session['student_id'] = student_id                              
                return render_template("admin.html")
               
            cur.close()  
            return render_template('login.html', error='Invalid student ID or password')
        
        except Exception as e:
            return f"Error: {e}"
    
    return render_template('login.html')

@app.route('/updatebusreg', methods=['GET', 'POST'])
def updatebusreg():
    if request.method == 'GET':
        return render_template('busreg.html')  
    elif request.method == 'POST':
        
        student_id = session['student_id']
        place = request.form['place']
        route = request.form['route']
        feeamount = request.form['feeamount']
        academicyear = request.form['academicyear']
        email = request.form['email']

       
        cur = mysql.connection.cursor()
        cur.execute("UPDATE bus_user SET place = %s, route = %s, fee = %s, academic_year = %s, email = %s WHERE student_id = %s", (place, route, feeamount, academicyear, email, student_id))
        mysql.connection.commit()
        cur.close()
    return render_template("main.html")

@app.route('/buspass')
def buspass():
    student_id = session['student_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT student_name, branch_name, sem, place, academic_year, route FROM bus_user WHERE student_id = %s", (student_id,))
    passdata = cur.fetchall()
    return render_template("pass.html", passdata=passdata, student_id=student_id)

@app.route('/payment')
def payment():
    student_id = session['student_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT fee, paid, due FROM bus_user WHERE student_id = %s", (student_id,))
    feedata = cur.fetchall()
    return render_template("payment.html", feedata=feedata)

@app.route('/busreg')
def busreg():
    return render_template("busreg.html")

@app.route('/businfo')
def businfo():
    return render_template("businfo.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/logout')
def logout():
    session.pop('student_id', None)
    return render_template("homepage.html")

@app.route('/paysbi')
def paysbi():
    return redirect("https://www.onlinesbi.sbi/sbicollect")

# adminpage paymentupdate
@app.route('/updateinfo', methods=['GET', 'POST'])
def updateinfo():
    if request.method == 'GET':
        return render_template('admin.html')  
    elif request.method == 'POST':
       
        student_id = request.form['student_id']
        paid = request.form['paid']
        due = request.form['due']
        
       
        cur = mysql.connection.cursor()
        cur.execute("UPDATE bus_user SET paid = %s, due = %s WHERE student_id = %s", (paid, due, student_id))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('admin'))

@app.route('/details')
def details():
    if 'student_id' not in session:
        return "Unauthorized", 401 
    
    student_id = session['student_id']  
    
    cur = mysql.connection.cursor()

    
    cur.execute("SELECT student_id, password, student_name, branch_name, sem, place, route, phone_no, email, fee, paid, due FROM bus_user")
    students_data = cur.fetchall()  
    
    cur.close()  
    return render_template("details.html", students_data=students_data)

@app.route('/downloadpass', methods=['POST'])
def downloadpass():
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT student_name, branch_name, sem, place, academic_year, route FROM bus_user WHERE student_id = %s", (student_id,))
    passdata = cur.fetchone()
    cur.close()

    if not passdata:
        return "No data found for the student.", 404

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Set background color
    c.setFillColorRGB(255, 255, 255)  # Dark blue color
    c.rect(0, 0, width, height, fill=1)

    # Draw bus pass outline
    c.setLineWidth(1)
    c.setFillColor("white")
    c.roundRect(30, height - 180, width - 60, 150, 10, stroke=1, fill=1)

    # College Name
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0,0,0.5)
    c.drawCentredString(width / 2, height - 180 + 60, "College of Engineering Trikaripur")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, height - 180 + 40, "Cheemeni, Kasaragod Dist-671313")

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 200, "Student Bus Pass")

    # Student details
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 230, f"Name: {passdata[0]}")
    c.drawString(50, height - 250, f"Student ID: {student_id}")
    c.drawString(50, height - 270, f"Branch: {passdata[1]}")
    c.drawString(50, height - 290, f"Semester: {passdata[2]}")
    c.drawString(50, height - 310, f"Place: {passdata[3]}")
    c.drawString(50, height - 330, f"Academic Year: {passdata[4]}")
    c.drawString(50, height - 350, f"Route: {passdata[5]}")
    c.drawString(50, height - 370, "Validity: MAY 2024")

    # Placeholder for image
    image_path = "static/assets/img/pass.jpg"
    c.drawImage(image_path, width - 160, height - 240, width=100, height=100)

    c.showPage()
    c.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='bus_pass.pdf', mimetype='application/pdf')




if __name__ == '__main__':
    app.run(debug=True)
