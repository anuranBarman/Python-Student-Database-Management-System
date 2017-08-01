#------------------------------------------#
#----Student Database Management System----#
#----created by Anuran Barman--------------#
#----modules: PyQt and Sqlite3-------------#
#----www.mranuran.com----------------------#
#----anuranbarman@gmail.com----------------#
#------------------------------------------#

import sys,sqlite3,time
from PyQt5 import QtGui
from PyQt5.QtWidgets import QTableWidgetItem,QTableWidget,QComboBox,QVBoxLayout,QGridLayout,QDialog,QWidget, QPushButton, QApplication, QMainWindow,QAction,QMessageBox,QLabel,QTextEdit,QProgressBar,QLineEdit
from PyQt5.QtCore import QCoreApplication


#DBHelper class holding all important functions for the application.
#addStudent() add a student given roll,name,gender,branch,year,academic_year,address,mobile
#searchStudent() searches for a student associating to the given roll number
#addPayment() adds the payment to the database
#searchPayment() searches for the payment  made by the student with the given roll number

#DB has 4 tables among which only two has rows and columns in it currenrly. as you expand the application and
#make it more complex you can use other tables as you like.
#the most important table which is used here is students and payments.

#students holds the records of the students and payments hold the records of the payments

#students(roll INTEGER,name TEXT,gender INTEGER,branch INTEGER,year INTEGER,academic_year INTEGER,address TEXT,mobile INTEGER)
#here geneder is either 0 for Male or 1 for Female
#branch has 6 values ranging from 0 to 5
#0->Mechanical,1->Civil,2->Electrical,3->ECE,4->CSE,5->IT
#academic year is when the student joined the college.
#other columns are self explanatory.

