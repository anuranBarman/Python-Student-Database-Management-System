import sys,sqlite3,time
from PyQt5 import QtGui
from PyQt5.QtWidgets import QTableWidgetItem,QTableWidget,QComboBox,QVBoxLayout,QGridLayout,QDialog,QWidget, QPushButton, QApplication, QMainWindow,QAction,QMessageBox,QLabel,QTextEdit,QProgressBar,QLineEdit
from PyQt5.QtCore import QCoreApplication

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
        self.c.execute("SELECT * from students WHERE roll="+str(roll))
        self.data=self.c.fetchone()
        if not self.data:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not find any student with roll no '+str(roll))
            return None
        self.list=[]
        for i in range(0,8):
            self.list.append(self.data[i])
        self.c.close()
        self.conn.close()
        showStudent(self.list)

    def addPayment(self,roll,fee,semester):
        reciept_no=int(time.time())
        date=time.strftime("%b %d %Y %H:%M:%S")
        try:
            self.c.execute("SELECT * from payments WHERE roll=" + str(roll))
            self.conn.commit()
            if not self.c.fetchone():
                if semester == 1:
                    self.c.execute("SELECT * from payments WHERE roll=" + str(roll) + " AND semester=0")
                    if not self.c.fetchone():
                        QMessageBox.warning(QMessageBox(), 'Error',
                                            'Student with roll no ' + str(
                                                roll) + ' has Odd Semester fee payment due.Pay that first.')
                        return None
                else:
                    self.c.execute("INSERT INTO payments (reciept_no,roll,fee,semester,reciept_date) VALUES (?,?,?,?,?)",(reciept_no, roll, fee, semester, date))
                    self.conn.commit()
                QMessageBox.information(QMessageBox(), 'Successful','Payment is added successfully to the database.\nReference ID=' + str(reciept_no))
            else:
                self.c.execute("SELECT * from payments WHERE roll=" + str(roll))
                self.data = self.c.fetchall()
                if len(self.data) == 2:
                    QMessageBox.warning(QMessageBox(), 'Error','Student with roll no ' + str(roll) + ' has already paid both semester fees.')
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
                elif self.data[0][3] == semester:
                    QMessageBox.warning(QMessageBox(), 'Error','Student with roll no ' + str(roll) + ' has already paid this semester fees.')
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


def showPaymentFunction(list):
    roll = -1
    recipt_no = -1
    fee = -1
    semester = -1
    recipt_date = ""

    recipt_no = list[0]
    roll = list[1]
    fee = list[2]
    if list[3] == 0:
        semester = "Odd Semester"
    elif list[3]==1:
        semester = "Paid for both Odd and Even Semester"
    recipt_date=list[4]


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = Login()

    if login.exec_() == QDialog.Accepted:
        window = Window()
        window.show()
    sys.exit(app.exec_())