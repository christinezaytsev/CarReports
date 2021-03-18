import pandas as pd
import numpy as np
from custom_errors import CSVError


def format_euro(column):
    column = column.apply(lambda x: "€{:,.0f}.-".format(round(x)))
    column = column.str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    return column


def validate_csv(df, correct_columns):
    if len(df.columns.to_list()) != len(correct_columns):
        raise CSVError(f'The listing csv does not have the correct number of columns. '
                       f'Please check that the columns are: {correct_columns}')
    if df.columns.to_list() != correct_columns:
        raise CSVError(f'The listing csv does not have the correct column names. '
                       f'Please check that the columns are: {correct_columns}')


def import_csv(listings_path, contacts_path):
    """Imports Listings and Contacts CSVs and checks formatting."""
    try:
        listings_df = pd.read_csv(listings_path)
        contacts_df = pd.read_csv(contacts_path)
    except FileNotFoundError:
        raise FileNotFoundError
    correct_listing = ['id', 'make', 'price', 'mileage', 'seller_type']
    correct_contacts = ['listing_id', 'contact_date']
    validate_csv(listings_df, correct_listing)
    validate_csv(contacts_df, correct_contacts)

    listings_df.columns = ['ID', 'Make', 'Price', 'Mileage', 'Seller Type']
    listings_df = listings_df.set_index('ID')
    contacts_df.columns = ['ID', 'Date']
    contacts_df = contacts_df.set_index('ID')
    return listings_df, contacts_df


def analyze_data(listings_df, contacts_df):
    """Creates dataframes for each desired report."""

    # Average Listing Selling Price per Seller Type
    avg_sell = listings_df.drop(['Mileage'], 1).groupby(['Seller Type']).mean().reset_index()
    avg_sell = avg_sell.sort_values(by=['Price'], ascending=False)
    avg_sell['Average in Euro'] = format_euro(avg_sell['Price'])
    avg_sell.drop('Price', inplace=True, axis=1)

    # Percentile distribution of available cars by Make
    count_make = listings_df.groupby(['Make']).size().reset_index(name='counts')
    count_make = count_make.sort_values(by=['counts'], ascending=False)
    count_make['Distribution'] = count_make['counts'] / count_make['counts'].sum() * 100
    count_make['Distribution'] = count_make['Distribution'].apply(lambda x: "{:.0f}%".format(x))
    count_make.drop('counts', inplace=True, axis=1)

    # Average price of the 30% most contacted listings
    most_contacted = contacts_df.groupby(['ID']).size().reset_index(name='counts')
    num_ids = float(most_contacted.shape[0]) * .3
    most_contacted = most_contacted.nlargest(int(num_ids), ['counts'])
    most_contacted = most_contacted.merge(listings_df['Price'], on='ID', how='left')
    avg_price = pd.DataFrame([int(most_contacted['Price'].mean())], columns=['Average price'])
    avg_price['Average price'] = format_euro(avg_price['Average price'])

    # The Top 5 most contacted listings per Month
    contacts_df['Datetime'] = pd.to_datetime(contacts_df['Date'], unit='ms')
    contacts_df['month_year'] = pd.to_datetime(contacts_df['Datetime']).dt.to_period('M')
    top_df = contacts_df.groupby(['ID', 'month_year']).size().reset_index(name='contacts')
    top_df = top_df.sort_values(by=['month_year', 'contacts'], ascending=False)
    top_df = top_df.merge(listings_df, on='ID', how='left').drop(['Seller Type'], 1)
    top_df['Price'] = format_euro(top_df['Price'])
    top_df = top_df[['ID', 'Make', 'Price', 'Mileage', 'contacts', 'month_year']]
    top_df.rename(columns={'ID': 'Listing Id', 'contacts': 'Total Amount of contacts',
                           'Price': 'Selling Price'}, inplace=True)
    months = top_df.month_year.unique()
    top_dict = {}
    for month in months:
        top_dict[month] = top_df[top_df["month_year"] == month].head()
    for month, df in top_dict.items():
        df.index = np.arange(1, len(df) + 1)
        df.index.name = 'Ranking'
        df.reset_index(inplace=True)
        df.drop('month_year', axis=1, inplace=True)

    return avg_sell, count_make, avg_price, top_dict
