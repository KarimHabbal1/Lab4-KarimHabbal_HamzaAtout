import sqlite3
from typing import List, Optional, Dict, Any

def create_schema(db_path="school.sqlite"):
    """this function is about create_schema

:param args: depends on usage
:type args: varies
:return: result of create_schema
:rtype: varies
"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER CHECK(age >= 0),
        email TEXT UNIQUE NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS instructors (
        instructor_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER CHECK(age >= 0),
        email TEXT UNIQUE NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        course_id TEXT PRIMARY KEY,
        course_name TEXT NOT NULL,
        instructor_id TEXT,
        FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
            ON UPDATE CASCADE ON DELETE SET NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        student_id TEXT,
        course_id TEXT,
        PRIMARY KEY (student_id, course_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id)
            ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
            ON UPDATE CASCADE ON DELETE CASCADE
    )
    """)
    conn.commit()
    conn.close()

def backup_database(src_path: str = "school.sqlite", dest_path: str = "backup.sqlite") -> None:
    """this function is about backup_database

:param args: depends on usage
:type args: varies
:return: result of backup_database
:rtype: varies
"""
    """Backup the SQLite database to another file."""
    with sqlite3.connect(src_path) as src, sqlite3.connect(dest_path) as dst:
        src.backup(dst)
    print(f"Database backed up from {src_path} to {dest_path}")

