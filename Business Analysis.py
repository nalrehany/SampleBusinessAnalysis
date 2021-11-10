import pandas as pd
import os
import glob
import plotly.express as px
import plotly.graph_objects as go
from itertools import combinations
from collections import Counter

# Read a list of csv's and merge them into one file

# Set the path where files are located
path = r'C:\Users\nalre\Downloads\SampleSet'

all_files = glob.glob(path + "/*.csv")

# Initialize a list
file_list = []

# Use this loop to the files separated by months
for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    file_list.append(df)

# Concatenate all of the files into one dataframe
year_data = pd.concat(file_list, axis=0, ignore_index=True)

# Take a look at our data
year_data.info()
year_data.head()

# Begin finding highest sales by month
# Split date to make accessing months easier
year_data[["Month", "day", "year"]] = year_data["Order Date"].str.split("/", expand=True)
year_data.drop(columns=['day','year'], inplace=True)
year_data.head()

# The data was slightly dirty, with the string 'Price Each' in the actual Price Each column

# Drop na's
year_data = year_data.dropna()
# Drop rows with strings in them
year_data = year_data[~year_data['Price Each'].isin(['Price Each'])]
# Adjust data type. No need for cent values
year_data['Price Each'] = year_data['Price Each'].astype('float32')

# Find the best month for sales by grouping the data, then summing the values of each month.
year_data_month = year_data.groupby('Month')['Price Each'].sum().to_frame().reset_index()

# Rename the column for clarity
year_data_month['Sales (USD Millions)'] = year_data_month['Price Each']

# Create plot
fig = px.bar(year_data_month, title = 'Sales by Month', x='Month', y='Sales (USD Millions)')
fig.show()

# What city sold the most products

# Isolate the city from the Purchase Address column
year_data[['Number','City', 'State']] = year_data['Purchase Address'].str.split(',', expand = True)

# Drop the created Number and State columns
year_data.drop(columns=['Number', 'State'], inplace=True)

# Find the sales per city by grouping the data, then summing the values of each city
year_data_city = year_data.groupby('City')['Price Each'].sum().to_frame().reset_index()

# Rename column in this DF for clarity
year_data_city['Sales (USD Millions)'] = year_data_city['Price Each']

# Visualize the new DF
year_data_city.head(15)

# To visualize this data on a map, it's required to import some data that has city coordinates
mapdf = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_us_cities.csv')

# Rename for clarity
mapdf['City'] = mapdf['name']

# The city names in both datasets had a spaces at the end, making merging impossible unless dealt with
mapdf['City'] = mapdf['City'].str.strip()
year_data_city['City'] = year_data_city['City'].str.strip()
year_data_city['City'] = year_data_city['City'].replace(['New York City'],'New York')

# Merge our city data with the data containing coordinates
mapdf1 = pd.merge(year_data_city, mapdf, how='inner', on='City')

# Drop duplicates made as various cities have the same name.
mapdf1 = mapdf1.drop_duplicates(subset = ['City'])

mapdf1.head()

# Provide an interactive visual representation of sales hotspots

mapdf1['text'] = mapdf1['City'] + '<br>Sales (USD Millions) ' + (mapdf1['Sales (USD Millions)']/1e6).astype(str)+' million'

limits = [(0,9)]
colors = ["royalblue"]
cities = []
scale = 6000

fig = go.Figure()


for i in range(len(limits)):
    lim = limits[i]
    df_sub = mapdf1[lim[0]:lim[1]]
    fig.add_trace(go.Scattergeo(
        locationmode = 'USA-states',
        lon = df_sub['lon'],
        lat = df_sub['lat'],
        text = df_sub['text'],
        marker = dict(
            size = df_sub['Sales (USD Millions)']/scale,
            color = colors[i],
            line_color='rgb(40,40,40)',
            line_width = 2,
            sizemode = 'area'
        ),
        name = '{0} - {1}'.format(lim[0],lim[1])))

fig.update_layout(
        title_text = 'Sales Hotspots',
        title_font_size = 25,
        showlegend = False,
        geo = dict(
            scope = 'usa',
            landcolor = 'rgb(217, 217, 217)',
        )
    )

fig.show()

# Find the ideal time to display adds
from datetime import datetime

# Extract the hour from the datetime in the data
year_data['Hour'] = pd.to_datetime(year_data['Order Date']).dt.hour

# Gather a count of the items 
value_counts = year_data['Hour'].value_counts()
# Turn the series into a dataframe for analysis
value_counts = pd.DataFrame(value_counts)
# Reset indexes
value_counts = value_counts.reset_index()
# Rename columns
value_counts.columns = ['Time', 'Orders']

#Plot the data
fig = px.bar(value_counts, 
             title = 'Orders by Hour of Day', 
             x='Time', 
             y='Orders', 
             labels = dict(Time="Time (24h)"))
fig.update_xaxes(nticks=25)
fig.show()

# Identify which products are most often sold together
# Create a new df and only select rows that share the same Order ID implicating duplicates
df = year_data[year_data['Order ID'].duplicated(keep = False)]

# Group the products that are bought in the same order, separate by a comma in the same value
df['Grouped'] = df.groupby('Order ID')['Product'].transform(lambda x: ','.join(x))

# Drop duplicates that are made
df2 = df[['Order ID', 'Grouped']].drop_duplicates()

# Instatiate a variable that keeps track of how many times the same item is counted
count = Counter()

# Create a loop that cycles through rows, counting combinations
for row in df2['Grouped']:
    row_list = row.split(',')
    count.update(Counter(combinations(row_list, 2)))

# Turn the data into a dataframe to make plotting possible 
most_common = pd.DataFrame(count.most_common(10), columns = ['Items', 'Amount Sold Together'])

# Convert rows that are as tuple to string
most_common['Items'] = most_common['Items'].astype('str')

# Remove the brackets and commas introduced by grouping and counting
most_common['Items'] = most_common['Items'].str.replace('(', '')
most_common['Items'] = most_common['Items'].str.replace(')', '')
most_common['Items'] = most_common['Items'].str.replace('\'', '')

# Plot
fig = px.bar(most_common, 
             title = 'Items Most Sold Together', 
             x='Items', 
             y='Amount Sold Together', 
             labels = dict(Time="Time (24h)"))

fig.show()

# What item sold the most

# Get a count of each value, in this case, distinct item sold
most_sales = df['Product'].value_counts()

# Turn the data into a data frame and reset index
most_sales = pd.DataFrame(most_sales)
most_sales = most_sales.reset_index()

# Rename columns
most_sales.columns = ['Item', 'Amount Sold']

# Plot the data
fig1 = px.bar(most_sales, 
             title = 'Sales by Item - Top 10', 
             x='Item', 
             y='Amount Sold', 
             labels = dict(Time="Time (24h)"))
fig1.update_xaxes(nticks=25, range=[0,10])
fig1.show()
