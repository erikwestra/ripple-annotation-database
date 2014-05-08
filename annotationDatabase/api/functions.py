""" annotationDatabase.api.functions

    This module implements the actual functionality of the Ripple Annotation
    Database API.

    This is implemented as a separate module so that the functions can be
    called either by the API view functions, or directly from the web
    interface.
"""
import datetime
import time

import simplejson as json

from django.utils.timezone import utc
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from annotationDatabase.shared.models import *

#############################################################################

def add(batch):
    """ Add a batch of annotations to the system.

        The parameters are as follows:

            batch

                A dictionary with the following entries:

                    'user_id' (required)

                        A string identifying the user who is uploading this
                        batch.

                    'annotations' (required)

                        An array of annotations to be submitted. Each array
                        entry should be an object with the following fields:

                            'account' (required)

                                The address of the Ripple account this
                                annotation is for.

                            'key' (required)

                                A string that uniquely identifies this
                                annotation for this account.

                            'value' (required)

                                The value of this annotation for this account,
                                as a string.

        If the request was successful, we return a dictionary which looks like
        this:

            {'success'   : True,
             'batch_num' : 1234}

        where 'batch_num' is the number of the newly-posted annotation batch.

        If an error occurred, we return a dictionary which looks like this:

            {'success' : False,
             'error'   : "..."}

        where 'error' is a string describing why the request failed.
    """
    if type(batch) is not dict:
        return {'success' : False,
                'error'   : "'batch' parameter must be an object"}

    if 'user_id' not in batch:
        return {'success' : False,
                'error'   : "batch must include a 'user_id' entry"}

    if 'annotations' not in batch:
        return {'success' : False,
                'error'   : "batch must include an 'annotations' entry"}

    if type(batch['annotations']) not in [list, tuple]:
        return {'success' : False,
                'error'   : "'annotations' entry must be an array"}

    annotationBatch = AnnotationBatch()
    annotationBatch.timestamp = datetime.datetime.utcnow().replace(tzinfo=utc)
    annotationBatch.user_id   = batch['user_id']
    annotationBatch.save()

    for entry in batch['annotations']:
        if type(entry) is not dict:
            return {'success' : False,
                    'error'   : "annotation entry must be an object"}

        if 'account' not in entry:
            return {'success' : False,
                    'error'   : "annotation must include an 'account' entry"}

        if 'key' not in entry:
            return {'success' : False,
                    'error'   : "annotation must include a 'key' entry"}

        if 'value' not in entry:
            return {'success' : False,
                    'error'   : "annotation must include a 'value' entry"}

        try:
            account = Account.objects.get(address=entry['account'])
        except Account.DoesNotExist:
            account = Account()
            account.address = entry['account']
            account.save()

        try:
            annotationKey = AnnotationKey.objects.get(key=entry['key'])
        except AnnotationKey.DoesNotExist:
            annotationKey = AnnotationKey()
            annotationKey.key = entry['key']
            annotationKey.save()

        annotation = Annotation()
        annotation.batch     = annotationBatch
        annotation.account   = account
        annotation.key       = annotationKey
        annotation.value     = entry['value']
        annotation.hidden    = False
        annotation.hidden_at = None
        annotation.hidden_by = None
        annotation.save()

    return {'success'   : True,
            'batch_num' : annotationBatch.id}

#############################################################################

