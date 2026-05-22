import streamlit as st

# page layout with 2 columns, title, favicon
col1, col2, = st.columns([1, 1], gap='large', vertical_alignment='top')
st.set_page_config(page_title='Exploring iNaturalist', page_icon='📊', layout='wide')

# add sidebar instruction
st.sidebar.success('Click "Database" above to explore the raw data')

# connect to postgresql database inaturalist
conn = st.connection("postgresql", type="sql")

# contents of column 1
with col1:
    st.title('Exploring iNaturalist')
    st.write(
        'iNaturalist is a non-profit organisation that helps users to identify the wildlife they find and shares '
        'these records with scientists to understand and protect nature around the world. Users have been submitting '
        'records in Sheffield since 2009 and these visualisations explore their activity.')


    # activity by month chart
    month_query = conn.query('SELECT CAST(EXTRACT(YEAR FROM d.observed_on) AS VARCHAR) AS obs_year, '
                                    'EXTRACT(MONTH FROM d.observed_on) AS obs_month, '
                                    'COUNT(o.observation_id) AS obs '
                             'FROM observations o '
                             'JOIN observation_datetime d '
                             'ON o.observation_id = d.observation_id '
                             'GROUP BY obs_year, obs_month '
                             'ORDER BY obs_year, obs_month;')

    st.subheader('Activity by month')
    st.line_chart(month_query, x='obs_month', y='obs', color='obs_year', x_label='Month', y_label='Observations')

    # observations by year chart
    obs_count = conn.query('SELECT EXTRACT(YEAR FROM d.observed_on) AS obs_year, '
                                  'COUNT(o.observation_id) AS obs '
                           'FROM observations o '
                           'JOIN observation_datetime d '
                           'ON o.observation_id = d.observation_id '
                           'GROUP BY obs_year '
                           'ORDER BY obs_year;')

    st.subheader('Activity by year')
    st.bar_chart(obs_count, x='obs_year', y='obs', x_label='Year', y_label='Observations', horizontal=True, sort='-obs_year')

# contents of column 2
with col2:
    # map with observations by year
    map_query = conn.query('SELECT EXTRACT(YEAR FROM d.observed_on) AS obs_date, '
	                              'o.latitude, '
	                              'o.longitude, '
	                              'COUNT(o.observation_id) AS obs '
                           'FROM observations o '
                           'JOIN observation_datetime d '
                           'ON o.observation_id = d.observation_id '
                           'GROUP BY obs_date, latitude, longitude '
                           'ORDER BY obs_date;')

    map_filter = st.slider('Select a year', min_value=2009, max_value=2026, value=2026)
    filtered_map = map_query[map_query['obs_date'] == map_filter]

    st.map(filtered_map)

    # taxonomic group chart
    taxon_query = conn.query('SELECT iconic_taxon_name as taxa, '
                                    'count(iconic_taxon_name) as taxa_count '
                             'FROM observations o JOIN species s '
                             'ON o.taxon_id = s.taxon_id '
                             'WHERE iconic_taxon_name IS NOT NULL '
                             'GROUP BY iconic_taxon_name;')

    st.subheader('Taxonomic groups')
    st.bar_chart(taxon_query, x='taxa', y='taxa_count', x_label='Taxonomic Group', y_label='Observations', horizontal=True)

# containers for dataframes
with st.container(horizontal=True):
    st.subheader('Top 10 users')
    st.subheader('How often do users agree or disagree with each other?', text_alignment='right')

with st.container(horizontal=True):
    # top users dataframe
    top_query = conn.query('SELECT u.user_login AS "Username", '
                                  'COUNT(u.user_login) AS "Observations" '
                           'FROM observations o '
                           'JOIN users u '
                           'ON o.user_id = u.user_id '
                           'GROUP BY u.user_login '
                           'ORDER BY COUNT(u.user_login) DESC '
                           'LIMIT 10;')

    st.dataframe(top_query, hide_index=True)

    # agreement/disagreement dataframe
    agree_query = conn.query('SELECT common_name AS "Common name",'
                                    'scientific_name AS "Scientific name", '
                                    'COUNT(observation_id) AS "Observations", '
                                    'SUM(num_identification_agreements) AS "Agreements", '
                                    'SUM(num_identification_disagreements) AS "Disagreements", '
                                    'ROUND(CAST(SUM(num_identification_agreements) AS decimal) * 100 / GREATEST(SUM(num_identification_agreements) '
                                        '+ SUM(num_identification_disagreements), 1), 2) AS "Percent agreements" '
                             'FROM observations o '
                             'JOIN species s '
                             'ON o.taxon_id = s.taxon_id '
                             'GROUP BY scientific_name, common_name '
                             'ORDER BY "Observations" DESC;')

    st.dataframe(agree_query, hide_index=True)