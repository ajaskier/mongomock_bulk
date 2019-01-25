import copy
import os
import unittest

import mongomock
from pymongo import ReplaceOne


def bulk_replace(collection, docs):
    bulks = []
    for current, update in docs:
        bulk = ReplaceOne(current, update)
        bulks.append(bulk)

    return collection.bulk_write(bulks)


class TestBulkReplace(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        if 'REAL_MONGO_CONNECTION_STRING' in os.environ:
            from pymongo import MongoClient
            client = MongoClient(os.environ['REAL_MONGO_CONNECTION_STRING'])
        else:
            client = mongomock.MongoClient('mongodb://example.server.com/testdb')

        cls.db = client.get_database()

    def setUp(self):

        dummy_docs = [
            {
                'name': 'Luke',
                'age': 40
            },
            {
                'name': 'Anna',
                'age': 42
            },
            {
                'name': 'Tom',
                'age': 16
            },
        ]
        self.db.people.insert_many(dummy_docs)

    def tearDown(self):
        self.db.people.drop()

    def test_bulk_replace_single_object(self):
        luke = list(self.db.people.find({'name': 'Luke'}))[0]
        older_luke = copy.deepcopy(luke)
        older_luke['age'] = 100

        update = [
            (luke, older_luke)
        ]

        res = bulk_replace(self.db.people, update)
        self.assertEqual(res.matched_count, 1)
        self.assertEqual(res.modified_count, 1)

    def test_bulk_replace_no_changes(self):
        luke = list(self.db.people.find({'name': 'Luke'}))[0]
        also_luke = copy.deepcopy(luke)

        update = [
            (luke, also_luke)
        ]

        res = bulk_replace(self.db.people, update)
        self.assertEqual(res.matched_count, 1)
        self.assertEqual(res.modified_count, 0)

    def test_bulk_replace_multiple_objects(self):
        luke = list(self.db.people.find({'name': 'Luke'}))[0]
        also_luke = copy.deepcopy(luke)

        anna = list(self.db.people.find({'name': 'Anna'}))[0]
        older_anna = copy.deepcopy(anna)
        older_anna['age'] = 100

        update = [
            (luke, also_luke),
            (anna, older_anna)
        ]

        res = bulk_replace(self.db.people, update)
        self.assertEqual(res.matched_count, 2)
        self.assertEqual(res.modified_count, 1)

    def test_bulk_replace_multiple_objects_partial_modify(self):
        luke = list(self.db.people.find({'name': 'Luke'}))[0]
        older_luke = copy.deepcopy(luke)
        older_luke['age'] = 100

        anna = list(self.db.people.find({'name': 'Anna'}))[0]
        older_anna = copy.deepcopy(anna)
        older_anna['age'] = 100

        update = [
            (luke, older_luke),
            (anna, older_anna)
        ]

        res = bulk_replace(self.db.people, update)
        self.assertEqual(res.matched_count, 2)
        self.assertEqual(res.modified_count, 2)


if __name__ == '__main__':
    unittest.main()
