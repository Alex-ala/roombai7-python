from roomba import Roomba
from time import sleep
import json

roomba = Roomba("10.4.0.17", "44EF51470B0843E2B2529E9F50A9C4C5", ":1:1551302838:l8utb1Yb8glanBwx")
roomba.connect()
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
