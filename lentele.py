from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

engine = create_engine("sqlite:///emails.db")
Base = declarative_base()


class Emailas(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True)
    name = Column("vardas", String)
    gender = Column("lytis", String)
    own_email = Column("siuntejo_email", String)
    to_email = Column("gavejo_email", String)
    subject = Column("antraste", String)
    inputs = Column("laisko_turinys", String)
    signature = Column("parasas", String)
    joke = Column("anekdotas", String)

    def __init__(self, name, gender, own_email, to_email, subject, inputs, signature, joke):
        self.name = name
        self.gender = gender
        self.own_email = own_email
        self.to_email = to_email
        self.subject = subject
        self.inputs = inputs
        self.signature = signature
        self.joke = joke

    # def __repr__(self):
    #     return f"{self.id} {self.name} - {self.price} : {self.created_date}"

Base.metadata.create_all(engine)