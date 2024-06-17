import streamlit as st
import plotly.express as px
import pandas as pd
import os
from streamlit_card import card 
from textblob import TextBlob
import warnings
from PIL import Image
warnings.filterwarnings('ignore')

st.set_page_config(page_title="OTT Platform Dashboard!!!", page_icon=":bar_chart:",layout="wide")

st.title(" :grey-background[:rainbow[Netflix + Amazon Prime + Disney Plus + Hotstar]] ")
st.subheader(":orange[Interactive Dashboard ]:chart_with_downwards_trend:")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

# Adjust the img_dir path to the correct location
img_dir = "img"

# Display platform logos in columns
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.image(os.path.join(img_dir, "netfix.jpg"), use_column_width=True)
with col2:
    st.image(os.path.join(img_dir, "amazontv.jpeg"), use_column_width=True)
with col3:
    st.image(os.path.join(img_dir, "disney.jpg"), use_column_width=True)
with col4:
    st.image(os.path.join(img_dir, "hotstar.jpg"), use_column_width=True)

# Browse and upload a file
fl = st.file_uploader(":file_folder: Upload a file", type=["csv"])

# Load data based on the uploaded file or default to a local file
if fl is not None:
    filename = fl.name
    df = pd.read_csv(fl, encoding="ISO-8859-1")
    title = filename.split('.')[0]  # Get the filename without extension
else:
    df = pd.read_csv(os.path.join("datasets", "Amazon_Prime.csv"), encoding="ISO-8859-1")
    title = "Amazon Prime"  # Default title if no file is uploaded

# Display the title based on the filename or default
st.write(f"# :blue[{title}]")

# Function to load data (caching can be added if needed)
def load_data():
    return df

st.markdown("<marquee style='color:yellow;'>🔴 In all Datasets columns name should be same.🔴 </marquee>", unsafe_allow_html=True)
df = load_data()
if 'release_Date' in df.columns:
    # Convert 'release_Date' to datetime, setting errors='coerce' to handle invalid dates
    df['release_Date'] = pd.to_datetime(df['release_Date'], errors='coerce')
    
    # Drop rows with NaN 'release_Date' values
    df = df.dropna(subset=['release_Date'])
    
    # Extract the year and convert to integer
    df['release_year'] = df['release_Date'].dt.year.astype(int)

   
# Filerd TOP KPI's

# TOTAL MOVIES
movie_type=df['type']=='Movie'
movies_counts=movie_type.sum()

# TOTAL TV SHOW
show_type=df['type']=='TV Show'
show_counts=show_type.sum()

# TOTAL COUNTRIES
country_count = df['country'].str.split(', ', expand=True).stack().nunique()

# TOTAL GENERS
genre_counts = df['genre'].str.split(', ', expand=True).stack().nunique()

#TOTAL DIRECTORS
director_counts = df['director'].str.split(', ', expand=True).stack().nunique()

#TOTAL DIRECTORS
cast_counts = df['cast'].str.split(', ', expand=True).stack().nunique()

#Create columns for KPIs
k1, k2, k3, k4, k5 = st.columns(5)
# Display KPIs
k1.metric("Total Movies",f"{movies_counts}")
k2.metric("Total TV Shows", f"{show_counts}")
k3.metric("Total Countries", f"{country_count}")
k4.metric("Total Geners",f"{genre_counts}")
k5.metric("Total Directors", f"{director_counts}")



#create columns 
p1,p2= st.columns(2)
# Filtered data of rating the pie chart
rating_filtered = df.groupby(['rating']).size().reset_index(name='counts')
rating_filtered['counts'] = rating_filtered['counts'].apply(lambda x: round(x) if x >= 10 else x)

# Display the pie chart
with p1:
    pieChart = px.pie(rating_filtered, values='counts', 
                      names='rating', title='Ratings',
                      color_discrete_sequence=px.colors.cyclical.Twilight)
    st.subheader(f'Rating Distribution :red[{title}]')
    st.plotly_chart(pieChart)

# Countplot of the 'type' column
type_counts = df['type'].value_counts()

with p2:
# Create a pie chart using plotly.express
   fig = px.pie(
    names=type_counts.index,
    values=type_counts,
    title='Show Types',
    labels={'name': 'Type', 'value': 'Count', 'percent': 'Percentage'},
    color_discrete_sequence=[ 'crimson', 'peachpuff']
   )
   st.subheader(f'Show Type Distribution :red[{title}]')
   st.plotly_chart(fig)

