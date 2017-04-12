from _mysql import DatabaseError
import csv
import datetime
import re
from analytics.libs import db_helper
from feedback.models import Classes, Student, Faculty, Subject, ClassFacSub, Feedback, FdbkQuestions, Category, \
    LOAquestions

__author__ = 'Akhil'


def is_unassigned(year, branch, classes):
    pattern = year+','+branch+',*'
    for cls in classes:
        if re.search(pattern, cls):
            return True
    return False


def update_classes():
    file = open('externals/student-class.csv', 'r')
    lines = file.readlines()
    now = datetime.datetime.today()
    classes = set()
    for line in lines:
        fields = line.split(',')
        branch = fields[1].strip()
        if branch == '':
            continue
        year = str(int(now.year) - int('20'+fields[0][0]+fields[0][1]))
        section = fields[2].strip()
        if section == '' and is_unassigned(year, branch, classes):
            continue
        classes.add(year+','+branch+','+section)

    for cls in classes:
        lst = cls.split(',')
        try:
            Classes.objects.create(year=lst[0], branch=lst[1], section=lst[2])

        except:
            pass
    file.close()
    return classes

def update_students():
    file = open('externals/student-class.csv', 'r')
    lines = file.readlines()
    now = datetime.datetime.today()
    classes = set()
    for line in lines:
        fields = line.split(',')
        student = fields[0].strip()
        branch = fields[1].strip()
        if branch == '':
            continue
        year = str(int(now.year) - int('20'+fields[0][0]+fields[0][1]))
        section = fields[2].strip()
        if section == '' and is_unassigned(year, branch, classes):
            continue

        try:
            cls = Classes.objects.get(year=year, branch=branch, section=section)
            Student.objects.create(hallticket_no=student, class_id=cls)
            classes.add(student)
        except:
            try:
               stu = Student.objects.get(hallticket_no=student)
               stu.class_id = Classes.objects.get(year=year, branch=branch, section=section)
            except:
                pass

    file.close()
    return classes


def update_faculty():
    file = open('externals/class-faculty-subject.csv', 'r')
    lines = file.readlines()
    faculty = set()
    for line in lines:
        fields = line.split(',')
        faculty.add(fields[1].strip())

    for fac in faculty:
        try:
            Faculty.objects.create(name=fac)
        except:
            pass

    file.close()
    return faculty


def update_subjects():
    file = open('externals/class-faculty-subject.csv', 'r')
    lines = file.readlines()
    file.close()
    subjects = set()
    for line in lines:
        fields = line.split(',')
        subjects.add(fields[2].strip())

    for subject in subjects:
        try:
            Subject.objects.create(name=subject)
        except:
            pass

    return subjects


def update_class_fac_sub():
    file = open('externals/class-faculty-subject.csv', 'r')
    lines = file.readlines()
    file.close()
    relations = set()
    for line in lines:
        fields = line.split(',')
        cls = fields[0].split('-')
        branch = cls[0].strip()
        section = cls[1].strip()
        year = cls[2].strip()[0]
        faculty = fields[1].strip()
        subject = fields[2].strip()
        relations.add(year+'-|-'+branch+'-|-'+section+'-|-'+faculty+'-|-'+subject)
    for relation in relations:
        params = relation.split('-|-')
        try:
            cls = Classes.objects.get(year=params[0], branch=params[1], section=params[2])
            faculty = Faculty.objects.get(name=params[3])
            subject = Subject.objects.get(name=params[4])
            ClassFacSub.objects.create(class_id=cls, faculty_id=faculty, subject_id=subject)
        except:
            pass

    return relations


def update_faculty_questions():
    file = open('externals/faculty-questions.csv', 'r')
    lines = file.readlines()
    file.close()
    questions = set()
    try:
        category = Category.objects.get(category='faculty')
    except:
        category = Category.objects.create(category='faculty')
    for line in lines:
        fields = line.split(',')
        question = fields[0].strip()
        subcategory = fields[1].strip()
        try:
            FdbkQuestions.objects.get(question=question, subcategory=subcategory)
            continue
        except:
            FdbkQuestions.objects.create(question=question, subcategory=subcategory, category=category)
            questions.add(question+'\t'+subcategory)

    return questions


def update_loa_questions():
    #file = open('externals/loa-questions.csv', 'r')
    file = open('externals/IT.csv', 'r')
    reader = csv.reader(file)
    questions = []
    for row in reader:
        questions.append(row)

    file.close()
    return questions