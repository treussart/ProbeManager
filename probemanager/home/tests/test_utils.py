""" venv/bin/python probemanager/manage.py test home.tests.test_utils """
from django.test import TestCase
from home.utils import create_upload_task, create_deploy_rules_task, create_reload_task, encrypt, decrypt, add_10_min, add_1_hour
from rules.models import Source
from home.models import Probe
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class TasksRulesTest(TestCase):
    fixtures = ['init', 'crontab', 'test-rules-source', 'test-home-server', 'test-home-probe']

    @classmethod
    def setUpTestData(cls):
        cls.test = 'test'

    def test_create_upload_task(self):
        create_upload_task(Source.get_by_id(1))
        periodic_task = PeriodicTask.objects.get(name='https://sslbl.abuse.ch/blacklist/sslblacklist.rules_upload_task')
        self.assertEqual(periodic_task.task, 'home.tasks.upload_url_http')
        self.assertEqual(periodic_task.args, str([Source.get_by_id(1).uri, ]).replace("'", '"'))

    def test_create_reload_task(self):
        create_reload_task(Probe.get_by_id(1))
        periodic_task = PeriodicTask.objects.get(name=Probe.get_by_id(1).name + '_reload_task')
        self.assertEqual(periodic_task.task, 'home.tasks.reload_probe')
        self.assertEqual(periodic_task.args, str([Probe.get_by_id(1).name, ]).replace("'", '"'))

    def test_create_deploy_rules_task(self):
        probe = Probe.get_by_id(1)
        create_deploy_rules_task(probe)
        periodic_task = PeriodicTask.objects.get(name=probe.name + '_deploy_rules_' + probe.scheduled_rules_deployment_crontab.__str__())
        self.assertEqual(periodic_task.task, 'home.tasks.deploy_rules')
        self.assertEqual(periodic_task.args, str([probe.name, ]).replace("'", '"'))

    def test_create_deploy_rules_task_with_schedule(self):
        probe = Probe.get_by_id(1)
        schedule = CrontabSchedule.objects.get(id=1)
        source = Source.objects.get(id=1)
        create_deploy_rules_task(probe, schedule, source)
        periodic_task = PeriodicTask.objects.get(name=probe.name + '_' + source.uri + '_deploy_rules_' + schedule.__str__())
        self.assertEqual(periodic_task.task, 'home.tasks.deploy_rules')
        self.assertEqual(periodic_task.args, str([probe.name, ]).replace("'", '"'))

    def test_encrypt_decrypt(self):
        test = encrypt(self.test)
        self.assertEqual(decrypt(test), self.test)

    def test_add_10_min(self):
        self.schedule, _ = CrontabSchedule.objects.get_or_create(minute='*',
                                                                 hour='*/2',
                                                                 day_of_week='*',
                                                                 day_of_month='*',
                                                                 month_of_year='*',
                                                                 )
        self.schedule.save()
        schedule_added = add_10_min(self.schedule)
        self.assertEqual(str(schedule_added), "10 */2 * * * (m/h/d/dM/MY)")

        self.schedule, _ = CrontabSchedule.objects.get_or_create(minute='*/30',
                                                                 hour='*',
                                                                 day_of_week='*',
                                                                 day_of_month='*',
                                                                 month_of_year='*',
                                                                 )
        self.schedule.save()
        schedule_added = add_10_min(self.schedule)
        self.assertEqual(str(schedule_added), "*/40 * * * * (m/h/d/dM/MY)")

        # each 2 minutes at 2 o'clock.
        self.schedule, _ = CrontabSchedule.objects.get_or_create(minute='*/22',
                                                                 hour='2',
                                                                 day_of_week='*',
                                                                 day_of_month='*',
                                                                 month_of_year='*',
                                                                 )
        self.schedule.save()
        schedule_added = add_10_min(self.schedule)
        self.assertEqual(str(schedule_added), "*/32 2 * * * (m/h/d/dM/MY)")

        self.schedule, _ = CrontabSchedule.objects.get_or_create(minute='*/52',
                                                                 hour='21',
                                                                 day_of_week='*',
                                                                 day_of_month='*',
                                                                 month_of_year='*',
                                                                 )
        self.schedule.save()
        schedule_added = add_10_min(self.schedule)
        self.assertEqual(str(schedule_added), "10 22 * * * (m/h/d/dM/MY)")

        self.schedule, _ = CrontabSchedule.objects.get_or_create(minute='*/52',
                                                                 hour='23',
                                                                 day_of_week='*',
                                                                 day_of_month='*',
                                                                 month_of_year='*',
                                                                 )
        self.schedule.save()
        schedule_added = add_10_min(self.schedule)
        self.assertEqual(str(schedule_added), "*/52 23 * * * (m/h/d/dM/MY)")

        schedule, _ = CrontabSchedule.objects.get_or_create(minute='50',
                                                            hour='*',
                                                            day_of_week='*',
                                                            day_of_month='*',
                                                            month_of_year='*',
                                                            )
        schedule_added = add_10_min(schedule)
        self.assertEqual(str(schedule_added), "0 */1 * * * (m/h/d/dM/MY)")

        schedule, _ = CrontabSchedule.objects.get_or_create(minute='0',
                                                            hour='1',
                                                            day_of_week='*',
                                                            day_of_month='*',
                                                            month_of_year='*',
                                                            )
        schedule_added = add_10_min(schedule)
        self.assertEqual(str(schedule_added), "10 1 * * * (m/h/d/dM/MY)")

        schedule, _ = CrontabSchedule.objects.get_or_create(minute='52',
                                                            hour='1',
                                                            day_of_week='*',
                                                            day_of_month='*',
                                                            month_of_year='*',
                                                            )
        schedule_added = add_10_min(schedule)
        self.assertEqual(str(schedule_added), "2 2 * * * (m/h/d/dM/MY)")

        schedule, _ = CrontabSchedule.objects.get_or_create(minute='52',
                                                            hour='23',
                                                            day_of_week='*',
                                                            day_of_month='*',
                                                            month_of_year='*',
                                                            )
        schedule_added = add_10_min(schedule)
        self.assertEqual(str(schedule_added), "52 23 * * * (m/h/d/dM/MY)")

        schedule, _ = CrontabSchedule.objects.get_or_create(minute='52',
                                                            hour='*/1',
                                                            day_of_week='*',
                                                            day_of_month='*',
                                                            month_of_year='*',
                                                            )
        schedule_added = add_10_min(schedule)
        self.assertEqual(str(schedule_added), "2 */2 * * * (m/h/d/dM/MY)")

        schedule, _ = CrontabSchedule.objects.get_or_create(minute='52',
                                                            hour='*/23',
                                                            day_of_week='*',
                                                            day_of_month='*',
                                                            month_of_year='*',
                                                            )
        schedule_added = add_10_min(schedule)
        self.assertEqual(str(schedule_added), "2 */24 * * * (m/h/d/dM/MY)")

        schedule, _ = CrontabSchedule.objects.get_or_create(minute='52',
                                                            hour='*/23-',
                                                            day_of_week='*',
                                                            day_of_month='*',
                                                            month_of_year='*',
                                                            )
        schedule_added = add_10_min(schedule)
        self.assertEqual(str(schedule_added), "52 */23- * * * (m/h/d/dM/MY)")

    def test_add_1_hour(self):
        self.schedule, _ = CrontabSchedule.objects.get_or_create(minute='2',
                                                                 hour='2',
                                                                 day_of_week='*',
                                                                 day_of_month='*',
                                                                 month_of_year='*',
                                                                 )
        self.schedule.save()
        schedule_added = add_1_hour(self.schedule)
        self.assertEqual(str(schedule_added), "2 3 * * * (m/h/d/dM/MY)")

        self.schedule, _ = CrontabSchedule.objects.get_or_create(minute='2',
                                                                 hour='23',
                                                                 day_of_week='*',
                                                                 day_of_month='*',
                                                                 month_of_year='*',
                                                                 )
        self.schedule.save()
        schedule_added = add_1_hour(self.schedule)
        self.assertEqual(str(schedule_added), "2 23 * * * (m/h/d/dM/MY)")

        self.schedule, _ = CrontabSchedule.objects.get_or_create(minute='2',
                                                                 hour='23',
                                                                 day_of_week='1',
                                                                 day_of_month='*',
                                                                 month_of_year='*',
                                                                 )
        self.schedule.save()
        schedule_added = add_1_hour(self.schedule)
        self.assertEqual(str(schedule_added), "2 0 2 * * (m/h/d/dM/MY)")

        self.schedule, _ = CrontabSchedule.objects.get_or_create(minute='2',
                                                                 hour='23',
                                                                 day_of_week='6',
                                                                 day_of_month='*',
                                                                 month_of_year='*',
                                                                 )
        self.schedule.save()
        schedule_added = add_1_hour(self.schedule)
        self.assertEqual(str(schedule_added), "2 0 0 * * (m/h/d/dM/MY)")

        self.schedule, _ = CrontabSchedule.objects.get_or_create(minute='*',
                                                                 hour='23',
                                                                 day_of_week='6',
                                                                 day_of_month='*',
                                                                 month_of_year='*',
                                                                 )
        self.schedule.save()
        schedule_added = add_1_hour(self.schedule)
        self.assertEqual(str(schedule_added), "* 23 6 * * (m/h/d/dM/MY)")

        self.schedule, _ = CrontabSchedule.objects.get_or_create(minute='2',
                                                                 hour='*',
                                                                 day_of_week='6',
                                                                 day_of_month='*',
                                                                 month_of_year='*',
                                                                 )
        self.schedule.save()
        schedule_added = add_1_hour(self.schedule)
        self.assertEqual(str(schedule_added), "2 * 6 * * (m/h/d/dM/MY)")
