""" python manage.py test rules.tests.test_models """
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from rules.models import DataTypeUpload, MethodUpload, ClassType, Source, RuleSet, Rule


class ClassTypeTest(TestCase):
    fixtures = ['init']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_class_type(self):
        all_class_type = ClassType.get_all()
        class_type = ClassType.get_by_id(1)
        self.assertEqual(len(all_class_type), 34)
        self.assertEqual(class_type.name, "unknown")
        self.assertEqual(str(class_type), "unknown")

        class_type = ClassType.get_by_name("unknown")
        self.assertEqual(class_type.name, "unknown")
        with self.assertLogs('rules.models', level='DEBUG'):
            ClassType.get_by_name("https")

        class_type = ClassType.get_by_id(99)
        self.assertEqual(class_type, None)
        with self.assertRaises(AttributeError):
            class_type.name
        with self.assertLogs('rules.models', level='DEBUG'):
            ClassType.get_by_id(99)
        with self.assertRaises(IntegrityError):
            ClassType.objects.create(name="unknown")


class DataTypeUploadTest(TestCase):
    fixtures = ['init']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_data_type_upload(self):
        all_data_type_upload = DataTypeUpload.get_all()
        data_type_upload = DataTypeUpload.get_by_id(1)
        self.assertEqual(len(all_data_type_upload), 2)
        self.assertEqual(data_type_upload.name, "one file not compressed")
        self.assertEqual(str(data_type_upload), "one file not compressed")

        data_type_upload = DataTypeUpload.get_by_name("one file not compressed")
        self.assertEqual(data_type_upload.name, "one file not compressed")
        with self.assertLogs('rules.models', level='DEBUG'):
            DataTypeUpload.get_by_name("https")

        data_type_upload = DataTypeUpload.get_by_id(99)
        self.assertEqual(data_type_upload, None)
        with self.assertRaises(AttributeError):
            data_type_upload.name
        with self.assertLogs('rules.models', level='DEBUG'):
            DataTypeUpload.get_by_id(99)
        with self.assertRaises(IntegrityError):
            DataTypeUpload.objects.create(name="one file not compressed")


class MethodUploadTest(TestCase):
    fixtures = ['init']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_method_upload(self):
        all_method_upload = MethodUpload.get_all()
        method_upload = MethodUpload.get_by_id(1)
        self.assertEqual(len(all_method_upload), 2)
        self.assertEqual(method_upload.name, "Upload file")
        self.assertEqual(str(method_upload), "Upload file")

        method_upload = MethodUpload.get_by_name("Upload file")
        self.assertEqual(method_upload.name, "Upload file")
        with self.assertLogs('rules.models', level='DEBUG'):
            MethodUpload.get_by_name("https")

        method_upload = MethodUpload.get_by_id(99)
        self.assertEqual(method_upload, None)
        with self.assertRaises(AttributeError):
            method_upload.name
        with self.assertLogs('rules.models', level='DEBUG'):
            MethodUpload.get_by_id(99)
        with self.assertRaises(IntegrityError):
            MethodUpload.objects.create(name="Upload file")


class RuleTest(TestCase):
    fixtures = ['init', 'test-rules-rule']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_rule(self):
        self.assertEqual(Rule.get_by_id(1).rev, 0)
        self.assertEqual(Rule.get_by_id(1).reference, "http://www.exemple.com")
        self.assertEqual(Rule.get_by_id(1).rule_full, """test""")
        self.assertTrue(Rule.get_by_id(1).enabled)

        all_rule = Rule.get_all()
        rule = Rule.get_by_id(1)
        self.assertEqual(len(all_rule), 1)
        self.assertEqual(rule.reference, "http://www.exemple.com")
        rule = Rule.get_by_id(99)
        self.assertEqual(rule, None)
        with self.assertRaises(AttributeError):
            rule.reference
        with self.assertLogs('rules.models', level='DEBUG'):
            Rule.get_by_id(99)

        rules = Rule.find("tes")
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].reference, "http://www.exemple.com")


class RuleSetTest(TestCase):
    fixtures = ['init', 'test-rules-ruleset']

    @classmethod
    def setUpTestData(cls):
        cls.date_now = timezone.now()

    def test_ruleset(self):
        self.assertEqual(RuleSet.get_by_id(1).name, "ruleset1")
        all_ruleset = RuleSet.get_all()
        ruleset = RuleSet.get_by_id(1)
        self.assertEqual(len(all_ruleset), 1)
        self.assertEqual(ruleset.name, "ruleset1")
        self.assertEqual(str(ruleset), "ruleset1")
        ruleset = RuleSet.get_by_id(99)
        self.assertEqual(ruleset, None)
        with self.assertRaises(AttributeError):
            ruleset.name
        with self.assertLogs('rules.models', level='DEBUG'):
            RuleSet.get_by_id(99)
        with self.assertRaises(IntegrityError):
            RuleSet.objects.create(name="ruleset1",
                                   description="",
                                   created_date=self.date_now
                                   )


class SourceTest(TestCase):
    fixtures = ['init', 'crontab', 'test-rules-source']

    @classmethod
    def setUpTestData(cls):
        pass

    def test_source(self):
        all_source = Source.get_all()
        source = Source.get_by_id(1)
        self.assertEqual(len(all_source), 1)
        self.assertEqual(source.method.name, "URL HTTP")
        self.assertEqual(source.data_type.name, "one file not compressed")
        self.assertEqual(source.uri, "https://sslbl.abuse.ch/blacklist/sslblacklist.rules")
        self.assertEqual(str(source), "https://sslbl.abuse.ch/blacklist/sslblacklist.rules")
        source = Source.get_by_uri("https://sslbl.abuse.ch/blacklist/sslblacklist.rules")
        self.assertEqual(source.data_type.name, "one file not compressed")

        with self.assertLogs('rules.models', level='DEBUG'):
            Source.get_by_uri("https://sslbl.abuse.ch/lacklist.rules")
        source = Source.get_by_id(99)
        self.assertEqual(source, None)
        with self.assertRaises(AttributeError):
            source.uri
        with self.assertLogs('rules.models', level='DEBUG'):
            Source.get_by_id(99)
        with self.assertRaises(IntegrityError):
            Source.objects.create(method=MethodUpload.get_by_id(1),
                                  uri="https://sslbl.abuse.ch/blacklist/sslblacklist.rules",
                                  data_type=DataTypeUpload.get_by_id(1),
                                  )