def hide(user_id, batch_num, account=None, annotation=None):
    """ Hide one or more annotations within the given batch.

        The parameters are as follows:

            'user_id' (required)

                A string identifying the user who is hiding these annotations.

            'batch_num' (required)

                The batch number of the annotation(s) to be hidden.

            'account' (optional)

                The Ripple address for the account to hide the annotations for.
                If this is not specified, the annotations for all accounts in
                the given batch will be hidden.

            'annotation' (optional)

                The name of the annotation to hide. If this is not specified,
                all matching annotations, regardless of the annotation name,
                will be hidden.

        If the request was successful, we return a dictionary which looks like
        this:

            {'success' : True}

        If an error occurred, we return a dictionary which looks like this:

            {'success' : False,
             'error'   : "..."}

        where 'error' is a string describing why the request failed.
    """
    try:
        annotationBatch = AnnotationBatch.objects.get(id=batch_num)
    except AnnotationBatch.DoesNotExist:
        return {'success' : False,
                'error'   : "No such batch"}

    if account != None:
        try:
            account = Account.objects.get(address=account)
        except Account.DoesNotExist:
            return {'success' : False,
                    'error'   : "No such account"}

    if annotation != None:
        try:
            annotationKey = AnnotationKey.objects.get(key=annotation)
        except AnnotationKey.DoesNotExist:
            return {'success' : False,
                    'error'   : "No such annotation"}

    if account != None and annotation != None:
        annotations_to_hide = Annotation.objects.filter(batch=annotationBatch,
                                                        account=account,
                                                        key=annotationKey)
    elif account != None and annotation == None:
        annotations_to_hide = Annotation.objects.filter(batch=annotationBatch,
                                                        account=account)
    elif account == None and annotation != None:
        annotations_to_hide = Annotation.objects.filter(batch=annotationBatch,
                                                        key=annotationKey)
    elif account == None and annotation == None:
        annotations_to_hide = Annotation.objects.filter(batch=annotationBatch)

    for annotation in annotations_to_hide:
        annotation.hidden    = True
        annotation.hidden_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        annotation.hidden_by = user_id
        annotation.save()

    return {'success' : True}

#############################################################################

def list_batches(page=1, rpp=100):
    """ Return a list of previously posted annotation batches.

        The parameters are as follows:

            'page'

                Which page of results to return. Note that page 1 is the most
                recent rpp batches. Increasing page numbers will return lists
                of batches going further back in time.

            'rpp'

                The number of results to return per page.

        If the request was successful, we return a dictionary which looks like
        this:

            {'success'   : True,
             'num_pages' : 10,
             'batches'   : [..]}

        'num_pages' is the number of pages of results that will be returned
        with the given 'rpp' value.

        Each entry in the 'batches' list will be a dictionary with the
        following entries:

            'batch_number'

                An integer uniquely identifying this batch.

            'timestamp'

                The date and time at which the batch was uploaded, as an
                integer number of seconds since midnight on the 1st of January,
                1970 ("unix time"), in UTC.

            'user_id'

                A string identifying who uploaded the batch.

        If an error occurred, we return a dictionary which looks like this:

            {'success' : False,
             'error'   : "..."}

        where 'error' is a string describing why the request failed.
    """
    paginator = Paginator(AnnotationBatch.objects.order_by("-id"), rpp)

    try:
        batches_in_page = paginator.page(page)
    except PageNotAnInteger:
        batches_in_page = paginator.page(1)
    except EmptyPage:
        batches_in_page = []

    batches = []
    for batch in batches_in_page:
        timestamp = int(time.mktime(batch.timestamp.timetuple()))
        batches.append({'batch_number' : batch.id,
                        'timestamp'    : timestamp,
                        'user_id'      : batch.user_id})

    return {'success'   : True,
            'num_pages' : paginator.num_pages,
            'batches'   : batches}

#############################################################################

