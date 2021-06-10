'''
Created on May 25, 2021

@author: 
'''
'''
intent of code is to fetch user selection criteria like bu name and product code
extract sales orders in local file system accordingly
data transformation of mapping wrp with options, mapping option names
run apriori algorithm for selected product
return results

TODO - yet to decide
extract source data from SQL server basis user selection criteria
save results back to SQL server 
'''
import pandas as pd
from mlxtend.frequent_patterns import apriori

dxr_file_path='DXR_Data_2019_20.xlsx'
wrp_file_path='WRP - Apr 2021.xlsx'
df_dxr_main=pd.read_excel(dxr_file_path,sheet_name=None)
df_dxr_options=df_dxr_main['Sheet4']
df_dxr=df_dxr_main['Sheet1']
df_wrp=pd.read_excel(wrp_file_path)
df_wrp=df_wrp[['VARCOND', 'ZCTR']]
items=df_wrp['VARCOND'].astype(str).to_list()
price=df_wrp['ZCTR'].astype(str).to_list()
df_dxr_options=df_dxr_options[['Options','Option Name']]
options=df_dxr_options['Options'].astype(str).to_list()
option_names=df_dxr_options['Option Name'].astype(str).to_list()
# map option, option names
dict_option_names=dict(zip(options,option_names))
# map option, wrp
dict_items_prices=dict(zip(items,price))

# fetch user selection criteria params, here bu and productcode
def get_recommendation(request):
    params=request.get_json()
    bu=params['BU']
    productcode=params['Productcode']
    productcode=str(productcode)
    item_list=[]
    wrp_list=[]
    df_dxr['Product Code']=df_dxr['Product Code'].astype(str)
    df=df_dxr[df_dxr['Product Code']==productcode][['Sales Doc Number','Options']]
    df['Options']=df['Options'].astype(str)
    df=df[df['Options']!=productcode]

    df['Quantity']=1
    b_plus = df.groupby(['Sales Doc Number', 'Options'])['Quantity'].sum().unstack().reset_index().fillna(0).set_index('Sales Doc Number')

    def encode_units(x):
        if x <= 0:
            return 0
        if x >= 1:
            return 1

    b_encode_plus = b_plus.applymap(encode_units)
    b_filter_plus = b_encode_plus[(b_encode_plus > 0).sum(axis=1)>=2]
#     run apriori 
    frequent_itemsets_plus = apriori(b_filter_plus, min_support=.5, 
                                     use_colnames=True).sort_values('support', ascending=False).reset_index(drop=True)

    frequent_itemsets_plus['length'] = frequent_itemsets_plus['itemsets'].apply(lambda x: len(x))

    frequent_itemsets_plus['options'] = [','.join(map(str, l)) for l in frequent_itemsets_plus['itemsets']]
    df_result=frequent_itemsets_plus
    df_result['option_name']=''
    df_result['WRP']=''
    df_result['Total_WRP']=''
    df_result['options']=df_result['options'].astype(str)
    for i in range(len(df_result['options'])):
        item=df_result['options'].iloc[i].split(',')
        item_list.append([dict_option_names[i] for i in item])
    df_result['options_names_list']=item_list
    for i in range(len(df_result['options_names_list'])):
        df_result['option_name'].iloc[i]=",".join(df_result['options_names_list'].iloc[i])
    # sum of wrp
    for i in range(len(df_result['options'])):
        item=df_result['options'].iloc[i].split(',')
        wrp_list.append([dict_items_prices[i] for i in item])
    df_result['WRP_list']=wrp_list
    for i in range(len(df_result['WRP_list'])):
        df_result['WRP'].iloc[i]=",".join(df_result['WRP_list'].iloc[i])
    for i in range(len(df_result['WRP'])):
        items = df_result['WRP'].iloc[i].split(',')
        items = [float(i) for i in items]
        df_result['Total_WRP'].iloc[i] = sum(items)
    df_result=df_result[['support', 'length', 'options', 'option_name', 'WRP', 'Total_WRP']]
    return df_result
    