class DBHelper():
    def __init__(self):
        self.conn=sqlite3.connect("sdms.db")
        self.c=self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS students(roll INTEGER,name TEXT,gender INTEGER,branch INTEGER,year INTEGER,academic_year INTEGER,address TEXT,mobile INTEGER)")
        self.c.execute("CREATE TABLE IF NOT EXISTS payments(reciept_no INTEGER,roll INTEGER,fee INTEGER,semester INTEGER,reciept_date TEXT)")
        self.c.execute("CREATE TABLE IF NOT EXISTS genders(id INTEGER,name TEXT)")
        self.c.execute("CREATE TABLE IF NOT EXISTS branches(id INTEGER,name TEXT)")
    def addStudent(self,roll,name,gender,branch,year,academic_year,address,mobile):
        try:
            self.c.execute("INSERT INTO students (roll,name,gender,branch,year,academic_year,address,mobile) VALUES (?,?,?,?,?,?,?,?)",(roll,name,gender,branch,year,academic_year,address,mobile))
            self.conn.commit()
            self.c.close()
            self.conn.close()
            QMessageBox.information(QMessageBox(),'Successful','Student is added successfully to the database.')
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not add student to the database.')

    def searchStudent(self,roll):
        #we make a DB query to search for a student holding the roll number. if we find any then we pass the result returned
        #from the DB to our custom function showStudent() which then analyze the list.
        self.c.execute("SELECT * from students WHERE roll="+str(roll))
        self.data=self.c.fetchone()

        #if there is no data returned by above cursor function fetchone() then it means there is no record
        #holding the roll number. so we show a warning box saying the same and return from the function.
        if not self.data:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not find any student with roll no '+str(roll))
            return None
        self.list=[]
        for i in range(0,8):
            self.list.append(self.data[i])
        self.c.close()
        self.conn.close()
        #it's out custom function which analyzes the list and show the output in tabular form to the application user.
        showStudent(self.list)


    #this function is the most important and complex part of the whole program. This adds the payment made by the student to the
    #database. roll and fee are integers and semester it either 0 for Odd semester or 1 for Even semester.
    #there are some posibilites here. They are-----
    #1.)admin tries to add a fresh entry but he has put semester as Even when the student has not paid the Odd semester fee
    #2.)admin tries to add entry for a student who has already paid his/her both semester fees
    #3.)admin tries to add entry for astudent for the same semester twice

    def addPayment(self,roll,fee,semester):
        reciept_no=int(time.time())
        date=time.strftime("%b %d %Y %H:%M:%S")
        try:
            #we check to see if any payment record exists in the database with the roll number
            self.c.execute("SELECT * from payments WHERE roll=" + str(roll))
            self.conn.commit()

            #if it does not exists then following possibilities may occur.
            if not self.c.fetchone():
                #admin tries to add fee for Even semester but student has not paid the Odd semester.
                if semester == 1:
                    #query to check if there is any record with same roll number and semester as 0 which is Odd Semester
                    self.c.execute("SELECT * from payments WHERE roll=" + str(roll) + " AND semester=0")

                    #above query fails. that means student has not paid the Odd semester fee. So we show
                    #a dialog saying the same.
                    if not self.c.fetchone():
                        QMessageBox.warning(QMessageBox(), 'Error',
                                            'Student with roll no ' + str(
                                                roll) + ' has Odd Semester fee payment due.Pay that first.')
                        return None
                else:
                    #admin is making entry for Odd semester first. That's okay. Go ahead.
                    self.c.execute("INSERT INTO payments (reciept_no,roll,fee,semester,reciept_date) VALUES (?,?,?,?,?)",(reciept_no, roll, fee, semester, date))
                    self.conn.commit()
                QMessageBox.information(QMessageBox(), 'Successful','Payment is added successfully to the database.\nReference ID=' + str(reciept_no))
            else:

                #as there is too much query execution for the same cursor object sometimes it acts weird. So to be
                #in the safe side we execute the same query again which is searching payments table
                #for records holding the given roll number.
                self.c.execute("SELECT * from payments WHERE roll=" + str(roll))

                #we fetch all records.
                self.data = self.c.fetchall()

                #if student has more than one records in the database that means he/she has paid both semester fees.
                if len(self.data) == 2:
                    QMessageBox.warning(QMessageBox(), 'Error','Student with roll no ' + str(roll) + ' has already paid both semester fees.')
                #admin is trying to make Even semester payment. We check if there is any record for Odd semester.
                #if it fails then it means it has to make the payment for the Odd semester first.
                #otherwise make the payment.
                elif semester==1:
                    self.c.execute("SELECT * from payments WHERE roll=" + str(roll)+" AND semester=0")
                    if not self.c.fetchone():
                        QMessageBox.warning(QMessageBox(), 'Error','Student with roll no ' + str(roll) + ' has Odd Semester fee payment due.Pay that first.')
                    else:
                        self.c.execute(
                            "INSERT INTO payments (reciept_no,roll,fee,semester,reciept_date) VALUES (?,?,?,?,?)",
                            (reciept_no, roll, fee, semester, date))
                        self.conn.commit()
                        QMessageBox.information(QMessageBox(), 'Successful',
                                                'Payment is added successfully to the database.\nReference ID=' + str(

                                                    reciept_no))
                #here we try to check if admin is trying to make payment for the same semester twice.
                elif self.data[0][3] == semester:
                    QMessageBox.warning(QMessageBox(), 'Error','Student with roll no ' + str(roll) + ' has already paid this semester fees.')
                #everything is fine. Go ahead and make the payment.
                else:
                    self.c.execute(
                        "INSERT INTO payments (reciept_no,roll,fee,semester,reciept_date) VALUES (?,?,?,?,?)",
                        (reciept_no, roll, fee, semester, date))
                    self.conn.commit()
                    QMessageBox.information(QMessageBox(), 'Successful',
                                            'Payment is added successfully to the database.\nReference ID=' + str(
                                                reciept_no))

        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not add payment to the database.')

        self.c.close()
        self.conn.close()

        #similar to the searchStudent() it will search for any record holding the roll number in the database.
        #it will then pass the returned list from the DB to the function searchStudentFunction()
        #here in the query we use ORDER BY reciept_no DESC so that rows with semester value as 1 comes first
        #if it exists. Then we can be sure that student has paid his/her both semester fees as we overcame
        #the possibility of adding Odd semester fee first. if there are any record for two semester
        #so they will come as semester=1 first then semester=0.
    def searchPayment(self,roll):
        self.c.execute("SELECT * from payments WHERE roll="+str(roll)+" ORDER BY reciept_no DESC")
        self.data=self.c.fetchone()
        if not self.data:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not find any student with roll no '+str(roll))
            return None
        self.list=self.data
        # for j in range(6):
        #     self.list.append(self.data[j])
        self.c.close()
        self.conn.close()
        showPaymentFunction(self.list)

