from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, session
import kgpl
from kgpl import KNPSStore

engine = create_engine('sqlite:///KGPLData.db', echo=False)

Session = sessionmaker(bind=engine)
s = Session()

if __name__ == '__main__':
    val1 = kgpl.KGPLStr("val1 str")
    val2 = kgpl.KGPLInt(42)
    valn = kgpl.KGPLStr("should not in local or remote database")

    store = KNPSStore.KNPSStore(None)
    store.StoreValues([val1,val2])
    session.make_transient(val1)
    store.StoreValues([val1, val2])
    print("exception suppressed")
    # store.StoreValues([val1, val2])
