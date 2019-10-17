import json
import math
import dateutil.parser
import datetime
import time
import os
import re
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

validationError = None


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }
def processCuisine(cuisine):
    if cuisine.lower() in "indian":
        cuisine="indpak"
    elif (cuisine.lower() in "breakfast" or cuisine.lower() in "brunch"):
        cuisine="breakfast_brunch"
    return cuisine


def validate_dining_suggestion(location, time, cuisine, phone_number):
    
    locationList = ['jersey city', 'hoboken', 'newport' , 'brooklyn' , 'manhattan']
    cuisineList = ['italian','japanese','chinese', 'mexican','indpak', 'thai', 'vietnamese', 'greek', 'german', 'french', 'brazilian', 'kosher', 'korean', 'irish', 'breakfast_brunch', 'mediterranean','scottish']
    cuisine= processCuisine(cuisine)
    
    if location is not None and location.lower() not in locationList:
        return build_validation_result(False,
                                       'location',
                                       'Currently, there is no service in {}, Please select from {}'.format(location,locationList))
    if cuisine is not None and cuisine.lower() not in cuisineList:
        return build_validation_result(False,
                                       'cuisine',
                                       'Please select cuisine from {}'.format(cuisineList))
    timeReg = re.compile("^(([0-1]{0,1}[0-9]( )?(AM|am|aM|Am|PM|pm|pM|Pm))|(([0]?[1-9]|1[0-2]) ?(:|\.) ?[0-5][0-9]( )?(AM|am|aM|Am|PM|pm|pM|Pm))|(([0]?[0-9]|1[0-9]|2[0-3])(:|\.)[0-5][0-9]))$")
    phReg =  re.compile("\+?\d?\s?\(?\w{3}\)?-?\w{3}-?\w{4}")
    if time is not None:
        if not (timeReg.match(time)):
            return build_validation_result(False, 'time', "Please tell me a valid time?")
    if phone_number is not None:
        if not (phReg.match(phone_number)):
            return build_validation_result(False, 'phone_number', "Can you please give me a valid phone number?")
            
    return build_validation_result(True, None, None)

def getSQSMessageBody(intent_request):
    msg={}
    msg['cuisine'] = get_slots(intent_request)["cuisine"]
    msg['time'] = get_slots(intent_request)["time"]
    msg['people'] = get_slots(intent_request)["people"]
    msg['location'] = get_slots(intent_request)["location"]
    msg['date'] = get_slots(intent_request)["date"]
    msg['phone_number'] = get_slots(intent_request)["phone_number"]
    return json.dumps(msg)
    

""" --- Functions that control the bot's behavior --- """


def diningSuggestionIntent(intent_request):
    """
    Performs dialog management and validation for soliciting dinner suggestions.
    The implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """

    cuisine = get_slots(intent_request)["cuisine"]
    time = get_slots(intent_request)["time"]
    numberOfPeople = get_slots(intent_request)["people"]
    location = get_slots(intent_request)["location"]
    phone_number = get_slots(intent_request)["phone_number"]
    
    source = intent_request['invocationSource']
    
    
    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_dining_suggestion(location, time, cuisine, phone_number)
        
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        # Pass the price of the flowers back through session attributes to be used in various prompts defined
        # on the bot model.
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

        return delegate(output_session_attributes, get_slots(intent_request))

    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thank you. You’re all set. Expect my suggestions shortly! Have a good day.'})


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingIntent':
        return greetingIntent(intent_request)
        
    elif intent_name == 'ThankyouIntent':
        return thankyouIntent(intent_request)
        
    elif intent_name == 'DiningSuggestionIntent':
        return diningSuggestionIntent(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def send_sqs_message(sqs_queue_url, msg_body):
    """
    :param sqs_queue_url: String URL of existing SQS queue
    :param msg_body: String message body
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """

    # Send the SQS message
    sqs_client = boto3.client('sqs')
    try:
        msg = sqs_client.send_message(QueueUrl=sqs_queue_url,
                                      MessageBody=msg_body)
    except ClientError as e:
        logging.error(e)
        return None
    return msg


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    sqs_queue_url = 'https://sqs.us-east-1.amazonaws.com/463589813520/dinigbot'

    # Set up logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(asctime)s: %(message)s')

    logging.info("")
    currentIntent = event['currentIntent']['name']
    invocationSource = event['invocationSource']
    
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    
    if invocationSource == "DialogCodeHook":
        return dispatch(event)

    elif invocationSource == "FulfillmentCodeHook":
        msg_body = getSQSMessageBody(event)
        msg = send_sqs_message(sqs_queue_url, msg_body)
        if msg is not None:
            logging.info(f'Sent SQS message ID: {msg["MessageId"]}')
        return close(event['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thank you. You’re all set. Expect my suggestions on your mobile phone shortly! Have a good day.'})