#this is a login function which shows a dialog for admin to log into the system.
# Default username and password are admin and admin respectively.
class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.userNameLabel=QLabel("Username")
        self.userPassLabel=QLabel("Password")
        self.textName = QLineEdit(self)
        self.textPass = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = QGridLayout(self)
        layout.addWidget(self.userNameLabel, 1, 1)
        layout.addWidget(self.userPassLabel, 2, 1)
        layout.addWidget(self.textName,1,2)
        layout.addWidget(self.textPass,2,2)
        layout.addWidget(self.buttonLogin,3,1,1,2)

        self.setWindowTitle("Login")


    def handleLogin(self):
        if (self.textName.text() == 'admin' and
            self.textPass.text() == 'admin'):
            self.accept()
        else:
            QMessageBox.warning(
                self, 'Error', 'Bad user or password')

#function to show the dialog with records of the student returned for the DB holding the roll number.
def showStudent(list):
        roll=0
        gender = ""
        branch = ""
        year = ""
        name = ""
        address = ""
        mobile = -1
        academic_year = -1

        roll=list[0]
        name=list[1]

        if list[2]==0:
            gender="Male"
        else:
            gender="Female"

        if list[3]==0:
            branch="Mechanical Engineering"
        elif list[3]==1:
            branch="Civil Engineering"
        elif list[3]==2:
            branch="Electrical Engineering"
        elif list[3]==3:
            branch="Electronics and Communication Engineering"
        elif list[3]==4:
            branch="Computer Science and Engineering"
        elif list[3]==5:
            branch="Information Technology"

        if list[4]==0:
            year="1st"
        elif list[4]==1:
            year="2nd"
        elif list[4]==2:
            year="3rd"
        elif list[4]==3:
            year="4th"

        academic_year=list[5]
        address=list[6]
        mobile=list[7]

        #we make the table here. Table has eight rows and 2 columns.
        #in PyQt tables are like grids. you have to place each QTableWidgetItem seprately corresponding to the grid system with x and y
        # both starting at 0 index. Then we populate the table with values from the passed list as we got all of them above.

        table=QTableWidget()
        tableItem=QTableWidgetItem()
        table.setWindowTitle("Student Details")
        table.setRowCount(8)
        table.setColumnCount(2)

        table.setItem(0, 0, QTableWidgetItem("Roll"))
        table.setItem(0, 1, QTableWidgetItem(str(roll)))
        table.setItem(1, 0, QTableWidgetItem("Name"))
        table.setItem(1, 1, QTableWidgetItem(str(name)))
        table.setItem(2, 0, QTableWidgetItem("Gender"))
        table.setItem(2, 1, QTableWidgetItem(str(gender)))
        table.setItem(3, 0, QTableWidgetItem("Branch"))
        table.setItem(3, 1, QTableWidgetItem(str(branch)))
        table.setItem(4, 0, QTableWidgetItem("Year"))
        table.setItem(4, 1, QTableWidgetItem(str(year)))
        table.setItem(5, 0, QTableWidgetItem("Academic Year"))
        table.setItem(5, 1, QTableWidgetItem(str(academic_year)))
        table.setItem(6, 0, QTableWidgetItem("Address"))
        table.setItem(6, 1, QTableWidgetItem(str(address)))
        table.setItem(7, 0, QTableWidgetItem("Mobile"))
        table.setItem(7, 1, QTableWidgetItem(str(mobile)))
        table.horizontalHeader().setStretchLastSection(True)
        table.show()
        dialog=QDialog()
        dialog.setWindowTitle("Student Details")
        dialog.resize(500,300)
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(table)
        dialog.exec()

