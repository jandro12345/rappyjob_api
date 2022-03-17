"""
rappy job
"""
import json
import falcon
import logging
import requests
from parsel import Selector
from config import *

api = falcon.App(cors_enable=True)
logging.basicConfig(level=logging.DEBUG)

class CptGetData():
    """
    Route from /api/cpt-get-data
    """
    @staticmethod
    def on_get(_, resp):
        """
        Function from get 
        """
        resp.body = ''
        return resp

    @staticmethod
    def on_post(req, resp):
        data_response: dict = {
                "data": [],
                "error": "",
                "url-native":"",
                "message": ""
            }
        try:
            req_data = json.loads(req.stream.read())
        except json.JSONDecodeError:
            data_response['error'] = "Bad Request "
            resp.body = json.dumps(data_response)
        format_url = '{}/trabajo-de-{}-en-lima'.format(url_cpt,req_data['parameter'].lower().replace(' ','-'))
        data_response['url-native'] = format_url
        response = requests.get(format_url, timeout=15)
        if response:
            html_text = response.text
            html = Selector(text=html_text)
            item = html.css('article')
            for data in item[:5]:
                title = data.css('h1 a ::text').extract_first()
                company = data.css('p a::text').extract_first()
                place = data.css('p.fs16 ::text').extract()[-1]
                url = data.css('h1 a ::attr(href)').extract_first()
                if url:
                    url = url_cpt + url
                description = data.css('p.fc_aux::text').extract_first()
                data_response['data'].append(
                   { 
                       "title": title,
                       "company": company,
                       "place": place,
                       "url": url,
                       "description": description
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
    def on_get(_, resp):
        """
        Function from get 
        """
        resp.body = ''
        return resp

    @staticmethod
    def on_post(req, resp):
        data_response: dict = {
                "data": [],
                "error": "",
                "url-native":"",
                "message": ""
            }
        try:
            req_data = json.loads(req.stream.read())
        except json.JSONDecodeError:
            data_response['error'] = "Bad Request "
            resp.body = json.dumps(data_response)
        format_url = '{}/SearchResult?date=2&rgns=Lima%2C%20Lima&ukw={}'.format(url_infoempleo, req_data['parameter'].lower().replace(' ','%20'))
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
                place = i.css('div.caption.d7cb2::text').extract_first()
                company = i.css('p.e2601::text').extract_first()
                data_response['data'].append({
                    "title": title,
                    "company": company,
                    "place": place,
                    "url": url,
                    "description": description
                })
            resp.body = json.dumps(data_response)
        return resp

api.add_route('/api/cpt-get-data', CptGetData())
api.add_route('/api/infoempleo-get-data',InfoempleoGetData())