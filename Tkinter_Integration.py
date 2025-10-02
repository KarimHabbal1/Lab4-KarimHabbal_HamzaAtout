"""
School Management System - Tkinter GUI Application

This module provides a complete school management system with a graphical user interface
built using Tkinter. It manages students, instructors, and courses with full CRUD operations
and data persistence using SQLite database.

Author: Lab4 Team
Course: EECE435L
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, csv, re, sqlite3
from typing import List
from db import DB, create_schema

# Regular expression pattern for validating email addresses
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

def validate_nonempty_str(value: str, field: str):
    """
    Validates that a string value is not empty or just whitespace.
    
    Args:
        value (str): The string value to validate
        field (str): The name of the field being validated (for error messages)
    
    Raises:
        ValueError: If the value is not a string or is empty/whitespace
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")

def validate_nonneg_int(value: int, field: str):
    """
    Validates that an integer value is non-negative.
    
    Args:
        value (int): The integer value to validate
        field (str): The name of the field being validated (for error messages)
    
    Raises:
        ValueError: If the value is not an integer or is negative
    """
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")

def validate_email(email: str):
    """
    Validates that an email address matches the required format.
    
    Args:
        email (str): The email address to validate
    
    Raises:
        ValueError: If the email format is invalid
    """
    if not isinstance(email, str) or not EMAIL_REGEX.match(email):
        raise ValueError(f"Invalid email: {email}")