# Create a Column
c1,c2 = st.columns(2)
# Display director-wise info
#st.markdown('**Total directors by total shows**')
if 'director' in df.columns: #this condition is for if there is that '' column in dataset then only display
   total_directors_by_shows = df['director'].str.split(',', expand=True).stack().value_counts().reset_index()
   total_directors_by_shows.columns = ['Director', 'Total Shows']
   with c1:
    director_option = st.selectbox('Select a director', total_directors_by_shows['Director'].unique())
    selected_shows = total_directors_by_shows[total_directors_by_shows['Director'] == director_option]['Total Shows'].values[0]
    st.markdown(f'The total number of Movies/shows directed by {director_option} is {selected_shows} in {title}.')

#Top 5 directors bar chart
if 'director' in df.columns:
   
   df['director'] = df['director'].fillna('Director not specified')
   directors_list = pd.DataFrame(df['director'].str.split(',', expand=True).stack())
   directors_list.columns = ['Directors']
   directors = directors_list.groupby(['Directors']).size().reset_index(name='Total Count')
   directors = directors[directors.Directors != 'Director not specified']
   directors = directors.sort_values(by=['Total Count'], ascending=False)
   top5Directors = directors.head()

# Display cast-wise information
if 'cast' in df.columns: #this condition is for if there is that '' column in dataset then only display
   total_cast_by_shows = df['cast'].str.split(',', expand=True).stack().value_counts().reset_index()
   total_cast_by_shows.columns = ['Cast', 'Total Shows']
   with c2:
    cast_option = st.selectbox('Select a cast', total_cast_by_shows['Cast'].unique())
    selected_shows = total_cast_by_shows[total_cast_by_shows['Cast'] == cast_option]['Total Shows'].values[0]
    st.markdown(f'The total number of shows cast by {cast_option} is {selected_shows}.')

# A Top 5 actors bar chart
if 'cast' in df.columns:
   df['cast'] = df['cast'].fillna('No cast specified')
   cast_df = pd.DataFrame(df['cast'].str.split(',', expand=True).stack())
   cast_df.columns = ['Actor']
   actors = cast_df.groupby(['Actor']).size().reset_index(name='Total Count')
   actors = actors[actors.Actor != 'No cast specified']
   actors = actors.sort_values(by=['Total Count'], ascending=False)
   top5Actors = actors.head()

# Display the bar chart
# Create two columns
col1, col2 = st.columns(2)
if 'director' in df.columns:
  with col1:
    st.subheader(f'TOP 5 DITECTORS :red[{title}]')
    barChart = px.bar(top5Directors, x='Total Count', y='Directors',
                       title= f'Directors who had done most Movies / TV Shows ',
                        color_discrete_sequence=['turquoise'])
    st.plotly_chart(barChart)
if 'cast' in df.columns:
  with col2:
    st.subheader(f'TOP 5 CAST :red[{title}]')
# Display the bar chart for top 5 actors
    barChart2 = px.bar(top5Actors, x='Total Count', y='Actor',
                       title=' Actors who had done most Movies / TV Shows',
                        color_discrete_sequence=['paleturquoise'])
    st.plotly_chart(barChart2)


# Top 5 genres bar chart
if 'genre' in df.columns: #this condition is for if there is that '' column in dataset then only display
   total_genre_by_shows = df['genre'].str.split(',', expand=True).stack().value_counts().reset_index()
   total_genre_by_shows.columns = ['Genre', 'Total']
   top5genre = total_genre_by_shows.head(10)

# Display the bar chart
if 'genre' in df.columns:
   
    st.subheader(f'Top 5 Genres :red[{title}]')
    barChart3 = px.bar(top5genre, y='Total', x='Genre',
                        title='Top 5 Genres',width=1450,
                 height=600,
                        color_discrete_sequence=['firebrick'])
    st.plotly_chart(barChart3)


# Create a columns for line and stackbar chart
l1,l2=st.columns(2)

# Line chart by release year
df1 = df[['type', 'release_year']]
df1 = df1.rename(columns={"release_year": "Release Year", "type": "Type"})
df2 = df1.groupby(['Release Year', 'Type']).size().reset_index(name='Total Count')
df2 = df2[df2['Release Year'] >= 2000]
with l1:
# Display the line chart
   st.subheader(f'Trends of Contents by Release Year :red[{title}]')
   graph = px.line(df2, x="Release Year", y="Total Count", color="Type", title="Trends")
   st.plotly_chart(graph)

# Sentiment Analysis

df3 = df[['release_year', 'description']]
df3 = df3.rename(columns={'release_year': 'Release Year', 'description': 'Description'})

# Replace NaN values with an empty string
df3['Description'] = df3['Description'].fillna('')

# Initialize a new 'Sentiment' column
df3['Sentiment'] = ''
for index, row in df3.iterrows():
    d = row['Description']
    testimonial = TextBlob(d)
    p = testimonial.sentiment.polarity
    if p == 0:
        sent = 'Neutral'
    elif p > 0:
        sent = 'Positive'
    else:
        sent = 'Negative'
    df3.loc[[index, 2], 'Sentiment'] = sent

