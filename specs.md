Ripple Annotation Database
--------------------------

This specification covers the __Ripple Annotation Database__, which is a system
for recording and retrieving "annotations" associated with Ripple accounts.
The Annotation Database consists of both an API and a password-protected admin
interface which lets end users access and work with this API.

Note that the admin interface only acts as a "front end" to the API -- there is
no functionality in the admin interface which cannot be accessed via the API
directly.

Because the Annotation Database may store sensitive information, the API and
admin interface are both protected.  API clients need to be authorized and
issued with an _authentication token_ which must be used whenever the API is
called.  Similarly, users accessing the admin interface must have a valid
username and password.


## Concepts ##

The Ripple Annotation Database is based around the concept of an Annotation.
An __Annotation__ is a single piece of information stored about a Ripple
account.  Each annotation consists of the following information:

> `account`
> 
> > The address of the Ripple account that this annotation is associated with.
> 
> `key`
> 
> > A string uniquely identifying this annotation for this account.
> 
> `value`
> 
> > A string specifying the value of this annotation for this account.
> 
> `hidden`
>
> > A flag which can be set to hide incorrectly-applied annotations.
> 
> `hidden_at`
>
> > The date and time at which the annotation was hidden.
> 
> `hidden_by`
> 
> > The user ID of the person who hid this annotation.

Note that annotations are uploaded and worked with in batches.  Each
__Annotation Batch__ is a collection of annotations which are uploaded or
worked with at one time.  Each batch has the following information associated
with it:

> `batch_number`
> 
> > A number uniquely identifying this batch.
> 
> `timestamp`
> 
> > The date and time at which the batch was uploaded.
> 
> `user_id`
> 
> > A string identifying who uploaded the batch.
>
> `annotations`
> 
> > A list of the annotations in the batch.

To allow users to maintain a set of annotation values via a client program, the
Ripple Annotation Database supports the notion of an __Annotation Template__.
This is a data structure listing a set of annotations and how the user can view
and edit those annotation values.  Each annotation template is given a unique
__name__, which indicates the purpose or context in which the template should be
used.  The template then contains a list of annotation entries, where each
annotation entry in the template will have the following information:

> `annotation`
> 
> > The annotation key value for the desired annotation, for example,
> > "`phone_number`".
> 
> `label`
> 
> > A string to be displayed to the user to identify the annotation, for
> > example, "phone number".
> 
> `type`
> 
> > A string indicating the type of annotation value to be entered.  The
> > following type values are currently supported:
> > 
> > > __choice__
> > > 
> > > > The user can choose between two or more values.
> > > 
> > > __field__
> > > 
> > > > The user can enter a value directly into an input field.
> 
> `default`
> 
> > The default value to use for this annotation, as a string.  If this is not
> > present, no default value should be set.
> 
> `choices`
> 
> > For "choice" annotations, this will be an array of possible values the user
> > can choose between.  Each entry in the array will be another array with two
> > entries, where the first entry is the desired annotation value, and the
> > second entry is the label to display to the user when this annotation value
> > is selected.  For example:
> >   
> >         choices: [["M", "Male"], ["F", "Female"]]
> 
> `field_size`
> 
> > For "field" annotations, this will be the desired width of the input field,
> > in characters.  This corresponds to the `size` attribute for an HTML
> > `<input>` tag.  Note that if this is not specified, the client will choose
> > a default width.
> 
> `field_required`
> 
> > For "field" annotations, this will be set to `true` if the user is required
> > to enter a value for this annotation.  If this is not present, the
> > annotation should not be required.
> 
> `field_min_length`
> 
> > For "field" annotations, this will be the minimum allowable length for this
> > annotation value.  If this is not present, no minimum length should be
> > imposed.
> 
> `field_max_length`
> 
> > For "field" annotations, this will be the maximum allowable length for this
> > annotation value.  If this is not present, no maximum length should be
> > imposed.

