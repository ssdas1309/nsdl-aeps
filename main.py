import streamlit as st
import pandas as pd
import numpy as np
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
mware = mware[['apiTid','status','userName']]
mware.rename(columns = {'apiTid':'RRN'}, inplace = True)
npci.rename(columns = {'Transaction Serial Number':'RRN'}, inplace = True)
switch = switch[['RRN','Transaction Status']]
# df_final.to_csv('alldata.csv')
# st.write(df_merge)
df_merge = pd.merge(pd.merge(npci, switch, on='RRN', how='outer', suffixes=("_npci","_switch")), mware, on='RRN', how='outer')
st.dataframe(df_merge)
df_merge.to_csv(index=False).encode('utf-8')
# st.download_button("Download CSV",df_merge.to_excel,file_name='Recon_file.csv',mime='text/csv')
# st.sidebar.download_button(label='Download CSV',data=result,mime='text/csv',file_name='Download.csv')
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'})
    worksheet.set_column('A:A', None, format1)
    writer.save()
    processed_data = output.getvalue()
    return processed_data
df_xlsx = to_excel(df_merge)
# df_xlsx=b'df_merge'
st.download_button(label='📥 Download Recon Result',
                                data=df_xlsx ,
                                file_name= 'df_merge.xlsx')
