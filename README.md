# DiningBot
A Dinner recomendation chatbot with a WebUI, built using AWS 

This is a simple restaurant recommendation chatbot that gathers user's requirements for dining, searches for restaurant matches, and sends a message with recommendations to the user's mobile phone.

Please use the webpage - https://sample-102020.s3.amazonaws.com/index.html - to access the WebUI of the chatbot.


The list of services used from AWS stack:
1. Amazon Simple Storage Service (S3) - to host the Web UI
2. API Gateway - to build API endpoints for the chatbot
3. Lambda - to accommodate the coordination between multiple services
4. Lex - for NLU and Dialog Management of the chatbot
5. Amazon Simple Queue Service (SQS) - for queuing the customer requests for restaurant recommendations
6. Amazon Elasticsearch service - to index key information of restaurants for a quick automated elastic search
7. DynamoDB - as a NoSQL database to store the restaurant information scraped from the Yelp API, used for providing non-indexed necessary details of restaurants to the user
8. Amazon Simple Notification Service (SNS) - to send an SMS with the restaurant recommendations and details to the user's mobile phone
9. Amazon Cognito - for user sign-up, sign-in and access control
10. Amazon Cloudwatch - to setup a Lambda trigger, which polls the queue periodically and performs a search for the user requests and sends an sms with the recommendations to the user
11. AWS Identity and Access Management (IAM) - to manage internal access between the services used. 

Other tools and services used:
1. Yelp API service - to gather restaurant information
2. HTML, Javascript, and CSS - to build a simple Web based UI for the chatbot
3. Swagger - to design the REST API for the chatbot
4. Python, Jupyter - to write scripts for scraping the data from Yelp API, storing the data into dynamo db, formatting the key data for Elastic Search Indexing, to perform bulk indexing operations on the Elasticsearch API, and for all the Lambda functions.
