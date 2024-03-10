import sys
import pandas  as pd
from dash import dcc,html,Dash,callback,Input,Output 
import plotly.express as ex
import plotly.graph_objects as go
import os 
import plotly.io as pio
import pathlib
########################
main_div="main_div"
main_body="main_body"
title_H1="title_H1"
test="test"
dropdown_diseases="dropdown_diseases"
dropdown_countries="dropdown_countries"
excute_button="excute_button"
graph_div="graph_div"
main_graph="main_graph"
H6_note="H6_note"
all_coun_butt="all_coun_butt"
all_dis_butt="all_dis_butt"
imgcompo="imagcompo"
divdropdown="divdropdown"
div_dropdown_diseases="div_dropdown_diseases"
div_dropdown_countries="div_dropdown_countries"
div_dropdown="div_dropdown"
##################################
PATH=pathlib.Path(__file__).parent
DATA_PATH=PATH.joinpath("data/gulf_df.csv").resolve()

### importing final file exported from  wrangling process
gulf_df=pd.read_csv(DATA_PATH)
df=gulf_df.drop(columns="Unnamed: 0",axis=1)
######### lists used
gulf_countries=['Saudi Arabia','United Arab Emirates',"Kuwait","Bahrain","Oman","Qatar","Iraq",] #country_list
diseases_list=gulf_df["cause"].unique().tolist()


##################################
image_path = 'assets/WHO_logo.png'

def mainbody ():
    app=Dash(__name__,title="the-body-of-one-file")
    app.layout=html.Div(id=main_div,className="main_div",children=[
        html.Div(id=imgcompo,children=[
                                            html.H1(id=title_H1,className="title_H1",children=["Total deaths in Arabic gulf countries by WHO "],style={"text-align":"center"}),
                                            html.Img(src=image_path,alt="WHO logo",width=50,height=50),
                                           ]),
        html.Div(id=div_dropdown,children=[
                                                html.Div(id=div_dropdown_diseases,children=[dcc.Dropdown(id=dropdown_diseases,options=diseases_list,value=["Mental Disorders"],multi=True,searchable=True,clearable=True,placeholder="Select the diseases you want....",className="dropdown_diseases",),
                                                html.Button(id=all_dis_butt,children=["All diseases"],n_clicks=0),]),
                                                html.Br(),
                                                html.Div(id=div_dropdown_countries,children=[dcc.Dropdown(id=dropdown_countries,options=gulf_countries,value=["Qatar"],multi=True,searchable=True,clearable=True,placeholder="Select the countries you want...."),
                                                html.Button(id=all_coun_butt,children=["All countries"],n_clicks=0),]),
                                                html.Br(),
        ]),

        html.Div(id=graph_div,children=[dcc.Graph(id=main_graph,figure=go.Figure())]),
        html.Br(),
        html.H5(id=H6_note,className="H6_note",children=["Note: these data were pulled only form World Health Organization"]),
    ])
            
    return app






def selecting_df(df,code_list,country_list):    #function to select  Dataframe based on country list and diseaes code list
    final_df=pd.DataFrame()
    if  isinstance(country_list ,list) == True:
        final_df=df.loc[df["country_name"].isin(country_list) & df["cause"].isin(code_list)]
    elif isinstance(country_list,str) == True:
        final_df=df.loc[df["country_name"].isin([country_list]) & df["cause"].isin(code_list)]
    return final_df

def selecting_country(df:pd.DataFrame,country_name:str)->pd.DataFrame: # function to select DataFrame based on country 
    final=pd.DataFrame()
    grouped =df.groupby("country_name")
    if country_name == None:
        final=pd.DataFrame()
    elif isinstance(country_name,str)==True:
        final=grouped.get_group(country_name)
    elif isinstance(country_name,list)==True:
        df_list=[]
        for i in range(0,len(country_name)):
            temp=grouped.get_group(country_name[i])
            df_list.append(temp)
        final=pd.concat(df_list)
    return final
    

def selecting_disease(df,disease_name): # function to chose dataframe based on certain diseaes
    final=pd.DataFrame()
    if disease_name==None:
        final=pd.DataFrame()
    elif isinstance(disease_name,str):
        filt=df["cause"]==disease_name
        final=df.loc[filt]
    elif isinstance(disease_name,list):
        filt=df["cause"].isin(disease_name)
        final=df.loc[filt]
    return final
 


def labling(df,code_series,): # functions to label coulmn
    temp=df.copy()
    code_list=code_series.to_list()
    for i in range(0,len(temp["cause"])):
        if temp["cause"].iloc[i] in code_list:
            temp["cause"].iloc[i]=code_series.name
    return temp





def final_filter(dataframe:pd.DataFrame,country: str,diseases:str)->pd.DataFrame:
    df=selecting_country(dataframe,country_name=country)
    df=selecting_disease(df=df,disease_name=diseases)
    df=df.rename(columns={"deaths1":"total death","country_name":"Country name","sex":"Sex"},)
    df.drop(columns="country",axis=1,inplace=True)
    df["Sex"]=df["Sex"].apply(lambda x : "Male" if x==1 else ("Female" if x ==2 else "Non-binary") )
    return df

################ used in interaction file ################
def empty_graph():
    fig=go.Figure()
    fig.update_layout(template="plotly_dark")
    return fig
    
    
    
                ################ graphing ################


def graphing(dataframe:pd.DataFrame,country: str,diseases:str)->go.Figure:
    df=final_filter(dataframe=dataframe,country=country,diseases=diseases)
    fig=ex.histogram(data_frame=df,x="year",y="total death",color="Country name",pattern_shape="Sex",)
    fig.update_layout(bargap=.2,template="plotly_dark")
    fig.update_xaxes(tickmode="linear",title="Year")
    fig.update_yaxes(title="Total deaths")
    return fig






@callback(Output(component_id=dropdown_diseases,component_property="value"),
                 Input(component_id=all_dis_butt,component_property="n_clicks"))
def all_diseaes(n_cl):
    if n_cl!=0:
        return diseases_list

@callback(Output(component_id=dropdown_countries,component_property="value"),
                 Input(component_id=all_coun_butt,component_property="n_clicks"))
def all_coun(n_cl): 
    if n_cl!=0:
        return gulf_countries



@callback(Output(component_id=main_graph,component_property="figure"),
          Input(component_id=dropdown_countries,component_property="value"),
          Input(component_id=dropdown_diseases,component_property="value"))
def graph(c_va,di_value):
    if c_va==None or di_value==None :
        return empty_graph()
    elif len(c_va)==0 or len(di_value)== 0:
        return empty_graph()
    else:
        fig=graphing(dataframe=df,diseases=di_value,country=c_va)
        return fig








app= mainbody()



server = app.server

if __name__ == "__main__":
    app.run(debug=True)
