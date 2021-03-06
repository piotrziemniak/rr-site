from django.contrib.auth.models import User
from django.db.models import Min, Sum, Max
from django.db.models.aggregates import Count
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from racerecordweb.models import Lap, Trial, Event, Driver, Car, EventDriver, TrialDriver
from tastypie.authorization import Authorization
import copy


class EventResource(ModelResource):
    class Meta:
        queryset = Event.objects.all();
        resource_name = 'event'
        include_resource_uri = False

    def alter_list_data_to_serialize(self, request, data_dict):
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del (data_dict['meta'])
                # Rename the objects.
                data_dict['events'] = copy.copy(data_dict['objects'])
                del (data_dict['objects'])
        return data_dict


class DriverResource(ModelResource):
    class Meta:
        queryset = Driver.objects.all();
        resource_name = 'driver'
        fields = ['last_name', 'first_name']
        include_resource_uri = False

    def alter_list_data_to_serialize(self, request, data_dict):
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del (data_dict['meta'])
                # Rename the objects.
                data_dict['drivers'] = copy.copy(data_dict['objects'])
                del (data_dict['objects'])
        return data_dict


class TrialResource(ModelResource):
    event = fields.ForeignKey(EventResource, 'event')
    filtering = {
        'id': ALL,
    }

    class Meta:
        queryset = Trial.objects.all()
        resource_name = 'trial'
        include_resource_uri = False
        filtering = {
            'name': ALL,
        }

    def alter_list_data_to_serialize(self, request, data_dict):
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del (data_dict['meta'])
                # Rename the objects.
                data_dict['trials'] = copy.copy(data_dict['objects'])
                del (data_dict['objects'])
        return data_dict


class CarResource(ModelResource):
    class Meta:
        queryset = Car.objects.all();
        resource_name = 'car'
        include_resource_uri = False

    def alter_list_data_to_serialize(self, request, data_dict):
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del (data_dict['meta'])
                # Rename the objects.
                data_dict['cars'] = copy.copy(data_dict['objects'])
                del (data_dict['objects'])
        return data_dict


class EventDriverResource(ModelResource):
    #laps = fields.ToManyField(LapResource, 'laps', related_name="lap", full=True, null=True)
    driver = fields.ForeignKey(DriverResource, 'driver', full=True, null=True)
    event = fields.ForeignKey(EventResource, 'event', full=True, null=True)

    class Meta:
        queryset = EventDriver.objects.all()
        resource_name = 'event_driver'
        #excludes = ['id']
        include_resource_uri = False
        authorization = Authorization()
        filtering = {
            'driver': ['first_name', 'last_name'],
        }

    def dehydrate(self, bundle):
        _n_1 = 0
        _min = 0
        _laps = 0
        _sum = 0
        for trial in bundle.obj.event.trials.all():
            times = bundle.obj.laps.filter(trial__id=trial.id).aggregate(Sum('time'), Min('time'), Max('time'), Count('time'))
            if times['time__min'] and times['time__max'] and times['time__sum']:
                _n_1 += times['time__sum'] - times['time__max']
                _min += times['time__min']
                _laps += times['time__count']
                _sum += times['time__sum']

        for index, lap in enumerate(bundle.obj.laps.all()):
            bundle.data['lap_%s' % index] = lap.time

        bundle.data['laps'] = _laps
        bundle.data['time_n_minus_1'] = _n_1
        bundle.data['time_sum'] = _sum
        bundle.data['time_n'] = _min
        bundle.data['first_name'] = bundle.obj.driver.first_name
        bundle.data['last_name'] = bundle.obj.driver.last_name

        del bundle.data['id']
        del bundle.data['driver']
        del bundle.data['event']

        return bundle

    def alter_list_data_to_serialize(self, request, data_dict):
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del (data_dict['meta'])
                # Rename the objects.
                data_dict['event_drivers'] = copy.copy(data_dict['objects'])
                del (data_dict['objects'])
        return data_dict


class TrialDriverResource(ModelResource):
    driver = fields.ForeignKey(DriverResource, 'driver', full=True, null=True)
    trial = fields.ForeignKey(TrialResource, 'trial', full=True, null=True)

    class Meta:
        queryset = TrialDriver.objects.all()
        resource_name = 'trial_driver'
        include_resource_uri = False
        authorization = Authorization()
        filtering = {
            'trial': ALL_WITH_RELATIONS,
        }

    def dehydrate(self, bundle):
        _n_1 = 0
        _min = 0
        _sum = 0
        times = bundle.obj.laps.all().aggregate(Sum('time'), Min('time'), Max('time'), Count('time'))
        if times['time__min'] and times['time__max'] and times['time__sum']:
            _n_1 += times['time__sum'] - times['time__max']
            _sum += times['time__sum']
            _min += times['time__min']

        for index, lap in enumerate(bundle.obj.laps.all()):
            bundle.data['lap_%s' % index] = lap.time

        bundle.data['laps'] = times['time__count']
        bundle.data['time_n_minus_1'] = _n_1
        bundle.data['time_n'] = _min
        bundle.data['time_sum'] = _sum
        bundle.data['first_name'] = bundle.obj.driver.first_name
        bundle.data['last_name'] = bundle.obj.driver.last_name
        bundle.data['trial_id'] = bundle.obj.trial.id

        del bundle.data['id']
        del bundle.data['driver']
        del bundle.data['trial']
        return bundle

    def alter_list_data_to_serialize(self, request, data_dict):
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del (data_dict['meta'])
                # Rename the objects.
                data_dict['trial_drivers'] = copy.copy(data_dict['objects'])
                del (data_dict['objects'])
        return data_dict


class LapResource(ModelResource):
    event_driver = fields.ForeignKey(EventDriverResource, 'event_driver', related_name='laps')
    #trial = fields.ForeignKey(Trial, 'trial', related_name='laps')

    class Meta:
        queryset = Lap.objects.all()
        resource_name = 'lap'
        excludes = ['penalty', 'penalty_value']
        include_resource_uri = True
        authorization = Authorization()


    def hydrate(self, bundle):
        (min, sec, msec) = [int(t) for t in bundle.data['time'].split(':')]
        bundle.data['time'] = int((min*60+sec)*1000+msec)
        trial = Trial.objects.get(id=bundle.data['trial_id'])
        event_driver = EventDriver.objects.get(event__id=bundle.data['event_id'],
                                               start_number=bundle.data['start_number'])
        bundle.obj.event_driver = event_driver
        bundle.obj.trial = trial
        del bundle.data['event_id']
        del bundle.data['trial_id']
        del bundle.data['start_number']
        return bundle

    def alter_list_data_to_serialize(self, request, data_dict):
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del (data_dict['meta'])
                # Rename the objects.
                data_dict['laps'] = copy.copy(data_dict['objects'])
                del (data_dict['objects'])
        return data_dict
