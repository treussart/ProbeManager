#!/usr/bin/env python
import os
import sys
import argparse
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'probemanager.settings.dev'
import django
from django.conf import settings
from django.test.utils import get_runner


def runtests():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--all", help="run all tests - default action", action="store_true", default=False)
    parser.add_argument("--app", help="run the tests for this app", nargs='+', action='append', dest='app', default=[])
    args = parser.parse_args()
    tests = []
    tests_all = []
    for test in glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/*/tests/test*.py'):
        file = os.path.basename(test)
        dir = os.path.basename(os.path.normpath(os.path.join(os.path.dirname(test), os.pardir)))
        tests_all.append(dir + '.tests.' + str(file.split('.')[0]))

    tests_app = []
    for test in tests_all:
        for app in args.app:
            for ap in app:
                if ap in test:
                    tests_app.append(test)

    if args.all or len(sys.argv) == 1:
        tests = tests_all
    else:
        tests += tests_app

    tests = sorted(tests)
    print("Tests that will be launched : " + str(tests))
    django.setup()
    testrunner = get_runner(settings)
    test_runner = testrunner()
    failures = test_runner.run_tests(tests)
    sys.exit(bool(failures))


if __name__ == "__main__":
    """ By default tests are executed by alphabetical order """
    runtests()
