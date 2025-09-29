import sys, json, csv, re
from typing import Dict, Any, List
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,QLabel, QLineEdit, QPushButton, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem,QMessageBox, QFileDialog, QAction, QToolBar)
from PyQt5.QtCore import Qt

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

def validate_nonempty_str(value: str, field: str):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")

def validate_nonneg_int(value: int, field: str):
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")

def validate_email(email: str):
    if not isinstance(email, str) or not EMAIL_REGEX.match(email):
        raise ValueError(f"Invalid email: {email}")

class Person:
    def __init__(self, name: str, age: int, email: str):
        validate_nonempty_str(name, "name")
        validate_nonneg_int(age, "age")
        validate_email(email)
        self.name = name
        self.age = age
        self._email = email
    def introduce(self):
        print(f"Hello, my name is {self.name}, I am {self.age} years old.")
    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Person", "name": self.name, "age": self.age, "email": self._email}
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Person":
        return cls(name=data["name"], age=data["age"], email=data["email"])

class Student(Person):
    def __init__(self, name: str, age: int, email: str, student_id: str):
        super().__init__(name, age, email)
        validate_nonempty_str(student_id, "student_id")
        self.student_id = student_id
        self.registered_courses: List["Course"] = []
    def register_course(self, course: "Course"):
        if not isinstance(course, Course):
            raise TypeError("course must be a Course object")
        if course not in self.registered_courses:
            self.registered_courses.append(course)
            if self not in course.enrolled_students:
                course._enroll_without_backlink(self)
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Student",
            "name": self.name,
            "age": self.age,
            "email": self._email,
            "student_id": self.student_id,
            "registered_course_ids": [c.course_id for c in self.registered_courses]
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        return cls(data["name"], data["age"], data["email"], data["student_id"])

class Instructor(Person):
    def __init__(self, name: str, age: int, email: str, instructor_id: str):
        super().__init__(name, age, email)
        validate_nonempty_str(instructor_id, "instructor_id")
        self.instructor_id = instructor_id
        self.assigned_courses: List["Course"] = []
    def assign_course(self, course: "Course"):
        if not isinstance(course, Course):
            raise TypeError("course must be a Course object")
        if course not in self.assigned_courses:
            self.assigned_courses.append(course)
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Instructor",
            "name": self.name,
            "age": self.age,
            "email": self._email,
            "instructor_id": self.instructor_id,
            "assigned_course_ids": [c.course_id for c in self.assigned_courses]
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Instructor":
        return cls(data["name"], data["age"], data["email"], data["instructor_id"])

class Course:
    def __init__(self, course_id: str, course_name: str, instructor: Instructor):
        validate_nonempty_str(course_id, "course_id")
        validate_nonempty_str(course_name, "course_name")
        if not isinstance(instructor, Instructor):
            raise TypeError("instructor must be an Instructor object")
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor
        self.enrolled_students: List[Student] = []
    def add_student(self, student: "Student"):
        if not isinstance(student, Student):
            raise TypeError("student must be a Student object")
        if student not in self.enrolled_students:
            self.enrolled_students.append(student)
            if self not in student.registered_courses:
                student.register_course(self)
    def _enroll_without_backlink(self, student: "Student"):
        if student not in self.enrolled_students:
            self.enrolled_students.append(student)
    def set_instructor(self, instructor: "Instructor"):
        if not isinstance(instructor, Instructor):
            raise TypeError("instructor must be an Instructor object")
        if self.instructor is instructor:
            if self not in instructor.assigned_courses:
                instructor.assigned_courses.append(self)
            return
        old = self.instructor
        self.instructor = instructor
        if old and self in old.assigned_courses:
            old.assigned_courses.remove(self)
        if self not in instructor.assigned_courses:
            instructor.assigned_courses.append(self)
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Course",
            "course_id": self.course_id,
            "course_name": self.course_name,
            "instructor_id": self.instructor.instructor_id,
            "enrolled_student_ids": [s.student_id for s in self.enrolled_students]
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any], instructor_lookup: Dict[str, Instructor]) -> "Course":
        return cls(data["course_id"], data["course_name"], instructor_lookup[data["instructor_id"]])

