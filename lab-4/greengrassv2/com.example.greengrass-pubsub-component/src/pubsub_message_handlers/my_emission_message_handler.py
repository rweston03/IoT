 
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0.

'''
my_system_message_handler.py
'''

__version__ = "0.0.1"
__status__ = "Development"
__copyright__ = "Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved."
__author__ = "Dean Colcott <https://www.linkedin.com/in/deancolcott/>"

import logging, random
 
# Config the logger.
log = logging.getLogger(__name__)
 
class MyEmissionMessageHandler():

    def __init__(self, publish_message, publish_error, message_formatter):
        
        self.publish_message = publish_message
        self.publish_error = publish_error
        self.message_formatter = message_formatter

        self.max_co2 = {}

    ########################################################
    ## Example User Defined Message handlers  ##############
    ########################################################
    
    def get_message_request(self, protocol, topic, message_id, status, route, message):
        '''
        This is an example of a user defined message handler that would expect to respond
        with a max emission measurement. Once this Class is registered with the SDK as a message_handler, 
        and PubSub messages received (on any subscribed topic)  with route = 'MyEmissionHandler.get_emission_request' 
        will be routed here.
        
        In this example, we read in parameters from the requests user defined message attribute,  
        create a well formed 'get_emission_request' message and publish it 
        to the protocol the request was made on (IPC or MQTT) on the default egress PubSub topic.

        Expected message format:
        message = {
            ...
            "vehicle_id" : "0",
            "vehicle_CO2": "12"
            ...
        }

        '''

        try:
            # Log just for Dev / Debug.
            log.info('get_emission_request received on protocol: {} - topic: {}'.format(protocol, topic))

            # Just as a demoenstration, take the sensor ID from the user defined message.
            # Add default value "default-sensor-1234", otherwise set to vaklue in message parameter.
            vehicle_id = message.get('vehicle_id', None)
            vehicle_CO2 = message.get('vehicle_CO2', None)
            status = message.get('status', None)

            if vehicle_id is None or vehicle_CO2 is None:
                log.warning(f"Missing vehicle data in message: {message}")
                return

            if vehicle_id not in self.max_co2:
                self.max_co2[vehicle_id] = vehicle_CO2
            else:
                self.max_co2[vehicle_id] = max(self.max_co2[vehicle_id], vehicle_CO2)

            if status == "DONE":
                self.send_message_response(protocol, topic, message_id, status, route, vehicle_id)

        except Exception as err:
            # Publish error to default error route, will log locally as an error as well. 
            err_msg = 'Exception in get_emission_request: {}'.format(err)
            self.publish_error(protocol, err_msg)

    def send_message_response(self, protocol, topic, message_id, status, route, vehicle_id):
            # Create a response message using the Greengrass PubSub SDK prefered message_formatter.
            # Reflect the request message_id for tracking, status and other fields as defeult.
            if vehicle_id in self.max_co2:
                max_co2_value = self.max_co2[vehicle_id]
                response_route = "MyEmissionHandler.get_message_request"
                msg = {
                    "vehicle_id" : vehicle_id,
                    "max_CO2": max_co2_value
                }
                response =  self.message_formatter.get_message(message_id=message_id, route=response_route, message=msg)
                self.publish_message(protocol=protocol, message=response)
            else:
                log.warning(f"No CO2 data found for vehicle {vehicle_id}.")