import re
username = " 23"
if re.findall(r'\s+',username)!=[]:
    print(True)
else:
    print(False)