Client systems can download a desired annotation template, and also download
the current annotation values for a given Ripple account.  This allows the
client system to display the annotation values to the user using the template,
and send any changes back to the Ripple Annotation Database as an annotation
batch.


## API Endpoints ##

The Ripple Annotation API currently supports the following endpoints:

> __`/add`__
> 
> > Add a batch of annotations to the database.
> > 
> > This endpoint accepts a batch of annotations in JSON format.  There are two
> > ways in which this JSON data can be supplied:
> > 
> > 1. By submitting an HTTP "POST" request with a `Content-Type` value of
> >    `application/json`.  In this case, the JSON data should be in the body
> >    of the HTTP request.
> > <p/>
> > 2. By using a query-string parameter named `batch`.  Note that in this
> >    case, any "`&`" characters in the JSON data should be replaced with
> >    "`%26`", and any "`=`" characters must be replaced with "`%3D`".  This
> >    avoids confusion when the query-string parameters are parsed by the
> >    server.
> > 
> > The JSON data must consist of a single object with the following fields:
> > 
> > > `user_id` _(required)_
> > > 
> > > > A string identifying the user who is uploading this batch.
> > > 
> > > `auth_token` _(required)_
> > > 
> > > > The calling system's authentication token.
> > > 
> > > `annotations` _(required)_
> > > 
> > > > An array of annotations to be submitted.  Each array entry should be an
> > > > object with the following fields:
> > > > 
> > > > > `account` _(required)_
> > > > > 
> > > > > > The address of the Ripple account this annotation is for.
> > > > > 
> > > > > `key` _(required)_
> > > > > 
> > > > > > A string that uniquely identifies this annotation for this account.
> > > > > 
> > > > > `value` _(required)_
> > > > > 
> > > > > > The value of this annotation for this account, as a string.
> > 
> > Upon completion, the server will return an HTTP status code of `200` (OK),
> > and the body of the response will have a content-type value of
> > `application/json`.  The body of the response will consist of a JSON object
> > describing the result of the API call.  If the request was successful, the
> > returned JSON object will look like this:
> > 
> > >     {
> > >       success: true,
> > >       batch_num: 1234,
> > >     }
> > 
> > As you would expect, `batch_num` is the number of the submitted annotation
> > batch.
> > 
> > If the request was not successful, the returned JSON object will look like
> > this:
> > 
> > >     {
> > >       success: false,
> > >       error: "..."
> > >     }
> > 
> > In this case, the `error` field will be a string describing why the request
> > failed.
> 
> __`/hide`__
> 
> > Hide one or more previously-added annotations.
> > 
> > This API endpoint takes the following query-string parameters:
> > 
> > > `user_id` _(required)_
> > > 
> > > > A string identifying the user who is hiding these annotations.
> > > 
> > > `auth_token` _(required)_
> > > 
> > > > The calling system's authentication token.
> > > 
> > > `batch_num` _(required)_
> > > 
> > > > The batch number of the annotation(s) to be hidden.
> > > 
> > > `account` _(optional)_
> > > 
> > > > The Ripple address for the account to hide the annotations for.  If
> > > > this is not specified, the annotations for all accounts in the given
> > > > batch will be hidden.
> > > 
> > > `annotation` _(optional)_
> > > 
> > > > The name of the annotation to hide.  If this is not specified, all
> > > > matching annotations, regardless of the annotation name, will be
> > > > hidden.
> > 
> > By choosing different combinations of query-string parameters, the caller
> > can choose to hide:
> > 
> > * All the annotations in a batch (eg, _"hide batch 10271"_).
> > 
> > * All the annotations for a given account within a batch (eg, _"hide all
> >   annotations for account r127491 in batch 10271"_).
> > 
> > * All occurrences of a given annotation within a batch (eg, _"hide all the
> >   'primary' annotations in batch 10271"_).
> > 
> > * A single annotation within a batch (eg, _"hide the 'primary' annotation
> >   for account r127491 in batch 10271"_).
> > 
> > Upon completion, the server will return an HTTP status code of `200` (OK),
> > and the body of the response will have a content-type value of
> > `application/json`.  The body of the response will consist of a JSON object
> > describing the result of the API call.  If the request was successful, the
> > returned JSON object will look like this:
> > 
> > >     {
> > >       success: true
> > >     }
> > 
> > If the request was not successful, the returned JSON object will look like
> > this:
> > 
> > >     {
> > >       success: false,
> > >       error: "..."
> > >     }
> > 
> > In this case, the `error` field will be a string describing why the request
> > failed.
> 
> __`/list`__
> 
> > Return a list of recently uploaded annotation batches.
> > 
> > This API takes the following query-string parameters:
> > 
> > > `auth_token` _(required)_
> > > 
> > > > The calling system's authentication token.
> > > 
> > > `page` _(optional)_
> > > 
> > > > Which page of results to return.  By default, we return page 1, which
> > > > is the most recent `rpp` batches.  Increasing page numbers will return
> > > > lists of batches going further back in time.
> > > 
> > > `rpp` _(optional)_
> > > 
> > > > The number of results to return per page.  By default, we return a
> > > > maximum of 100 batches in each page of results.
> > 
> > Upon completion, the server will return an HTTP status code of `200` (OK),
> > and the body of the response will have a content-type value of
> > `application/json`.  The body of the response will consist of a JSON object
> > describing the result of the API call.  If the request was successful, the
> > returned JSON object will look like this:
> > 
> > >     {
> > >       success: true,
> > >       num_pages: /* integer */,
> > >       batches: [ /* array of batch objects */ ]
> > >     }
> > 
> > The `num_pages` value will be the number of pages of results which will be
> > returned for the given `rpp` value.
> > 
> > Each entry in the `batches` array will be an object with the following
> > fields:
> > 
> > > `batch_number`
> > > 
> > > > An integer uniquely identifying this batch.
> > > 
> > > `timestamp`
> > > 
> > > > The date and time at which the batch was uploaded, as an integer number
> > > > of seconds since midnight on the 1st of January, 1970 ("unix time"), in
> > > > UTC.
> > > 
> > > `user_id`
> > > 
> > > > A string identifying who uploaded the batch.
> > 
> > If the request was not successful, the returned JSON object will look like
> > this:
> > 
> > >     {
> > >       success: false,
> > >       error: "..."
> > >     }
> > 
> > In this case, the `error` field will be a string describing why the request
> > failed.
> 
> __`/get/{batch_number}`__
> 
> > Return the contents of a single uploaded annotation batch.
> > 
> > Note that the desired batch number is included as part of the URL itself.
> > 
> > The following query string parameter must be included with this request:
> > 
> > > `auth_token` _(required)_
> > > 
> > > > The calling system's authentication token.
> > 
> > Upon completion, the server will return an HTTP status code of `200` (OK),
> > and the body of the response will have a content-type value of
> > `application/json`.  The body of the response will consist of a JSON object
> > describing the result of the API call.  If the request was successful, the
> > returned JSON object will look like this:
> > 
> > >     {
> > >       success: true,
> > >       batch_number: 1234,
> > >       timestamp: 1310669017,
> > >       user_id: "erik",
> > >       annotations: [ /* array of annotation objects */ ]
> > >     }
> > 
> > The `batch_number`, `timestamp` and `user_id` fields are the same values as
> > returned by the __`/list`__ endpoint, above.  These are returned for
> > convenience.  Each entry in the `annotations` array will be an object with
> > the following fields:
> > 
> > > `account`
> > > 
> > > > The address of the Ripple account this annotation is associated with.
> > > 
> > > `key`
> > > 
> > > > A string uniquely identifying this annotation for this account.
> > > 
> > > `value`
> > > 
> > > > The value of this annotation for this account.
> > > 
> > > `hidden`
> > > 
> > > > Has this particular annotation entry been hidden?
> > > 
> > > `hidden_at`
> > > 
> > > > If the annotation has been hidden, this will be the date and time at
> > > > which the annotation was hidden, as an integer number of seconds since
> > > > midnight on the 1st of January, 1970 ("unix time"), in UTC.
> > > 
> > > `hidden_by`
> > > 
> > > > If the annotation has been hidden, this will be the `user_id` value for
> > > > the user who hid this annotation.
> > 
> > Note that the `hidden_at` and `hidden_by` fields will only be present if
> > the annotation has been hidden.
> > 
> > If the request was not successful, the returned JSON object will look like
> > this:
> > 
> > >     {
> > >       success: false,
> > >       error: "..."
> > >     }
> > 
> > In this case, the `error` field will be a string describing why the request
> > failed.
> 
> __`/accounts`__
> 
> > Return a list of Ripple accounts which have annotations.
> > 
> > This API takes the following query-string parameters:
> > 
> > > `auth_token` _(required)_
> > > 
> > > > The calling system's authentication token.
> > 
> > > `page` _(optional)_
> > > 
> > > > Which page of results to return.  By default, we return page 1, which
> > > > is the first page of accounts.  Increasing page numbers will return
> > > > more accounts, ascending in alphabetical order.
> > > 
> > > `rpp` _(optional)_
> > > 
> > > > The number of results to return per page.  By default, we return a
> > > > maximum of 1000 accounts in each page of results.
> > 
> > Upon completion, the server will return an HTTP status code of `200` (OK),
> > and the body of the response will have a content-type value of
> > `application/json`.  The body of the response will consist of a JSON object
> > describing the result of the API call.  If the request was successful, the
> > returned JSON object will look like this:
> > 
> > >     {
> > >       success: true,
> > >       num_pages: /* integer */,
> > >       accounts: [ /* array of account addresses */ ]
> > >     }
> > 
> > The `num_pages` value will be the number of pages of results which will be
> > returned for the given `rpp` value.
> > 
> > Each entry in the `accounts` array will be the Ripple address of the
> > matching account, as a string.
> > 
> > If the request was not successful, the returned JSON object will look like
> > this:
> > 
> > >     {
> > >       success: false,
> > >       error: "..."
> > >     }
> > 
> > In this case, the `error` field will be a string describing why the request
> > failed.
> 
> __`/account/{account}`__
> 
> > Return the annotations currently associated with a single Ripple account.
> > 
> > Note that the address of the desired Ripple account is included as part of
> > the URL itself.
> > 
> > The following query string parameter must be supplied:
> > 
> > > `auth_token` _(required)_
> > > 
> > > > The calling system's authentication token.
> > 
> > Upon completion, the server will return an HTTP status code of `200` (OK),
> > and the body of the response will have a content-type value of
> > `application/json`.  The body of the response will consist of a JSON object
> > describing the result of the API call.  If the request was successful, the
> > returned JSON object will look like this:
> > 
> > >     {
> > >       success: true,
> > >       annotations: [ /* array of annotation objects */ ]
> > >     }
> > 
> > Each entry in the `annotations` array will be an object with the following
> > fields:
> > 
> > > `key`
> > > 
> > > > A string uniquely identifying this annotation for this account.
> > > 
> > > `value`
> > > 
> > > > The value of this annotation for this account.
> > 
> > If the request was not successful, the returned JSON object will look like
> > this:
> > 
> > >     {
> > >       success: false,
> > >       error: "..."
> > >     }
> > 
> > In this case, the `error` field will be a string describing why the request
> > failed.
> 
> __`/account_history/{account}`__
> 
> > Return a complete history of all changes made to a single Ripple account's
> > annotations over time.
> > 
> > Note that the address of the desired Ripple account is included as part of
> > the URL itself.
> > 
> > The following query string parameter must be supplied:
> > 
> > > `auth_token` _(required)_
> > > 
> > > > The calling system's authentication token.
> > 
> > Upon completion, the server will return an HTTP status code of `200` (OK),
> > and the body of the response will have a content-type value of
> > `application/json`.  The body of the response will consist of a JSON object
> > describing the result of the API call.  If the request was successful, the
> > returned JSON object will look like this:
> > 
> > >     {
> > >       success: true,
> > >       annotations: [ /* array of annotation history objects */ ]
> > >     }
> > 
> > Each entry in the `annotations` array will be an object with the following
> > fields:
> > 
> > > `key`
> > > 
> > > > A string uniquely identifying this annotation for this account.
> > > 
> > > `history`
> > > 
> > > > An array of changes made to this annotation value over time.  The
> > > > entries in this array are in date-descending order (that is, the
> > > > most recent change is the first entry in the array).  Each entry in the
> > > > `history` array will be an object with the following fields:
> > > > 
> > > > > `batch_number`
> > > > > 
> > > > > > The batch number in which this change was applied.
> > > > > 
> > > > > `value`
> > > > > 
> > > > > > The value that this annotation was set to within this batch.
> > > > > 
> > > > > `timestamp`
> > > > > 
> > > > > > The date and time at which this value was originally applied, as an
> > > > > > integer number of seconds since midnight on the 1st of January,
> > > > > > 1970 ("unix time"), in UTC.
> > > > > 
> > > > > `user_id`
> > > > > 
> > > > > > A string identifying who initially applied this annotation.
> > > > > 
> > > > > `hidden`
> > > > > 
> > > > > > Has this particular annotation entry been hidden?
> > > > > 
> > > > > `hidden_at`
> > > > > 
> > > > > > If the annotation has been hidden, this will be the date and time
> > > > > > at which the annotation was hidden, as an integer number of seconds
> > > > > > since midnight on the 1st of January, 1970 ("unix time"), in UTC.
> > > > > 
> > > > > `hidden_by`
> > > > > 
> > > > > > If the annotation has been hidden, this will be the `user_id` value
> > > > > > for the user who hid this annotation.
> > > > 
> > > > Note that the `hidden_at` and `hidden_by` fields will only be present
> > > > if the annotation has been hidden within this batch.
> > 
> > If the request was not successful, the returned JSON object will look like
> > this:
> > 
> > >     {
> > >       success: false,
> > >       error: "..."
> > >     }
> > 
> > In this case, the `error` field will be a string describing why the request
> > failed.
> 
> __`/search`__
> 
> > Search for accounts which match the given search query,
> > 
> > The following query string parameters must be supplied:
> > 
> > > `auth_token` _(required)_
> > > 
> > > > The calling system's authentication token.
> > > 
> > > 'query' _(required)_
> > > 
> > > > A string containing the query to search against.  Note that any "`&`"
> > > > characters in the query string must be replaced with "`%26`", and any
> > > > "`=`" characters must be replaced with "`%3D`".  This avoids confusion
> > > > when the query-string parameters are parsed by the server.
> > 
> > The search query consists of one or more _query terms_, where each query
> > term is a string of the form:
> > 
> > > `<annotation_key> <comparison> <value>`
> > 
> > For example:
> > 
> > > `name = "john"`  
> > > `status != 'CURRENT'`
> > 
> > Within a query term, the `<annotation_key>` is the name of the annotation
> > that you are comparing, `<comparison>` is the type of comparison you want
> > to do, and `<value>` is a string (surrounded by single or double quotes)
> > that you want to compare against.
> > 
> > The following comparison operators are currently supported:
> > 
> > > `=`  
> > > `<`  
> > > `>`  
> > > `<=`  
> > > `>=`  
> > > `!=`
> > 
> > > > _Note that the `<` and `>` operators perform alphanumeric comparisons as
> > > > all annotation values are treated as strings._
> > 
> > The search query can consist of just one query term, or it can consist of
> > multiple terms, surrounded by parentheses and joined with `and`, `or` or
> > `not` operators.  For example:
> > 
> > > `(name = "john") and (status != "CURRENT")`  
> > > `not ((name = "john") or (name = "harry"))`  
> > 
> > The search query is used to identify those accounts which have current
> > annotation values matching the supplied search term(s).
> > 
> > Upon completion, the server will return an HTTP status code of `200` (OK),
> > and the body of the response will have a content-type value of
> > `application/json`.  The body of the response will consist of a JSON object
> > describing the result of the API call.  If the request was successful, the
> > returned JSON object will look like this:
> > 
> > >     {
> > >       success: true,
> > >       accounts: [ /* array of matching accounts */ ]
> > >     }
> > 
> > Each entry in the `accounts` array will be the Ripple address of the
> > matching account, as a string.
> > 
> > If the request was not successful, the returned JSON object will look like
> > this:
> > 
> > >     {
> > >       success: false,
> > >       error: "..."
> > >     }
> > 
> > In this case, the `error` field will be a string describing why the request
> > failed.
> 
> __`/set_template/{template}`__
> 
> > Add or update an annotation template in the database.
> > 
> > Note that the name of the desired annotation template is included as part
> > of the URL itself.
> > 
> > This endpoint accepts a single annotation template, in JSON format.  There
> > are two ways in which this JSON data can be supplied:
> > 
> > 1. By submitting an HTTP "POST" request with a `Content-Type` value of
> >    `application/json`.  In this case, the JSON data should be in the body
> >    of the HTTP request.
> > <p/>
> > 2. By using a query-string parameter named `template`.  Note that in this
> >    case, any "`&`" characters in the JSON data should be replaced with
> >    "`%26`", and any '`=`" characters must be replaced with "`%3D`".  This
> >    avoids confusion when the query-string parameters are parsed by the
> >    server.
> > 
> > The JSON data must consist of an object with the following fields:
> > 
> > > `auth_token` _(required)_
> > > 
> > > > The calling system's authentication token.
> > > 
> > > `template` _(required)_
> > > 
> > > > An array of annotation entries to be included in the template.  Each
> > > > array entry should be an object with the following fields:
> > > > 
> > > > > `annotation` _(required)_
> > > > > 
> > > > > > The annotation key value for the desired annotation, for example,
> > > > > > "`phone_number`".
> > > > > 
> > > > > `label` _(required)_
> > > > > 
> > > > > > A string to be displayed to the user to identify the annotation,
> > > > > > for example, "`phone number`".
> > > > > 
> > > > > `type` _(required)_
> > > > > 
> > > > > > A string indicating the type of annotation value to be entered.
> > > > > > The following type values are currently supported:
> > > > > > 
> > > > > > > __choice__
> > > > > > > 
> > > > > > > > The user can choose between two or more values.
> > > > > > > 
> > > > > > > __field__
> > > > > > > 
> > > > > > > > The user can enter a value directly into an input field.
> > > > > 
> > > > > `default` _(optional)_
> > > > > 
> > > > > > The default value to use for this annotation, as a string.  If this
> > > > > > is not present, no default value should be set.
> > > > > 
> > > > > `choices` _(required for "choice" annotations)_
> > > > > 
> > > > > > An array of possible values the user can choose between.  Each
> > > > > > entry in the array will be another array with two entries, where
> > > > > > the first entry is the desired annotation value, and the second
> > > > > > entry is the label to display to the user when this annotation
> > > > > > value is selected.  For example:
> > > > > >   
> > > > > >         choices: [["M", "Male"], ["F", "Female"]]
> > > > > 
> > > > > `field_size` _(optional, only for "field" annotations)_
> > > > > 
> > > > > > The desired width of the input field, in characters.  This
> > > > > > corresponds to the `size` attribute for an HTML `<input>` tag.
> > > > > > Note that if this is not specified, the client will choose a
> > > > > > default width.
> > > > > 
> > > > > `field_required` _(optional, only for "field" annotations)_
> > > > > 
> > > > > > Set this to `true` if the user is required to enter a value for
> > > > > > this annotation.  If this is not present, the annotation will not
> > > > > > be required.
> > > > > 
> > > > > `field_min_length` _(optional, only for "field" annotations)_
> > > > > 
> > > > > > The minimum allowable length for this annotation value.  If this is
> > > > > > not present, no minimum length will be imposed.
> > > > > 
> > > > > `field_max_length` _(optional, only for "field" annotations)_
> > > > > 
> > > > > > The maximum allowable length for this annotation value.  If this is
> > > > > > not present, no maximum length will be imposed.
> > 
> > If there is already an annotation template with the given name, it will be
> > replaced by the updated values.  Otherwise, a new template with that name
> > will be created.
> > 
> > Upon completion, the server will return an HTTP status code of `200` (OK),
> > and the body of the response will have a content-type value of
> > `application/json`.  The body of the response will consist of a JSON object
> > describing the result of the API call.  If the request was successful, the
> > returned JSON object will look like this:
> > 
> > >     {
> > >       success: true,
> > >     }
> > 
> > If the request was not successful, the returned JSON object will look like
> > this:
> > 
> > >     {
> > >       success: false,
> > >       error: "..."
> > >     }
> > 
> > In this case, the `error` field will be a string describing why the request
> > failed.
> 
> __`/get_template/{template}`__
> 
> > Return the contents of the given annotation template.
> > 
> > Note that the name of the desired annotation template is included as part
> > of the URL itself.
> > 
> > The following query string parameter must be supplied:
> > 
> > > `auth_token` _(required)_
> > > 
> > > > The calling system's authentication token.
> > 
> > Upon completion, the server will return an HTTP status code of `200` (OK),
> > and the body of the response will have a content-type value of
> > `application/json`.  The body of the response will consist of a JSON object
> > describing the result of the API call.  If the request was successful, the
> > returned JSON object will look like this:
> > 
> > >     {
> > >       success: true,
> > >       template: [ /* array of annotation entries */ ]
> > >     }
> > 
> > Each entry in the 'template' array will be an object with the following
> > fields:
> > 
> > > `annotation`
> > > 
> > > > The annotation key value for the desired annotation, for example,
> > > > "`phone_number`".
> > > 
> > > `label`
> > > 
> > > > A string to be displayed to the user to identify the annotation, for
> > > > example, "`phone number`".
> > > 
> > > `type`
> > > 
> > > > A string indicating the type of annotation value to be entered.  The
> > > > following type values are currently supported:
> > > > 
> > > > > __choice__
> > > > > 
> > > > > > The user can choose between two or more values.
> > > > > 
> > > > > __field__
> > > > > 
> > > > > > The user can enter a value directly into an input field.
> > > 
> > > `default`
> > > 
> > > > The default value to use for this annotation, as a string.  If this is
> > > > not present, no default value should be set.
> > > 
> > > `choices`
> > > 
> > > > An array of possible values the user can choose between.  Each entry in
> > > > the array will be another array with two entries, where the first entry
> > > > is the desired annotation value, and the second entry is the label to
> > > > display to the user when this annotation value is selected.  For
> > > > example:
> > > >   
> > > >         choices: [["M", "Male"], ["F", "Female"]]
> > > 
> > > `field_size`
> > > 
> > > > The desired width of the input field, in characters.  This corresponds
> > > > to the `size` attribute for an HTML `<input>` tag.  Note that if this
> > > > is not specified, the client will choose a default width.
> > > 
> > > `field_required`
> > > 
> > > > Set this to `true` if the user is required to enter a value for this
> > > > annotation.  If this is not present, the annotation will not be
> > > > required.
> > > 
> > > `field_min_length`
> > > 
> > > > The minimum allowable length for this annotation value.  If this is not
> > > > present, no minimum length will be imposed.
> > > 
> > > `field_max_length`
> > > 
> > > > The maximum allowable length for this annotation value.  If this is not
> > > > present, no maximum length will be imposed.
> > 
> > If the request was not successful, the returned JSON object will look like
> > this:
> > 
> > >     {
> > >       success: false,
> > >       error: "..."
> > >     }
> > 
> > In this case, the `error` field will be a string describing why the request
> > failed.

Note that all the API endpoints can be called using either HTTP "POST" or HTTP
"GET" -- the API makes no distinction based on the HTTP method.


## Admin Interface ##

While the above API calls allow full access to all the functionality of the
Ripple Annotation Database, they are not particularly convenient for end users
to access.  To this end, the Annotation Database also provides a
password-protected admin interface.  When accessing the main URL for the
Annotation Database (__`/`__), the user will be redirected to the "Log In"
screen, where they will have to log in before they can do anything else.

Let's take a closer look at the log in screen, and then the other options
available via the admin interface.

### Log In ###

> __`/admin/login`__

When the user first accesses the admin interface, either via the `/admin` URL,
or by a redirection from the main URL for the database, `/`, they will be taken
to this URL.  This displays a dialog box asking the user to enter their
username and password.  Once the user has logged in, they will be redirected
back to the `/admin` URL to display the main menu.

### Main Menu ###

> __`/admin`__

If the user has not logged in when they access this URL, they will be
redirected back to `/admin/login` so they can enter a valid username and
password.  

Once the user has logged in, they will be presented with the following options:

>     Add Annotation  
>     Upload Annotations  
>     View Uploaded Annotations  
>     View Account Annotations  
>     Search  
>     Edit Annotation Templates
>     Add/Edit Users  
>     Change password  
>     Log out

These options link to other URLs providing the various features of the admin
interface, as described below.

### Add Annotation ###

> __`/admin/add`__

This page will let the user add a single annotation value.  Note that a dummy
batch will be created for this annotation, so the user is effectively creating
a batch with just one entry.

This page is provided for convenience, making it easier for users to add
annotations without having to upload them.

### Upload Annotations ###

> __`/admin/upload`__

This page will let the user upload a batch of annotations using a tab-delimited
text file.

### View Uploaded Annotations ###

> __`/admin/annotation`__

The user will be presented with a list of uploaded annotation batches, and can
click on a batch to view its contents.  The batch contents will then be
displayed, showing meta-information about the batch as a whole, as well as the
individual annotations within the batch.

An option is provided to hide an annotation within the batch.  Note that this
is not reversable -- once an annotation has been hidden, the only way to unhide
it again is to apply that annotation again, in a different batch.  This ensures
that the system maintains a complete audit trail of all changes made to the
annotations over time.

### View Account Annotations ###

> __`/admin/account`__

The user will be asked to enter the Ripple address for a desired account.  A
list of all annotations currently in force for that account will then be shown,
along with the batch number where this annotation was applied.

### Search ###

> __`/admin/search`__

The user will be asked to enter up to three annotation keys and their
associated values.  The system will then search for matching Ripple accounts,
and display the Ripple address for those matching accounts.

### Edit Annotation Templates ###

> __`/admin/templates`__

This lets the user view the list of annotation templates, and upload a new
template from an Excel spreadsheet.  Existing templates can be deleted if
desired.

### Add/Edit Users ###

> __`/admin/users`__

Note that this option is only available for "admin" users.  This page lets the
user add, edit and remove other users from the system.

### Change Password ###

> __`/admin/password`__

This page lets the user change their password.

### Log Out ###

> __`/admin/logout`__

This page logs the user out again.  The "login" page will then be displayed.

