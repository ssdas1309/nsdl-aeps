import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
from pyxlsb import open_workbook as open_xlsb
from io import BytesIO
st.title("ISERVEU RECON PROCESS")
Mware = st.file_uploader('mware a file containing m/w data')
Npci = st.file_uploader('npci a file containing npci data')
Switch=st.file_uploader('switch a file containing switch data')
mware=pd.read_excel(Mware)
npci=pd.read_excel(Npci)
switch=pd.read_excel(Switch)
# import streamlit as st
# import pandas as pd
# import numpy as np
# mware = pd.read_excel(r'NSDL AEPS MIDDLEWARE FILE - 24-10-2022.xlsx')
# # print(mware)
# npci = pd.read_excel(r'NSDL AEPS NPCI FILE - 24-10-2022.xlsx')
# # print(npci)
# switch = pd.read_excel(r'NSDL AEPS SWITCH FILE - 24-10-2022.xlsx')
# print(switch)
#MIDDILE WARE
mware = mware[['apiTid','operationPerformed','status', 'amountTransacted', 'createdDate', 'transactionMode']]
mware.rename(columns={'apiTid':'RRN', 'transactionMode':'Transaction Type','status':'Transaction Status', 'amountTransacted':'Transaction Amount', 'createdDate':'Transaction Date Time'}, inplace = True)
mware.loc[mware['Transaction Type'] == 'AEPS_CASH_WITHDRAWAL', 'Transaction Type'] = 'cash withdrawal'
mware.loc[mware['Transaction Type'] == 'AEPS_MINI_STATEMENT', 'Transaction Type'] = 'mini statement'
mware.loc[mware['Transaction Type'] == 'AEPS_BALANCE_ENQUIRY', 'Transaction Type'] = 'balance enquiry'
# print("BEFORE MERGE MWARE DATA:",mware)
#NPCI
npci = npci[['Transaction Serial Number', 'Transaction Type', 'Response Code', 'Actual Transaction Amount', 'Transaction Date']]
npci.rename(columns={'Transaction Serial Number': 'RRN', 'Transaction Type': 'Transaction Type', 'Response Code':'Transaction Status', 'Actual Transaction Amount':'Transaction Amount', 'Transaction Date':'Transaction Date Time' }, inplace = True)
npci['Transaction Status'] = np.where(npci['Transaction Status'] == '00', 'SUCCESS', 'FAILED')
npci.loc[npci['Transaction Type'] == 4, 'Transaction Type'] = 'cash withdrawal'
npci.loc[npci['Transaction Type'] == 7, 'Transaction Type'] = 'mini statement'
npci.loc[npci['Transaction Type'] == 5, 'Transaction Type'] = 'balance enquiry'
# print("BEFORE MERGE NPCI DATA:",npci)
#SWITCH
switch = switch[['RRN', 'Transaction Type', 'Transaction Status', 'Transaction Amount', 'Transaction Date Time']]
switch.loc[switch['Transaction Type'] == 'Offus Withdrawal txn', 'Transaction Type'] = 'cash withdrawal'
switch.loc[switch['Transaction Type'] == 'Offus Mini Statement', 'Transaction Type'] = 'mini statement'
switch.loc[switch['Transaction Type'] == 'OFFUS Balance enquiry', 'Transaction Type'] = 'balance enquiry'
# print("BEFORE MERGE SWITCH",switch)
#MERGE
df_merge = pd.merge(pd.merge(npci, switch, on='RRN', how='outer', suffixes=("_npci","_switch")), mware, on='RRN', how='outer')
#list of column matches
column_match1 = ['Transaction Status', 'Transaction Amount','Transaction Type']
#match of three excel sheet of this column
for key in column_match1:
    df_merge['{}_final_status'.format(key)] = df_merge[['{}_switch'.format(key), '{}_npci'.format(key)]].eq(df_merge['{}'.format(key)], axis=0).all(axis=1)
    df_merge['{}_final_status'.format(key)] = np.where(df_merge['{}_final_status'.format(key)] == 0, '{} '.format(key), '')
    
print("2 column merge report 3excel sheet::",df_merge)
# column_match2 = ['Transaction Type']
# #list of column matches in 2 excel sheet
# for key in column_match2:
#     df_merge['{}_final_status'.format(key)] = np.where((df_merge['{}_switch'.format(key)] == df_merge['{}_npci'.format(key)]),'{} '.format(key), '' )
#match1 AND match2 concatenate
# column_match = column_match1 + column_match2
#this will print the why column not matched
df_merge['final_status_description'] = ''
for key in column_match1:
    df_merge['final_status_description'] += df_merge['{}_final_status'.format(key)]

df_merge['final_status'] = ''
#this list for the match or mismatch
df_merge['final_status'] = np.where(df_merge['final_status_description'] == '', 'Match', 'Mismatch')

for key in column_match1:
    del df_merge['{}_final_status'.format(key)]
print("MATCH COUNT:", df_merge['final_status'].value_counts())
print("final status:::",df_merge['final_status'])
print("merge columns:",df_merge.columns)
df_merge.to_csv('final data.csv')
st.write(df_merge)
st.write(df_merge['final_status'].value_counts())


