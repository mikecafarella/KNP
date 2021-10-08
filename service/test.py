from sqlalchemy import Column, Integer, String, Boolean, DateTime, LargeBinary
from sqlalchemy import ForeignKey, Table, create_engine
from sqlalchemy.orm import relationship, backref, Session
from sqlalchemy.ext.declarative import declarative_base

from models import *

import datetime

# Base = declarative_base()

# dataobjects_predecessor = Table(
#     "dataobject_predecessor",
#     Base.metadata,
#     Column("object_id", Integer, ForeignKey("dataobject.id")),
#     Column("predecessor_id", Integer, ForeignKey("dataobject.id")),
# )
#
# class ObjectName(Base):
#     __tablename__ = "objectname"
#     id = Column(Integer, primary_key=True)
#     owner_id = Column(Integer, ForeignKey("user.id"))
#     name = Column(String)
#     description = Column(String)
#     created = Column(DateTime, default=datetime.datetime.now)
#     modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
#
#     is_deleted = Column(Boolean, default=False)
#
#     #versions
#
# class NameAssignment(Base):
#     __tablename__ = "nameassignment"
#     id = Column(Integer, primary_key=True)
#     owner_id = Column(Integer, ForeignKey("user.id"))
#     name = Column(String)
#     description = Column(String)
#     created = Column(DateTime, default=datetime.datetime.now)
#     modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
#
#     is_deleted = Column(Boolean, default=False)
#
# class DataObject(Base):
#     __tablename__ = "dataobject"
#     id = Column(Integer, primary_key=True)
#     owner_id = Column(Integer, ForeignKey("user.id"))
#     datatype = Column(String)
#     comment = Column(String)
#     created = Column(DateTime, default=datetime.datetime.now)
#     modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
#
#     is_deleted = Column(Boolean, default=False)
#
#     predecessors = relationship(
#         "DataObject",
#         secondary=dataobjects_predecessor,
#         primaryjoin=id == dataobjects_predecessor.c.object_id,
#         secondaryjoin=id == dataobjects_predecessor.c.predecessor_id,
#         backref="successors"
#     )
#
#     # parents = relationship(
#     #     'Person',
#     #     secondary=parent_child,
#     #     primaryjoin=person_id == parent_child.c.ChildId,
#     #     secondaryjoin=person_id == parent_child.c.ParentId
#     #     backref=backref('children')
#     # )
#
# class DataContents(Base):
#     __tablename__ = "datacontents"
#     id = Column(Integer, primary_key=True)
#     mimetype = Column(String)
#     contents = Column(LargeBinary)
#
# class User(Base):
#     __tablename__ = "user"
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     email = Column(String, unique=True)
#     created = Column(DateTime, default=datetime.datetime.now)
#     modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
#
#     posts = relationship("Post", backref=backref("author"))
#     dataobjs = relationship("DataObject", backref=backref("owner"))
#     # publishers = relationship(
#     #     "Publisher", secondary=author_publisher, back_populates="authors"
#     # )
#
# class Post(Base):
#     __tablename__ = "post"
#     id = Column(Integer, primary_key=True)
#     author_id = Column(Integer, ForeignKey("user.id"))
#     title = Column(String)
#     content = Column(String)
#     published = Column(Boolean)
#     created = Column(DateTime, default=datetime.datetime.now)
#     modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
#
#
# class Timeline(Base):
#     __tablename__ = "timeline"
#     id = Column(Integer, primary_key=True)
#     op = Column(String)
#     timestamp = Column(DateTime)
#     owner_id = Column(Integer, ForeignKey("user.id"))
#     ref_id = Column(Integer, ForeignKey("objectname.id"))



# """Main entry point of program"""
# Connect to the database using SQLAlchemy
sqlite_filepath = "knps.db"
engine = create_engine(f"sqlite:///{sqlite_filepath}")
with Session(engine) as session:
    # the identical MetaData object is also present on the
    # declarative base
    Base.metadata.create_all(engine)

    u = User(name="Mike Anderson", email="mrander@umich.edu")
    session.add(u)

    session.commit()
