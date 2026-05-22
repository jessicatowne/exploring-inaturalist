import streamlit as st

# title and favicon
st.set_page_config(page_title='Exploring iNaturalist', page_icon='🔎')

# add sidebar instruction
st.sidebar.success('Click "Visualisations" above to see user activity')

# connect to postgresql database inaturalist
conn = st.connection("postgresql", type="sql")

# function to return sql query
def load_df():
    df = conn.query('SELECT '
                        'o.observation_id, '
                        's.taxon_id, '
                        'u.user_id, '
                        'u.user_login, '
                        'o.species_guess, '
                        's.common_name, '
                        's.scientific_name, '
                        's.iconic_taxon_name, '
                        'o.quality_grade, '
                        'o.license, '
                        'o.num_identification_agreements, '
                        'o.num_identification_disagreements, '
                        'o.captive_cultivated, '
                        'o.latitude, '
                        'o.longitude, '
                        'DATE(d.observed_on) AS observed_on, '
                        'DATE(d.created_at) AS created_at, '
                        'DATE(d.updated_at) AS updated_at, '
                        'm.url, '
                        'm.image_url, '
                        'm.tag_list, '
                        'm.description '
                    'FROM observations o '
                    'JOIN species s '
                    'ON o.taxon_id = s.taxon_id '
                    'JOIN users u '
                    'ON o.user_id = u.user_id '
                    'JOIN observation_datetime d '
                    'ON o.observation_id = d.observation_id '
                    'JOIN observation_metadata m '
                    'ON o.observation_id = m.observation_id;')

    # find unique values for dropdown boxes
    taxonomic_group_options = df.iconic_taxon_name.unique()
    license_options = df.license.unique()
    captive_cult_options = df.captive_cultivated.unique()
    quality_grade_options = df.quality_grade.unique()

    # min date and max date for slider
    min_date = df.observed_on.min()
    max_date = df.observed_on.max()

    # return dataframe
    return df, taxonomic_group_options, license_options, captive_cult_options, quality_grade_options, min_date, max_date

# function to check if dropdown boxes are used
def check_rows(column, options):
    return res.loc[res[column].isin(options)]

# call load_df() function
df, taxonomic_group_options, license_options, captive_cult_options, quality_grade_options, min_date, max_date = load_df()

# create dataframe res to be filtered
res = df

# text input boxes for species and username
textbox_cols = st.columns(2)
species_query = textbox_cols[0].text_input("Search for a species")
username_query = textbox_cols[1].text_input("Search for a username")

# dropdown boxes for taxonomic group, license, captive/cultivated, and quality grade
dropdown_cols = st.columns(4)
taxonomic_group = dropdown_cols[0].multiselect("Taxonomic group", taxonomic_group_options)
license = dropdown_cols[1].multiselect("License", license_options)
captive_cult = dropdown_cols[2].multiselect("Captive/cultivated", captive_cult_options)
quality_grade = dropdown_cols[3].multiselect("Quality grade", quality_grade_options)

# date range slider
date_col = st.columns(1)
min_date_range, max_date_range = date_col[0].slider('Select a date range', min_value=min_date, max_value=max_date, value=(min_date, max_date))

# filter dataframe by input
if species_query != "":
    res = res.loc[res.common_name.str.contains(species_query)]

if username_query != "":
    res = res.loc[res.user_login.str.contains(username_query)]

if taxonomic_group:
    res = check_rows("iconic_taxon_name", taxonomic_group)

if license:
    res = check_rows("license", license)

if captive_cult:
    res = check_rows("captive_cultivated", captive_cult)

if quality_grade:
    res = check_rows("quality_grade", quality_grade)

if date_col[0].checkbox("Use this date range"):
    res = res.loc[(res.observed_on > min_date_range) & (res.observed_on < max_date_range)]

# print filtered dataframe
st.dataframe(res, hide_index=True)

# add divider
st.write('---')

# explanation of columns
legend = '''
    **observation_id**: Unique identifier for an observation  
    **user_id**: Unique identifier for a user   
    **taxon_id**: Unique identifier for a species  
    **user_login**: Username  
    **species_guess**: Initial identification submitted by a user  
    **common_name**: Common name for final identification   
    **scientific_name**: Scientific name for final identification   
    **iconic_taxon_name**: Taxonomic group for final identification   
    **quality_grade**: Whether an observation fulfils research criteria or still requires ID  
    **license**: Copyright license  
    **num_identification_agreements**: Number of positive votes for identification  
    **num_identification_disagreements**: Number of negative votes for identification  
    **captive_cultivated**: Whether the observation is of a captive or cultivated organism  
    **latitude**: Latitude  
    **longitude**: Longitude  
    **observed_on**: Date the observation was made  
    **created_at**: Date the observation was uploaded  
    **updated_at**: Date the observation was updated  
    **url**: URL of the observation  
    **image_url**: URL of the image of the observation  
    **tag_list**: Tags of the observation  
    **description**: Description of the observation  
'''

# print legend
st.markdown(legend)