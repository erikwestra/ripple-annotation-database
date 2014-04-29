Ripple Annotation Database
--------------------------

This specification covers the __Ripple Annotation Database__, which is a system
for recording and retrieving "annotations" associated with Ripple accounts.
The Annotation Database consists of both an API and a password-protected web
interface which lets end users access and work with this API.

Note that the web interface only acts as a "front end" to the API -- there is
no functionality in the web interface which cannot be accessed via the API
directly.


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
> > > `page`
> > > 
> > > > Which page of results to return.  By default, we return page 1, which
> > > > is the most recent `rpp` batches.  Increasing page numbers will return
> > > > lists of batches going further back in time.
> > > 
> > > `rpp`
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
> > > `page`
> > > 
> > > > Which page of results to return.  By default, we return page 1, which
> > > > is the first page of accounts.  Increasing page numbers will return
> > > > more accounts, ascending in alphabetical order.
> > > 
> > > `rpp`
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
> > Search for accounts which match the given set of query parameters.
> > 
> > Any supplied query string parameters are used to search for accounts which
> > have the given annotation value.  For example, the following API call:
> > 
> > > `/search?primary=RL&secondary=CST`
> > 
> > will return only those accounts which have an annotation named "primary"
> > with the value "RL" and an annotation named "secondary" with the value
> > "CST".
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

Note that all the API endpoints can be called using either HTTP "POST" or HTTP
"GET" -- the API makes no distinction based on the HTTP method.

## Web Interface ##

While the above API calls allow full access to all the functionality of the
Ripple Annotation Database, they are not particularly convenient for end users
to access.  To this end, the Annotation Database also provides a
password-protected web interface.  When accessing the main URL for the
Annotation Database (__`/`__), the user will be redirected to the "Log In"
screen, where they will have to log in before they can do anything else.

Let's take a closer look at the log in screen, and then the other options
available via the web interface.

### Log In ###

> __`/web/login`__

When the user first accesses the web interface, either via the `/web` URL, or
by a redirection from the main URL for the database, `/`, they will be taken to
this URL.  This displays a dialog box asking the user to enter their username
and password.  Once the user has logged in, they will be redirected back to the
`/web` URL to display the main menu.

### Main Menu ###

> __`/web`__

If the user has not logged in when they access this URL, they will be
redirected back to `/web/login` so they can enter a valid username and
password.  

Once the user has logged in, they will be presented with the following options:

>     Add Annotation  
>     Upload Annotations  
>     View Uploaded Annotations  
>     View Account Annotations  
>     Search  
>     Add/Edit Users  
>     Change password  
>     Log out

These options link to other URLs providing the various features of the web
interface, as described below.

### Add Annotation ###

> __`/web/add`__

This page will let the user add a single annotation value.  Note that a dummy
batch will be created for this annotation, so the user is effectively creating
a batch with just one entry.

This page is provided for convenience, making it easier for users to add
annotations without having to upload them.

### Upload Annotations ###

> __`/web/upload`__

This page will let the user upload a batch of annotations using a tab-delimited
text file.

### View Uploaded Annotations ###

> __`/web/annotation`__

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

> __`/web/account`__

The user will be asked to enter the Ripple address for a desired account.  A
list of all annotations currently in force for that account will then be shown,
along with the batch number where this annotation was applied.

### Search ###

> __`/web/search`__

The user will be asked to enter up to three annotation keys and their
associated values.  The system will then search for matching Ripple accounts,
and display the Ripple address for those matching accounts.

### Add/Edit Users ###

> __`/web/users`__

Note that this option is only available for "admin" users.  This page lets the
user add, edit and remove other users from the system.

### Change Password ###

> __`/web/password`__

This page lets the user change their password.

### Log Out ###

> __`/web/logout`__

This page logs the user out again.  The "login" page will then be displayed.
