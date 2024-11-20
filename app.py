import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt

st.header('Used Car Data')
st.write('Filter the data below to take a deeper look')

used_car_sales = pd.read_csv("vehicles_us.csv")

# cleaning up/enhancing the dataset

# creating a function to return the first word in used_car_sales['model'] 
# and return it to store the manufacturer

def extract_manufacturer(n):
    split_str = n.split()
    manufacturer = split_str[0]
    return manufacturer

used_car_sales['manufacturer'] = used_car_sales['model'].apply(extract_manufacturer)

# filling blank values in 'is_4wd' with 0, to represent no 4wd
used_car_sales['is_4wd'] = used_car_sales['is_4wd'].fillna(0)

# filling in model_year with median year for each model
median_year = used_car_sales.groupby('model')['model_year'].median()
used_car_sales['model_year'] = used_car_sales.apply(
    lambda row: median_year[row['model']] if pd.isnull(row['model_year']) else row['model_year'], 
    axis=1
)

# Filling in cylinders with median cylinders for each model
median_cylinders = used_car_sales.groupby('model')['cylinders'].median()
used_car_sales['cylinders'] = used_car_sales.apply(
    lambda row: median_cylinders[row['model']] if pd.isnull(row['cylinders']) else row['cylinders'], 
    axis=1
)

# to fill nulls for odometer, we'll want to get the mean value for the model AND year, so we can have a more accurate value
# we'll create a new column of model_plus_year
used_car_sales['model_plus_year'] = used_car_sales['model_year'].astype(str) + used_car_sales['model']
mean_miles = used_car_sales.groupby('model_plus_year')['odometer'].mean()
used_car_sales['odometer'] = used_car_sales.apply(
    lambda row: mean_miles[row['model_plus_year']] if pd.isnull(row['odometer']) else row['odometer'], 
    axis=1
)
used_car_sales['odometer'] = used_car_sales['odometer'].round(0)

used_car_sales['age'] = 2024 - used_car_sales['model_year']

# beginning the streamlit design

manufacturer_choice = used_car_sales['manufacturer'].unique()

selected_menu = st.selectbox('Select a manufacturer', manufacturer_choice)

min_year, max_year = int(used_car_sales['model_year'].min()), int(used_car_sales['model_year'].max())

year_range = st.slider("Choose model years", value=(min_year, max_year), min_value=min_year, max_value=max_year)

actual_range = list(range(year_range[0], year_range[1]+1))

used_car_sales_filtered = used_car_sales[(used_car_sales['manufacturer'] == selected_menu) & (used_car_sales['model_year'].isin(actual_range))]

show_all = st.checkbox('Show all manufacturers?', value=False)

if show_all:
    used_car_sales_filtered = used_car_sales[used_car_sales['model_year'].isin(actual_range)]

used_car_sales_filtered

st.header("Average Prices")

list_for_bar = ['manufacturer', 'type', 'condition']

selected_bar = st.selectbox("Average price based on", list_for_bar)

avg_selected = used_car_sales.groupby(selected_bar)['price'].mean()

fig1 = px.bar(avg_selected)
fig1.update_layout(title="<b> Average sale price by {}</b>".format(selected_bar))
st.plotly_chart(fig1)



st.header("Price Analysis")
st.write("Analyzing what might influence price more")

list_for_hist = ['fuel', 'transmission', 'cylinders', 'is_4wd', 'paint_color']

selected_hist = st.selectbox("Split for price distribution", list_for_hist)

used_car_sales_hist = used_car_sales

remove_high_hist = st.checkbox("Remove high sales (>$100,000)? ", value=False)

if remove_high_hist:
    used_car_sales_hist = used_car_sales.query('price <= 100000')

fig2 = px.histogram(used_car_sales_hist, x='price', color=selected_hist)
fig2.update_layout(title="<b> Split of price by {}</b>".format(selected_hist))
st.plotly_chart(fig2)



# Defining a function to quantify the age group of a vehicle. 
# This can give us an easy way to identify new cars vs medium aged cars vs old cars
def age_category(x):
    if x < 5: return '<5'
    elif  x >= 5 and x < 10: return '5-10'
    elif x >= 10 and x < 20: return '10-20'
    else: return '>20'

used_car_sales['age_category'] = used_car_sales['age'].apply(age_category)

list_for_scatter = ['condition', 'odometer', 'age', 'manufacturer', 'paint_color', 'cylinders', 'days_listed']

choice_for_scatter = st.selectbox("Price dependency", list_for_scatter)

used_car_sales_scatter = used_car_sales

remove_high_scatter = st.checkbox("Remove high sales (>$100,000)?", value=False)

if remove_high_scatter:
    used_car_sales_scatter = used_car_sales.query('price <= 100000')

fig3 = px.scatter(used_car_sales_scatter, x='price', y=choice_for_scatter, color='age_category')
fig3.update_layout(title="<b> Price vs {}</b>".format(choice_for_scatter))
st.plotly_chart(fig3)