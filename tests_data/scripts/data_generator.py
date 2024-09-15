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

from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://user:password@host/database')
metadata = MetaData()

# Define your table structure
my_table = Table('your_table', metadata,
    Column('column1', Integer),
    Column('column2', String)
)

# Create the table (if it doesn't exist)
metadata.create_all(engine)

# Insert mock data
with sessionmaker(bind=engine)() as session:
    session.add(my_table(column1=1, column2='mock data'))
    session.commit()