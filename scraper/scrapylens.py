import os, re, time,socket
from urllib.request import urlopen, Request
from os.path import join as pjoin
from urllib3.exceptions import HTTPError
from bs4 import BeautifulSoup
from .guardar_patente import consultadb
from .captcha import resolver_captcha

def getnroresult(query):

    #probar conexion con url 
    url='https://www.lens.org/lens/search?preview=true&q='
    url += query
    #url='file:///home/soledad/Escritorio/practicacurso/webplayground-master/webtesbigpat/titlephotovoltaicandfull_textpanelandfull_textsolar/search-result0.html'
    print(url)
    try:
        response = urlopen(url)
    except HTTPError as e:
        print(e)
    else:
        webContent = response.read()
        cleanQuery = re.sub(r'\W+', '', query)
        if not os.path.exists(cleanQuery):
            os.makedirs(cleanQuery)
        #save the result to the new directory
        filename = cleanQuery + '/' + 'prueba'
        f = open(filename + ".html", 'w')
        f.write(str(webContent.decode("utf8")))
        f.close

        html = BeautifulSoup(webContent, "html.parser")
        
        # obtener la cantidad de resultados
        if html.find('g-recaptcha') == 1:
            resolver_captcha(url)
        else:
            try:
                nroresult=html.find('a', {'class': 'breadnum resultCount'}).getText().strip()
            except AttributeError:
                print('no se recupero información')

            else:    
                nroresult=int(nroresult[0:nroresult.find('Patent Results')].replace(',',''))
                #obtener solo hasta 500 patentes
                if nroresult > 500:
                    nroresult=500        
                
                pageCount = nroresult / 10
                remainder = nroresult % 10
                if remainder > 0:
                    pageCount += 1
                
                return pageCount

def getSearchResults(query,pageCount):

    cleanQuery = re.sub(r'\W+', '', query)
    if not os.path.exists(cleanQuery):
        os.makedirs(cleanQuery)

    for pages in range(1, int(pageCount)+1):
    #each part of the URL. Split up to be easier to read. 
        url = 'https://www.lens.org/lens/search?preview=true&'
        url += 'p=' + str(pages-1)
        url += '&st=true' 
        url += '&q=' + query
        #print (url)
    #download the page and save the result.
        try:
            response = urlopen(url)
        except HTTPError as e:
            print(e)
        else:
            webContent = response.read()

    #save the result to the new directory
        filename = cleanQuery + '/' + 'search-result'+ str(pages)
        f = open(filename + ".html", 'w')
        f.write(str(webContent.decode("utf8")))
        f.close

    #pause 
        time.sleep(30)

def getIndivTrials(query):
    failedAttempts = []
    failedAttempts1 = []
    cleanQuery = re.sub(r'\W+', '', query)
    searchResults = os.listdir(cleanQuery)

    urls = []

    #find search-results pages
    for files in searchResults:
        registro = ''
        if files.find("search-result") != -1:
            f = open(cleanQuery + "/" + files, 'r')
            text = f.read().split(" ")
            f.close()

            for words in text:
                if words.find('href="/lens/patent/') != -1:
                    if registro != words[words.find('href="/lens/patent/') +19: words.find('href="/lens/patent/')+38]:
                        patente=words[words.find('href="/lens/patent/') +19: words.find('href="/lens/patent/')+38]
                        if patente.find('_') == -1:
                            urls.append(words[words.find('href="/lens/patent/') +19: words.find('href="/lens/patent/')+38])
                            registro = words[words.find('href="/lens/patent/') +19: words.find('href="/lens/patent/')+38]

    for items in urls:
        #generate the URL
        url = "https://www.lens.org/lens/patent/" + items
        #download the page
        socket.setdefaulttimeout(10)
        try:
            try:
                response = urlopen(url)
            except HTTPError as e:
                print(e)
            else:
                webContent = response.read()
                #create the filename and place it in the new directory
                filename = items + '.html'
                filePath = pjoin(cleanQuery, filename)
                #save the file
                f = open(filePath, 'w')
                f.write(str(webContent.decode("utf8")))
                f.close
        except:
            failedAttempts.append(url)
        #pause
        time.sleep(30)
    print ("failed to download: " + str(failedAttempts))

    for items1 in failedAttempts:
        #generate the URL
        url = items1
        #download the page
        socket.setdefaulttimeout(10)
        try:
            try:
                 response = urlopen(url)
            except HTTPError as e:
                print(e)
            else:
                webContent = response.read()

            #create the filename and place it in the new directory
            filename = items + '.html'
            filePath = pjoin(cleanQuery, filename)
            #save the file
            f = open(filePath, 'w')
            f.write(webContent.decode("utf8"))
            f.close
        except:
            failedAttempts1.append(url)
        #pause
        time.sleep(30)
    print ("failed to download1: " + str(failedAttempts1))

