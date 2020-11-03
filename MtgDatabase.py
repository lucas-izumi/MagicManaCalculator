import datetime
import sys
import time

import ZODB
import ZODB.FileStorage
import transaction
from warnings import warn

from mtgtools.PSetList import PSetList
from mtgtools.PCardList import PCardList
from api_requests import get_tot_mtgio_cards, process_mtgio_sets, process_mtgio_cards


class MtgDB:
    def __init__(self, storage_path, read_only):
        self.storage = ZODB.FileStorage.FileStorage(storage_path, read_only=read_only)
        self.database = ZODB.DB(self.storage)
        self.connection = self.database.open()
        self.root = self.connection.root

        try:
            self.root.scryfall_cards
        except (AttributeError, KeyError):
            self.root.scryfall_cards = PCardList()

        try:
            self.root.scryfall_sets
        except (AttributeError, KeyError):
            self.root.scryfall_sets = PSetList()

        try:
            self.root.mtgio_cards
        except (AttributeError, KeyError):
            self.root.mtgio_cards = PCardList()

        try:
            self.root.mtgio_sets
        except (AttributeError, KeyError):
            self.root.mtgio_sets = PSetList()

    def mtgio_update(self, verbose=True, workers=8):
        """Completely updates the database from magicthegathering.io downloading new sets and cards and also
        updating the current objects if there are any changes.

        Args:
            verbose (bool): If enabled, prints out progression messages during the updating process.
            workers (int): Maximum numbers fo threads for the updating.
        """
        start = round(time.time())
        current_cards = self.root.mtgio_cards
        current_sets = self.root.mtgio_sets
        old_set_count = len(current_sets)
        old_card_count = len(current_cards)

        if verbose:
            print('Attempting to update the current database objects and fetch new data.')
            print('querying magicthegathering.io API...')

        # Update sets
        obsolete_sets = process_mtgio_sets(current_sets)

        tot_new_cards = get_tot_mtgio_cards() - old_card_count
        tot_new_sets = len(current_sets) + len(obsolete_sets) - old_set_count

        if verbose:
            print('Found a total of {} new sets and {} new cards'.format(tot_new_sets, tot_new_cards))
            print('Fetching new cards and updating old.')
            print('-----------------------------------------------------------------------------------------------')

        # Update cards
        process_mtgio_cards(current_sets, current_cards, verbose=verbose, workers=workers)

        # Transfer cards from obsolete sets to new ones
        for obsolete_set in obsolete_sets:
            cards = obsolete_set.cards
            if cards:
                pset = current_sets.where_exactly(code=cards[0].set)
                if len(pset):
                    pset[0].extend(cards)

        if verbose:
            sys.stdout.write('\rSaving and committing...')

        transaction.commit()
        self.database.pack()

        if verbose:
            update_str = '\rThe magicthegathering.io database is now up to date!\nElapsed time: {}'
            sys.stdout.write(update_str.format(datetime.timedelta(seconds=round(time.time()) - start)))

    def update_new_from_mtgio(self, verbose=True, workers=8):
        """deprecated"""
        warn('This method is currently deprecated. The method "mtgio_update" is automatically called instead"')
        self.mtgio_update(verbose=verbose, workers=workers)

    def full_update_from_mtgio(self, verbose=True, workers=8):
        """deprecated"""
        warn('This method is currently deprecated. The method "mtgio_update" is automatically called instead"')
        self.mtgio_update(verbose=verbose, workers=workers)

    def format_and_pack(self):
        """Formats the database. After this operation, the old objects are still available in 'mydata.fs.old'
        storage.
        """
        answer = input('Attempting to format the whole database. Continue (y/n)?')

        if answer == 'y' or answer == 'yes':
            self.root.scryfall_sets = PSetList()
            self.root.scryfall_cards = PCardList()
            self.root.mtgio_sets = PSetList()
            self.root.mtgio_cards = PCardList()
            transaction.commit()
            self.database.pack()

    def close(self):
        """Closes the database properly. Using this is recommended after you are done using the database."""
        self.connection.close()
        self.database.close()
        self.storage.close()

    def commit(self):
        """Commits any changes to the database."""
        transaction.commit()

    def abort(self):
        """Aborts any changes made to the database."""
        transaction.abort()

    def pack(self):
        """Packs the database."""
        self.database.pack()
