import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Define the CSV file to store attendance and nutrition survey records
SURVEY_DATA_FILE = 'smart_nutrition_edema_sam_case_2027.csv'

SOKOTO_LGAS = [
    "Select LGA", "Binji", "Bodinga", "Dange Shuni", "Gada", "Goronyo", 
    "Gudu", "Gwadabawa", "Illela", "Isa", "Kware", "Kebbe", "Rabah", 
    "Sabon Birni", "Shagari", "Silame", "Sokoto North", "Sokoto South", 
    "Tambuwal", "Tangaza", "Tureta", "Wamako", "Wurno", "Yabo"
]

def load_survey_data():
    required_columns = [
        'Timestamp', 'State', 'LGA', 'Cluster Number', 'Household ID', 
        'Participant Name', 'Age (Months)', 'Sex', 'MUAC (cm)', 'Edema Status', 'Phone Number'
    ]
    
    if os.path.exists(SURVEY_DATA_FILE):
        df = pd.read_csv(SURVEY_DATA_FILE)
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            for col in missing_cols:
                df[col] = None
            df.to_csv(SURVEY_DATA_FILE, index=False)
        return df
    return pd.DataFrame(columns=required_columns)

def save_survey_data(df):
    df.to_csv(SURVEY_DATA_FILE, index=False)

# --- Elegant App Configuration ---
st.set_page_config(page_title="SMART Nutrition Survey 2027", layout="wide", page_icon="📊")