class SchoolApp(tk.Tk):
    """
    Main application class for the School Management System.
    
    This class creates and manages the complete GUI for handling students,
    instructors, and courses. It inherits from tk.Tk to create the main window
    and provides all the functionality for data entry, editing, and viewing.
    """
    
    def __init__(self):
        """
        Initialize the School Management System application.
        
        Sets up the main window, database connection, and all GUI components
        including forms, tables, and menu systems.
        """
        super().__init__()
        # Configure main window properties
        self.title("School Management System")
        self.geometry("1100x700")
        self.resizable(True, True)
        
        # Initialize database and connection
        create_schema("school.sqlite")
        self.db = DB("school.sqlite")
        
        # Build all GUI components
        self._build_menu()
        self._build_forms()
        self._build_actions()
        self._build_notebook()
        self._build_search()
        
        # Load initial data and setup
        self._refresh_all_views()
        self._refresh_dropdowns()
        
        # Track which records are being edited
        self.edit_mode = {"students": None, "instructors": None, "courses": None}

    def _build_menu(self):
        """
        Creates the application menu bar with file operations.
        
        Builds a menu system that allows users to save/load data snapshots
        and export data to CSV format.
        """
        menubar = tk.Menu(self)
        
        # Create File menu with import/export options
        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="Save Snapshot (JSON)...", command=self._save_to_file)
        filemenu.add_command(label="Load Snapshot (JSON)...", command=self._load_from_file)
        filemenu.add_command(label="Export CSV...", command=self._export_csv)
        
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

    def _build_forms(self):
        """
        Creates the data entry forms for students, instructors, and courses.
        
        Builds three side-by-side forms that allow users to add or edit
        student, instructor, and course information with appropriate input fields.
        """
        # Main container for all forms
        forms_frame = ttk.LabelFrame(self, text="Forms")
        forms_frame.pack(fill="x", padx=10, pady=10)
        
        # Student form section
        sf = ttk.Frame(forms_frame)
        sf.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        ttk.Label(sf, text="Add / Edit Student").grid(row=0, column=0, columnspan=4, sticky="w")
        
        # Student form labels
        ttk.Label(sf, text="Name").grid(row=1, column=0, sticky="e")
        ttk.Label(sf, text="Age").grid(row=1, column=2, sticky="e")
        ttk.Label(sf, text="Email").grid(row=2, column=0, sticky="e")
        ttk.Label(sf, text="Student ID").grid(row=2, column=2, sticky="e")
        
        # Student form input fields
        self.s_name = ttk.Entry(sf, width=20)
        self.s_age = ttk.Entry(sf, width=8)
        self.s_email = ttk.Entry(sf, width=25)
        self.s_id = ttk.Entry(sf, width=15)
        
        # Position student form fields
        self.s_name.grid(row=1, column=1, padx=5)
        self.s_age.grid(row=1, column=3, padx=5)
        self.s_email.grid(row=2, column=1, padx=5)
        self.s_id.grid(row=2, column=3, padx=5)
        
        # Student form buttons
        self.s_add_btn = ttk.Button(sf, text="Add Student", command=self._add_or_update_student)
        self.s_add_btn.grid(row=3, column=1, pady=5, sticky="w")
        ttk.Button(sf, text="Clear", command=lambda: self._clear_form("students")).grid(row=3, column=3, pady=5, sticky="e")
        
        # Instructor form section
        inf = ttk.Frame(forms_frame)
        inf.grid(row=0, column=1, padx=10, pady=10, sticky="nw")
        ttk.Label(inf, text="Add / Edit Instructor").grid(row=0, column=0, columnspan=4, sticky="w")
        
        # Instructor form labels
        ttk.Label(inf, text="Name").grid(row=1, column=0, sticky="e")
        ttk.Label(inf, text="Age").grid(row=1, column=2, sticky="e")
        ttk.Label(inf, text="Email").grid(row=2, column=0, sticky="e")
        ttk.Label(inf, text="Instructor ID").grid(row=2, column=2, sticky="e")
        
        # Instructor form input fields
        self.i_name = ttk.Entry(inf, width=20)
        self.i_age = ttk.Entry(inf, width=8)
        self.i_email = ttk.Entry(inf, width=25)
        self.i_id = ttk.Entry(inf, width=15)
        
        # Position instructor form fields
        self.i_name.grid(row=1, column=1, padx=5)
        self.i_age.grid(row=1, column=3, padx=5)
        self.i_email.grid(row=2, column=1, padx=5)
        self.i_id.grid(row=2, column=3, padx=5)
        
        # Instructor form buttons
        self.i_add_btn = ttk.Button(inf, text="Add Instructor", command=self._add_or_update_instructor)
        self.i_add_btn.grid(row=3, column=1, pady=5, sticky="w")
        ttk.Button(inf, text="Clear", command=lambda: self._clear_form("instructors")).grid(row=3, column=3, pady=5, sticky="e")
        
        # Course form section
        cf = ttk.Frame(forms_frame)
        cf.grid(row=0, column=2, padx=10, pady=10, sticky="nw")
        ttk.Label(cf, text="Add / Edit Course").grid(row=0, column=0, columnspan=4, sticky="w")
        
        # Course form labels
        ttk.Label(cf, text="Course ID").grid(row=1, column=0, sticky="e")
        ttk.Label(cf, text="Name").grid(row=1, column=2, sticky="e")
        ttk.Label(cf, text="Instructor").grid(row=2, column=0, sticky="e")
        
        # Course form input fields
        self.c_id = ttk.Entry(cf, width=15)
        self.c_name = ttk.Entry(cf, width=25)
        self.c_instructor = ttk.Combobox(cf, state="readonly", values=[])  # Dropdown for selecting instructor
        
        # Position course form fields
        self.c_id.grid(row=1, column=1, padx=5)
        self.c_name.grid(row=1, column=3, padx=5)
        self.c_instructor.grid(row=2, column=1, padx=5, sticky="w")
        
        # Course form buttons
        self.c_add_btn = ttk.Button(cf, text="Add Course", command=self._add_or_update_course)
        self.c_add_btn.grid(row=3, column=1, pady=5, sticky="w")
        ttk.Button(cf, text="Clear", command=lambda: self._clear_form("courses")).grid(row=3, column=3, pady=5, sticky="e")

    def _build_actions(self):
        """
        Creates the enrollment and assignment section.
        
        Builds interface elements for registering students to courses
        and assigning instructors to courses using dropdown selections.
        """
        # Main actions container
        act = ttk.LabelFrame(self, text="Enrollment & Assignment")
        act.pack(fill="x", padx=10, pady=5)
        
        # Student registration section
        ttk.Label(act, text="Register Student to Course").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0,5))
        ttk.Label(act, text="Student").grid(row=1, column=0, sticky="e")
        ttk.Label(act, text="Course").grid(row=1, column=2, sticky="e")
        
        # Dropdown menus for student registration
        self.reg_student_cb = ttk.Combobox(act, state="readonly", values=[], width=25)
        self.reg_course_cb = ttk.Combobox(act, state="readonly", values=[], width=25)
        self.reg_student_cb.grid(row=1, column=1, padx=5, pady=2)
        self.reg_course_cb.grid(row=1, column=3, padx=5, pady=2)
        ttk.Button(act, text="Register", command=self._register_student_to_course).grid(row=1, column=4, padx=8)
        
        # Instructor assignment section
        ttk.Label(act, text="Assign Instructor to Course").grid(row=2, column=0, columnspan=4, sticky="w", pady=(10,5))
        ttk.Label(act, text="Instructor").grid(row=3, column=0, sticky="e")
        ttk.Label(act, text="Course").grid(row=3, column=2, sticky="e")
        
        # Dropdown menus for instructor assignment
        self.asg_instructor_cb = ttk.Combobox(act, state="readonly", values=[], width=25)
        self.asg_course_cb = ttk.Combobox(act, state="readonly", values=[], width=25)
        self.asg_instructor_cb.grid(row=3, column=1, padx=5, pady=2)
        self.asg_course_cb.grid(row=3, column=3, padx=5, pady=2)
        ttk.Button(act, text="Assign", command=self._assign_instructor_to_course).grid(row=3, column=4, padx=8)

    def _build_notebook(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        self.students_tab = ttk.Frame(nb)
        nb.add(self.students_tab, text="Students")
        self.students_tab.rowconfigure(0, weight=1)
        self.students_tab.columnconfigure(0, weight=1)
        self.students_tv = ttk.Treeview(
            self.students_tab,
            columns=("id","name","age","email","courses"),
            show="headings",
            selectmode="browse"
        )
        for col, txt, w in [
            ("id","Student ID",120),("name","Name",180),("age","Age",60),
            ("email","Email",220),("courses","Registered Courses",320)
        ]:
            self.students_tv.heading(col, text=txt)
            self.students_tv.column(col, width=w, anchor="w")
        stu_y = ttk.Scrollbar(self.students_tab, orient="vertical", command=self.students_tv.yview)
        stu_x = ttk.Scrollbar(self.students_tab, orient="horizontal", command=self.students_tv.xview)
        self.students_tv.configure(yscrollcommand=stu_y.set, xscrollcommand=stu_x.set)
        self.students_tv.grid(row=0, column=0, sticky="nsew", padx=(5,0), pady=(5,0))
        stu_y.grid(row=0, column=1, sticky="ns", padx=(0,5), pady=(5,0))
        stu_x.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0,5))
        self.students_tv.bind("<Double-1>", lambda e: self._load_selected_into_form("students"))
        self.instructors_tab = ttk.Frame(nb)
        nb.add(self.instructors_tab, text="Instructors")
        self.instructors_tab.rowconfigure(0, weight=1)
        self.instructors_tab.columnconfigure(0, weight=1)
        self.instructors_tv = ttk.Treeview(
            self.instructors_tab,
            columns=("id","name","age","email","courses"),
            show="headings",
            selectmode="browse"
        )
        for col, txt, w in [
            ("id","Instructor ID",120),("name","Name",180),("age","Age",60),
            ("email","Email",220),("courses","Assigned Courses",320)
        ]:
            self.instructors_tv.heading(col, text=txt)
            self.instructors_tv.column(col, width=w, anchor="w")
        ins_y = ttk.Scrollbar(self.instructors_tab, orient="vertical", command=self.instructors_tv.yview)
        ins_x = ttk.Scrollbar(self.instructors_tab, orient="horizontal", command=self.instructors_tv.xview)
        self.instructors_tv.configure(yscrollcommand=ins_y.set, xscrollcommand=ins_x.set)
        self.instructors_tv.grid(row=0, column=0, sticky="nsew", padx=(5,0), pady=(5,0))
        ins_y.grid(row=0, column=1, sticky="ns", padx=(0,5), pady=(5,0))
        ins_x.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0,5))
        self.instructors_tv.bind("<Double-1>", lambda e: self._load_selected_into_form("instructors"))
        self.courses_tab = ttk.Frame(nb)
        nb.add(self.courses_tab, text="Courses")
        self.courses_tab.rowconfigure(0, weight=1)
        self.courses_tab.columnconfigure(0, weight=1)
        self.courses_tv = ttk.Treeview(
            self.courses_tab,
            columns=("id","name","instructor","students"),
            show="headings",
            selectmode="browse"
        )
        for col, txt, w in [
            ("id","Course ID",120),("name","Course Name",220),
            ("instructor","Instructor",200),("students","Enrolled Students",420)
        ]:
            self.courses_tv.heading(col, text=txt)
            self.courses_tv.column(col, width=w, anchor="w")

        crs_y = ttk.Scrollbar(self.courses_tab, orient="vertical", command=self.courses_tv.yview)
        crs_x = ttk.Scrollbar(self.courses_tab, orient="horizontal", command=self.courses_tv.xview)
        self.courses_tv.configure(yscrollcommand=crs_y.set, xscrollcommand=crs_x.set)
        self.courses_tv.grid(row=0, column=0, sticky="nsew", padx=(5,0), pady=(5,0))
        crs_y.grid(row=0, column=1, sticky="ns", padx=(0,5), pady=(5,0))
        crs_x.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0,5))
        self.courses_tv.bind("<Double-1>", lambda e: self._load_selected_into_form("courses"))
        ctl = ttk.Frame(self)
        ctl.pack(fill="x", padx=10, pady=5)
        ttk.Button(ctl, text="Edit Selected", command=self._edit_selected).pack(side="left")
        ttk.Button(ctl, text="Delete Selected", command=self._delete_selected).pack(side="left", padx=8)

    def _build_search(self):
        """
        Creates the search interface for filtering displayed records.
        
        Builds a search bar that allows users to filter students, instructors,
        and courses by name, ID, or course associations.
        """
        # Search container
        bar = ttk.LabelFrame(self, text="Search")
        bar.pack(fill="x", padx=10, pady=5)
        
        # Search components
        ttk.Label(bar, text="Query (Name / ID / Course)").pack(side="left", padx=6)
        self.search_var = tk.StringVar()  # Variable to hold search text
        self.search_entry = ttk.Entry(bar, textvariable=self.search_var, width=40)
        self.search_entry.pack(side="left", padx=6)
        
        # Search action buttons
        ttk.Button(bar, text="Search", command=self._apply_search).pack(side="left", padx=6)
        ttk.Button(bar, text="Clear", command=self._clear_search).pack(side="left", padx=6)

    def _add_or_update_student(self):
        """
        Adds a new student or updates an existing student's information.
        
        Validates form input, then either creates a new student record
        or updates an existing one based on the current edit mode.
        """
        try:
            # Get form values and validate them
            name = self.s_name.get().strip()
            age = int(self.s_age.get().strip())
            email = self.s_email.get().strip()
            sid = self.s_id.get().strip()
            
            # Validate all input fields
            validate_nonempty_str(name,"name"); validate_nonneg_int(age,"age"); validate_email(email); validate_nonempty_str(sid,"student_id")
            
            # Add new student or update existing one
            if self.edit_mode["students"] is None:
                self.db.create_student(sid, name, age, email)
            else:
                # Update existing student
                sid_key = self.edit_mode["students"]
                self.db.update_student(sid_key, name, age, email)
                # Handle ID changes by creating new record if needed
                if sid != sid_key:                    
                    try:
                        self.db.delete_student(sid)
                    except sqlite3.IntegrityError:
                        pass
                    self.db.create_student(sid, name, age, email)
            
            # Reset form and refresh displays
            self._clear_form("students")
            self._refresh_all_views(); self._refresh_dropdowns()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"DB constraint failed: {e}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _add_or_update_instructor(self):
        try:
            name = self.i_name.get().strip()
            age = int(self.i_age.get().strip())
            email = self.i_email.get().strip()
            iid = self.i_id.get().strip()
            validate_nonempty_str(name,"name"); validate_nonneg_int(age,"age"); validate_email(email); validate_nonempty_str(iid,"instructor_id")
            if self.edit_mode["instructors"] is None:
                self.db.create_instructor(iid, name, age, email)
            else:
                iid_key = self.edit_mode["instructors"]
                self.db.update_instructor(iid_key, name, age, email)
                if iid != iid_key:
                    try:
                        self.db.delete_instructor(iid)
                    except sqlite3.IntegrityError:
                        pass
                    self.db.create_instructor(iid, name, age, email)
            self._clear_form("instructors")
            self._refresh_all_views(); self._refresh_dropdowns()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"DB constraint failed: {e}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _add_or_update_course(self):
        try:
            cid = self.c_id.get().strip()
            cname = self.c_name.get().strip()
            ins_label = self.c_instructor.get().strip()
            validate_nonempty_str(cid,"course_id"); validate_nonempty_str(cname,"course_name")
            if not ins_label:
                raise ValueError("Please select an instructor")
            ins_id = ins_label.split(" | ")[0]
            if self.edit_mode["courses"] is None:
                self.db.create_course(cid, cname, ins_id)
            else:
                cid_key = self.edit_mode["courses"]
                self.db.update_course(cid_key, course_name=cname, instructor_id=ins_id)
                if cid != cid_key:
                    try:
                        self.db.delete_course(cid)
                    except sqlite3.IntegrityError:
                        pass
                    self.db.create_course(cid, cname, ins_id)
            self._clear_form("courses")
            self._refresh_all_views(); self._refresh_dropdowns()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"DB constraint failed: {e}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _register_student_to_course(self):
        try:
            s_label = self.reg_student_cb.get().strip()
            c_label = self.reg_course_cb.get().strip()
            if not s_label or not c_label:
                raise ValueError("Select a student and a course")
            sid = s_label.split(" | ")[0]
            cid = c_label.split(" | ")[0]
            self.db.register_student(sid, cid)
            self._refresh_all_views()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"DB constraint failed: {e}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _assign_instructor_to_course(self):
        try:
            i_label = self.asg_instructor_cb.get().strip()
            c_label = self.asg_course_cb.get().strip()
            if not i_label or not c_label:
                raise ValueError("Select an instructor and a course")
            iid = i_label.split(" | ")[0]
            cid = c_label.split(" | ")[0]
            self.db.update_course(cid, instructor_id=iid)  
            self._refresh_all_views(); self._refresh_dropdowns()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"DB constraint failed: {e}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _refresh_all_views(self, filtered_query: str = ""):
        """
        Updates all data display tables with current database information.
        
        Args:
            filtered_query (str): Optional search query to filter displayed records
        
        Refreshes the student, instructor, and course tables with the latest
        data from the database, applying any search filters if provided.
        """
        # Convert search query to lowercase for case-insensitive matching
        q = filtered_query.lower().strip()
        
        # Refresh students table
        self.students_tv.delete(*self.students_tv.get_children())
        for s in self.db.list_students():
            courses_str = ", ".join(self.db.list_student_courses(s["student_id"]))
            row = (s["student_id"], s["name"], s["age"], s["email"], courses_str)
            # Show row if no filter or if filter matches ID, name, or courses
            if not q or q in s["student_id"].lower() or q in s["name"].lower() or q in courses_str.lower():
                self.students_tv.insert("", "end", iid=f"stu:{s['student_id']}", values=row)
        
        # Refresh instructors table
        self.instructors_tv.delete(*self.instructors_tv.get_children())
        ins_list = self.db.list_instructors()
        for ins in ins_list:
            rows = self.db.conn.execute(
                "SELECT course_id FROM courses WHERE instructor_id=? ORDER BY course_id",
                (ins["instructor_id"],)
            ).fetchall()
            courses_str = ", ".join([r["course_id"] for r in rows])
            row = (ins["instructor_id"], ins["name"], ins["age"], ins["email"], courses_str)
            # Show row if no filter or if filter matches ID, name, or courses
            if not q or q in ins["instructor_id"].lower() or q in ins["name"].lower() or q in courses_str.lower():
                self.instructors_tv.insert("", "end", iid=f"ins:{ins['instructor_id']}", values=row)
        
        # Refresh courses table
        self.courses_tv.delete(*self.courses_tv.get_children())
        for c in self.db.list_courses():
            students_str = ", ".join(self.db.list_course_students(c["course_id"]))
            instr_label = f"{(c['instructor_id'] or '').strip()} - {(c.get('instructor_name') or '').strip()}"
            row = (c["course_id"], c["course_name"], instr_label, students_str)
            # Show row if no filter or if filter matches ID, name, or students
            if not q or q in c["course_id"].lower() or q in c["course_name"].lower() or q in students_str.lower():
                self.courses_tv.insert("", "end", iid=f"crs:{c['course_id']}", values=row)

    def _apply_search(self):
        """
        Applies the current search query to filter displayed records.
        """
        self._refresh_all_views(self.search_var.get())

    def _clear_search(self):
        """
        Clears the search query and shows all records.
        """
        self.search_var.set("")
        self._refresh_all_views()

    def _edit_selected(self):
        tv, kind = self._current_tv_and_kind()
        if not tv:
            return
        sel = tv.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a row to edit.")
            return
        self._load_selected_into_form(kind)

    def _delete_selected(self):
        tv, kind = self._current_tv_and_kind()
        if not tv:
            return
        sel = tv.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a row to delete.")
            return
        iid = sel[0]
        try:
            if kind == "students":
                sid = iid.split("stu:")[1]
                self.db.delete_student(sid)
            elif kind == "instructors":
                insid = iid.split("ins:")[1]
                self.db.delete_instructor(insid) 
                messagebox.showwarning("Warning", "Deleted instructor. Courses taught by them should be reassigned.")
            elif kind == "courses":
                cid = iid.split("crs:")[1]
                self.db.delete_course(cid)
            self._refresh_all_views()
            self._refresh_dropdowns()
            self._clear_form(kind)
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"DB constraint failed: {e}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load_selected_into_form(self, kind):
        tv = {"students": self.students_tv, "instructors": self.instructors_tv, "courses": self.courses_tv}[kind]
        sel = tv.selection()
        if not sel:
            return
        row = tv.item(sel[0], "values")
        if kind == "students":
            sid, name, age, email = row[0], row[1], row[2], row[3]
            self.s_name.delete(0, tk.END); self.s_name.insert(0, name)
            self.s_age.delete(0, tk.END); self.s_age.insert(0, age)
            self.s_email.delete(0, tk.END); self.s_email.insert(0, email)
            self.s_id.delete(0, tk.END); self.s_id.insert(0, sid)
            self.edit_mode["students"] = sid
            self.s_add_btn.config(text="Update Student")
        elif kind == "instructors":
            iid, name, age, email = row[0], row[1], row[2], row[3]
            self.i_name.delete(0, tk.END); self.i_name.insert(0, name)
            self.i_age.delete(0, tk.END); self.i_age.insert(0, age)
            self.i_email.delete(0, tk.END); self.i_email.insert(0, email)
            self.i_id.delete(0, tk.END); self.i_id.insert(0, iid)
            self.edit_mode["instructors"] = iid
            self.i_add_btn.config(text="Update Instructor")
        elif kind == "courses":
            cid, cname, instr_label = row[0], row[1], row[2]
            self.c_id.delete(0, tk.END); self.c_id.insert(0, cid)
            self.c_name.delete(0, tk.END); self.c_name.insert(0, cname)
            try:
                iid = instr_label.split(" - ")[0].strip()
                if iid:
                    for i in self.db.list_instructors():
                        if i["instructor_id"] == iid:
                            self.c_instructor.set(f"{iid} | {i['name']}")
                            break
            except:
                pass
            self.edit_mode["courses"] = cid
            self.c_add_btn.config(text="Update Course")

    def _clear_form(self, kind):
        if kind == "students":
            for w in (self.s_name, self.s_age, self.s_email, self.s_id): w.delete(0, tk.END)
            self.edit_mode["students"] = None
            self.s_add_btn.config(text="Add Student")
        elif kind == "instructors":
            for w in (self.i_name, self.i_age, self.i_email, self.i_id): w.delete(0, tk.END)
            self.edit_mode["instructors"] = None
            self.i_add_btn.config(text="Add Instructor")
        elif kind == "courses":
            for w in (self.c_id, self.c_name): w.delete(0, tk.END)
            self.c_instructor.set("")
            self.edit_mode["courses"] = None
            self.c_add_btn.config(text="Add Course")

    def _snapshot(self):
        students = self.db.list_students()
        instructors = self.db.list_instructors()
        courses = self.db.list_courses()
        regs = [dict(r) for r in self.db.conn.execute("SELECT student_id, course_id FROM registrations ORDER BY student_id, course_id")]
        return {"students": students, "instructors": instructors, "courses": courses, "registrations": regs}

    def _clear_all_tables(self):
        self.db.conn.execute("DELETE FROM registrations")
        self.db.conn.execute("DELETE FROM courses")
        self.db.conn.execute("DELETE FROM students")
        self.db.conn.execute("DELETE FROM instructors")
        self.db.conn.commit()

    def _save_to_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._snapshot(), f, indent=2)
            messagebox.showinfo("Saved", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load_from_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON","*.json")])
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

            self._refresh_all_views()
            self._refresh_dropdowns()
            messagebox.showinfo("Loaded", f"Loaded from {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _export_csv(self):
        folder = filedialog.askdirectory()
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
            messagebox.showinfo("Exported", f"CSV files saved in {folder}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _refresh_dropdowns(self):
        """
        Updates all dropdown menus with current database information.
        
        Refreshes the combobox values for course instructor selection,
        student registration, and instructor assignment dropdowns.
        """
        # Update course form instructor dropdown
        self.c_instructor["values"] = [f"{i['instructor_id']} | {i['name']}" for i in self.db.list_instructors()]
        
        # Update registration dropdowns
        self.reg_student_cb["values"] = [f"{s['student_id']} | {s['name']}" for s in self.db.list_students()]
        self.reg_course_cb["values"] = [f"{c['course_id']} | {c['course_name']}" for c in self.db.list_courses()]
        
        # Update assignment dropdowns
        self.asg_instructor_cb["values"] = [f"{i['instructor_id']} | {i['name']}" for i in self.db.list_instructors()]
        self.asg_course_cb["values"] = [f"{c['course_id']} | {c['course_name']}" for c in self.db.list_courses()]

    def _current_tv_and_kind(self):
        """
        Determines which table view is currently active and its type.
        
        Returns:
            tuple: (TreeView widget, string type) or (None, None) if none active
        """
        focus_widget = self.focus_get()
        for tv, kind in [(self.students_tv,"students"), (self.instructors_tv,"instructors"), (self.courses_tv,"courses")]:
            if focus_widget is tv or tv.focus():
                return tv, kind
        if self.students_tv.selection(): return self.students_tv, "students"
        if self.instructors_tv.selection(): return self.instructors_tv, "instructors"
        if self.courses_tv.selection(): return self.courses_tv, "courses"
        return None, None

if __name__ == "__main__":
    # Create and run the School Management System application
    app = SchoolApp()
    app.mainloop()