def mesANumero(mes):
    m = {
        'jan': "01",
        'feb': "02",
        'mar': "03",
        'apr': "04",
        'may': "05",
        'jun': "06",
        'jul': "07",
        'aug': "08",
        'sep': "09",
        'oct': "10",
        'nov': "11",
        'dec': "12"
        }

    try:
        out = str(m[mes.lower()])
        return out
    except:
        raise ValueError('No es un mes')

def lensexcel(query,idecu):

    #nombre de la carpeta 
    cleanQuery = re.sub(r'\W+', '', query)
    #lista de archivos
    searchResults = os.listdir(cleanQuery)
    #lista de inventores
    listinv=[]    

    for files in searchResults:
        if files.find("search-resul") == -1:
            f = open(cleanQuery + "/" + files, 'r')
            nomarchivo=files[0:files.find('.')]
            text = f.read()
            f.close()
            #lista de inventores y aplicantes
            listinv=[]
            listapl=[]
            listainventor=[]
            listaaplicante=[]
            listatiponum=[]
            listanumero=[]
            # Pasamos el contenido HTML de la web a un objeto BeautifulSoup()
            html = BeautifulSoup(text, "html.parser")

            # Obtenemos todos los divs donde estan las entradas 
            entradas = html.find('div', {'class': 'clearfix-both listing'})
            #print(str(entradas))
                
            #Titulo
            titulo = entradas.find('h2', {'class': 'doc-title'}).getText()
            titulo=titulo.replace("'","")
            #print ("Titulo: " +titulo)

            
            #patentFrontPage > div.result-with-sidebar
            fulltext = entradas.find('div', {'class': 'result-with-sidebar'}).getText().strip()
            

            #Resumen
            resumen = fulltext[fulltext.find('Abstract')+8:fulltext.find('Claims')].strip()
            resumen=resumen.replace("'","")
            #print('resumen:'+resumen[:30])

            #Claims
            if (entradas.find('ol', {'class': 'claims'})!= None):
                claims =  entradas.find('ol', {'class': 'claims'}).getText().strip()
                claims=re.sub(r'\W+', ' ',claims)
                claims=claims.replace("'","")
            else:
                claims="No disponible"

            #cip
            if entradas.find('ul', {'id': 'classIpcrFilter'}) !=None:
                IPCS=entradas.find('ul', {'id': 'classIpcrFilter'}).getText()
                IPC=IPCS[0 : IPCS.find('Explore more patents')].strip()
                #print('cip:' + IPC)
                subgrupo=IPC[IPC.find('/'):]
                IPC=IPC.replace(subgrupo, "/00")
                clasificacionweb=IPC[0:4]+' '+IPC[4:]
            else:
                clasificacionweb="AAAA 00/00"
            
            #Inventores        
            inventoresul=entradas.findAll('ul',{'id': 'inventorFilter'})
            
            for invent in inventoresul:
                inventoresli =invent.findAll('li')
                for inventores in inventoresli:
                    inventor=inventores.getText().strip()
                    listinv.append(inventor[inventor.find('View all patents where Inventors')+32:])
            for l in listinv:
                if l.find('Author') == -1:
                    l=l.replace("'","")
                    #print('inventor: '+l)
                    listainventor.append(l)
                        
                    
            
            #Solicitantes
            aplicantesul=entradas.findAll('ul',{'id': 'applicantFilter'})
            
            for apli in aplicantesul:
                aplicantesli =apli.findAll('li')
                for aplicantes in aplicantesli:
                    aplicante=aplicantes.getText().strip()
                    listapl.append(aplicante[aplicante.find('View all patents where Applicants')+34:])
            l1=' '
            for l in listapl:
                if l != l1:
                    l1=l
                    l=l.replace("'","")
                    #print('aplicante: ' + l) 
                    listaaplicante.append(l)
                    
            #Numero de Patente 
            numpat=entradas.findAll('ul',{'class': 'list-bordered list-unstyled list-history'})
            for n in numpat:
                listanum =n.findAll('li')
                for numeros in listanum:
                    patron = re.compile(r'\W+')
                    numero=patron.split(numeros.getText().strip())
                    #tipo de numero (aplicacion, publicacion, prioridad)
                    tiponumero=numero[0]
                    #fecha
                    mesn=mesANumero(numero[1])
                    fecha=numero[3]+'-'+mesn+'-'+numero[2]
                    #codigo patente
                    codpatente=''.join(numero[5:])
                    #pais   
                    pais = numero[4]    
                    #lista con cada numero de una patente
                    listatiponum=[tiponumero,fecha,pais,codpatente]
                    listanumero.append(listatiponum)
      
            #Estado div class="doc-id"''.join
            estadoweb = re.sub(r'\W+', ' ',entradas.find('div', {'class': 'doc-id'}).getText())
            #print("Estado: " +estadoweb)

            #link Patenteclasificacionweb
            linkweb='https://www.lens.org/lens/patent/' +(re.sub(r'\W+', '',entradas.find('div', {'class': 'lens-id'}).getText()))
            #print("link: " +linkweb)
                
            #insertar Estado o buscar Estado

            query = ("select  id, desc_estado FROM estados WHERE desc_estado = '" + estadoweb+"'")
            datos=consultadb(query)
            if len(datos)!=0:
                if str(datos[0][1])==estadoweb:
                    est=str(datos[0][0])
            else:
                query = ("INSERT INTO estados(desc_estado) VALUES('" + estadoweb+"') RETURNING id")
                datos=consultadb(query)
                est=str(datos)

            
            #buscar id_cip
            query = ("select id, cod_cip from cip where cod_cip='" + clasificacionweb+"'")
            datos=consultadb(query)
            if len(datos)==0:
                cip=str(9570)
                
            else:
                cip=str(datos[0][0])
            
            #insertar patente
            query = ("INSERT INTO patentes (titulo_patente,resumen_patente,claims_patente,estado_id,clasificacion_id,ecuacion_id_id) VALUES('" +titulo+ "','"+resumen+"','"+claims+"',"+est+","+cip+"," + str(idecu)+") RETURNING id")
            datos=consultadb(query)
            lastIDPatente=str(datos)

            #insertar relacion patente-ecuacion
            #query= ("insert into ecuacion_patente (ecuacion_id, patente_id) values (" + str(idecu) +"," + lastIDPatente+") returning id")
            #datos=consultadb(query)

            invsol=[listainventor,listaaplicante]
            tipo='I'
            for t in invsol:
                for l in t:
                    query = ("select  id,nombre_inventor_solicitante FROM inventores_solicitantes WHERE nombre_inventor_solicitante = '" + l+"'")
                    datos=consultadb(query)
                    if len(datos)!=0:
                        if str(datos[0][1])==l:
                            lastIDInventor=str(datos[0][0])
                    else:
                        query = ("INSERT INTO inventores_solicitantes(nombre_inventor_solicitante) VALUES('" + l+"') RETURNING id")
                        datos=consultadb(query)
                        lastIDInventor=str(datos)
                        
                    query=("insert into pat_inv_sol(tipo_pat_inv_sol,inventor_solicitante_id,patente_id) values('"+tipo+"','"+lastIDInventor+"','"+lastIDPatente+"') RETURNING id;")
                    datos=consultadb(query)
                tipo='S'
        

            for listatiponum in listanumero:

                query = ("select id,nombre_tipo_numero from tipo_numero where nombre_tipo_numero='" + listatiponum[0]+"'")
                datos=consultadb(query)
                tipnum=str(datos[0][0])

                query = ("select id,cod_pais from paises where cod_pais='" + listatiponum[2]+"'")
                datos=consultadb(query)
                idpais=str(datos[0][0])

                query=("insert into numeros_patentes(cod_serie_patente,fecha_numero_patente,num_pat_pais_id,tipo_numero_id,patente_id)values('"+listatiponum[3]+"','"+listatiponum[1]+"',"+idpais+","+tipnum+","+lastIDPatente+") RETURNING id;")
                datos=consultadb(query)

            query = ("select id,nombre_repositorio from repositorios where nombre_repositorio='Lens'")
            datos=consultadb(query)
            repo=str(datos[0][0])

            query = ("INSERT INTO patentes_repositorios (repositorio_id,patente_id,link_patente_repositorio) VALUES(" +repo+","+lastIDPatente+",'"+linkweb+ "') RETURNING id")
            datos=consultadb(query)