import sys, json, csv, re, sqlite3  # Standard libraries
from typing import List
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,QLabel, QLineEdit, QPushButton, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem,QMessageBox, QFileDialog, QAction, QToolBar)
from PyQt5.QtCore import Qt
from db import DB, create_schema  # Database helpers

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")  # Simple email validation

def validate_nonempty_str(value: str, field: str):
    """Raise error if value is not a non-empty string."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")

def validate_nonneg_int(value: int, field: str):
    """Raise error if value is not a non-negative integer."""
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")

def validate_email(email: str):
    """Raise error if email is not valid."""
    if not isinstance(email, str) or not EMAIL_REGEX.match(email):
        raise ValueError(f"Invalid email: {email}")

class SchoolQt(QMainWindow):
    """
    Main window for the school management system.
    Handles all UI and database interactions.
    """
    def __init__(self):
        # Set up window, database, and UI
        super().__init__()
        self.setWindowTitle("School Management System")
        self.resize(1200, 750)
        create_schema("school.sqlite")
        self.db = DB("school.sqlite")
        self.edit_mode = {"students": None, "instructors": None, "courses": None}
        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
        # Build all UI sections
        self._build_menu_toolbar()
        central = QWidget()
        root = QVBoxLayout(central)
        root.addLayout(self._forms_section())
        root.addLayout(self._actions_section())
        root.addLayout(self._search_section())
        root.addWidget(self._tables_section())
        self.setCentralWidget(central)

    def _build_menu_toolbar(self):
        # Create menu and toolbar actions
        save_act = QAction("Save Snapshot (JSON)...", self); save_act.triggered.connect(self._save_json)
        load_act = QAction("Load Snapshot (JSON)...", self); load_act.triggered.connect(self._load_json)
        export_act = QAction("Export CSV...", self); export_act.triggered.connect(self._export_csv)
        toolbar = QToolBar("Main"); self.addToolBar(toolbar)
        toolbar.addAction(save_act); toolbar.addAction(load_act); toolbar.addAction(export_act)

    def _forms_section(self):
        # Build forms for adding/editing entities
        layout = QHBoxLayout()
        layout.addWidget(self._student_form())
        layout.addWidget(self._instructor_form())
        layout.addWidget(self._course_form())
        return layout

    def _student_form(self):
        # Student form UI
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
        # Instructor form UI
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
        # Course form UI
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
        # Section for registering students and assigning instructors
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
        # Search bar section
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Search (Name / ID / Course):"))
        self.search_edit = QLineEdit()
        go = QPushButton("Search"); go.clicked.connect(self._apply_search)
        clr = QPushButton("Clear"); clr.clicked.connect(self._clear_search)
        layout.addWidget(self.search_edit); layout.addWidget(go); layout.addWidget(clr); layout.addStretch(1)
        return layout

    def _tables_section(self):
        # Tables for displaying students, instructors, and courses
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
        # Update dropdowns with current data from DB
        self.c_instructor.clear()
        self.c_instructor.addItems([f"{i['instructor_id']} | {i['name']}" for i in self.db.list_instructors()])
        self.reg_student.clear()
        self.reg_student.addItems([f"{s['student_id']} | {s['name']}" for s in self.db.list_students()])
        self.reg_course.clear()
        self.reg_course.addItems([f"{c['course_id']} | {c['course_name']}" for c in self.db.list_courses()])
        self.asg_instructor.clear()
        self.asg_instructor.addItems([f"{i['instructor_id']} | {i['name']}" for i in self.db.list_instructors()])
        self.asg_course.clear()
        self.asg_course.addItems([f"{c['course_id']} | {c['course_name']}" for c in self.db.list_courses()])

    def _refresh_tables(self, q: str = ""):
        # Refresh all tables based on search query
        q = q.lower().strip()
        self.stu_table.setRowCount(0)
        for s in self.db.list_students():
            courses = ", ".join(self.db.list_student_courses(s["student_id"]))
            if not q or q in s["student_id"].lower() or q in s["name"].lower() or q in courses.lower():
                r = self.stu_table.rowCount(); self.stu_table.insertRow(r)
                for col, val in enumerate([s["student_id"], s["name"], str(s["age"]), s["email"], courses]):
                    self.stu_table.setItem(r, col, QTableWidgetItem(val))
        self.ins_table.setRowCount(0)
        for ins in self.db.list_instructors():
            rows = self.db.conn.execute(
                "SELECT course_id FROM courses WHERE instructor_id=? ORDER BY course_id",
                (ins["instructor_id"],)
            ).fetchall()
            courses_str = ", ".join([r["course_id"] for r in rows])
            if not q or q in ins["instructor_id"].lower() or q in ins["name"].lower() or q in courses_str.lower():
                r = self.ins_table.rowCount(); self.ins_table.insertRow(r)
                for col, val in enumerate([ins["instructor_id"], ins["name"], str(ins["age"]), ins["email"], courses_str]):
                    self.ins_table.setItem(r, col, QTableWidgetItem(val))
        self.crs_table.setRowCount(0)
        for c in self.db.list_courses():
            students_str = ", ".join(self.db.list_course_students(c["course_id"]))
            instr_label = f"{c['instructor_id'] or ''} - {c.get('instructor_name') or ''}"
            if not q or q in c["course_id"].lower() or q in c["course_name"].lower() or q in students_str.lower():
                r = self.crs_table.rowCount(); self.crs_table.insertRow(r)
                for col, val in enumerate([c["course_id"], c["course_name"], instr_label, students_str]):
                    self.crs_table.setItem(r, col, QTableWidgetItem(val))
        for table in (self.stu_table, self.ins_table, self.crs_table):
            table.resizeColumnsToContents()

    def _refresh_all(self):
        # Refresh dropdowns and tables
        self._refresh_dropdowns()
        self._refresh_tables()

    def _apply_search(self):
        # Apply search filter
        self._refresh_tables(self.search_edit.text())

    def _clear_search(self):
        # Clear search filter
        self.search_edit.setText("")
        self._refresh_tables("")

    def _parse_int(self, s: str, field: str) -> int:
        # Parse integer from string, raise error if invalid
        try:
            return int(s.strip())
        except:
            raise ValueError(f"{field} must be an integer")

    def _selected_row_values(self, table: QTableWidget) -> List[str]:
        # Get values from the selected row in a table
        rows = table.selectionModel().selectedRows()
        if not rows: return []
        row = rows[0].row()
        return [table.item(row, c).text() if table.item(row, c) else "" for c in range(table.columnCount())]

    def _add_or_update_student(self):
        # Add or update a student in the database
        try:
            name = self.s_name.text().strip()
            age = self._parse_int(self.s_age.text(), "age")
            email = self.s_email.text().strip()
            sid = self.s_id.text().strip()
            validate_nonempty_str(name,"name"); validate_nonneg_int(age,"age"); validate_email(email); validate_nonempty_str(sid,"student_id")
            if self.edit_mode["students"] is None:
                self.db.create_student(sid, name, age, email)
            else:
                sid_key = self.edit_mode["students"]
                self.db.update_student(sid_key, name, age, email)
                if sid != sid_key:
                    self.db.delete_student(sid)
                    self.db.create_student(sid, name, age, email)
            self._clear_form("students"); self._refresh_all()
        except sqlite3.IntegrityError as e:
            QMessageBox.critical(self, "Error", f"DB constraint failed: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _add_or_update_instructor(self):
        # Add or update an instructor in the database
        try:
            name = self.i_name.text().strip()
            age = self._parse_int(self.i_age.text(), "age")
            email = self.i_email.text().strip()
            iid = self.i_id.text().strip()
            validate_nonempty_str(name,"name"); validate_nonneg_int(age,"age"); validate_email(email); validate_nonempty_str(iid,"instructor_id")
            if self.edit_mode["instructors"] is None:
                self.db.create_instructor(iid, name, age, email)
            else:
                iid_key = self.edit_mode["instructors"]
                self.db.update_instructor(iid_key, name, age, email)
                if iid != iid_key:
                    self.db.delete_instructor(iid)
                    self.db.create_instructor(iid, name, age, email)
            self._clear_form("instructors"); self._refresh_all()
        except sqlite3.IntegrityError as e:
            QMessageBox.critical(self, "Error", f"DB constraint failed: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _add_or_update_course(self):
        # Add or update a course in the database
        try:
            cid = self.c_id.text().strip()
            cname = self.c_name.text().strip()
            ins_label = self.c_instructor.currentText().strip()
            validate_nonempty_str(cid,"course_id"); validate_nonempty_str(cname,"course_name")
            if not ins_label: raise ValueError("Please select an instructor")
            ins_id = ins_label.split(" | ")[0]
            if self.edit_mode["courses"] is None:
                self.db.create_course(cid, cname, ins_id)
            else:
                cid_key = self.edit_mode["courses"]
                self.db.update_course(cid_key, course_name=cname, instructor_id=ins_id)
                if cid != cid_key:
                    self.db.delete_course(cid)
                    self.db.create_course(cid, cname, ins_id)
            self._clear_form("courses"); self._refresh_all()
        except sqlite3.IntegrityError as e:
            QMessageBox.critical(self, "Error", f"DB constraint failed: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _register_student_to_course(self):
        # Register a student to a selected course
        try:
            s_label = self.reg_student.currentText().strip()
            c_label = self.reg_course.currentText().strip()
            if not s_label or not c_label: raise ValueError("Select a student and a course")
            sid = s_label.split(" | ")[0]; cid = c_label.split(" | ")[0]
            self.db.register_student(sid, cid)
            self._refresh_all()
        except sqlite3.IntegrityError as e:
            QMessageBox.critical(self, "Error", f"DB constraint failed: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _assign_instructor_to_course(self):
        # Assign an instructor to a selected course
        try:
            i_label = self.asg_instructor.currentText().strip()
            c_label = self.asg_course.currentText().strip()
            if not i_label or not c_label: raise ValueError("Select an instructor and a course")
            iid = i_label.split(" | ")[0]; cid = c_label.split(" | ")[0]
            self.db.update_course(cid, instructor_id=iid)
            self._refresh_all()
        except sqlite3.IntegrityError as e:
            QMessageBox.critical(self, "Error", f"DB constraint failed: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _edit_selected(self):
        # Edit the selected row in the current table
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
                iid = (instr.split(" - ")[0]).strip()
                if iid:
                    label = None
                    for i in self.db.list_instructors():
                        if i["instructor_id"] == iid:
                            label = f"{iid} | {i['name']}"
                            break
                    if label:
                        idx = self.c_instructor.findText(label)
                        if idx >= 0: self.c_instructor.setCurrentIndex(idx)
            except:
                pass
            self.edit_mode["courses"] = cid; self.c_add_btn.setText("Update Course")

    def _delete_selected(self):
        # Delete the selected row in the current table
        tab = self.tabs.currentWidget()
        try:
            if tab is self.stu_table:
                vals = self._selected_row_values(self.stu_table)
                if not vals: QMessageBox.information(self,"Info","Select a student row to delete."); return
                sid = vals[0]
                self.db.delete_student(sid)
            elif tab is self.ins_table:
                vals = self._selected_row_values(self.ins_table)
                if not vals: QMessageBox.information(self,"Info","Select an instructor row to delete."); return
                iid = vals[0]
                self.db.delete_instructor(iid) 
                QMessageBox.warning(self, "Warning", "Deleted instructor. Reassign affected courses.")
            elif tab is self.crs_table:
                vals = self._selected_row_values(self.crs_table)
                if not vals: QMessageBox.information(self,"Info","Select a course row to delete."); return
                cid = vals[0]
                self.db.delete_course(cid)
            self._clear_form("students"); self._clear_form("instructors"); self._clear_form("courses")
            self._refresh_all()
        except sqlite3.IntegrityError as e:
            QMessageBox.critical(self, "Error", f"DB constraint failed: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _clear_form(self, kind):
        # Clear the form fields for the given entity type
        if kind == "students":
            self.s_name.clear(); self.s_age.clear(); self.s_email.clear(); self.s_id.clear()
            self.edit_mode["students"] = None; self.s_add_btn.setText("Add Student")
        elif kind == "instructors":
            self.i_name.clear(); self.i_age.clear(); self.i_email.clear(); self.i_id.clear()
            self.edit_mode["instructors"] = None; self.i_add_btn.setText("Add Instructor")
        elif kind == "courses":
            self.c_id.clear(); self.c_name.clear(); self.c_instructor.setCurrentIndex(-1)
            self.edit_mode["courses"] = None; self.c_add_btn.setText("Add Course")

    def _snapshot(self):
        # Take a snapshot of all data for export
        students = self.db.list_students()
        instructors = self.db.list_instructors()
        courses = self.db.list_courses()
        regs = [dict(r) for r in self.db.conn.execute("SELECT student_id, course_id FROM registrations ORDER BY student_id, course_id")]
        return {"students": students, "instructors": instructors, "courses": courses, "registrations": regs}

    def _clear_all_tables(self):
        # Remove all data from all tables in the DB
        self.db.conn.execute("DELETE FROM registrations")
        self.db.conn.execute("DELETE FROM courses")
        self.db.conn.execute("DELETE FROM students")
        self.db.conn.execute("DELETE FROM instructors")
        self.db.conn.commit()

    def _save_json(self):
        # Save all data to a JSON file
        path, _ = QFileDialog.getSaveFileName(self, "Save Snapshot", "", "JSON Files (*.json)")
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._snapshot(), f, indent=2)
            QMessageBox.information(self, "Saved", f"Saved to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _load_json(self):
        # Load all data from a JSON file
        path, _ = QFileDialog.getOpenFileName(self, "Load Snapshot", "", "JSON Files (*.json)")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._clear_all_tables()
            for i in data.get("instructors", []):
                self.db.create_instructor(i["instructor_id"], i["name"], int(i["age"]), i["email"])
            for s in data.get("students", []):
                self.db.create_student(s["student_id"], s["name"], int(s["age"]), s["email"])
            for c in data.get("courses", []):
                self.db.create_course(c["course_id"], c["course_name"], c.get("instructor_id"))
            for r in data.get("registrations", []):
                self.db.register_student(r["student_id"], r["course_id"])
            self._clear_form("students"); self._clear_form("instructors"); self._clear_form("courses")
            self._refresh_all()
            QMessageBox.information(self, "Loaded", f"Loaded from {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _export_csv(self):
        # Export all data to CSV files
        folder = QFileDialog.getExistingDirectory(self, "Choose Folder to Export CSVs")
        if not folder: return
        try:
            with open(f"{folder}/students.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["student_id","name","age","email","registered_courses"])
                for s in self.db.list_students():
                    courses = " ".join(self.db.list_student_courses(s["student_id"]))
                    w.writerow([s["student_id"], s["name"], s["age"], s["email"], courses])
            with open(f"{folder}/instructors.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["instructor_id","name","age","email","assigned_courses"])
                for ins in self.db.list_instructors():
                    rows = self.db.conn.execute(
                        "SELECT course_id FROM courses WHERE instructor_id=? ORDER BY course_id",
                        (ins["instructor_id"],)
                    ).fetchall()
                    courses = " ".join([r["course_id"] for r in rows])
                    w.writerow([ins["instructor_id"], ins["name"], ins["age"], ins["email"], courses])
            with open(f"{folder}/courses.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["course_id","course_name","instructor_id","instructor_name","enrolled_students"])
                for c in self.db.list_courses():
                    students = " ".join(self.db.list_course_students(c["course_id"]))
                    w.writerow([c["course_id"], c["course_name"], c["instructor_id"] or "", c.get("instructor_name") or "", students])
            QMessageBox.information(self, "Exported", f"CSV files saved in {folder}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    # Entry point: start the application
    app = QApplication(sys.argv)
    w = SchoolQt()
    w.show()
    sys.exit(app.exec_())