class DB:
    """this is the class i made for DB:

    :param args: init args if any
    :type args: varies
    """
    def __init__(self, path: str = "school.sqlite"):
        """this function is about __init__

:param args: depends on usage
:type args: varies
:return: result of __init__
:rtype: varies
"""
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def create_student(self, student_id: str, name: str, age: int, email: str) -> None:
        """this function is about create_student

:param args: depends on usage
:type args: varies
:return: result of create_student
:rtype: varies
"""
        self.conn.execute(
            "INSERT INTO students(student_id,name,age,email) VALUES(?,?,?,?)",
            (student_id, name, age, email),
        )
        self.conn.commit()

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        """this function is about get_student

:param args: depends on usage
:type args: varies
:return: result of get_student
:rtype: varies
"""
        row = self.conn.execute(
            "SELECT * FROM students WHERE student_id=?", (student_id,)
        ).fetchone()
        return dict(row) if row else None

    def list_students(self) -> List[Dict[str, Any]]:
        """this function is about list_students

:param args: depends on usage
:type args: varies
:return: result of list_students
:rtype: varies
"""
        rows = self.conn.execute("SELECT * FROM students ORDER BY student_id").fetchall()
        return [dict(r) for r in rows]

    def update_student(self, student_id: str, name: str, age: int, email: str) -> None:
        """this function is about update_student

:param args: depends on usage
:type args: varies
:return: result of update_student
:rtype: varies
"""
        self.conn.execute(
            "UPDATE students SET name=?, age=?, email=? WHERE student_id=?",
            (name, age, email, student_id),
        )
        self.conn.commit()

    def delete_student(self, student_id: str) -> None:
        """this function is about delete_student

:param args: depends on usage
:type args: varies
:return: result of delete_student
:rtype: varies
"""
        self.conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
        self.conn.commit()

    def create_instructor(self, instructor_id: str, name: str, age: int, email: str) -> None:
        """this function is about create_instructor

:param args: depends on usage
:type args: varies
:return: result of create_instructor
:rtype: varies
"""
        self.conn.execute(
            "INSERT INTO instructors(instructor_id,name,age,email) VALUES(?,?,?,?)",
            (instructor_id, name, age, email),
        )
        self.conn.commit()

    def get_instructor(self, instructor_id: str) -> Optional[Dict[str, Any]]:
        """this function is about get_instructor

:param args: depends on usage
:type args: varies
:return: result of get_instructor
:rtype: varies
"""
        row = self.conn.execute(
            "SELECT * FROM instructors WHERE instructor_id=?", (instructor_id,)
        ).fetchone()
        return dict(row) if row else None

    def list_instructors(self) -> List[Dict[str, Any]]:
        """this function is about list_instructors

:param args: depends on usage
:type args: varies
:return: result of list_instructors
:rtype: varies
"""
        rows = self.conn.execute("SELECT * FROM instructors ORDER BY instructor_id").fetchall()
        return [dict(r) for r in rows]

    def update_instructor(self, instructor_id: str, name: str, age: int, email: str) -> None:
        """this function is about update_instructor

:param args: depends on usage
:type args: varies
:return: result of update_instructor
:rtype: varies
"""
        self.conn.execute(
            "UPDATE instructors SET name=?, age=?, email=? WHERE instructor_id=?",
            (name, age, email, instructor_id),
        )
        self.conn.commit()

    def delete_instructor(self, instructor_id: str) -> None:
        """this function is about delete_instructor

:param args: depends on usage
:type args: varies
:return: result of delete_instructor
:rtype: varies
"""
        self.conn.execute("DELETE FROM instructors WHERE instructor_id=?", (instructor_id,))
        self.conn.commit()

    def create_course(self, course_id: str, course_name: str, instructor_id: Optional[str]) -> None:
        """this function is about create_course

:param args: depends on usage
:type args: varies
:return: result of create_course
:rtype: varies
"""
        self.conn.execute(
            "INSERT INTO courses(course_id,course_name,instructor_id) VALUES(?,?,?)",
            (course_id, course_name, instructor_id),
        )
        self.conn.commit()

    def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        """this function is about get_course

:param args: depends on usage
:type args: varies
:return: result of get_course
:rtype: varies
"""
        row = self.conn.execute(
            """SELECT c.course_id, c.course_name, c.instructor_id,
                      i.name AS instructor_name, i.email AS instructor_email
               FROM courses c
               LEFT JOIN instructors i ON i.instructor_id = c.instructor_id
               WHERE c.course_id=?""",
            (course_id,),
        ).fetchone()
        return dict(row) if row else None

    def list_courses(self) -> List[Dict[str, Any]]:
        """this function is about list_courses

:param args: depends on usage
:type args: varies
:return: result of list_courses
:rtype: varies
"""
        rows = self.conn.execute(
            """SELECT c.course_id, c.course_name, c.instructor_id,
                      i.name AS instructor_name
               FROM courses c
               LEFT JOIN instructors i ON i.instructor_id = c.instructor_id
               ORDER BY c.course_id"""
        ).fetchall()
        return [dict(r) for r in rows]

    def update_course(self, course_id: str, course_name: Optional[str] = None,instructor_id: Optional[str] = None) -> None:
        """this function is about update_course

        :param args: depends on usage
        :type args: varies
        :return: result of update_course
        :rtype: varies
        """
        if course_name is None and instructor_id is None:
            return
        if course_name is not None and instructor_id is not None:
            self.conn.execute(
                "UPDATE courses SET course_name=?, instructor_id=? WHERE course_id=?",
                (course_name, instructor_id, course_id),
            )
        elif course_name is not None:
            self.conn.execute(
                "UPDATE courses SET course_name=? WHERE course_id=?",
                (course_name, course_id),
            )
        else:
            self.conn.execute(
                "UPDATE courses SET instructor_id=? WHERE course_id=?",
                (instructor_id, course_id),
            )
        self.conn.commit()

    def delete_course(self, course_id: str) -> None:
        """this function is about delete_course

:param args: depends on usage
:type args: varies
:return: result of delete_course
:rtype: varies
"""
        self.conn.execute("DELETE FROM courses WHERE course_id=?", (course_id,))
        self.conn.commit()

    def register_student(self, student_id: str, course_id: str) -> None:
        """this function is about register_student

:param args: depends on usage
:type args: varies
:return: result of register_student
:rtype: varies
"""
        self.conn.execute(
            "INSERT OR IGNORE INTO registrations(student_id, course_id) VALUES(?,?)",
            (student_id, course_id),
        )
        self.conn.commit()

    def unregister_student(self, student_id: str, course_id: str) -> None:
        """this function is about unregister_student

:param args: depends on usage
:type args: varies
:return: result of unregister_student
:rtype: varies
"""
        self.conn.execute(
            "DELETE FROM registrations WHERE student_id=? AND course_id=?",
            (student_id, course_id),
        )
        self.conn.commit()

    def list_course_students(self, course_id: str) -> List[str]:
        """this function is about list_course_students

:param args: depends on usage
:type args: varies
:return: result of list_course_students
:rtype: varies
"""
        rows = self.conn.execute(
            "SELECT student_id FROM registrations WHERE course_id=? ORDER BY student_id",
            (course_id,),
        ).fetchall()
        return [r["student_id"] for r in rows]

    def list_student_courses(self, student_id: str) -> List[str]:
        """this function is about list_student_courses

:param args: depends on usage
:type args: varies
:return: result of list_student_courses
:rtype: varies
"""
        rows = self.conn.execute(
            "SELECT course_id FROM registrations WHERE student_id=? ORDER BY course_id",
            (student_id,),
        ).fetchall()
        return [r["course_id"] for r in rows]

    def close(self) -> None:
        """this function is about close

:param args: depends on usage
:type args: varies
:return: result of close
:rtype: varies
"""
        self.conn.close()

if __name__ == "__main__":
    create_schema()
    backup_database("school.sqlite", "school_backup.sqlite")