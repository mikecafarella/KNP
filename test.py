import kgpl
from kgpl import value, variable, load_var
# wendy
valw0 = value("excellent", comment="initial", user="Wendy")
valw1 = value("bad", comment="initial", user="Wendy")
varw0 = variable(valw1, "shareWithTony", user="Wendy")
valw2 = value("60 pts is bad", comment="initial", user="Wendy", dependency=[valw0, valw1])
varw1 = variable(valw2, comment="shareWithPeter&Tony", user="Wendy")

# Tony
urlSharedbyWendy1 = varw0.getVid()
urlSharedbyWendy2 = varw1.getVid()
varFromWendy1 = load_var(urlSharedbyWendy1)
varFromWendy2 = load_var(urlSharedbyWendy2)
valt0 = value("0 pts is bad", comment="inference", user="Tony", dependency=[varFromWendy1])
valt1 = value("60 pts is not bad", comment="argue", user="Tony", dependency=[varFromWendy1, varFromWendy2])
vart0 = variable(valt1, comment="conclusion", user="Tony")

# Peter
urlSharedbyWendy1 = varw1.getVid()
urlSharedbyTony1 = vart0.getVid()
varFromWendy1 = load_var(urlSharedbyWendy1)
varFromTony1 = load_var(urlSharedbyTony1)
valp0 = value("60 pts is bad enough", comment="I agree", user="Peter", dependency=[varFromWendy1])
valp1 = value("OK 0 pts is worse", comment="I disagree now", user="Peter", dependency=[varFromTony1])
varp0 = variable(valp1, comment="my conclusion", user="Tony")

# Wendy
urlSharedbyPeter1 = varp0.getVid()
varFromPeter = load_var(urlSharedbyPeter1)
valw3 = value("wendy again", comment="haha", user="Wendy", dependency=[varFromPeter])

# Someone not specifying his name
urlSharedbyTony1 = vart0.getVid()
urlSharedbyPeter1 = varp0.getVid()
varFromTony1 = load_var(urlSharedbyTony1)
varFromPeter1 = load_var(urlSharedbyPeter1)
vala0 = value("I agree but I will never get 0", comment="haha", dependency=[varFromPeter1, varFromTony1])
vara0 = variable(vala0, comment="I am so clever")
