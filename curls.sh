curl --dump-header - -X POST -H "Content-Type: application/json"  http://localhost:8000/py/api/v1/lap/?format=json -d '{"lap_nr": 1, "penalty": "11:08:26", "penalty_value": "22", "time": "11:08:25", "start_number":"12", "trial_id":"1"}'
curl --dump-header - -X POST -H "Content-Type: application/json"  http://localhost:8000/py/api/v1/lap/?format=json -d '{"lap_nr": 1, "time": "11:08:25", "start_number":"1", "event_id":"1", "trial_id":"2"}'



localhost:8000/py/api/v1/trial_driver/?trial=1
localhost:8000/py/api/v1/event_driver