def get(batch_number):
    """ Return the contents of the given annotation batch.

        The parameters are as follows:

            'batch_number'

                The number of the desired annotation batch.

        If the request was successful, we return a dictionary which looks like
        this:

            {'success'      : true,
             'batch_number' : 1234,
             'timestamp'    : 1310669017,
             'user_id'      : "...",
             'annotations'  : [...]}

        where the various entries are as follows:

            'batch_number'

                An integer uniquely identifying the batch.

            'timestamp'

                The date and time at which the batch was uploaded, as an
                integer number of seconds since midnight on the 1st of January,
                1970 ("unix time"), in UTC.

            'user_id'

                A string identifying who uploaded the batch.

            'annotations'

                A list of the annotations within the batch.  Each list item
                will be a dictionary with the following entries:

                    'account'

                        The address of the Ripple account this annotation is
                        associated with.

                    'key'

                        A string uniquely identifying this annotation for this
                        account.

                    'value'

                        The value of this annotation for this account.

                    'hidden'

                        Has this particular annotation entry been hidden?

                    'hidden_at'

                        If the annotation has been hidden, this will be the
                        date and time at which the annotation was hidden, as an
                        integer number of seconds since midnight on the 1st of
                        January, 1970 ("unix time"), in UTC.

                    'hidden_by'

                        If the annotation has been hidden, this will be the
                        user_id value for the user who hid this annotation.

        If an error occurred, we return a dictionary which looks like this:

            {'success' : False,
             'error'   : "..."}

        where 'error' is a string describing why the request failed.
    """
    try:
        annotationBatch = AnnotationBatch.objects.get(id=batch_number)
    except AnnotationBatch.DoesNotExist:
        return {'success' : False,
                'error'   : "No such batch"}

    annotations = []
    for annotation in Annotation.objects.filter(batch=annotationBatch):
        annotations.append({'account' : annotation.account.address,
                            'key'     : annotation.key.key,
                            'value'   : annotation.value,
                            'hidden'  : annotation.hidden})
        if annotation.hidden:
            hidden_at = int(time.mktime(annotation.hidden_at.timetuple()))
            annotations[-1]['hidden_at'] = hidden_at
            annotations[-1]['hidden_by'] = annotation.hidden_by

    timestamp = int(time.mktime(annotationBatch.timestamp.timetuple()))

    return {'success'      : True,
            'batch_number' : annotationBatch.id,
            'timestamp'    : timestamp,
            'user_id'      : annotationBatch.user_id,
            'annotations'  : annotations}

#############################################################################

def list_accounts(page=1, rpp=1000):
    """ Return a list of Ripple accounts which have annotations.

        The parameters are as follows:

            'page'

                Which page of results to return.  Note that the first page is
                page number 1, and the accounts are listed alphabetically in
                ascending order.

            'rpp'

                The number of results to return per page.

        If the request was successful, we return a dictionary which looks like
        this:

            {'success'   : True,
             'num_pages' : 10,
             'accounts'  : [...]}

        'num_pages' is the number of pages of results that will be returned
        with the given 'rpp' value.

        Each entry in the 'accounts' list will be the Ripple address of an
        account, as a string.

        If an error occurred, we return a dictionary which looks like this:

            {'success' : False,
             'error'   : "..."}

        where 'error' is a string describing why the request failed.
    """
    paginator = Paginator(Account.objects.order_by("address"), rpp)

    try:
        accounts_in_page = paginator.page(page)
    except PageNotAnInteger:
        accounts_in_page = paginator.page(1)
    except EmptyPage:
        accounts_in_page = []

    accounts = []
    for account in accounts_in_page:
        accounts.append(account.address)

    return {'success'   : True,
            'num_pages' : paginator.num_pages,
            'accounts'  : accounts}

#############################################################################

