import kgpl_client as kgpl
import random
total = 0
server_url = "http://127.0.0.1:5000/val/"
for i in range(0, 20):
    user_name = "user ." + str(i)
    for y in range(0, random.randint(1, 4)):
        d = []
        if (total > 5):
            for j in range(0, 3):
                d.append(server_url + str(random.randint(1, total - 1)))
        a = kgpl.value(1, "comment", user=user_name, dependency=d)
        kgpl.variable(a, "comment_var", user=user_name)
        total += 1

a = kgpl.value(123, "ss")
kgpl.variable(a.vid, "ss")

