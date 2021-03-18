from flask import Flask, render_template
from analyze import import_csv, analyze_data
import os

app = Flask(__name__)


@app.route('/')
def run():
    """Main function to generate and render reports."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    listings = os.path.join(root_dir, 'data/listings.csv')
    contacts = os.path.join(root_dir, 'data/contacts.csv')
    listings_df, contacts_df = import_csv(listings, contacts)
    avg_sell, make, avg_price, top_dict = analyze_data(listings_df, contacts_df)
    return render_template('tables.html', avg_sell=avg_sell, make=make, avg_price=avg_price, top_dict=top_dict)


if __name__ == '__main__':
    app.run(debug=True)
