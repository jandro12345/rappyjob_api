"""
rappy job
"""
from datetime import datetime,timedelta
import json
from sqlite3 import Cursor
import falcon
import logging
import requests
from parsel import Selector
from config import *
from psycopg2 import connect,extras
import jwt
import bcrypt

api = falcon.App(cors_enable=True)
logging.basicConfig(level=logging.DEBUG)

def order_time(time):
    try:
        if 'horas' in time or 'hora' in time:
            time_temp = [int(Numero) for Numero in time.split() if Numero.isdigit()][0]
            time_temp = (datetime.now() - timedelta(hours=time_temp)).strftime("%Y-%m-%d %H:%M:%S")
        elif 'días' in time or 'día' in time:
            time_temp = [int(Numero) for Numero in time.split() if Numero.isdigit()][0]
            time_temp = (datetime.now() - timedelta(days=time_temp)).strftime("%Y-%m-%d %H:%M:%S")
        elif 'minutos' in time or 'minuto' in time: 
            time_temp = [int(Numero) for Numero in time.split() if Numero.isdigit()][0]
            time_temp = (datetime.now() - timedelta(minutes=time_temp)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_temp = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")
    except IndexError:
        time_temp = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    return time_temp
    

class CptGetData():
    """
    Route from /api/cpt-get-data
    """
    @staticmethod
    def on_post(_, resp):
        """
        Function from post
        """
        resp.body = ''
        return resp

    @staticmethod
    def on_get(req, resp):
        data_response: dict = {
                "data": [],
                "error": "",
                "url-native":"",
                "message": ""
            }
        req_data = str(req.params['parameter']).replace('-',' ')
        format_url = '{}/trabajo-de-{}-en-lima'.format(URL_CPT,req_data.lower().replace(' ','-'))
        data_response['url-native'] = format_url
        response = requests.get(format_url, timeout=15)
        if response:
            html_text = response.text
            html = Selector(text=html_text)
            item = html.css('article')
            for data in item[:5]:
                title = data.css('h1 a ::text').extract_first()
                company = data.css('p.fs16 a::text').extract_first()
                place = data.css('p.fs16 ::text').extract()[-1]
                url = data.css('h1 a ::attr(href)').extract_first()
                time = data.css('p.fs13::text').extract_first()
                if url:
                    url = URL_CPT + url
                description = data.css('p.fc_aux::text').extract_first()
                if not company:
                    company = ""
                if not time:
                    time = "1 hora atras"
                elif time == "Ayer":
                    time = "Hace 1 día"
                time_validate = order_time(time)
                data_response['data'].append(
                   { 
                       "title": str(title).upper(),
                       "company": str(company).upper(),
                       "place": str(place).replace('\r',' ').replace('\n','').strip(),
                       "url": url,
                       "description": str(description),
                       "time": str(time),
                       "time_order":time_validate
                   }
                )
            data_response['message'] = "Successful"
            resp.body = json.dumps(data_response)
        return resp


class InfoempleoGetData():
    """
    Route from /api/infoempleo-get-data
    """
    @staticmethod
    def on_post(_, resp):
        """
        Function from post
        """
        resp.body = ''
        return resp

    @staticmethod
    def on_get(req, resp):
        data_response: dict = {
                "data": [],
                "error": "",
                "url-native":"",
                "message": ""
            }
        req_data = str(req.params['parameter']).replace('-',' ')
        format_url = '{}/SearchResult?date=2&rgns=Lima%2C%20Lima&ukw={}'.format(URL_INFOEMPLEO, req_data.lower().replace(' ','%20'))
        response = requests.get(format_url, timeout=15)
        data_response['url-native'] = format_url
        if response:
            html_text = response.text
            html = Selector(text=html_text)
            item = html.css('article._2caa5._5d7c4')
            
            for i in item[:5]:
                url = i.css('a ::attr(href)').extract_first()
                title2 = i.css('span._1b9db span::text').extract()
                title1 = i.css('span._1b9db b::text').extract()
                title ="".join( title1 + title2)
                description = i.css('div._10840 span::text').extract()
                if not description:
                    description = i.css('div._10840::text').extract()
                description = "".join(description)
                place = i.css('div.caption::text').extract_first()
                company = i.css('p.e2601::text').extract_first()
                time = i.css('div._131cd div.caption._0ae25::text').extract_first()
                if not company:
                    company = ""
                if not time:
                    time = "1 hora atras"
                elif time == "Ayer":
                    time = "Hace 1 día"
                time_validate = order_time(time)
                data_response['data'].append({
                    "title": title,
                    "company": company,
                    "place": place,
                    "url": url,
                    "description": description.replace('\r',''),
                    "time": time,
                    "time_order": time_validate
                })
            resp.body = json.dumps(data_response)
        return resp

class Register():
    """
    Route from /api/register
    """
    @staticmethod
    def on_post(req, resp):
        """
        Function from post
        """
        data_response: dict = {
                "data": [],
                "error": "",
                "message": ""
            }
        try:
            parameter = json.loads(req.stream.read())
        except:
            print("error en decodificar json")
        conn = connect(dsn=DSN)
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute('Select * from login where username=%s',(parameter['username'],))
        if cursor.fetchall():
            data_response['error'] = "El Usuario ya existe"
        else:
            parameter.pop('passwordconfirm', None)
            pass_encode = bcrypt.hashpw(parameter['password'].encode(), bcrypt.gensalt())
            parameter['password'] = pass_encode.decode()
            cursor.execute('insert into login (' + ', '.join(list(parameter.keys())) +
                           ') values ' + str(tuple(parameter.values())))
            conn.commit()
            data_response["message"] = "Registro Realizado"
        conn.close()
        resp.body = json.dumps(data_response)
        return resp

    @staticmethod
    def on_get(_, resp):
        """
        Function from get
        """
        resp.body = ''
        return resp


api.add_route('/api/cpt-get-data', CptGetData())
api.add_route('/api/infoempleo-get-data',InfoempleoGetData())
api.add_route('/api/register',Register())