#function to show the payments records holding the roll number given
def showPaymentFunction(list):
    roll = -1
    recipt_no = -1
    fee = -1
    semester = -1
    recipt_date = ""

    recipt_no = list[0]
    roll = list[1]
    fee = list[2]

    #as I said earlier if semester value is 0 that means Odd semester and if it is 1 then student has paid both semester fees
    #as we eliminated the possibility of adding Even semester payment record first.
    if list[3] == 0:
        semester = "Odd Semester"
    elif list[3]==1:
        semester = "Paid for both Odd and Even Semester"
    recipt_date=list[4]


    #we do the same as showing student details. we make a table with 5 rows and 2 columns.
    #then we create QTableWidgetItem for each box of the grid system.
    table = QTableWidget()
    tableItem = QTableWidgetItem()
    table.setWindowTitle("Student Payment Details")
    table.setRowCount(5)
    table.setColumnCount(2)

    table.setItem(0, 0, QTableWidgetItem("Receipt No"))
    table.setItem(0, 1, QTableWidgetItem(str(recipt_no)))
    table.setItem(1, 0, QTableWidgetItem("Roll"))
    table.setItem(1, 1, QTableWidgetItem(str(roll)))
    table.setItem(2, 0, QTableWidgetItem("Total Fee"))
    table.setItem(2, 1, QTableWidgetItem(str(fee)))
    table.setItem(3, 0, QTableWidgetItem("Semester"))
    table.setItem(3, 1, QTableWidgetItem(str(semester)))
    table.setItem(4, 0, QTableWidgetItem("Receipt Date"))
    table.setItem(4, 1, QTableWidgetItem(str(recipt_date)))

    table.horizontalHeader().setStretchLastSection(True)
    table.show()
    dialog = QDialog()
    dialog.setWindowTitle("Student Payment Details Details")
    dialog.resize(500, 300)
    dialog.setLayout(QVBoxLayout())
    dialog.layout().addWidget(table)
    dialog.exec()

#this is class which inherits QDialog to create the entry form of adding student functionality.
#it has two drops down as gender with options like Male and Female and another Branch holding 6 options like
#ME,CE,EE,ECE,CSE,IT (abbreviated here)
#it has three buttons. Reset,Add,Cancel.
#Reset clear the text fields, Add calls the function addStudent() which in turn calls addStudent() of DBHelper class.
class AddStudent(QDialog):
    def __init__(self):
        super().__init__()

        #general variables
        self.gender=-1
        self.branch=-1
        self.year=-1
        self.roll=-1
        self.name=""
        self.address=""
        self.mobile=-1
        self.academic_year=-1


        self.btnCancel=QPushButton("Cancel",self)
        self.btnReset=QPushButton("Reset",self)
        self.btnAdd=QPushButton("Add",self)

        self.btnCancel.setFixedHeight(30)
        self.btnReset.setFixedHeight(30)
        self.btnAdd.setFixedHeight(30)

        self.yearCombo=QComboBox(self)
        self.yearCombo.addItem("1st")
        self.yearCombo.addItem("2nd")
        self.yearCombo.addItem("3rd")
        self.yearCombo.addItem("4th")

        self.genderCombo = QComboBox(self)
        self.genderCombo.addItem("Male")
        self.genderCombo.addItem("Female")

        self.branchCombo = QComboBox(self)
        self.branchCombo.addItem("Mechanical")
        self.branchCombo.addItem("Civil")
        self.branchCombo.addItem("Electrical")
        self.branchCombo.addItem("Electronics and Communication")
        self.branchCombo.addItem("Computer Science")
        self.branchCombo.addItem("Information Technology")


        self.rollLabel=QLabel("Roll No")
        self.nameLabel=QLabel("Name")
        self.addressLabel = QLabel("Address")
        self.mobLabel = QLabel("Mobile")
        self.yearLabel = QLabel("Current Year")
        self.academicYearLabel = QLabel("Academic Year")
        self.branchLabel = QLabel("Branch")
        self.genderLabel=QLabel("Gender")

        self.rollText=QLineEdit(self)
        self.nameText=QLineEdit(self)
        self.addressText = QLineEdit(self)
        self.mobText = QLineEdit(self)
        self.academicYearText = QLineEdit(self)

        self.grid=QGridLayout(self)
        self.grid.addWidget(self.rollLabel,1,1)
        self.grid.addWidget(self.nameLabel,2,1)
        self.grid.addWidget(self.genderLabel, 3, 1)
        self.grid.addWidget(self.addressLabel, 4, 1)
        self.grid.addWidget(self.mobLabel, 5, 1)
        self.grid.addWidget(self.branchLabel, 6, 1)
        self.grid.addWidget(self.yearLabel,7,1)
        self.grid.addWidget(self.academicYearLabel, 8, 1)





        self.grid.addWidget(self.rollText,1,2)
        self.grid.addWidget(self.nameText,2,2)
        self.grid.addWidget(self.genderCombo, 3, 2)
        self.grid.addWidget(self.addressText, 4, 2)
        self.grid.addWidget(self.mobText, 5, 2)
        self.grid.addWidget(self.branchCombo, 6, 2)
        self.grid.addWidget(self.yearCombo,7,2)
        self.grid.addWidget(self.academicYearText, 8, 2)



        #adding three buttons
        self.grid.addWidget(self.btnReset,9,1)
        self.grid.addWidget(self.btnCancel,9,3)
        self.grid.addWidget(self.btnAdd,9,2)

        #button connectors
        self.btnAdd.clicked.connect(self.addStudent)
        self.btnCancel.clicked.connect(QApplication.instance().quit)
        self.btnReset.clicked.connect(self.reset)

        self.setLayout(self.grid)
        self.setWindowTitle("Add Student Details")
        self.resize(500,300)
        self.show()
        sys.exit(self.exec())

    def reset(self):
        self.rollText.setText("")
        self.academicYearText.setText("")
        self.nameText.setText("")
        self.addressText.setText("")
        self.mobText.setText("")

    def addStudent(self):
        self.gender=self.genderCombo.currentIndex()
        self.year=self.yearCombo.currentIndex()
        self.branch=self.branchCombo.currentIndex()
        self.roll=int(self.rollText.text())
        self.name=self.nameText.text()
        self.academic_year=int(self.academicYearText.text())
        self.address=self.addressText.text()
        self.mobile=int(self.mobText.text())

        self.dbhelper=DBHelper()
        self.dbhelper.addStudent(self.roll,self.name,self.gender,self.branch,self.year,self.academic_year,self.address,self.mobile)