# Custom CSS styling for a polished look
st.markdown("""
    <style>
    .main-title { font-size:38px !important; font-weight: bold; color: #1E3A8A; }
    .section-header { font-size:22px !important; font-weight: 600; color: #0F766E; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🏛️ Sokoto State Bureau of Statistics</p>', unsafe_allow_html=True)
st.subheader('SMART Nutrition Survey 2027 — EDEMA or SAM Cases Registry')
st.markdown("---")

current_df = load_survey_data()

# --- TOP ROW: HIGHLIGHT METRICS ---
if not current_df.empty:
    total_registered = len(current_df)
    malnutrition_cases = len(current_df[current_df['MUAC (cm)'] < 11.5])
    edema_cases = len(current_df[current_df['Edema Status'] == 'Present ( +++ )'])
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📋 Total Logged Cases", total_registered)
    m2.metric("⚠️ Severe Malnutrition (MUAC < 11.5cm)", malnutrition_cases, delta=f"{malnutrition_cases} Critical", delta_color="inverse")
    m3.metric("💧 Bilateral Edema Cases", edema_cases, delta=f"{edema_cases} Urgent", delta_color="inverse")
    m4.metric("🗺️ Unique LGAs Screened", current_df['LGA'].dropna().nunique())
    st.markdown("---")

# HERE IS WHERE COL1 AND COL2 ARE CREATED FIRST!
col1, col2 = st.columns([3, 2])

# --- COLUMN 1: ENHANCED INTERACTIVE ENTRY FORM ---
with col1:
    st.markdown('<p class="section-header">📝 Case Screening & Admission Intake</p>', unsafe_allow_html=True)
    
    # Initialize session state keys for the inputs if they don't exist yet
    if "form_hh_id" not in st.session_state:
        st.session_state.form_hh_id = ""
    if "form_name" not in st.session_state:
        st.session_state.form_name = ""
    if "form_phone" not in st.session_state:
        st.session_state.form_phone = ""

    with st.form('nutrition_edema_sam_form', clear_on_submit=False):
        st.markdown("##### 📍 Geographic Identifiers")
        geo_col1, geo_col2, geo_col3 = st.columns(3)
        with geo_col1:
            state = st.text_input('State', value='Sokoto', disabled=True)
        with geo_col2:
            lga = st.selectbox('Local Government Area (LGA)', options=SOKOTO_LGAS)
        with geo_col3:
            cluster_no = st.number_input('Cluster Number', min_value=1, max_value=999, value=1, step=1)
            
        st.markdown("##### 👶 Participant Demographics")
        hh_id = st.text_input('Household ID', key="form_hh_id")
        name = st.text_input('Participant Full Name', key="form_name")
        
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            age = st.number_input('Age (in Months)', min_value=0, max_value=120, value=6, step=1)
        with sub_col2:
            sex = st.selectbox('Sex', options=['Select', 'Male', 'Female'])
            
        st.markdown("##### 🩺 Nutrition Anthropometry Metrics")
        anthro_col1, anthro_col2 = st.columns(2)
        with anthro_col1:
            muac = st.number_input('MUAC (Mid-Upper Arm Circumference in cm)', min_value=5.0, max_value=30.0, value=12.5, step=0.1)
        with anthro_col2:
            edema = st.selectbox('Edema Status (Bilateral Pitting Edema)', options=['Absent ( - )', 'Present ( +++ )'])
        
        phone_number = st.text_input('Contact Phone Number', key="form_phone")
        
        st.markdown(" ")
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            submitted = st.form_submit_button('Submit Case Entry', type='primary')
        with btn_col2:
            clear_submitted = st.form_submit_button('Reset Blank Layout')

        # Clear Action Execution
        if clear_submitted:
            st.session_state.form_hh_id = ""
            st.session_state.form_name = ""
            st.session_state.form_phone = ""
            st.rerun()

        if submitted:
            if lga != 'Select LGA' and hh_id and name and sex != 'Select' and phone_number:
                new_record = pd.DataFrame([{
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'State': state,
                    'LGA': lga,
                    'Cluster Number': int(cluster_no),
                    'Household ID': hh_id,
                    'Participant Name': name,
                    'Age (Months)': int(age),
                    'Sex': sex,
                    'MUAC (cm)': float(muac),
                    'Edema Status': edema,
                    'Phone Number': phone_number
                }])
                
                updated_df = pd.concat([current_df, new_record], ignore_index=True)
                save_survey_data(updated_df)
                
                # Auto clear form inputs upon successful logging
                st.session_state.form_hh_id = ""
                st.session_state.form_name = ""
                st.session_state.form_phone = ""
                
                st.success(f'✅ Successfully logged case record for {name}.')
                st.rerun()
            else:
                st.error('❌ Validation Failure: Please fill out all options, assign a Sex, and pick a valid LGA.')

# --- COLUMN 2: REGISTRY MANAGEMENT & GRAPHICAL ANALYTICS ---
with col2:
    st.markdown('<p class="section-header">🛠️ Registry Controls</p>', unsafe_allow_html=True)
    
    with st.expander("❌ De-register or Purge Erroneous Record"):
        with st.form('registry_removal_form'):
            if not current_df.empty:
                current_df['Select_Label'] = current_df['LGA'].astype(str) + " | Cluster: " + current_df['Cluster Number'].astype(str) + " | HH: " + current_df['Household ID'].astype(str)
                label_to_remove = st.selectbox('Select Specific Entry Context to Purge', options=current_df['Select_Label'].unique())
                
                matching_rows = current_df[current_df['Select_Label'] == label_to_remove]
                remove_submitted = st.form_submit_button('Permanently Delete Entry', type='secondary')
                
                if remove_submitted and not matching_rows.empty:
                    target_row = matching_rows.iloc[0]
                    updated_df = current_df[
                        ~((current_df['LGA'] == target_row['LGA']) & 
                          (current_df['Cluster Number'] == target_row['Cluster Number']) & 
                          (current_df['Household ID'] == target_row['Household ID']))
                    ]
                    if 'Select_Label' in updated_df.columns:
                        updated_df = updated_df.drop(columns=['Select_Label'])
                    save_survey_data(updated_df)
                    st.success('🗑️ Record scrubbed from database storage.')
                    st.rerun()
            else:
                st.info("Roster empty.")

    st.markdown('<p class="section-header">📊 Case Volume by Region</p>', unsafe_allow_html=True)
    if not current_df.empty:
        lga_counts = current_df['LGA'].dropna().value_counts()
        if not lga_counts.empty:
            st.bar_chart(lga_counts, color="#0F766E")
        else:
            st.info("No valid geographical inputs yet.")
    else:
        st.info("Awaiting field data.")

# --- SECTION 3: INFOGRAPHIC DATA REGISTRY SHEET ---
st.markdown("---")
st.markdown('<p class="section-header">📋 Live Cases Sheet & Infographic Risk Level</p>', unsafe_allow_html=True)

if 'Select_Label' in current_df.columns:
    current_df = current_df.drop(columns=['Select_Label'])

if not current_df.empty:
    infographic_df = current_df.copy()
    infographic_df['Malnutrition Severity Tracker'] = (20.0 - infographic_df['MUAC (cm)'].astype(float)).clip(lower=0, upper=15)

    st.data_editor(
        infographic_df.sort_values(by="Timestamp", ascending=False),
        column_config={
            "Malnutrition Severity Tracker": st.column_config.ProgressColumn(
                "Risk Infographic (Longer Bar = Worse Malnutrition)",
                help="Visualizes acute crisis danger level based inversely on MUAC width thresholds",
                format="%.1f",
                min_value=0,
                max_value=12,
                color="red"
            )
        },
        disabled=True,
        use_container_width=True
    )
    
    csv_buffer = current_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Exportable Master EDEMA/SAM Survey Sheet (CSV)",
        data=csv_buffer,
        file_name=f"SMART_Edema_SAM_Master_Export_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.info('The master roster sheet is completely empty right now.')