class DataManager:
    def __init__(self):
        self.students: Dict[str, Student] = {}
        self.instructors: Dict[str, Instructor] = {}
        self.courses: Dict[str, Course] = {}
    def email_in_use(self, email: str, exclude_kind: str = None, exclude_id: str = None) -> bool:
        for s in self.students.values():
            if s._email == email and not (exclude_kind == "student" and s.student_id == exclude_id):
                return True
        for i in self.instructors.values():
            if i._email == email and not (exclude_kind == "instructor" and i.instructor_id == exclude_id):
                return True
        return False
    def add_student(self, student: Student):
        if not isinstance(student, Student): raise TypeError("student must be a Student object")
        if student.student_id in self.students: raise ValueError(f"Duplicate student_id: {student.student_id}")
        if self.email_in_use(student._email): raise ValueError(f"Email already in use: {student._email}")
        self.students[student.student_id] = student
    def add_instructor(self, instructor: Instructor):
        if not isinstance(instructor, Instructor): raise TypeError("instructor must be an Instructor object")
        if instructor.instructor_id in self.instructors: raise ValueError(f"Duplicate instructor_id: {instructor.instructor_id}")
        if self.email_in_use(instructor._email): raise ValueError(f"Email already in use: {instructor._email}")
        self.instructors[instructor.instructor_id] = instructor
    def add_course(self, course: Course):
        if not isinstance(course, Course): raise TypeError("course must be a Course object")
        if course.course_id in self.courses: raise ValueError(f"Duplicate course_id: {course.course_id}")
        self.courses[course.course_id] = course
        course.set_instructor(course.instructor)
    def to_dict(self):
        return {
            "students": [s.to_dict() for s in self.students.values()],
            "instructors": [i.to_dict() for i in self.instructors.values()],
            "courses": [c.to_dict() for c in self.courses.values()]
        }
    def save_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
    @classmethod
    def load_json(cls, path: str) -> "DataManager":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        dm = cls()
        for i_data in data.get("instructors", []):
            instr = Instructor.from_dict(i_data)
            dm.instructors[instr.instructor_id] = instr
        for s_data in data.get("students", []):
            stu = Student.from_dict(s_data)
            dm.students[stu.student_id] = stu
        for c_data in data.get("courses", []):
            course = Course.from_dict(c_data, dm.instructors)
            dm.courses[course.course_id] = course
            course.set_instructor(course.instructor)
        for c_data in data.get("courses", []):
            course = dm.courses[c_data["course_id"]]
            for sid in c_data.get("enrolled_student_ids", []):
                student = dm.students.get(sid)
                if student and student not in course.enrolled_students:
                    course.enrolled_students.append(student)
                    if course not in student.registered_courses:
                        student.registered_courses.append(course)
        return dm

class SchoolQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("School Management System")
        self.resize(1200, 750)
        self.dm = DataManager()
        self.edit_mode = {"students": None, "instructors": None, "courses": None}
        self._build_ui()
        self._refresh_all()
    def _build_ui(self):
        self._build_menu_toolbar()
        central = QWidget()
        root = QVBoxLayout(central)
        root.addLayout(self._forms_section())
        root.addLayout(self._actions_section())
        root.addLayout(self._search_section())
        root.addWidget(self._tables_section())
        self.setCentralWidget(central)
    def _build_menu_toolbar(self):
        save_act = QAction("Save...", self); save_act.triggered.connect(self._save_json)
        load_act = QAction("Load...", self); load_act.triggered.connect(self._load_json)
        export_act = QAction("Export CSV...", self); export_act.triggered.connect(self._export_csv)
        toolbar = QToolBar("Main"); self.addToolBar(toolbar)
        toolbar.addAction(save_act); toolbar.addAction(load_act); toolbar.addAction(export_act)
    def _forms_section(self):
        layout = QHBoxLayout()
        layout.addWidget(self._student_form())
        layout.addWidget(self._instructor_form())
        layout.addWidget(self._course_form())
        return layout
    def _student_form(self):
        g = QGroupBox("Add / Edit Student")
        grid = QGridLayout(g)
        self.s_name = QLineEdit(); self.s_age = QLineEdit(); self.s_email = QLineEdit(); self.s_id = QLineEdit()
        grid.addWidget(QLabel("Name"), 0,0); grid.addWidget(self.s_name,0,1)
        grid.addWidget(QLabel("Age"), 0,2); grid.addWidget(self.s_age,0,3)
        grid.addWidget(QLabel("Email"),1,0); grid.addWidget(self.s_email,1,1)
        grid.addWidget(QLabel("Student ID"),1,2); grid.addWidget(self.s_id,1,3)
        self.s_add_btn = QPushButton("Add Student"); self.s_add_btn.clicked.connect(self._add_or_update_student)
        clr = QPushButton("Clear"); clr.clicked.connect(lambda: self._clear_form("students"))
        grid.addWidget(self.s_add_btn,2,1); grid.addWidget(clr,2,3)
        return g
    def _instructor_form(self):
        g = QGroupBox("Add / Edit Instructor")
        grid = QGridLayout(g)
        self.i_name = QLineEdit(); self.i_age = QLineEdit(); self.i_email = QLineEdit(); self.i_id = QLineEdit()
        grid.addWidget(QLabel("Name"), 0,0); grid.addWidget(self.i_name,0,1)
        grid.addWidget(QLabel("Age"), 0,2); grid.addWidget(self.i_age,0,3)
        grid.addWidget(QLabel("Email"),1,0); grid.addWidget(self.i_email,1,1)
        grid.addWidget(QLabel("Instructor ID"),1,2); grid.addWidget(self.i_id,1,3)
        self.i_add_btn = QPushButton("Add Instructor"); self.i_add_btn.clicked.connect(self._add_or_update_instructor)
        clr = QPushButton("Clear"); clr.clicked.connect(lambda: self._clear_form("instructors"))
        grid.addWidget(self.i_add_btn,2,1); grid.addWidget(clr,2,3)
        return g
    def _course_form(self):
        g = QGroupBox("Add / Edit Course")
        grid = QGridLayout(g)
        self.c_id = QLineEdit(); self.c_name = QLineEdit(); self.c_instructor = QComboBox()
        grid.addWidget(QLabel("Course ID"),0,0); grid.addWidget(self.c_id,0,1)
        grid.addWidget(QLabel("Name"),0,2); grid.addWidget(self.c_name,0,3)
        grid.addWidget(QLabel("Instructor"),1,0); grid.addWidget(self.c_instructor,1,1,1,3)
        self.c_add_btn = QPushButton("Add Course"); self.c_add_btn.clicked.connect(self._add_or_update_course)
        clr = QPushButton("Clear"); clr.clicked.connect(lambda: self._clear_form("courses"))
        grid.addWidget(self.c_add_btn,2,1); grid.addWidget(clr,2,3)
        return g
    def _actions_section(self):
        layout = QHBoxLayout()
        reg_box = QGroupBox("Register Student to Course")
        rg = QGridLayout(reg_box)
        self.reg_student = QComboBox(); self.reg_course = QComboBox()
        rg.addWidget(QLabel("Student"),0,0); rg.addWidget(self.reg_student,0,1)
        rg.addWidget(QLabel("Course"),0,2); rg.addWidget(self.reg_course,0,3)
        btn = QPushButton("Register"); btn.clicked.connect(self._register_student_to_course)
        rg.addWidget(btn,0,4)
        asg_box = QGroupBox("Assign Instructor to Course")
        ag = QGridLayout(asg_box)
        self.asg_instructor = QComboBox(); self.asg_course = QComboBox()
        ag.addWidget(QLabel("Instructor"),0,0); ag.addWidget(self.asg_instructor,0,1)
        ag.addWidget(QLabel("Course"),0,2); ag.addWidget(self.asg_course,0,3)
        btn2 = QPushButton("Assign"); btn2.clicked.connect(self._assign_instructor_to_course)
        ag.addWidget(btn2,0,4)
        layout.addWidget(reg_box); layout.addWidget(asg_box)
        return layout
    def _search_section(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Search (Name / ID / Course):"))
        self.search_edit = QLineEdit()
        go = QPushButton("Search"); go.clicked.connect(self._apply_search)
        clr = QPushButton("Clear"); clr.clicked.connect(self._clear_search)
        layout.addWidget(self.search_edit); layout.addWidget(go); layout.addWidget(clr); layout.addStretch(1)
        return layout
    def _tables_section(self):
        self.tabs = QTabWidget()
        self.stu_table = QTableWidget(0,5)
        self.stu_table.setHorizontalHeaderLabels(["Student ID","Name","Age","Email","Courses"])
        self.stu_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ins_table = QTableWidget(0,5)
        self.ins_table.setHorizontalHeaderLabels(["Instructor ID","Name","Age","Email","Courses"])
        self.ins_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.crs_table = QTableWidget(0,4)
        self.crs_table.setHorizontalHeaderLabels(["Course ID","Course Name","Instructor","Students"])
        self.crs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabs.addTab(self.stu_table, "Students")
        self.tabs.addTab(self.ins_table, "Instructors")
        self.tabs.addTab(self.crs_table, "Courses")
        ctl = QWidget(); ctl_layout = QHBoxLayout(ctl)
        edit_btn = QPushButton("Edit Selected"); edit_btn.clicked.connect(self._edit_selected)
        del_btn = QPushButton("Delete Selected"); del_btn.clicked.connect(self._delete_selected)
        ctl_layout.addWidget(edit_btn); ctl_layout.addWidget(del_btn); ctl_layout.addStretch(1)
        wrap = QWidget(); v = QVBoxLayout(wrap); v.addWidget(self.tabs); v.addWidget(ctl)
        return wrap
    def _refresh_dropdowns(self):
        self.c_instructor.clear()
        self.c_instructor.addItems([f"{iid} | {ins.name}" for iid, ins in self.dm.instructors.items()])
        self.reg_student.clear()
        self.reg_student.addItems([f"{sid} | {s.name}" for sid, s in self.dm.students.items()])
        self.reg_course.clear()
        self.reg_course.addItems([f"{cid} | {c.course_name}" for cid, c in self.dm.courses.items()])
        self.asg_instructor.clear()
        self.asg_instructor.addItems([f"{iid} | {ins.name}" for iid, ins in self.dm.instructors.items()])
        self.asg_course.clear()
        self.asg_course.addItems([f"{cid} | {c.course_name}" for cid, c in self.dm.courses.items()])
    def _refresh_tables(self, q: str = ""):
        q = q.lower().strip()
        self.stu_table.setRowCount(0)
        for sid, s in self.dm.students.items():
            courses_str = ", ".join([c.course_id for c in s.registered_courses])
            if not q or q in sid.lower() or q in s.name.lower() or q in courses_str.lower():
                r = self.stu_table.rowCount(); self.stu_table.insertRow(r)
                for col, val in enumerate([sid, s.name, str(s.age), s._email, courses_str]):
                    self.stu_table.setItem(r, col, QTableWidgetItem(val))
        self.ins_table.setRowCount(0)
        for iid, ins in self.dm.instructors.items():
            courses_str = ", ".join([c.course_id for c in ins.assigned_courses])
            if not q or q in iid.lower() or q in ins.name.lower() or q in courses_str.lower():
                r = self.ins_table.rowCount(); self.ins_table.insertRow(r)
                for col, val in enumerate([iid, ins.name, str(ins.age), ins._email, courses_str]):
                    self.ins_table.setItem(r, col, QTableWidgetItem(val))
        self.crs_table.setRowCount(0)
        for cid, c in self.dm.courses.items():
            students_str = ", ".join([s.student_id for s in c.enrolled_students])
            instr_label = f"{c.instructor.instructor_id} - {c.instructor.name}"
            if not q or q in cid.lower() or q in c.course_name.lower() or q in students_str.lower():
                r = self.crs_table.rowCount(); self.crs_table.insertRow(r)
                for col, val in enumerate([cid, c.course_name, instr_label, students_str]):
                    self.crs_table.setItem(r, col, QTableWidgetItem(val))
        for table in (self.stu_table, self.ins_table, self.crs_table):
            table.resizeColumnsToContents()
    def _refresh_all(self):
        self._refresh_dropdowns()
        self._refresh_tables()
    def _apply_search(self):
        self._refresh_tables(self.search_edit.text())
    def _clear_search(self):
        self.search_edit.setText("")
        self._refresh_tables("")
    def _parse_int(self, s: str, field: str) -> int:
        try:
            return int(s.strip())
        except:
            raise ValueError(f"{field} must be an integer")
    def _selected_row_values(self, table: QTableWidget) -> List[str]:
        rows = table.selectionModel().selectedRows()
        if not rows: return []
        row = rows[0].row()
        return [table.item(row, c).text() if table.item(row, c) else "" for c in range(table.columnCount())]
    def _add_or_update_student(self):
        try:
            name = self.s_name.text().strip()
            age = self._parse_int(self.s_age.text(), "age")
            email = self.s_email.text().strip()
            sid = self.s_id.text().strip()
            if self.edit_mode["students"] is None:
                if self.dm.email_in_use(email):
                    raise ValueError(f"Email already in use: {email}")
                stu = Student(name, age, email, sid)
                self.dm.add_student(stu)
            else:
                sid_key = self.edit_mode["students"]
                stu = self.dm.students[sid_key]
                if sid != sid_key and sid in self.dm.students: raise ValueError(f"Duplicate student_id: {sid}")
                validate_nonempty_str(name, "name"); validate_nonneg_int(age, "age"); validate_email(email); validate_nonempty_str(sid, "student_id")
                if self.dm.email_in_use(email, exclude_kind="student", exclude_id=sid_key):
                    raise ValueError(f"Email already in use: {email}")
                stu.name = name; stu.age = age; stu._email = email
                if sid != sid_key:
                    self.dm.students.pop(sid_key); self.dm.students[sid] = stu; stu.student_id = sid
            self._clear_form("students"); self._refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    def _add_or_update_instructor(self):
        try:
            name = self.i_name.text().strip()
            age = self._parse_int(self.i_age.text(), "age")
            email = self.i_email.text().strip()
            iid = self.i_id.text().strip()
            if self.edit_mode["instructors"] is None:
                if self.dm.email_in_use(email):
                    raise ValueError(f"Email already in use: {email}")
                ins = Instructor(name, age, email, iid)
                self.dm.add_instructor(ins)
            else:
                iid_key = self.edit_mode["instructors"]
                ins = self.dm.instructors[iid_key]
                if iid != iid_key and iid in self.dm.instructors: raise ValueError(f"Duplicate instructor_id: {iid}")
                validate_nonempty_str(name, "name"); validate_nonneg_int(age, "age"); validate_email(email); validate_nonempty_str(iid, "instructor_id")
                if self.dm.email_in_use(email, exclude_kind="instructor", exclude_id=iid_key):
                    raise ValueError(f"Email already in use: {email}")
                ins.name = name; ins.age = age; ins._email = email
                if iid != iid_key:
                    self.dm.instructors.pop(iid_key); self.dm.instructors[iid] = ins; ins.instructor_id = iid
            self._clear_form("instructors"); self._refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    def _add_or_update_course(self):
        try:
            cid = self.c_id.text().strip()
            cname = self.c_name.text().strip()
            ins_label = self.c_instructor.currentText().strip()
            if not ins_label: raise ValueError("Please select an instructor")
            ins_id = ins_label.split(" | ")[0]
            instructor = self.dm.instructors.get(ins_id)
            if instructor is None: raise ValueError("Instructor not found")
            if self.edit_mode["courses"] is None:
                course = Course(cid, cname, instructor)
                self.dm.add_course(course)
            else:
                cid_key = self.edit_mode["courses"]
                course = self.dm.courses[cid_key]
                if cid != cid_key and cid in self.dm.courses: raise ValueError(f"Duplicate course_id: {cid}")
                validate_nonempty_str(cname, "course_name")
                course.course_name = cname
                course.set_instructor(instructor)
                if cid != cid_key:
                    self.dm.courses.pop(cid_key); self.dm.courses[cid] = course; course.course_id = cid
            self._clear_form("courses"); self._refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    def _register_student_to_course(self):
        try:
            s_label = self.reg_student.currentText().strip()
            c_label = self.reg_course.currentText().strip()
            if not s_label or not c_label: raise ValueError("Select a student and a course")
            sid = s_label.split(" | ")[0]; cid = c_label.split(" | ")[0]
            stu = self.dm.students.get(sid); crs = self.dm.courses.get(cid)
            if not stu or not crs: raise ValueError("Invalid selection")
            crs.add_student(stu)
            self._refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    def _assign_instructor_to_course(self):
        try:
            i_label = self.asg_instructor.currentText().strip()
            c_label = self.asg_course.currentText().strip()
            if not i_label or not c_label: raise ValueError("Select an instructor and a course")
            iid = i_label.split(" | ")[0]; cid = c_label.split(" | ")[0]
            ins = self.dm.instructors.get(iid); crs = self.dm.courses.get(cid)
            if not ins or not crs: raise ValueError("Invalid selection")
            crs.set_instructor(ins)
            self._refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    def _edit_selected(self):
        tab = self.tabs.currentWidget()
        if tab is self.stu_table:
            vals = self._selected_row_values(self.stu_table)
            if not vals: QMessageBox.information(self,"Info","Select a student row to edit."); return
            sid, name, age, email = vals[0], vals[1], vals[2], vals[3]
            self.s_name.setText(name); self.s_age.setText(age); self.s_email.setText(email); self.s_id.setText(sid)
            self.edit_mode["students"] = sid; self.s_add_btn.setText("Update Student")
        elif tab is self.ins_table:
            vals = self._selected_row_values(self.ins_table)
            if not vals: QMessageBox.information(self,"Info","Select an instructor row to edit."); return
            iid, name, age, email = vals[0], vals[1], vals[2], vals[3]
            self.i_name.setText(name); self.i_age.setText(age); self.i_email.setText(email); self.i_id.setText(iid)
            self.edit_mode["instructors"] = iid; self.i_add_btn.setText("Update Instructor")
        elif tab is self.crs_table:
            vals = self._selected_row_values(self.crs_table)
            if not vals: QMessageBox.information(self,"Info","Select a course row to edit."); return
            cid, cname, instr = vals[0], vals[1], vals[2]
            self.c_id.setText(cid); self.c_name.setText(cname)
            try:
                iid = instr.split(" - ")[0]; ins = self.dm.instructors[iid]
                label = f"{iid} | {ins.name}"; idx = self.c_instructor.findText(label)
                if idx >= 0: self.c_instructor.setCurrentIndex(idx)
            except:
                pass
            self.edit_mode["courses"] = cid; self.c_add_btn.setText("Update Course")
    def _delete_selected(self):
        tab = self.tabs.currentWidget()
        try:
            if tab is self.stu_table:
                vals = self._selected_row_values(self.stu_table)
                if not vals: QMessageBox.information(self,"Info","Select a student row to delete."); return
                sid = vals[0]; stu = self.dm.students.get(sid)
                if stu:
                    for c in list(stu.registered_courses):
                        if stu in c.enrolled_students: c.enrolled_students.remove(stu)
                    self.dm.students.pop(sid, None)
            elif tab is self.ins_table:
                vals = self._selected_row_values(self.ins_table)
                if not vals: QMessageBox.information(self,"Info","Select an instructor row to delete."); return
                iid = vals[0]; ins = self.dm.instructors.get(iid)
                if ins:
                    for c in list(ins.assigned_courses):
                        try:
                            c.instructor = ins
                        except:
                            pass
                    self.dm.instructors.pop(iid, None)
                    QMessageBox.warning(self, "Warning", "Deleted instructor. Reassign affected courses.")
            elif tab is self.crs_table:
                vals = self._selected_row_values(self.crs_table)
                if not vals: QMessageBox.information(self,"Info","Select a course row to delete."); return
                cid = vals[0]; crs = self.dm.courses.get(cid)
                if crs:
                    for s in list(crs.enrolled_students):
                        if crs in s.registered_courses: s.registered_courses.remove(crs)
                    if crs in crs.instructor.assigned_courses:
                        crs.instructor.assigned_courses.remove(crs)
                    self.dm.courses.pop(cid, None)
            self._clear_form("students"); self._clear_form("instructors"); self._clear_form("courses")
            self._refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    def _clear_form(self, kind):
        if kind == "students":
            self.s_name.clear(); self.s_age.clear(); self.s_email.clear(); self.s_id.clear()
            self.edit_mode["students"] = None; self.s_add_btn.setText("Add Student")
        elif kind == "instructors":
            self.i_name.clear(); self.i_age.clear(); self.i_email.clear(); self.i_id.clear()
            self.edit_mode["instructors"] = None; self.i_add_btn.setText("Add Instructor")
        elif kind == "courses":
            self.c_id.clear(); self.c_name.clear(); self.c_instructor.setCurrentIndex(-1)
            self.edit_mode["courses"] = None; self.c_add_btn.setText("Add Course")
    def _save_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "JSON Files (*.json)")
        if not path: return
        try:
            self.dm.save_json(path)
            QMessageBox.information(self, "Saved", f"Saved to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    def _load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Data", "", "JSON Files (*.json)")
        if not path: return
        try:
            self.dm = DataManager.load_json(path)
            self._clear_form("students"); self._clear_form("instructors"); self._clear_form("courses")
            self._refresh_all()
            QMessageBox.information(self, "Loaded", f"Loaded from {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    def _export_csv(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Folder to Export CSVs")
        if not folder: return
        try:
            with open(f"{folder}/students.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["student_id","name","age","email","registered_courses"])
                for s in self.dm.students.values():
                    w.writerow([s.student_id, s.name, s.age, s._email, " ".join([c.course_id for c in s.registered_courses])])
            with open(f"{folder}/instructors.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["instructor_id","name","age","email","assigned_courses"])
                for ins in self.dm.instructors.values():
                    w.writerow([ins.instructor_id, ins.name, ins.age, ins._email, " ".join([c.course_id for c in ins.assigned_courses])])
            with open(f"{folder}/courses.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["course_id","course_name","instructor_id","instructor_name","enrolled_students"])
                for c in self.dm.courses.values():
                    w.writerow([c.course_id, c.course_name, c.instructor.instructor_id, c.instructor.name, " ".join([s.student_id for s in c.enrolled_students])])
            QMessageBox.information(self, "Exported", f"CSV files saved in {folder}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SchoolQt()
    w.show()
    sys.exit(app.exec_())