#it is the dialog for adding payment functionality. It has only one drop down for semester with options
#like Odd semester and Even semester.
#other fields are roll,fee.
class AddPayment(QDialog):
    def __init__(self):
        super().__init__()

        #general variables
        self.reciept_no=-1
        self.roll=-1
        self.fee=-1
        self.semester=-1
        self.date=-1



        self.btnCancel=QPushButton("Cancel",self)
        self.btnReset=QPushButton("Reset",self)
        self.btnAdd=QPushButton("Add",self)

        self.btnCancel.setFixedHeight(30)
        self.btnReset.setFixedHeight(30)
        self.btnAdd.setFixedHeight(30)

        self.semesterCombo = QComboBox(self)
        self.semesterCombo.addItem("Odd")
        self.semesterCombo.addItem("Even")

        self.rollLabel=QLabel("Roll No")
        self.feeLabel=QLabel("Total Fee")
        self.semesterLabel = QLabel("Semester")

        self.rollText=QLineEdit(self)
        self.feeLabelText=QLineEdit(self)


        self.grid=QGridLayout(self)
        self.grid.addWidget(self.rollLabel,1,1)
        self.grid.addWidget(self.feeLabel,2,1)
        self.grid.addWidget(self.semesterLabel, 3, 1)


        self.grid.addWidget(self.rollText,1,2)
        self.grid.addWidget(self.feeLabelText,2,2)
        self.grid.addWidget(self.semesterCombo, 3, 2)

        #adding three buttons
        self.grid.addWidget(self.btnReset,4,1)
        self.grid.addWidget(self.btnCancel,4,3)
        self.grid.addWidget(self.btnAdd,4,2)

        #button connectors
        self.btnAdd.clicked.connect(self.addPayment)
        self.btnCancel.clicked.connect(QApplication.instance().quit)
        self.btnReset.clicked.connect(self.reset)

        self.setLayout(self.grid)
        self.setWindowTitle("Add Payment Details")
        self.resize(400,200)
        self.show()
        sys.exit(self.exec())
    def reset(self):
        self.rollText.setText("")
        self.feeLabelText.setText("")

    def addPayment(self):
        self.semester=self.semesterCombo.currentIndex()
        self.roll=int(self.rollText.text())
        self.fee=int(self.feeLabelText.text())

        self.dbhelper=DBHelper()
        self.dbhelper.addPayment(self.roll,self.fee,self.semester)



