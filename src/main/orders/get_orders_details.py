import requests
import json
import os
import re
from datetime import datetime
from google.cloud import storage
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv
from os import system

#================================================TOTAL DE PAGINAS===============================================================
headers = {"Accept": "application/json","Content-Type": "application/json","X-VTEX-API-AppKey": "vtexappkey-mercury-PKEDGA","X-VTEX-API-AppToken": "OJMQPKYBXPQSXCNQHWECEPDPMNVWAEGFBKKCNRLANUBZGNUWAVLSCIPZGWDCOCBTIKQMSLDPKDOJOEJZTYVFSODSVKWQNJLLTHQVWHEPRVHYTFLBNEJPGWAUHYQIPMBA"}
querystring = {"f_creationDate":"creationDate:[2021-08-01T01:00:00.000Z TO 2021-08-31T01:59:59.999Z]","f_hasInputInvoice":"false"}
urlPag = "https://mercury.vtexcommercestable.com.br/api/oms/pvt/orders"
responsePag = requests.request("GET", urlPag, headers=headers, params=querystring)
formJson = json.loads(responsePag.text)
paging = formJson["paging"]
total = paging["total"]
tableDetails = []
dataorderDe=[]
OrderF = []
print("Total de paginas: "+str(paging["total"])+" mes de agosto")
contador = 0
#================================================TOTAL DE PAGINAS===============================================================

def replace_blank_dict(d):
    if not d:
        return None
    if type(d) is list:
        for list_item in d:
            if type(list_item) is dict:
                for k, v in list_item.items():
                    list_item[k] = replace_blank_dict(v)
    if type(d) is dict:
        for k, v in d.items():
            d[k] = replace_blank_dict(v)
    return d

#================================================Obtener Orden Por ID============================================================
def insertar(ids,headers):
  urlDetail = "https://mercury.vtexcommercestable.com.br/api/oms/pvt/orders/"+ids+""
  response = requests.request("GET", urlDetail, headers=headers)
  result = re.sub('[!@#$|]', '', response.text)
  data = json.loads(result)
  return data
#================================================Obtener Orden Por ID============================================================


for i in range(2):
  i =+1
  OrderId = []
  #print("===========================================================================")
  url = "https://mercury.vtexcommercestable.com.br/api/oms/pvt/orders?page="+str(i)+""
  response = requests.request("GET", url, headers=headers, params=querystring)
  formatoJson = json.loads(response.text)
  listOrder = formatoJson["list"]
  for ids in listOrder:
    OrderId.append(ids["orderId"])
  for x in OrderId:
    contador = contador + 1
    print("Registros guardados: "+str(contador)+" Total de páginas: "+str(total)+" Total de registros: "+str(total*15))
    orderDe = insertar(str(x),headers)
    OrderF.append(orderDe)
    for order in OrderF:
        for k, v in order.items():
            order[k] = replace_blank_dict(v)
    

formatoOrder =  json.dumps(OrderF)

system("touch /home/bred_valenzuela/test/temp.json")

text_file = open("/home/bred_valenzuela/test/temp.json", "w")
text_file.write(formatoOrder)
text_file.close()

system("cat temp.json | jq -c '.[]' > /home/bred_valenzuela/test/DetailOrders_NDJSON.json")
system("chmod 777 convert.py")
system("./convert.py < /home/bred_valenzuela/test/DetailOrders_NDJSON.json > /home/bred_valenzuela/test/DetailOrders.json")

load_dotenv()

client = bigquery.Client()
filename = '/home/bred_valenzuela/test/DetailOrders.json'
dataset_id = 'landing_zone'
table_id = 'shopstar_detalle_orders'

dataset_ref = client.dataset(dataset_id)
table_ref = dataset_ref.table(table_id)
job_config = bigquery.LoadJobConfig()
job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
job_config.autodetect = True

with open(filename, "rb") as source_file:
    job = client.load_table_from_file(
        source_file,
        table_ref,
        location="southamerica-east1",  # Must match the destination dataset location.
        job_config=job_config,
    )  # API request

job.result()  # Waits for table load to complete.

print("Loaded {} rows into {}:{}.".format(job.output_rows, dataset_id, table_id))
