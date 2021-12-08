from sqlalchemy import Column, Integer, String, Boolean, DateTime, LargeBinary
from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from database import Base

import datetime

dataversions_predecessor = Table(
    "dataversion_predecessor",
    Base.metadata,
    Column("version_id", Integer, ForeignKey("dataversion.id")),
    Column("predecessor_id", Integer, ForeignKey("dataversion.id")),
)

dataversions_generator = Table(
    "dataversions_generator",
    Base.metadata,
    Column("version_id", Integer, ForeignKey("dataversion.id")),
    Column("generator_id", Integer, ForeignKey("dataversion.id")),
)

class BlobObject(Base):
    __tablename__ = "blobs"
    id = Column(String, primary_key=True)
    contents = Column(LargeBinary)

class DataObject(Base):
    __tablename__ = "dataobject"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    name = Column(String)
    description = Column(String)
    created = Column(DateTime, default=datetime.datetime.now)
    modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    versions = relationship("DataVersion", back_populates="dataobject", order_by="desc(DataVersion.created)")

    is_deleted = Column(Boolean, default=False)

class DataVersion(Base):
    __tablename__ = "dataversion"
    id = Column(Integer, primary_key=True)
    dataobject_id = Column(Integer, ForeignKey("dataobject.id"))
    owner_id = Column(Integer, ForeignKey("user.id"))
    datatype = Column(String)
    comment = Column(String)
    created = Column(DateTime, default=datetime.datetime.now)
    modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    is_deleted = Column(Boolean, default=False)

    dataobject = relationship("DataObject", back_populates="versions")
    contents = relationship("DataContents", uselist=False, back_populates="dataversion")

    predecessors = relationship(
        "DataVersion",
        secondary=dataversions_predecessor,
        primaryjoin=id == dataversions_predecessor.c.version_id,
        secondaryjoin=id == dataversions_predecessor.c.predecessor_id,
        backref=backref("successors")
    )

    generators = relationship(
        "DataVersion",
        secondary=dataversions_generator,
        primaryjoin=id == dataversions_generator.c.version_id,
        secondaryjoin=id == dataversions_generator.c.generator_id,
        backref=backref("generated")
    )

class DataContents(Base):
    __tablename__ = "datacontents"
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey("dataversion.id"))
    mimetype = Column(String)
    contents = Column(LargeBinary)
    created = Column(DateTime, default=datetime.datetime.now)
    modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    dataversion = relationship("DataVersion", uselist=False, back_populates = "contents")

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    created = Column(DateTime, default=datetime.datetime.now)
    modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    posts = relationship("Post", backref=backref("author"))
    dataobjects = relationship("DataObject", backref=backref("owner"))
    dataversions = relationship("DataVersion", backref=backref("owner"))

class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("user.id"))
    title = Column(String)
    content = Column(String)
    published = Column(Boolean)
    created = Column(DateTime, default=datetime.datetime.now)
    modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class Timeline(Base):
    __tablename__ = "timeline"
    id = Column(Integer, primary_key=True)
    op = Column(String)
    timestamp = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("user.id"))
    ref_id = Column(Integer, ForeignKey("dataobject.id"))
