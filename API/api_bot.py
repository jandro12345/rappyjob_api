import requests
from config import *
from psycopg2 import connect,extras

conn = connect(dsn=DSN)
cursor = conn.cursor(cursor_factory=extras.DictCursor)
query = '''
        select 
            pu.id,pu.parameter,lo.email 
        from 
            parameter_user as pu 
        left join 
            login as lo 
        on 
            pu.id_user = lo.id 
        where
            pu.status = true
        '''
cursor.execute(query)
data = cursor.fetchall()
print(data)
