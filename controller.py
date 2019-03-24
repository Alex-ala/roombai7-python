from roomba import Roomba
from time import sleep
import json
from pprint import pprint

roomba = Roomba("10.4.0.17", "44EF51470B0843E2B2529E9F50A9C4C5", ":1:1553325425:NLnNlriixEfLF0bE")
roomba.connect()
sleep(10)
# roomba.set_internal_mapping(True)
# roomba.set_language('en-US')
# roomba.set_stop_on_full_bin(True)
# sleep(30)
# roomba.start_training()
# sleep(5)
sleep(5)
roomba.disconnect()


# while True:
#     topic=input('topic:')
#     command=dict()
#     command['initiator']='localApp'
#     command['time'] = int(time())
#     if topic == 'delta':
#         command['command'] = json.loads(input('options'))
#     else:
#         command['command']=input('command:')
#     roomba.send_command(topic, command)
