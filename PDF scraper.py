# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 19:57:21 2023

@author: mateo
"""

import pandas as pd
import re
import tika
from tika import parser
tika.initVM()

file_name = "pdf_to_scrape.pdf" #PDF to be scraped
df = pd.read_csv("empty_df.csv") #empty dataframe to fill
df.head()

#Function to obtain a list with all the PDF information
def input_file_processing(file_name):
    parsedPDF = parser.from_file(file_name)
    content = parsedPDF['content']
    contentlist = content.split('\n')
    contentlist = list(filter(lambda a: a != '', contentlist)) #Remove empty lines
    contentlist = list(filter(lambda a: len(a)>=2, contentlist)) #Remove lines with less than 2 letters
    contentlist = list(filter(lambda a: bool(re.search('^[A-Z -.\']+( - [A-Z -.\'])',a))==False, contentlist)) #To filter head-names of pages
    return contentlist


contentlist = input_file_processing(file_name) #The list

#Function to detect the nature of element in the list and fill the dataframe
def parse_content_in_file(contentlist,df):
    position_counter = 0
    skipping_lines = 0
    name = ''
    company = ''
    phone = ''
    fax = ''
    address = ''
    city = ''
    email = ''
    pobox = ''
    for i in contentlist:
        if i == 'X : LAW22ACH01' or i == 'X : LAW22ACH02' or i == 'X : LAW22ACH03':
            skipping_lines = 5
        if skipping_lines > 0:
            skipping_lines -= 1
            #print(i)
            continue
        if position_counter==0:
            name = i
            #print('name = ' + name)
        if position_counter==1:
            if re.match('\(?\d{3}\)?[-\.]? *\d{3}[-\.]? *[-\.]?\d{4}',i):
                phone = i
                #print('phone = ' + phone)
            else:
                position_counter+=1
        if position_counter==2:
            if i.startswith('Fax') and re.search('\(?\d{3}\)?[-\.]? *\d{3}[-\.]? *[-\.]?\d{4}',i):
                fax = i
                #print('fax = ' + fax)
            else:
                position_counter+=1
        if position_counter==3:
            if bool(re.search('[0-9]',i))==False:
                company = i
                #print('company = ' + company)
            else:
                position_counter+=1
        if position_counter==4:
            if (i.startswith(('PO','P.O','P. O.')) or re.match(r'^\d{1,5}',i) or re.search('^([^,]+),\s([A-Z]{2})(?:\s(\d{5}))?$',i.strip()) or re.search('^([^,]+),\s([A-Z]{2})(?:\s(\d{5}))?-?\d{4}?$',i.strip()) or re.search('@', i) or i.strip().endswith(('(L3)','(G3)','(IN)','(LC)','(LC)414','(LC)427','(LC)415','(LC)430','(RT)','(MLTY)','(JD)','(FLC)','(JDS)','(JDA)','CERT_PARAL'))) ==False:
                company = company + i
                #print('company2 = ' + company)
            else:
                position_counter+=1
        if position_counter==5:
            if i.startswith(('PO','P.O','P. O.')):
                pobox = i
                #print('pobox = ' + pobox)
            else:
                position_counter+=1
        if position_counter==6:
            if re.match(r'^\d{1,5}',i):
                address = i
                #print('address = ' + address)
            else:
                position_counter+=1
        if position_counter==7:
            if (re.search('^([^,]+),\s([A-Z]{2})(?:\s(\d{5}))?$',i.strip()) or re.search('^([^,]+),\s([A-Z]{2})(?:\s(\d{5}))?-?\d{4}?$',i.strip()) or re.search('@', i) or i.strip().endswith(('(L3)','(G3)','(IN)','(LC)','(LC)414','(LC)427','(LC)415','(LC)430','(RT)','(MLTY)','(JD)','(FLC)','(JDS)','(JDA)','CERT_PARAL')))==False:
                address = address + ' ' + i
                #print('address2 = ' + address)
            else:
                position_counter+=1
        if position_counter==8:
            if re.search('^([^,]+),\s([A-Z]{2})(?:\s(\d{5}))?$',i.strip()) or re.search('^([^,]+),\s([A-Z]{2})(?:\s(\d{5}))?-?\d{4}?$',i.strip()):
                city = i
                #print('city = ' + city)
            else:
                position_counter+=1
        if position_counter==9:
            if re.search('@', i): 
                email = i
                #print('email = ' + email)
            else:
                position_counter+=1
        if position_counter==10:
            if i.strip().endswith(('(L3)','(G3)','(IN)','(LC)','(LC)414','(LC)427','(LC)415','(LC)430','(RT)','(MLTY)','(JD)','(FLC)','(JDS)','(JDA)','CERT_PARAL')):
                
                df2 = {'last_name':name, 'first_name':'', 'company':company, 'phone_number':phone, 'fax_number':fax, 'address':address, 'pobox':pobox ,'city':city, 'state':'', 'zip_code':'', 'email':email}
                df2 = pd.DataFrame([df2])
                df = pd.concat([df, df2], ignore_index=True)
                
                position_counter = 0 #Resetting position counter for the next block
                #Re-initializing Variables
                name = i            
                company = ''
                phone = ''
                fax = ''
                address = ''
                city = ''
                email = ''
                pobox = ''
            
        position_counter+=1
    df2 = {'last_name':name, 'first_name':'', 'company':company, 'phone_number':phone, 'fax_number':fax, 'address':address, 'pobox':pobox ,'city':city, 'state':'', 'zip_code':'', 'email':email}
    df2 = pd.DataFrame([df2])
    df = pd.concat([df, df2], ignore_index=True)
    return df
         
b = parse_content_in_file(contentlist,df) #Dataframe with all the information
b.head()

b.to_csv("output_csv_1.csv") #First version of csv output

df = pd.read_csv("output_csv_1.csv")

df = df.drop('Unnamed: 0',1) #Delete unnecesary column of indexes

df['last_name']
df2 = df['last_name'].str.split(',', expand=True)

df3 = df2.iloc[:,1].str.split('(', expand=True)
df3.head()

df4 = df3.iloc[:,1].str.split(')', expand=True)
df4.head()

df['LAST_NAME'] = df2.iloc[:,[0]]
df['FIRST_NAME'] = df3.iloc[:,[0]]
df['STATUS'] = df4.iloc[:,[0]]

df['LAST_NAME'] = df['LAST_NAME'].str.strip()
df['FIRST_NAME'] = df['FIRST_NAME'].str.strip()
df['STATUS'] = df['STATUS'].str.strip()
df['address'] = df['address'].str.strip()
df['email'] = df['email'].str.strip()
df['pobox'] = df['pobox'].str.strip()
df['company'] = df['company'].str.strip()

df = df[['LAST_NAME','FIRST_NAME','STATUS','company','PHONE_NUM','FAX_NUM','address','pobox','city','email']]

df5 = df['phone_number'].str.partition('Fax')
df6 = df5.iloc[:,1].str.cat(df5.iloc[:,2])

df['FAX_NUM'] = df6

df['PHONE_NUM'] = df5.iloc[:,[0]]
df['PHONE_NUM'] = df['PHONE_NUM'].str.strip()
df['FAX_NUM'] = df['FAX_NUM'].str.strip()

df7 = df['city'].str.split(',', expand=True)

df['CITY'] = df7.iloc[:,[0]]
df['CITY'] = df['CITY'].str.strip()

df8 = df7.iloc[:,1].str.strip()

df9 = df8.str.split(' ', expand=True)

df['STATE'] = df9.iloc[:,[0]]
df['ZIP'] = df9.iloc[:,[1]]

df = df[['LAST_NAME','FIRST_NAME','STATUS','company','PHONE_NUM','FAX_NUM','address','pobox','CITY','STATE','ZIP','email']]

df = df.fillna('')
df.to_csv("output_csv_2.csv",index=False)

df10 = pd.read_csv("output_csv_2.csv")

#Definitive DF
dfdef = df10.rename(columns={'company': 'COMPANY', 'address': 'ADDRESS', 'pobox': 'POBOX', 'email': 'EMAIL', 'LAST_NAME': 'LAST NAME', 'FIRST_NAME': 'FIRST NAME', 'PHONE_NUM': 'PHONE NUMBER', 'FAX_NUM': 'FAX NUMBER'})

dfstate = dfdef.groupby('STATE')

dfdef['STATE'].unique()

dfdef.to_excel("excel_spreadsheet.xlsx")

states = ['SC', 'FL', 'MD', 'GA', 'DC', 'AZ', 'NC', 'AL', 'VA', 'KY', 'NY',
       'TN', 'TX', 'CA', 'WA', 'MI', 'AR', 'MS', 'NJ', 'ID', 'IL', 'MA',
       'MO', 'DE', 'NV', 'PA', 'HI', 'IA', 'IN', 'CT', 'NH', 'CO', 'ME',
       'OH', 'UT', 'NM', 'MT', 'WY', 'WI', 'AE', 'OK', 'LA', 'OR', 'WV',
       'NE', 'MN', 'ND', 'AP', 'VI', 'PR', 'VT', 'AK', 'RI', 'KS',
       'SD']

#To get an ss for every state
for state in states:
    dfState = dfstate.get_group(state)
    dfState.to_excel("excel_spreadsheet"+state+".xlsx")