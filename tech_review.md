# Beyond classify.sh
## Practical lessons integrating Text Analysis into non-trivial apps, Fabio Arciniegas CS410

In the process of learning Text Analysis topics one comes across many different useful libraries and tools, all of which include a quickstart tutorial, usually a single-user, single threaded command line application with pre-provisioned ideal data, which uses the safest and simplest api in the system. From that point to a real working application (mobile, voice, web) there is a big chasm.  This article contains a few modest but practical tips to bridge the gap:

## Invest in configuration scaffolding (take ALL the configuration out of the code)

In sample applications the parameters and configuration files are hand-written and embedded as literals in the code. In a real app you are realistically going to run the algorithms hundreds of times during development and adjusting parameters by hand, deleting intermediate directores, and modifying configuration files can be not only tedious but very error prone.

A library that allows you abstract all the configuration out of the code and manage it from (a) the app, (b) the framework admin interface and (c) the database directly is not a luxury but a necessity. I used dynamic-preferences (https://django-dynamic-preferences.readthedocs.io/en/latest/index.html) to keep the parameters affecting the evaluation of reviews and saved hours of manual repetition, it will be only more important for larger applications.

Another advantage of having configuration abstracted out and automated is avoiding small gotchas such as metapy requiring the deletion of intermediate files. 

## Adopt a data model that reflects the concept, not the input/output of a library

Sample apps usually have single nice pre-packaged clean data source but even within a single library such as META there are a couple of corpus representation options you can choose from (file, line, svm) , not to mention that even in a relatively small app you are bound to use several different text-related libraries.In "Identify Shills" I used eight, partly because I wanted to try several I had not used but also because it is natural and often inexpensive to use different tools for different aspects.

Throughout the app the same data will be massaged into different representations (d3 parallels coordinates needs the the topic distributions as json array of anonymous dicts, doc implied, while google charts needs it as two arrays of arrays and the pandas code that calculates the z-scores needs it as a dataframe).

When it comes to persist in the database the topic distributions and similar data which is used in different ways throughout the app, it's best to capture a more general conceptual representation like lists of maps of documents to probabilities rather than the specific input expected by say, a graph library. Rendering views quickly by cutting corners with the model representation can be a temptation. Resist it. The transformation from a clear conceptual representation to anything needed by a library is usually trivial but the translation between two library-specific representations is not.

## Prepare early for Asynchronous behavior

Unless you are working on a command line utility, practically no real application can afford asking the user to wait for seconds or dozens of seconds as a text analysis task completes.  Whether driven by volume or responsiveness chances are heavy tasks such as text analysis have to be wrapped around asynchrnous blocks (through queues or threads) and a messaging mechanism will need to be in place to report progress and results.

If you are working within a Software As A Service environment such as AWS this is practically a built-in model and the architecture of queues and notifications such as SNS are easy to use. If you are working closer to the metal you will need to wrap workers into queues or threads yourself. In either case some amount of notification logic will be required in the user interface.

Asynchronous behavior is unavoidable so better prepare for it early. The keywords are queues such as RabbitMQ and the natural equivalent in your platform/framework of channels.

## Acknowledge the wrapping (dealing with C/C++ libraries wrapped in python)

Text analysis libraries for python and other high level languages are often wrappers for C/C++ originals. As with any wrapper, there will be (a) impedence mismatch when the concepts or data structures don't translate easily from one language to another and (b) gaps in documentation and features.

In my experience the best you can do (rather than spend hours trying to google the python-specific answer when there is nothing but the original C++ documentation) is get good at introspection of objects in your language of choice. ``dir``, ```type```, ```inspect``` are lifesavers in python. See more http://book.pythontips.com/en/latest/object_introspection.html


##  Be prepared to work at PAAS level, SAAS text analysis may not be customizable or cheap enough yet (2018)

The promise of Text Analysis as a Service is enticing and no doubt AWS Comprehend and similar offerings will improve in the future. As of 2018, however, Text Analysis packaged as Software As A Service level (SAAS) may be very easy to use but not customizable or cheap enough.

The tasks involved in the Identify Shills app (https://www.youtube.com/watch?v=gCZt6Mc0N6U) (Topic Analysis, Sentiment Analysis, and Custom classification) are all in some form supported by Amazon AWS. There are some roadblocks, however, and some of them were deal breakers. 

The following are roadblocks I found while initially considering to implement some of the functionality in AWS Comprehend. I ended up opting for a complete library-based solution, if the following issues would apply to your project maybe it will save you time knowing they exist in the AWS Comprehend option:

## Topic Analysis: cost
Topic Analysis in AWS is billed (as of December 15, 2018) at a flat rate of $1 for the first 100Mb in a job and at $0.0004 per MB after that. The volume of text data for a single movie is a mere 98Kb to 300Kb, but UI responsiveness require that each is processed in real time, not in batch. In other words we could be paying $0.0004 per movie analyzed. A high price when you consider a simple t1.micro instance ($8.50 month) could trivially do 10000 of those within a daily usage and during development it could be done in the developers machine.


## Topic Analysis: lack of customization
Topic Analysis in AWS is made (non-surprisingly) using LDA. However, the specific flavor used is not specified. Meta on the other hand offers the option of LDA using collapsed variational Bayes, Gibbs sampling (faster) and parallel lda gibbs (gibs exploting multiple cores). Options for maximum iterations are also ommitted for simplicty from the AWS API.

## Language detection: latency, complexity
Dominant language detection is often important, in my case to ignore non-english reviews, but it is not too expensive. It can be done reasonably for single documents within milliseconds with a single call to a function with a string parameter, so having to incur the cost of putting sources in S3, and the latency of the API call seems unnecessary.

## Sentiment analysis: opacity behind s3 affects malleability
The Comprehend API for sentiment analyis returns single [0,1] float numbers for positive and negative feeling, which is not unlike many libraries, but because the logic is tightly encapsulated behind the restful api and it requires s3 buckets as inputs it becomes harder to build upon it for variations like stratified ratings (e.g stars). In python libraries this is easier as techniques such as removing a few items from the corpus before doing another round of binary classfication are easier to execute (for example in views of datasets).

## Save SAAS for NLP APIs, not for Bag of Words
Finally, it seems to me the most distinctive APIS in AWS comprehend, and probably those worth the cost, are those with a more decisive NLP-flavor, in particular DetectKeyPhrases, and DetectEntities. In contrast, more "bag of word" problems may be cheaper and more flexible implemented without the SAAS offering.


Fabio Arciniegas,  December 2018











