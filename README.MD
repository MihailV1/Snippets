install requirements: 
`pip install -r requirements.txt`

run project:
`python manage.py runserver`

run django-extensions console: 
`python manage.py shell_plus --ipython`

tags = [  "Python", "JavaScript", "Java", "C++", "Go", "Ruby",  "Algorithms", "Sorting", "Recursion", "Binary Trees", "Graphs", "Dynamic Programming", "Django", "Flask", "React", "Docker", "Git", "PostgreSQL"]
for tag_name in tags:
    Tag.objects.get_or_create(name=tag_name)
