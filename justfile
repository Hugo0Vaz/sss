
add pkg:
    pip install --upgrade -r requirements.txt && pip install {{pkg}} && pip freeze > requirements.txt