def account(account):
    """ Return the annotations currently associated with the given account.

        The parameters are as follows:

            'account'

                The Ripple address of the desired account.

        If the request was successful, we return a dictionary which looks like
        this:

            {'success'      : true,
             'annotations'  : [...]}

        where 'annotations' is a list of annotations currently associated with
        the given account.  Each item in this list will be a dictionary with
        the following entries:

            'key'

                A string uniquely identifying this annotation for this account.

            'value'

                The value of this annotation for this account.

        If an error occurred, we return a dictionary which looks like this:

            {'success' : False,
             'error'   : "..."}

        where 'error' is a string describing why the request failed.
    """
    try:
        account = Account.objects.get(address=account)
    except Account.DoesNotExist:
        return {'success' : False,
                'error'   : "No such account"}

    values = {} # Maps annotation key to [timestamp, value] tuple.

    for annotation in Annotation.objects.filter(account=account):
        if annotation.hidden: continue

        key       = annotation.key.key
        timestamp = annotation.batch.timestamp
        value     = annotation.value

        if key not in values:
            values[key] = [timestamp, value]
        else:
            prevTimestamp,prevValue = values[key]
            if timestamp > prevTimestamp:
                # Use the most recent value.
                values[key][1] = value

    annotations = []
    for key in sorted(values.keys()):
        annotations.append({'key'   : key,
                            'value' : values[key][1]})

    return {'success'     : True,
            'annotations' : annotations}

#############################################################################

def account_history(account):
    """ Return a complete history of the given account's annotations.

        The parameters are as follows:

            'account'

                The Ripple address of the desired account.

        If the request was successful, we return a dictionary which looks like
        this:

            {'success'      : true,
             'annotations'  : [...]}

        where 'annotations' is a list of all the annotations that have ever
        been associated with the given account.  Each item in this list will be
        a dictionary with the following entries:

            'key'

                A string uniquely identifying this annotation for this account.

            'history'

                A list of the changes made to this annotation over time, in
                date-descending order (that is, the most recent change is the
                first item in the list).  Each item in this list will be a
                dictionary with the following entries:

                    'batch_number'

                        The batch number in which this change was applied.

                    'value'

                        The value that this annotation was set to within this
                        batch.

                    'timestamp'

                        The date and time at which this value was originally
                        applied, as an integer number of seconds since midnight
                        on the 1st of January, 1970 ("unix time"), in UTC.

                    'user_id'

                        A string identifying who initially applied this
                        annotation.

                    'hidden'

                        Has this particular annotation entry been hidden?

                    'hidden_at'

                        If the annotation has been hidden, this will be the
                        date and time at which the annotation was hidden, as an
                        integer number of seconds since midnight on the 1st of
                        January, 1970 ("unix time"), in UTC.

                    'hidden_by'

                        If the annotation has been hidden, this will be the
                        'user_id' value for the user who hid this annotation.

                Note that the 'hidden_at' and 'hidden_by' fields will only be
                present if the annotation has been hidden within this batch.

        If an error occurred, we return a dictionary which looks like this:

            {'success' : False,
             'error'   : "..."}

        where 'error' is a string describing why the request failed.
    """
    try:
        account = Account.objects.get(address=account)
    except Account.DoesNotExist:
        return {'success' : False,
                'error'   : "No such account"}

    annotations = []

    query = Annotation.objects.filter(account=account).order_by("-id")
    for annotation in query:
        found = False
        for entry in annotations:
            if entry['key'] == annotation.key.key:
                found = True
                break

        if not found:
            # This is the first time we've encountered this annotation key ->
            # create a new history entry for it.
            entry = {'key'     : annotation.key.key,
                     'history' : []}
            annotations.append(entry)

        timetuple = annotation.batch.timestamp.timetuple()
        timestamp = int(time.mktime(timetuple))

        history_entry = {'batch_number' : annotation.batch.id,
                         'value'        : annotation.value,
                         'timestamp'    : timestamp,
                         'user_id'      : annotation.batch.user_id,
                         'hidden'       : annotation.hidden}

        if annotation.hidden:
            timetuple = annotation.hidden_at.timetuple()
            hidden_at = int(time.mktime(timetuple))
            history_entry['hidden_at'] = hidden_at
            history_entry['hidden_by'] = annotation.hidden_by

        entry['history'].append(history_entry)

    return {'success'     : True,
            'annotations' : annotations}

#############################################################################

