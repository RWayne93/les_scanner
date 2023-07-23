import streamlit as st
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from entitlements import check_pay
from cola import calculate_total_pay_month
from location_code_constants import LOCATION_CODES
from mha_constants import MHA

flipped_location_codes = {v: k for k, v in LOCATION_CODES.items()}
location_codes_list = list(flipped_location_codes.keys())
flipped_mha = {v: k for k, v in MHA.items()}
mha_list = list(flipped_mha.keys())


# Azure Form Recognizer API endpoint and key
endpoint = "https://westus.api.cognitive.microsoft.com/"
model_id = "les_scanner"

# Streamlit app
def app():
    key = 'azure form recognizer api key goes here'
    st.title('LES Analyzer')
    st.write('Upload your LES as a pdf file to analyze')

    # File upload
    uploaded_file = st.file_uploader('Choose a PDF file', type='pdf')

    if uploaded_file is not None:
        # Check if this is the first upload
        if 'entitlements' not in st.session_state:
            # Send file to Azure Form Recognizer
            data = uploaded_file.read()
            document_analysis_client = DocumentAnalysisClient(endpoint, AzureKeyCredential(key))
            poller = document_analysis_client.begin_analyze_document(model_id, data)
            result = poller.result()

            entitlements = {}
            # Display results
            for idx, document in enumerate(result.documents):
                # st.write("--------Analyzing document #{}--------".format(idx + 1))
                # st.write("Document has type {}".format(document.doc_type))
                # st.write("Document has confidence {}".format(document.confidence))
                # st.write("Document was analyzed by model with ID {}".format(result.model_id))
                for name, field in document.fields.items():
                    field_value = field.value if field.value else field.content
                   # st.write("......found field of type '{}' with value '{}' and with confidence {}".format(field.value_type, field_value, field.confidence))

                    # If the field value is a string and contains a space, it may be a key-value pair
                    if field.value_type == 'string' and ' ' in field_value:
                        parts = field_value.split(' ')
                        key = ' '.join(parts[:-1])  # join all parts except the last one with a space
                        value = parts[-1]  # the last part should be the value
                        entitlements[key] = float(value)  # save as float in the dictionary

            st.session_state['entitlements'] = entitlements
        else:
            entitlements = st.session_state['entitlements']

        #st.write({'entitlements': entitlements})
        st.write('Entitlements:')
        st.write('\n'.join([f'{key}: {value}' for key, value in sorted(entitlements.items())]))

        # Now we collect COLA parameters
        #loc_code = st.text_input("Enter Location Code:").upper()
        selected_mha_description = st.selectbox('Select an MHA This will be to check your BHA:', options=mha_list)
        mha_code = flipped_mha[selected_mha_description]
        selected_location_description = st.selectbox('Select a Location:', options=location_codes_list)
        loc_code = flipped_location_codes[selected_location_description]
        rank = st.text_input("Enter Rank:").upper()
        depend = st.number_input("Enter Number of Dependents:", min_value=0, step=1)
        service = st.number_input("Enter years in service:", min_value=0, step=1)
        barracks_options = ["YES", "NO"]
        barracks = st.selectbox("Enter Barrack Status:", options=barracks_options).upper()

        if st.button("Calculate"):
            cola = calculate_total_pay_month(loc_code, rank, depend, service, barracks)
            if entitlements['COLA'] != cola:
                st.write(f"Your current COLA is: {entitlements['COLA']} however you should be getting: {cola} There might be something wrong with your COLA. Please check your COLA.")
            check_pay(entitlements, rank, years=service, mha=mha_code)

app()

