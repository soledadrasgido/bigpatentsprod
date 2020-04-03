import psycopg2

def consultadb(consulta):  
    try:
        cnx = psycopg2.connect(host="127.0.0.1", database="big_patents_db", user="postgres", password="1234")

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
  
    else:
        cursor = cnx.cursor()
        #ejecutamos una consulta
        datos=cursor.execute(consulta)
        #segun yo checa si la primera palabra del la consulta el select
        if consulta.startswith("select"):
        #realiza la consulta y lo almacena en datos
            datos = cursor.fetchall()
        #si no es select hace las modificaciones a la BD
        else:
        #hace efectiva la escritura de los datos
            cnx.commit()
        #datos se vuelve en nada
            datos = cursor.fetchone()[0]
        #cerramos el cursor
        cursor.close()
        #cerramos la conexion
        cnx.close()
        #regresamos la variable datos
        return datos