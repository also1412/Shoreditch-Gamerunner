##########
#### Run the test suite for Shoreditch Gamerunner
##########

import unittest
import os, sys
import argparse

import test

def list_modules(dir, module_path = ''):
	modules = []
	for f in os.listdir(dir):
		module_name, ext = os.path.splitext(f) # Handles no-extension files, etc.
		if os.path.isdir('test/' + module_name):
			modules.extend(list_modules(dir + '/' + module_name, module_path + module_name + '.'))
		elif ext == '.py' and not module_name == '__init__': # Important, ignore .pyc/other files.
			__import__(module_path + module_name)
			modules.append(sys.modules[module_path + module_name])

	return modules

def run_tests(scope = None):
	suite = unittest.TestSuite()

	import test

	modules = []

	if scope:
		suite.addTests(unittest.TestLoader().loadTestsFromName(scope))
	else:
		for module in list_modules(os.path.dirname(test.__file__), 'test.'):
			suite.addTests(unittest.TestLoader().loadTestsFromModule(module))
	
	res = unittest.TextTestRunner(verbosity=2).run(suite)
	return len(res.failures)

parser = argparse.ArgumentParser(description='Test the Settlers of Shoreditch game')
parser.add_argument('--test_scope')
args = parser.parse_args()

if args.test_scope:
	sys.exit(run_tests(args.test_scope))
else:
	sys.exit(run_tests())