def search(criteria):
    """ Return a list of the accounts which match the given annotation values.

        The parameters are as follows:

            'criteria'

                A list of (key,value) tuples, specifying the annotations and
                their required values.

        If the request was successful, we return a dictionary which looks like
        this:

            {'success'   : true,
              'accounts' : [...]}

        where 'accounts' is a list of strings identifying the Ripple accounts
        which have the given annotation values.

        If an error occurred, we return a dictionary which looks like this:

            {'success' : False,
             'error'   : "..."}

        where 'error' is a string describing why the request failed.

        Note that the implementation of this function is quite simplistic at
        the moment -- it's not optimised to handle overwritten values
        efficiently.
    """
    # Start by searching for all accounts which have the given annotation
    # values.  Note that they may have been overwritten...we then have to
    # filter out accounts which no longer have these values.

    matching_accounts = None # initially.
    for key,value in criteria:
        try:
            annotationKey = AnnotationKey.objects.get(key=key)
        except AnnotationKey.DoesNotExist:
            continue

        accounts = set() # Set of Account record IDs.
        for annotation in Annotation.objects.filter(key=annotationKey,
                                                    value=value):
            accounts.add(annotation.account.id)

        if matching_accounts == None:
            matching_accounts = accounts
        else:
            matching_accounts = matching_accounts.intersection(accounts)

    if matching_accounts == None:
        matching_accounts = set()

    # We now have a list of all potential accounts which at one stage matched
    # the search criteria.  See if the search criteria still applies to those
    # accounts.

    still_matching_accounts = []
    for account_id in matching_accounts:
        account = Account.objects.get(id=account_id)

        annotations_by_date = {} # Maps annotation key to [timestamp,value]
                                 # tuple for most recent value.

        for annotation in Annotation.objects.filter(account=account,
                                                    hidden=False):
            if annotation.key.key in annotations_by_date:
                annotation_entry = annotations_by_date[annotation.key.key]
                if annotation_entry[0] < annotation.batch.timestamp:
                    # Remember most recent value.
                    annotation_entry[0] = annotation.batch.timestamp
                    annotation_entry[1] = annotation.value
            else:
                # This is the first time we've seen this annotation key ->
                # remember the details.
                annotation_entry = [annotation.batch.timestamp,
                                    annotation.value]
                annotations_by_date[annotation.key.key] = annotation_entry

        # See if the annotation values still match the desired values.

        still_matches = True # initially.

        for key,value in criteria:
            if annotations_by_date[key][1] != value:
                still_matches = False
                break

        if still_matches:
            still_matching_accounts.append(account.address)

    # Finally, return the still-matching accounts back to the caller.

    return {'success'  : True,
            'accounts' : still_matching_accounts}

#############################################################################

