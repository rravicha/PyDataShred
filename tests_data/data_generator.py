from faker import Faker
from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData
from sqlalchemy.orm import sessionmaker

# ... (same as above)

fake = Faker()

# Insert mock data using faker
with sessionmaker(bind=engine)() as session:
    for _ in range(10):
        session.add(my_table(column1=fake.random_int(), column2=fake.sentence()))
    session.commit()