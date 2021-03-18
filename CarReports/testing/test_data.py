import pytest
import os, sys
sys.path.append("..")
from contextlib import nullcontext as does_not_raise
from custom_errors import CSVError
from analyze import import_csv, analyze_data


def create_path(file):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(root_dir, file)
    return filepath


class TestData:
    @pytest.mark.parametrize('contacts, contacts_expectation',
                             [pytest.param('sample_data/contacts.csv', does_not_raise()),
                              pytest.param('sample_data/does_not_exist.csv', pytest.raises(FileNotFoundError)),
                              pytest.param('sample_data/incorrect_header.csv',
                                           pytest.raises(CSVError,
                                                         match=f'The listing csv does not have the correct column names. '
                                                               f'Please check that the columns are: .*')),
                              pytest.param('sample_data/too_many_columns.csv',
                                           pytest.raises(CSVError,
                                                         match=f'The listing csv does not have the correct number of columns. '
                                                               f'Please check that the columns are: .*'))]
                             )
    def test_import_csv(self, contacts, contacts_expectation):
        listings = 'sample_data/listings.csv'
        raise_exp = does_not_raise()
        if not isinstance(contacts_expectation, does_not_raise):
            raise_exp = contacts_expectation

        with raise_exp:
            listings_cv = create_path(listings)
            contacts_cv = create_path(contacts)
            listings_df, contacts_df = import_csv(listings_cv, contacts_cv)

    def test_analyze_data(self):
        listings_cv = create_path('sample_data/listings.csv')
        contacts_cv = create_path('sample_data/contacts.csv')
        listings_df, contacts_df = import_csv(listings_cv, contacts_cv)
        avg_sell, make, avg_price, top_dict = analyze_data(listings_df, contacts_df)
        assert avg_sell.iloc[0]['Average in Euro'] == '€26.080,-'
        assert avg_price.iloc[0][0] == '€24.638,-'