def set_template(template_name, template):
    """ Add or update an annotation template in the database.

        The parameters are as follows:

            'template_name'

                The name of the template.

            'template'

                A list of annotation entries to be included in the template.
                Each list item should be a dictionary with the following
                entries:

                    'annotation' (required)

                        The annotation key value for the desired annotation,
                        for example, "phone_number".

                    'label' (required)

                        A string to be displayed to the user to identify the
                        annotation, for example, "phone number".

                    'type' (required)

                        A string indicating the type of annotation value to be
                        entered. The following type values are currently
                        supported:

                            choice

                                The user can choose between two or more values.

                            field

                                The user can enter a value directly into an
                                input field.

                    'default' (optional)

                        The default value to use for this annotation, as a
                        string. If this is not present, no default value should
                        be set.

                    'choices' (required for "choice" annotations)

                        An array of possible values the user can choose
                        between. Each entry in the array will be another array
                        with two entries, where the first entry is the desired
                        annotation value, and the second entry is the label to
                        display to the user when this annotation value is
                        selected. For example:

                            choices: [["M", "Male"], ["F", "Female"]]

                    'field_size' (optional, only for "field" annotations)

                        The desired width of the input field, in characters.
                        This corresponds to the size attribute for an HTML
                        <input> tag. Note that if this is not specified, the
                        client will choose a default width.

                    'field_required' (optional, only for "field" annotations)

                        Set this to true if the user is required to enter a
                        value for this annotation. If this is not present, the
                        annotation will not be required.

                    'field_min_length' (optional, only for "field" annotations)

                        The minimum allowable length for this annotation value.
                        If this is not present, no minimum length will be
                        imposed.

                    'field_max_length' (optional, only for "field" annotations)

                        The maximum allowable length for this annotation value.
                        If this is not present, no maximum length will be
                        imposed.

        If there is already an annotation template with the given name, it will
        be replaced by the updated values. Otherwise, a new template with that
        name will be created.

        If the request was successful, we return a dictionary which looks like
        this:

            {'success' : True}

        If the request was not successful, we return a dictionary which looks
        like this:

            {'success' : False,
             'error'   : "..."}

        where 'error' is a string describing why the request failed.
    """
    # Convert the supplied template entries into a list of
    # AnnotationTemplateEntry objects.  At the same time, we check that the
    # correct set of parameters have been supplied.

    if type(template) not in [list, tuple]:
        return {'success' : False,
                'error'   : "'template' entry must be an array"}

    entries = []
    for src_entry in template:
        if type(src_entry) is not dict:
            return {'success' : False,
                    'error'   : "'template' list item must be an object"}

        if "annotation" not in src_entry:
            return {'success' : False,
                    'error'   : "template entry missing required " +
                                "'annotation' field"}

        if "label" not in src_entry:
            return {'success' : False,
                    'error'   : "template entry missing required " +
                                "'label' field"}

        if "type" not in src_entry:
            return {'success' : False,
                    'error'   : "template entry missing required " +
                                "'type' field"}

        if src_entry['type'] not in ["choice", "field"]:
            return {'success' : False,
                    'error'   : "template entry type must be 'choice' or " +
                                "'field'"}

        if src_entry['type'] == "choice":
            if "choices" not in src_entry:
                return {'success' : False,
                        'error'   : "choice template entry type must have a " +
                                    "'choices' field"}

        try:
            annotationKey = AnnotationKey.objects.get(
                                    key=src_entry['annotation'])
        except AnnotationKey.DoesNotExist:
            annotationKey = AnnotationKey()
            annotationKey.key = src_entry['annotation']
            annotationKey.save()

        entry = AnnotationTemplateEntry()
        entry.annotation = annotationKey
        entry.label      = src_entry['label']
        entry.type       = src_entry['type']
        entry.default    = src_entry.get("default")

        if entry.type == "choice":
            entry.choices = json.dumps(src_entry['choices'])
        elif entry.type == "field":
            if "field_size" in src_entry:
                entry.field_size = src_entry['field_size']
            if "field_required" in src_entry:
                entry.field_required = src_entry['field_required']
            if "field_min_length" in src_entry:
                entry.field_min_length = src_entry['field_min_length']
            if "field_max_length" in src_entry:
                entry.field_max_length = src_entry['field_max_length']

        entries.append(entry)

    # If we get here, the supplied parameters are acceptable -> add (or
    # replace) the AnnotationTemplate.

    try:
        existing_template = AnnotationTemplate.objects.get(name=template_name)
    except AnnotationTemplate.DoesNotExist:
        existing_template = None

    if existing_template != None:
        # Delete the old template.
        AnnotationTemplateEntry.objects.filter(
                                    template=existing_template).delete()
        existing_template.delete()

    template = AnnotationTemplate()
    template.name = template_name
    template.save()

    for entry in entries:
        entry.template = template
        entry.save()

    # Finally, tell the caller the good news.

    return {'success' : True}

#############################################################################

