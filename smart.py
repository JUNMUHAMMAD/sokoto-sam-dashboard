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
        # Added key parameters to link inputs directly to session state memory
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

        # Clear Action Execution: Wipes out state memory strings before reloading
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
                
                # Success! Now clean out form fields for the next incoming patient entry
                st.session_state.form_hh_id = ""
                st.session_state.form_name = ""
                st.session_state.form_phone = ""
                
                st.success(f'✅ Successfully logged case record for {name}.')
                st.rerun()
            else:
                st.error('❌ Validation Failure: Please fill out all options, assign a Sex, and pick a valid LGA.')
    st.info('The master roster sheet is completely empty right now.')
