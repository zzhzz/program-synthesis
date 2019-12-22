#!/usr/bin/python  
import os,os.path,time,datetime,signal,platform,subprocess
import pprint
import sexp
import translator
import sys
import traceback

programdir = '../' 
testroot = '../'
hiddentests = testroot + 'hidden_tests/'
opentests = testroot + 'open_tests/'

class TimeoutError(Exception):  
	pass  
  
def stripComments(bmFile):
    noComments = '('
    for line in bmFile:
        line = line.split(';', 1)[0]
        noComments += line
    return noComments + ')'

def run_command(cmd, timeout=60):  
	is_linux = platform.system() == 'Linux'  
	  
	p = subprocess.Popen(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid if is_linux else None)  
	t_beginning = datetime.datetime.now()
	seconds_passed = 0  
	while True:  
		timepassed = datetime.datetime.now() - t_beginning
		rtimepassed = timepassed.seconds + timepassed.microseconds/1000000.0		
		if p.poll() is not None:  
			break  
		if timeout and rtimepassed > timeout:  
			if is_linux:  
				os.killpg(p.pid, signal.SIGTERM)  
			else:  
				p.terminate()  
			raise TimeoutError(cmd, timeout)  
		time.sleep(0.01)  
	return p.stdout.read().decode('UTF-8'),rtimepassed 

def my_test(cmd,outputfile,testname,timeout=300):
	outputfile.write('\t%s:'%(testname))	
	print(cmd)
	try:  
		result,rtime = run_command(cmd, timeout)  
	except TimeoutError:  
		outputfile.write( 'timeout after %i \n' %(timeout) ) 
	else:  		
		print(result)
		benchmarkFile = open(testname, encoding='utf-8')
		bm = stripComments(benchmarkFile)
		bmExpr = sexp.sexp.parseString(bm, parseAll=True).asList()[0] #Parse string to python list
		checker=translator.ReadQuery(bmExpr)
		try:  
			checkresult = checker.check(result)
		except :  
			traceback.print_exc()
			#outputfile.write('Wrong Answer: Invalid check result %s(%f)\n' %(result,rtime))
			outputfile.write('Invalid format\t%f\n' %(rtime))  
		else:  		
			if(checkresult == None):
				outputfile.write('Passed\t%f\n' %(rtime))
			else:
				#outputfile.write('Wrong Answer: get %s(%f)\n' %(result,rtime))
				outputfile.write('Wrong Answer\t%f\n' %(rtime))
		
if __name__ == '__main__':  
	timeout = 300
	testresultfile = sys.argv[1] + '.txt'
	outfile = open(testresultfile,'w')
	programdir = sys.argv[1]
	i = 0
	toexe = programdir+'/main.py '
	cmd = 'python3 '
	i = i + 1
	print(i)
	for testgroup in [opentests]:
		for test in os.listdir(testgroup):
			arg = testgroup + test
			my_test(cmd+toexe+arg,outfile,arg,timeout)