def get_template(template_name):
    """ Return the contents of the given annotation template.

        If the request was successful, we return a dictionary which looks like
        this:

            {'success' : True,
             'template' : [...]}

        where 'template' is the list of annotation entries which make up the
        template.  Each item in this list will be a dictionary with the
        following entries:

            'annotation'

                The annotation key value for this annotation, for example,
                "phone_number".

            'label'

                A string to be displayed to the user to identify the
                annotation, for example, "phone number".

            'type'

                A string indicating the type of annotation value to be entered.
                The following type values are currently supported:

                    choice

                        The user can choose between two or more values.

                    field

                        The user can enter a value directly into an input
                        field.

            'default'

                The default value to use for this annotation, as a
                string. If this is not present, no default value should
                be set.

            'choices'

                An array of possible values the user can choose between. Each
                entry in the array will be another array with two entries,
                where the first entry is the desired annotation value, and the
                second entry is the label to display to the user when this
                annotation value is selected. For example:

                    choices: [["M", "Male"], ["F", "Female"]]

                Note that this entry will only be present for "choice"
                annotations.

            'field_size'

                If present, this will be the desired width of the input field,
                in characters.  This corresponds to the size attribute for an
                HTML <input> tag. Note that if this is not specified, the
                client will choose a default width.

            'field_required'

                If present, this will be True if the user is required to enter
                a value for this annotation. If this is not present, the
                annotation will not be required.

            'field_min_length'

                If this is present, it will be the minimum allowable length for
                this annotation value.  If this is not present, no minimum
                length will be imposed.

            'field_max_length'

                If this is present, it will be the maximum allowable length for
                this annotation value.  If this is not present, no maximum
                length will be imposed.

        If the request was not successful, we return a dictionary which looks
        like this:

            {'success' : False,
             'error'   : "..."}

        where 'error' is a string describing why the request failed.
    """
    try:
        template = AnnotationTemplate.objects.get(name=template_name)
    except AnnotationTemplate.DoesNotExist:
        return {'success' : False,
                'error'   : "No such template"}

    entries = AnnotationTemplateEntry.objects.filter(template=template)

    data = []
    for entry in entries.order_by("id"):
        item = {}
        item['annotation'] = entry.annotation.key
        item['label']      = entry.label
        item['type']       = entry.type

        if entry.default != None:
            item['default'] = entry.default

        if entry.choices != None:
            item['choices'] = json.loads(entry.choices)

        if entry.field_size != None:
            item['field_size'] = entry.field_size

        if entry.field_required != None:
            item['field_required'] = entry.field_required

        if entry.field_min_length != None:
            item['field_min_length'] = entry.field_min_length

        if entry.field_max_length != None:
            item['field_max_length'] = entry.field_max_length

        data.append(item)

    return {'success'  : True,
            'template' : data}

#############################################################################

def list_templates(page=1, rpp=100):
    """ Return a list of uploaded annotation templates.

        The parameters are as follows:

            'page'

                Which page of results to return. Note that the templates are
                listed alphabetically, and page 1 is the first page of
                templates.

            'rpp'

                The number of results to return per page.

        If the request was successful, we return a dictionary which looks like
        this:

            {'success'   : True,
             'num_pages' : 10,
             'templates' : [..]}

        'num_pages' is the number of pages of results that will be returned
        with the given 'rpp' value.

        Each entry in the 'templates' list will be a dictionary with the
        following entries:

            'id'

                The unique record ID for this annotation template.

            'name'

                The name for this annotation template.

        If an error occurred, we return a dictionary which looks like this:

            {'success' : False,
             'error'   : "..."}

        where 'error' is a string describing why the request failed.
    """
    paginator = Paginator(AnnotationTemplate.objects.order_by("name"), rpp)

    try:
        templates_in_page = paginator.page(page)
    except PageNotAnInteger:
        templates_in_page = paginator.page(1)
    except EmptyPage:
        templates_in_page = []

    templates = []
    for template in templates_in_page:
        templates.append({'id'   : template.id,
                          'name' : template.name})

    return {'success'   : True,
            'num_pages' : paginator.num_pages,
            'templates' : templates}

