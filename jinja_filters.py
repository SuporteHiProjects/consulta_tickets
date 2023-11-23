import re
from jinja2 import Environment

def regex_findall(s, pattern):
    return re.findall(pattern, s)

# Adiciona a função ao ambiente Jinja2
environment = Environment()
environment.filters['regex_findall'] = regex_findall
