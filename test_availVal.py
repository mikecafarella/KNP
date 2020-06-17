from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import kgpl

engine = create_engine('sqlite:///KGPLData.db', echo=False)

Session = sessionmaker(bind=engine)
s = Session()

if __name__ == '__main__':
    store = kgpl.KNPSStore(None)
    print(store.availVal())

