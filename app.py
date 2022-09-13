from numpy import rec, size
from simple_salesforce import Salesforce
import requests
import pandas as pd
from io import StringIO
import streamlit as st
import streamlit.components.v1 as stc
from PIL import Image
import urllib.parse
import base64
import time

sf = Salesforce(username='',password='',security_token='')

sf_instance = 'https://flexability.lightning.force.com/'
reportId = '00O4W000007xprJUAQ'
export = '?isdtp=p1&export=1&enc=UTF-8&xf=csv'
sfUrl = sf_instance + reportId + export
response = requests.get(sfUrl, headers=sf.headers, cookies={'sid': sf.session_id})
download_report = response.content.decode('utf-8')
df1 = pd.read_csv(StringIO(download_report))

descri=sf.SCSCHAMPS__Job__c.describe()
a = [field['name'] for field in descri['fields']]

results=sf.query_all("""
    SELECT
    Name,Domain__c,Industry__c,Function2__c,SCSCHAMPS__Job_Title__c,Position_Location_City__c,SCSCHAMPS__Stage__c,Desired_Skills__c,SCSCHAMPS__Job_Description__c,Experience__c
    from SCSCHAMPS__Job__c
    where SCSCHAMPS__Stage__c='Open'
    """)

records = [dict(Name=rec['Name'],
                Domain__c=rec['Domain__c'],
                Industry__c=rec['Industry__c'],
                Function2__c=rec['Function2__c'],
                SCSCHAMPS__Job_Title__c=rec['SCSCHAMPS__Job_Title__c'],
                Position_Location_City__c=rec['Position_Location_City__c'],
                SCSCHAMPS__Stage__c=rec['SCSCHAMPS__Stage__c'],
                Desired_Skills__c=rec['Desired_Skills__c'],
                SCSCHAMPS__Job_Description__c=rec['SCSCHAMPS__Job_Description__c'],
                Experience__c=rec['Experience__c'])
                for rec in results['records']]

df = pd.DataFrame(records) 

JOB_HTML_TEMPLATE = """
<div style="width:100%;height:100%;margin:1px;margin-bottom:8px;padding:5px;
position:relative;border-radius:5px;box-shadow:0 0 1px 1px #eee;
 background-color: #31333F;border-left: 5px solid #6c6c6c;color:white;">
<h5>{}</h5>
<h6 style="color:#99FF00;">{}</h6>
<h6 style="color:#FF3366;">{}</h6>
</div>
"""


JOB_DES_HTML_TEMPLATE = """
<div style='color: #FF3366;font-style:courier'>
{}
</div>
"""

JOB_SKILLS_HTML_TEMPLATE = """
<div style='color: #FF0066'>
{}
</div>
"""


image = Image.open('hero_1.jpg')
flex = Image.open('flex.png')

def main():
    st.image(flex)
    menu = ['Home','About']
    choice = st.sidebar.selectbox('Menu',menu)
    if choice == 'Home':
        st.button("Home")  

        with st.sidebar:
            with st.form(key='searchform'):
                with st.sidebar:
                    ZeroFilter = st.selectbox('Enter Domain',options=df['Domain__c'].unique())
                    
                df1 = df.query('Domain__c == @ZeroFilter')

  #              with st.sidebar:
  #                  FirstFilter = st.multiselect('Enter Industry',options=df['Industry__c'].unique(),default=df1['Industry__c'].unique())

                #df2 = st.session_state.df.query('Industry__c == @ZeroFilter')

                with st.sidebar:
                    SecondFilter = st.multiselect('Enter Job field',options=df1['Function2__c'].unique())

                df3 = df.query('Function2__c == @SecondFilter')

                with st.sidebar:
                    FourthFilter = st.multiselect('Select Location',options=df['Position_Location_City__c'].unique(),default='Mumbai')
                df4 = df3.query('Position_Location_City__c == @FourthFilter')

                with st.sidebar:
                    submit_search = st.form_submit_button(label='Search')
        if not submit_search:
            st.image(image)

        if submit_search:
            st.success('You searched for {} Job Roles in {} at {}'.format(ZeroFilter,SecondFilter,FourthFilter[0]))



        # Results
        col1, col2 = st.columns([2,1])
        with col1:
            if submit_search:
                num_of_results = df4.shape[0]
                st.subheader('Showing {} Open Mandates'.format(num_of_results))
                

                for i in df4.values.tolist():
                    name = i[0]
                    role = i[4]
                    location = i[5]
                    desc = i[8]
                    exp = 'Exp: ' + i[9]
                    skills = i[7]
                    st.markdown(JOB_HTML_TEMPLATE.format(role,location,exp),unsafe_allow_html=True)

                    #Description
                    with st.expander('Description'):
                        stc.html(JOB_DES_HTML_TEMPLATE.format(desc),scrolling=True)
                    # Skills
                    with st.expander('Skills'):
                        stc.html(JOB_SKILLS_HTML_TEMPLATE.format(skills),scrolling=True)
                    # Apply 
                    link = 'https://docs.google.com/forms/d/e/1FAIpQLSeBKHuX6x36Z80NB6faEeX5g23T9z2lNa5a-QeiIupyChTVRQ/viewform?usp=pp_url&entry.746677692={}&2083700979=&entry.592548609=d{}&entry.2020110615=Data+science'.format(name,role)
                    url = link.replace(" ","+")
                    st.write(f'''
                   
    <a target="_blank" href={{}}>
        <input type="button" style="background-color:#FF3366;color:white;width:70px;height:35px;border-radius:5px;margin-bottom:25px;" value="Apply">
        
    </a>
    '''.format(url),
    unsafe_allow_html=True
)
                    
                                                           

                
                

                    
    else:
        st.write(f"""
        <h3>About</h3>
        """,unsafe_allow_html=True)
        st.markdown("<style>.element-container{opacity:1 !important}</style>", unsafe_allow_html=True)
        st.write('The application fetches Real Time Data from the Database and further filters out Open Mandates')
        st.write('For Business related queries contact us on : ')
        st.write('For App related Software issues, security vulnerabilities, suggestions and feedback to improve user experience contact : robin.kiliyilathu@flexability.in')

if __name__ == '__main__':
    main()