#this is the main window which holds everything. It holds for buttons.
#Enter Student Details
#Enter Payment Details
#Show Student Details
#Show Payment Details
#it has two functions named enterstudent() and enterpayment() which show the dialogs created above respectively
#another two functions showStudent() and showStudentPaymentDialog() shows dialog for the user to enter the roll number
#he or she wants to search records for.
#showStudent() and showPayment() which are the actual functions which call the corresponding ssearching functions of the
#DBHelper class. These two functions are connected to the 'search' button of the dialog where user enters the roll number.
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rollToBeSearched=0
        self.vbox = QVBoxLayout()
        self.text = QLabel("Enter the roll no of the student")
        self.editField = QLineEdit()
        self.btnSearch = QPushButton("Search", self)
        self.btnSearch.clicked.connect(self.showStudent)
        self.vbox.addWidget(self.text)
        self.vbox.addWidget(self.editField)
        self.vbox.addWidget(self.btnSearch)
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Enter Roll No")
        self.dialog.setLayout(self.vbox)

        self.rollForPayment = 0
        self.vboxPayment = QVBoxLayout()
        self.textPayment = QLabel("Enter the roll no of the student")
        self.editFieldPayment = QLineEdit()
        self.btnSearchPayment = QPushButton("Search", self)
        self.btnSearchPayment.clicked.connect(self.showStudentPayment)
        self.vboxPayment.addWidget(self.textPayment)
        self.vboxPayment.addWidget(self.editFieldPayment)
        self.vboxPayment.addWidget(self.btnSearchPayment)
        self.dialogPayment = QDialog()
        self.dialogPayment.setWindowTitle("Enter Roll No")
        self.dialogPayment.setLayout(self.vboxPayment)

        self.btnEnterStudent=QPushButton("Enter Student Details",self)
        self.btnEnterPayment=QPushButton("Enter Payment Details",self)
        self.btnShowStudentDetails=QPushButton("Show Student Details",self)
        self.btnShowPaymentDetails=QPushButton("Show Payment Details",self)

        #picture
        self.picLabel=QLabel(self)
        self.picLabel.resize(150,150)
        self.picLabel.move(120,20)
        self.picLabel.setScaledContents(True)
        self.picLabel.setPixmap(QtGui.QPixmap("user.png"))

        self.btnEnterStudent.move(15,170)
        self.btnEnterStudent.resize(180,40)
        self.btnEnterStudentFont=self.btnEnterStudent.font()
        self.btnEnterStudentFont.setPointSize(13)
        self.btnEnterStudent.setFont(self.btnEnterStudentFont)
        self.btnEnterStudent.clicked.connect(self.enterstudent)

        self.btnEnterPayment.move(205,170)
        self.btnEnterPayment.resize(180, 40)
        self.btnEnterPaymentFont = self.btnEnterStudent.font()
        self.btnEnterPaymentFont.setPointSize(13)
        self.btnEnterPayment.setFont(self.btnEnterPaymentFont)
        self.btnEnterPayment.clicked.connect(self.enterpayment)

        self.btnShowStudentDetails.move(15, 220)
        self.btnShowStudentDetails.resize(180, 40)
        self.btnShowStudentDetailsFont = self.btnEnterStudent.font()
        self.btnShowStudentDetailsFont.setPointSize(13)
        self.btnShowStudentDetails.setFont(self.btnShowStudentDetailsFont)
        self.btnShowStudentDetails.clicked.connect(self.showStudentDialog)

        self.btnShowPaymentDetails.move(205, 220)
        self.btnShowPaymentDetails.resize(180, 40)
        self.btnShowPaymentDetailsFont = self.btnEnterStudent.font()
        self.btnShowPaymentDetailsFont.setPointSize(13)
        self.btnShowPaymentDetails.setFont(self.btnShowPaymentDetailsFont)
        self.btnShowPaymentDetails.clicked.connect(self.showStudentPaymentDialog)

        self.resize(400,280)
        self.setWindowTitle("Student Database Management System")

    def enterstudent(self):
        enterStudent=AddStudent()
    def enterpayment(self):
        enterpayment=AddPayment()
    def showStudentDialog(self):
        self.dialog.exec()
    def showStudentPaymentDialog(self):
        self.dialogPayment.exec()
    def showStudent(self):
        if self.editField.text() is "":
            QMessageBox.warning(QMessageBox(), 'Error',
                                'You must give the roll number to show the results for.')
            return None
        showstudent = DBHelper()
        showstudent.searchStudent(int(self.editField.text()))
    def showStudentPayment(self):
        if self.editFieldPayment.text() is "":
            QMessageBox.warning(QMessageBox(), 'Error',
                                'You must give the roll number to show the results for.')
            return None
        showstudent = DBHelper()
        showstudent.searchPayment(int(self.editFieldPayment.text()))

#main function which shows the login dialog first. if user puts the correct username and password it then goes to the main window
#where there are four buttons as mentioned above.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = Login()

    if login.exec_() == QDialog.Accepted:
        window = Window()
        window.show()
    sys.exit(app.exec_())