""" annotationDatabase.api.tests

    This module implements the various unit tests for the Ripple Annotation
    Database's "api" application.
"""
import simplejson as json

import django.test

from annotationDatabase.shared.models import *

from annotationDatabase.api import functions

#############################################################################

class AddTestCase(django.test.TestCase):
    """ Unit tests for the "/add" API endpoint.
    """
    def test_add_in_body(self):
        """ Test the "/add" endpoint with a batch in the body of the request.
        """
        batch = {'user_id'     : "erik",
                 'annotations' : [
                     dict(account="r123", key="owner", value="erik"),
                     dict(account="r124", key="owner", value="erik")
                 ]
                }

        response = self.client.post("/add", data=json.dumps(batch),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        response = json.loads(response.content)

        if not response['success']:
            self.fail(response['error'])
        self.assertItemsEqual(response.keys(), ['success', 'batch_num'])


    def test_add_query_params(self):
        """ Test the "/add" endpoint with a batch in a query parameter.
        """
        batch = {'user_id'     : "erik",
                 'annotations' : [
                     dict(account="r123", key="owner", value="erik"),
                     dict(account="r124", key="owner", value="erik")
                 ]
                }

        batch_data = json.dumps(batch)
        batch_data = batch_data.replace("&", "%26")
        batch_data = batch_data.replace("=", "%3D")

        response = self.client.get("/add", data={'batch' : batch_data})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        response = json.loads(response.content)

        if not response['success']:
            self.fail(response['error'])
        self.assertItemsEqual(response.keys(), ['success', 'batch_num'])

#############################################################################

class HideTestCase(django.test.TestCase):
    """ Unit tests for the "/hide" API endpoint.
    """
    def test_hide(self):
        """ Test the "/hide" endpoint.
        """
        batch = {'user_id'     : "erik",
                 'annotations' : [
                     dict(account="r123", key="owner", value="erik"),
                     dict(account="r124", key="owner", value="erik")
                 ]
                }

        response = functions.add(batch)
        if not response['success']:
            self.fail(response['error'])
        batch_num = response['batch_num']

        response = self.client.get("/hide", data={'user_id'   : "erik",
                                                  'batch_num' : batch_num,
                                                  'account'   : "r123"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        response = json.loads(response.content)

        self.assertItemsEqual(response.keys(), ['success'])
        if not response['success']:
            self.fail(response['error'])

        batch   = AnnotationBatch.objects.get(id=batch_num)
        account = Account.objects.get(address="r123")
        key     = AnnotationKey.objects.get(key="owner")

        annotation = Annotation.objects.get(batch=batch,
                                            account=account,
                                            key=key)

        self.assertEqual(annotation.hidden,    True)
        self.assertEqual(annotation.hidden_by, "erik")

#############################################################################

class ListTestCase(django.test.TestCase):
    """ Unit tests for the "/list" endpoint.
    """
    def test_list(self):
        """ Test the "/list" endpoint.
        """
        batch = {'user_id'     : "erik",
                 'annotations' : [
                     dict(account="r123", key="owner", value="erik"),
                     dict(account="r124", key="owner", value="erik")
                 ]
                }

        response = functions.add(batch)
        if not response['success']:
            self.fail(response['error'])
        batch_num = response['batch_num']

        response = self.client.get("/list", data={'page' : 1, 'rpp' : 100})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        response = json.loads(response.content)

        self.assertItemsEqual(response.keys(),
                              ['success', 'num_pages', 'batches'])
        if not response['success']:
            self.fail(response['error'])

        found = False # initially.
        for batch in response['batches']:
            if batch['batch_number'] == batch_num:
                found = True
                break

        self.assertTrue(found)

#############################################################################

class GetTestCase(django.test.TestCase):
    """ Unit tests for the "/get" endpoint.
    """
    def test_get(self):
        """ Test the "/get" endpoint.
        """
        batch = {'user_id'     : "erik",
                 'annotations' : [
                     dict(account="r123", key="owner", value="erik"),
                     dict(account="r124", key="owner", value="erik")
                 ]
                }

        response = functions.add(batch)
        if not response['success']:
            self.fail(response['error'])
        batch_num = response['batch_num']

        response = self.client.get("/get/%d" % batch_num)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        response = json.loads(response.content)

        self.assertItemsEqual(response.keys(), ['success', 'batch_number',
                                                'timestamp', 'user_id',
                                                'annotations'])
        if not response['success']:
            self.fail(response['error'])
        self.assertEqual(response['batch_number'], batch_num)
        self.assertEqual(response['user_id'], "erik")
        self.assertEqual(len(response['annotations']), 2)

#############################################################################

class AccountsTestCase(django.test.TestCase):
    """ Unit tests for the "/accounts" endpoint.
    """
    def test_accounts(self):
        """ Test the "/accounts" endpoint.
        """
        batch = {'user_id'     : "erik",
                 'annotations' : [
                     dict(account="r123", key="owner", value="erik"),
                     dict(account="r124", key="owner", value="erik")
                 ]
                }

        response = functions.add(batch)
        if not response['success']:
            self.fail(response['error'])

        response = self.client.get("/accounts", data={'page' : 1,
                                                      'rpp'  : 1000})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        response = json.loads(response.content)

        self.assertItemsEqual(response.keys(), ['success', 'accounts'])
        if not response['success']:
            self.fail(response['error'])

        self.assertTrue("r123" in response['accounts'])
        self.assertTrue("r124" in response['accounts'])

#############################################################################

class AccountTestCase(django.test.TestCase):
    """ Unit tests for the "/account" endpoint.
    """
    def test_account(self):
        """ Test the "/account" endpoint.
        """
        batch = {'user_id'     : "erik",
                 'annotations' : [
                     dict(account="r123", key="owner", value="erik"),
                     dict(account="r124", key="owner", value="erik")
                 ]
                }

        response = functions.add(batch)
        if not response['success']:
            self.fail(response['error'])

        response = self.client.get("/account/r123")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        response = json.loads(response.content)

        self.assertItemsEqual(response.keys(), ['success', 'annotations'])
        if not response['success']:
            self.fail(response['error'])

        found = False
        for annotation in response['annotations']:
            if annotation['key'] == "owner":
                self.assertEqual(annotation['value'], "erik")
                found = True

        self.assertTrue(found)

#############################################################################

class AccountHistoryTestCase(django.test.TestCase):
    """ Unit tests for the "/account_history" endpoint.
    """
    def test_account_history(self):
        """ Test the "/account_history" endpoint.
        """
        batch = {'user_id'     : "erik",
                 'annotations' : [
                     dict(account="r123", key="owner", value="erik"),
                 ]
                }

        response = functions.add(batch)
        if not response['success']:
            self.fail(response['error'])

        batch = {'user_id'     : "erik",
                 'annotations' : [
                     dict(account="r123", key="owner", value="tom")
                 ]
                }

        response = functions.add(batch)
        if not response['success']:
            self.fail(response['error'])

        response = self.client.get("/account_history/r123")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        response = json.loads(response.content)

        self.assertItemsEqual(response.keys(), ['success', 'annotations'])
        if not response['success']:
            self.fail(response['error'])

        # NOTE: The following is pretty dumb right now.  Improve tests later.

        found = False
        for annotation in response['annotations']:
            if annotation['key'] == "owner":
                found = True

        self.assertTrue(found)

#############################################################################

class SearchTestCase(django.test.TestCase):
    """ Unit tests for the "/search" endpoint.
    """
    def test_search(self):
        """ Test the "/search" endpoint.
        """
        batch = {'user_id'     : "erik",
                 'annotations' : [
                     dict(account="r123", key="owner", value="erik"),
                     dict(account="r124", key="owner", value="erik")
                 ]
                }

        response = functions.add(batch)
        if not response['success']:
            self.fail(response['error'])

        response = self.client.get("/search?owner=erik")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/json")

        response = json.loads(response.content)

        self.assertItemsEqual(response.keys(), ['success', 'accounts'])
        if not response['success']:
            self.fail(response['error'])

        self.assertTrue("r123" in response['accounts'])
        self.assertTrue("r124" in response['accounts'])

