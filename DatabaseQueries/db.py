
class Persondb:
    def __init__(self,cursor,conn) -> None:
        self.cursor=cursor
        self.conn=conn
        
    def person_details(self,status,person,check):
        self.cursor.execute(f'''
                SELECT * FROM {status} WHERE CNAME= '{person.name}' AND
                    CDAY='{person.day}'
                    ''')
        # name=''
        # time=''
        # day=''
        if check==0:
            count=0
            for row in self.cursor.fetchall():
                count=1
                # name = row.CNAME
                # time = row.CTIMEIN
                # day = row.CDAY
            
            self.conn.commit()
            
            res = count
            return res
        else:
            count='0'
            for row in self.cursor.fetchall():
                count=row.CTIMEOUT
                # name = row.CNAME
                # time = row.CTIMEOUT
                # day = row.CDAY
            
            self.conn.commit()
            
            res = count
            return res
   
    def add(self,person,status):
         self.cursor.execute(f'''
                INSERT INTO {status}
                VALUES
                ('{person.name}','{person.time}','{person.day}')
                ''')
         self.conn.commit()
    def update(self,person,status):
        self.cursor.execute(f'''
            UPDATE  {status} SET CTIMEOUT='{person.time}'
            WHERE CNAME=
            '{person.name}' AND CDAY ='{person.day}'
            ''')
        self.conn.commit()