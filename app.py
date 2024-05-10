from flask import Flask, render_template, request, redirect, url_for, make_response
import mysql.connector


# instantiate the app
app = Flask(__name__)


mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password= "20011016",
    database = "last_resort")



@app.route('/')
def home():
    #Link to the index page.
    return render_template('index.html')


@app.route('/facilities')
def facilities():
    cursor = mydb.cursor()
    # Query to count different types of facilities (e.g., swimming pools, gyms, etc.) in one hotel
    query1 = '''
    SELECT facility_type.typeName, COUNT(hotel_facility.typeId) 
    FROM facility_type 
    JOIN hotel_facility ON hotel_facility.typeId = facility_type.typeId 
    GROUP BY facility_type.typeName;
    '''
    cursor.execute(query1)
    results_query1 = cursor.fetchall()

    # Query to find facilities that need an upgrade, ordering them by the descending days since last upgraded
    query2 = '''
    SELECT facilityName, DATEDIFF(CURDATE(), MAX(lastUpgraded)) AS daysSinceLastUpgrade FROM hotel_facility GROUP BY facilityName ORDER BY daysSinceLastUpgrade DESC LIMIT 3;
    '''
    cursor.execute(query2)
    results_query2 = cursor.fetchall()

    # Query to find the oldest facilities, limited to the two oldest
    query3 = '''
    SELECT facilityName, timeBuilt 
    FROM hotel_facility 
    ORDER BY timeBuilt ASC 
    LIMIT 2;
    '''
    cursor.execute(query3)
    results_query3 = cursor.fetchall()

    # Return template with results
    return render_template('facilities.html', query1=results_query1, query2=results_query2, query3=results_query3)


@app.route('/customers')
def customers():
    cursor = mydb.cursor()
    # Query to identify the top 10 most-spent customers and display their demographic information
    query1 = '''
    SELECT profile.profileId, firstName, lastName, organization, SUM(totalRoomCharges + totalExtraCharges) AS totalSpent
    FROM profile
    JOIN customer ON customer.profileId = profile.profileId
    GROUP BY profile.profileId, firstName, lastName, organization
    ORDER BY totalSpent DESC
    LIMIT 10;
    '''
    cursor.execute(query1)
    results_query1 = cursor.fetchall()

    # Query to calculate the average length of stay for each reservation type
    query2 = '''
    SELECT reservationType, AVG(TIMESTAMPDIFF(HOUR, reservationStartDateTime, reservationEndDateTime)) AS avgHours
    FROM reservation
    GROUP BY reservationType;
    '''
    cursor.execute(query2)
    results_query2 = cursor.fetchall()

    return render_template('customers.html', query1=results_query1, query2=results_query2)


@app.route('/employees')
def employees():
    cursor = mydb.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(employeeId) AS numberOfEmployees FROM employee;")
    employee_count = cursor.fetchone()

    cursor.execute("""
        SELECT employeeGender, COUNT(*) as count 
        FROM employee 
        GROUP BY employeeGender;
    """)
    gender_data = cursor.fetchall()

    cursor.execute("""
        SELECT employeeRace, COUNT(*) as count 
        FROM employee 
        GROUP BY employeeRace;
    """)
    race_data = cursor.fetchall()

    cursor.execute("""
        SELECT employeeNationality, COUNT(*) as count 
        FROM employee 
        GROUP BY employeeNationality;
    """)
    nationality_data = cursor.fetchall()

    # Detailed demographics for listing
    cursor.execute("""
        SELECT employeeGender, employeeRace, employeeNationality,
               TIMESTAMPDIFF(YEAR, employeeBirthday, CURDATE()) AS age
        FROM employee;
    """)
    detailed_demographics = cursor.fetchall()

    # Monthly salary
    cursor.execute("""
        SELECT employeeName, ROUND(employeeSalary / 12) AS monthSalary
        FROM employee;
    """)
    monthly_salaries = cursor.fetchall()

    # Average monthly salary
    cursor.execute("""
        SELECT ROUND(SUM(ROUND(employeeSalary / 12)) / COUNT(employeeId)) AS averageMonthSalary
        FROM employee;
    """)
    average_salary = cursor.fetchone()

    cursor.close()
    return render_template('employees.html',
                           employee_count=employee_count,
                           gender_data=gender_data,
                           race_data=race_data,
                           nationality_data=nationality_data,
                           demographics=detailed_demographics,
                           monthly_salaries=monthly_salaries,
                           average_salary=average_salary)



@app.errorhandler(Exception)
def handle_error(e):
    """
    Output any errors - good for debugging.
    """
    return render_template('error.html', error=e) # render the edit template


if __name__ == "__main__":
    app.run(debug = True, port = 3000)