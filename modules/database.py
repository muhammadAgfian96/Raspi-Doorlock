class DatabaseHelper:
    def __init__(self, host, port, db_name, username, password):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user = username
        self.password = password
    
    def getConfig(self):
        pass

    def insertDBServer(self, data):
        """to insert data to MySQL Server
            - data: 
                [0] name: string,
                [1] mask: boolean,
                [2] suhu: float,
                [3] door_name: string"""
        try:
            connection = mysql.connector.connect(host=self.mysql_config['host'],
                                                    port=self.mysql_config['port'],
                                                    database=self.mysql_config['database'],
                                                    user=self.mysql_config['user'],
                                                    password=self.mysql_config['password'])
            cursor = connection.cursor()
            nama = data[0]
            mask = False
            suhu = data[1]
            door_name = 'Ruang Kerja AITI'

            query_insert_db = f"""INSERT INTO raspi_test(name, mask, suhu, door_name) 
                                    VALUES ('{name}', {mask}, {suhu}, '{door_name}')"""
            result  = cursor.execute(query_insert_db)
            connection.commit()
            print(f"Success to MySQL: {name}, {mask}, {suhu}, {door_name}")
            main_log.info(f"Succes Entered Data: {name}, {mask}, {suhu}, {door_name}")
        except mysql.connector.Error as error :
            connection.rollback()
            main_log.error("Failed to MySQL: {}".format(error))
        except:
            raise
        finally:
            if(connection.is_connected()):
                cursor.close()
                connection.close()
            else:
                main_log.error("MySQL Cant Connect! Wrong Password/Host/Username/something")