df3 = df3.groupby(['Release Year', 'Sentiment']).size().reset_index(name='Total Count')
df3 = df3[df3['Release Year'] > 2005]

with l2:
# Display the bar chart for sentiment analysis
   st.subheader(f'Sentiment Analysis on Contents :red[{title}]')
   barGraph = px.bar(df3, x="Release Year", y="Total Count", color="Sentiment", title="Sentiment Analysis")
   st.plotly_chart(barGraph)


#TOP 10 MOVIES OR TV SHOWS RELEASED IN MAX COUNTRIES
# Create 'country_count' column
df['country_count'] = df['country'].apply(lambda x: len(str(x).split(',')) if pd.notnull(x) and x != '[]' else 0)

# Function to generate top 10 chart
def generate_top_10_chart(data, title, x_label, y_label):
    # Sort the DataFrame based on the 'country_count' column in descending order
    sorted_data = data.sort_values(by='country_count', ascending=True)

    # Select the top 10 entries with the maximum number of countries
    top_10_data = sorted_data.tail(10)

    #Display top 10 in bar chart
    fig = px.bar(top_10_data, x='country_count', y='title', orientation='h', text='country_count',
                 labels={'country_count': x_label, 'title': y_label}, title=title,width=1400,height=600,
                 color='country_count', color_continuous_scale='viridis')

    return fig

# Streamlit user input
data_type = st.selectbox('Choose Type', ['Movie', 'TV Show'])

# Filter data based on user selection
filtered_df = df[df['type'] == data_type]

# Create chart based on user selection
st.subheader(f'TOP 10 {data_type}s Released in Max Countries :red[{title}]')
st.plotly_chart(generate_top_10_chart(filtered_df, f'Top 10 {data_type}s', 'Number of Countries Released', f'{data_type} Title'))

# Filter data for the top 10 countries
top_countries = df['country'].value_counts().head(10).index
filtered_df = df[df['country'].isin(top_countries)]

# Split the 'genre' column and expand the DataFrame
genres_expanded = filtered_df['genre'].str.split(', ', expand=True).stack().reset_index(level=1, drop=True)
genres_expanded.name = 'genre'  # Rename the column

# Add the expanded 'genre' column back to the DataFrame
filtered_df = filtered_df.drop('genre', axis=1).join(genres_expanded)

# Create a hierarchical DataFrame
hierarchical_df = filtered_df.groupby(['country', 'genre', 'release_year', 'type', 'title', 'description']).size().reset_index(name='count')
hierarchical_df['color'] = pd.Categorical(hierarchical_df['country']).codes

# Streamlit Title
st.title('TOP 10 Countries - Hierarchical')

# Display Treemap
fig = px.treemap(hierarchical_df,
                 path=['country', 'type', 'genre', 'release_year', 'title', 'description'],
                 values='count',
                 width=1450,
                 height=600,
                 color='color',  # Specify the color column
                 color_continuous_scale='Sunset')  # You can choose a different color scale

st.plotly_chart(fig)

#Create and filter Heatmap

if 'date_added' in df.columns:
    st.subheader(f'Movies or TV Shows Which are Added on Platform by Year :red[{title}]')
        # Convert 'date_added' to datetime with 'coerce' option
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')

    # Drop rows with NaT (parsing errors)
    df = df.dropna(subset=['date_added'])

    # Extract day, month, and year
    df['day'] = df['date_added'].dt.day
    df['month'] = df['date_added'].dt.strftime('%B')
    df['year'] = df['date_added'].dt.year

    # USER INPUT
    selected_year = st.number_input("Enter the year to display (e.g., 2021): ", value=2021, min_value=int(df['year'].min()), max_value=int(df['year'].max()))

    # Check if the selected year exists in the DataFrame
    if selected_year in df['year'].unique():
        # Filter the DataFrame based on the selected year
        selected_data = df[df['year'] == selected_year]
        # Pivot the dataframe to create the heatmap
        pivot_df = selected_data.pivot_table(values='show_id', index='month', 
                                             columns='day', aggfunc='count', fill_value=0)

        # Create heatmap using Plotly Express
        fig = px.imshow(
            pivot_df,
            labels=dict(x='Day', y='Month', color='Number of Shows'),
            y=pivot_df.index,
            color_continuous_scale='YlGnBu'
        )

        # Update layout
        fig.update_layout(
            title=f'Heatmap of Shows/Movies Added in {selected_year}',
            xaxis_title='Day',
            yaxis_title='Month',
            width=1450,
            height=500
        )

        # Show the plot using Streamlit
        st.plotly_chart(fig)

    else:
        st.write(f"No data available for the year {selected_year}.")



