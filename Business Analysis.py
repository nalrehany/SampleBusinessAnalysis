{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d7f79ad1",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import os\n",
    "import glob\n",
    "import plotly.express as px\n",
    "import plotly.graph_objects as go\n",
    "from itertools import combinations\n",
    "from collections import Counter"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "41c01154",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Read a list of csv's and merge them into one file\n",
    "\n",
    "# Set the path where files are located\n",
    "path = r'C:\\Users\\nalre\\Downloads\\SampleSet'\n",
    "\n",
    "all_files = glob.glob(path + \"/*.csv\")\n",
    "\n",
    "# Initialize a list\n",
    "file_list = []\n",
    "\n",
    "# Use this loop to the files separated by months\n",
    "for filename in all_files:\n",
    "    df = pd.read_csv(filename, index_col=None, header=0)\n",
    "    file_list.append(df)\n",
    "\n",
    "# Concatenate all of the files into one dataframe\n",
    "year_data = pd.concat(file_list, axis=0, ignore_index=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2783ab6a",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Take a look at our data\n",
    "year_data.info()\n",
    "year_data.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1b664c1c",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Begin finding highest sales by month\n",
    "# Split date to make accessing months easier\n",
    "year_data[[\"Month\", \"day\", \"year\"]] = year_data[\"Order Date\"].str.split(\"/\", expand=True)\n",
    "year_data.drop(columns=['day','year'], inplace=True)\n",
    "year_data.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5278dd1c",
   "metadata": {},
   "outputs": [],
   "source": [
    "# The data was slightly dirty, with the string 'Price Each' in the actual Price Each column\n",
    "\n",
    "# Drop na's\n",
    "year_data = year_data.dropna()\n",
    "# Drop rows with strings in them\n",
    "year_data = year_data[~year_data['Price Each'].isin(['Price Each'])]\n",
    "# Adjust data type. No need for cent values\n",
    "year_data['Price Each'] = year_data['Price Each'].astype('float32')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2a6fef6f",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Take a look\n",
    "year_data.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0f7ce783",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Find the best month for sales by grouping the data, then summing the values of each month.\n",
    "year_data_month = year_data.groupby('Month')['Price Each'].sum().to_frame().reset_index()\n",
    "\n",
    "# Rename the column for clarity\n",
    "year_data_month['Sales (USD Millions)'] = year_data_month['Price Each']\n",
    "\n",
    "# Create plot\n",
    "fig = px.bar(year_data_month, title = 'Sales by Month', x='Month', y='Sales (USD Millions)')\n",
    "fig.show()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3c0cef4d",
   "metadata": {},
   "outputs": [],
   "source": [
    "year_data_month.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "fe0afaa1",
   "metadata": {},
   "outputs": [],
   "source": [
    "# What city sold the most products\n",
    "\n",
    "# Isolate the city from the Purchase Address column\n",
    "year_data[['Number','City', 'State']] = year_data['Purchase Address'].str.split(',', expand = True)\n",
    "\n",
    "# Drop the created Number and State columns\n",
    "year_data.drop(columns=['Number', 'State'], inplace=True)\n",
    "\n",
    "# Find the sales per city by grouping the data, then summing the values of each city\n",
    "year_data_city = year_data.groupby('City')['Price Each'].sum().to_frame().reset_index()\n",
    "\n",
    "# Rename column in this DF for clarity\n",
    "year_data_city['Sales (USD Millions)'] = year_data_city['Price Each']\n",
    "\n",
    "# Visualize the new DF\n",
    "year_data_city.head(15)\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0f81d83b",
   "metadata": {},
   "outputs": [],
   "source": [
    "# To visualize this data on a map, it's required to import some data that has city coordinates\n",
    "mapdf = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_us_cities.csv')\n",
    "\n",
    "# Rename for clarity\n",
    "mapdf['City'] = mapdf['name']\n",
    "\n",
    "# The city names in both datasets had a spaces at the end, making merging impossible unless dealt with\n",
    "mapdf['City'] = mapdf['City'].str.strip()\n",
    "year_data_city['City'] = year_data_city['City'].str.strip()\n",
    "year_data_city['City'] = year_data_city['City'].replace(['New York City'],'New York')\n",
    "\n",
    "# Merge our city data with the data containing coordinates\n",
    "mapdf1 = pd.merge(year_data_city, mapdf, how='inner', on='City')\n",
    "\n",
    "# Drop duplicates made as various cities have the same name.\n",
    "mapdf1 = mapdf1.drop_duplicates(subset = ['City'])\n",
    "\n",
    "mapdf1.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3400be31",
   "metadata": {
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# Provide an interactive visual representation of sales hotspots\n",
    "\n",
    "mapdf1['text'] = mapdf1['City'] + '<br>Sales (USD Millions) ' + (mapdf1['Sales (USD Millions)']/1e6).astype(str)+' million'\n",
    "\n",
    "limits = [(0,9)]\n",
    "colors = [\"royalblue\"]\n",
    "cities = []\n",
    "scale = 6000\n",
    "\n",
    "fig = go.Figure()\n",
    "\n",
    "\n",
    "for i in range(len(limits)):\n",
    "    lim = limits[i]\n",
    "    df_sub = mapdf1[lim[0]:lim[1]]\n",
    "    fig.add_trace(go.Scattergeo(\n",
    "        locationmode = 'USA-states',\n",
    "        lon = df_sub['lon'],\n",
    "        lat = df_sub['lat'],\n",
    "        text = df_sub['text'],\n",
    "        marker = dict(\n",
    "            size = df_sub['Sales (USD Millions)']/scale,\n",
    "            color = colors[i],\n",
    "            line_color='rgb(40,40,40)',\n",
    "            line_width = 2,\n",
    "            sizemode = 'area'\n",
    "        ),\n",
    "        name = '{0} - {1}'.format(lim[0],lim[1])))\n",
    "\n",
    "fig.update_layout(\n",
    "        title_text = 'Sales Hotspots',\n",
    "        title_font_size = 25,\n",
    "        showlegend = False,\n",
    "        geo = dict(\n",
    "            scope = 'usa',\n",
    "            landcolor = 'rgb(217, 217, 217)',\n",
    "        )\n",
    "    )\n",
    "\n",
    "fig.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "720fdbff",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Find the ideal time to display adds\n",
    "from datetime import datetime\n",
    "\n",
    "# Extract the hour from the datetime in the data\n",
    "year_data['Hour'] = pd.to_datetime(year_data['Order Date']).dt.hour\n",
    "\n",
    "# Gather a count of the items \n",
    "value_counts = year_data['Hour'].value_counts()\n",
    "# Turn the series into a dataframe for analysis\n",
    "value_counts = pd.DataFrame(value_counts)\n",
    "# Reset indexes\n",
    "value_counts = value_counts.reset_index()\n",
    "# Rename columns\n",
    "value_counts.columns = ['Time', 'Orders']\n",
    "\n",
    "#Plot the data\n",
    "fig = px.bar(value_counts, \n",
    "             title = 'Orders by Hour of Day', \n",
    "             x='Time', \n",
    "             y='Orders', \n",
    "             labels = dict(Time=\"Time (24h)\"))\n",
    "fig.update_xaxes(nticks=25)\n",
    "fig.show()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2fa2d8be",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Identify which products are most often sold together\n",
    "# Create a new df and only select rows that share the same Order ID implicating duplicates\n",
    "df = year_data[year_data['Order ID'].duplicated(keep = False)]\n",
    "\n",
    "# Group the products that are bought in the same order, separate by a comma in the same value\n",
    "df['Grouped'] = df.groupby('Order ID')['Product'].transform(lambda x: ','.join(x))\n",
    "\n",
    "# Drop duplicates that are made\n",
    "df2 = df[['Order ID', 'Grouped']].drop_duplicates()\n",
    "\n",
    "# Instatiate a variable that keeps track of how many times the same item is counted\n",
    "count = Counter()\n",
    "\n",
    "# Create a loop that cycles through rows, counting combinations\n",
    "for row in df2['Grouped']:\n",
    "    row_list = row.split(',')\n",
    "    count.update(Counter(combinations(row_list, 2)))\n",
    "\n",
    "# Turn the data into a dataframe to make plotting possible \n",
    "most_common = pd.DataFrame(count.most_common(10), columns = ['Items', 'Amount Sold Together'])\n",
    "\n",
    "# Convert rows that are as tuple to string\n",
    "most_common['Items'] = most_common['Items'].astype('str')\n",
    "\n",
    "# Remove the brackets and commas introduced by grouping and counting\n",
    "most_common['Items'] = most_common['Items'].str.replace('(', '')\n",
    "most_common['Items'] = most_common['Items'].str.replace(')', '')\n",
    "most_common['Items'] = most_common['Items'].str.replace('\\'', '')\n",
    "\n",
    "# Plot\n",
    "fig = px.bar(most_common, \n",
    "             title = 'Items Most Sold Together', \n",
    "             x='Items', \n",
    "             y='Amount Sold Together', \n",
    "             labels = dict(Time=\"Time (24h)\"))\n",
    "\n",
    "fig.show()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8d26ec2e",
   "metadata": {},
   "outputs": [],
   "source": [
    "# What item sold the most\n",
    "\n",
    "# Get a count of each value, in this case, distinct item sold\n",
    "most_sales = df['Product'].value_counts()\n",
    "\n",
    "# Turn the data into a data frame and reset index\n",
    "most_sales = pd.DataFrame(most_sales)\n",
    "most_sales = most_sales.reset_index()\n",
    "\n",
    "# Rename columns\n",
    "most_sales.columns = ['Item', 'Amount Sold']\n",
    "\n",
    "# Plot the data\n",
    "fig1 = px.bar(most_sales, \n",
    "             title = 'Sales by Item - Top 10', \n",
    "             x='Item', \n",
    "             y='Amount Sold', \n",
    "             labels = dict(Time=\"Time (24h)\"))\n",
    "fig1.update_xaxes(nticks=25, range=[0,10])\n",
    "fig1.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "279a74cf",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.8"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
