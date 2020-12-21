#!"C:\Python38\python.exe"
### input.py contains basic read and write functions to work with input.json ###
### input.json contains stkoyee records containing name, closeDates and id of the stkoyees ###
import sys, datetime
import json 




### read_input_json function reads from input.json and return the json object ###
def read_input_json(file_nm):
	with open(file_nm, 'r') as input:
	
		obj = json.load(input)
		
		return obj



### read_input_stkoyees function reads from json object and return the top-level stkoyee record json object ###
def read_input_stocks(obj):
	return obj['stockData'][0]


### read_input_name function reads from json object and return the a particular index position of stkoyee record name json object ###
def read_input_name(objStk, stkIdx):
	return objStk['StockRecord'][stkIdx]['name']


### read_input_symbol function reads from json object and return the a particular index position of stkoyee record id json object ###
def read_input_symbol(objStk, stkIdx):
	return objStk['StockRecord'][stkIdx]['symbol']


### read_input_closeDates function reads from json object and return the particular index position of stkoyee record closeDates json object ###
def read_input_closeDates(objStk, stkIdx):
	return objStk['StockRecord'][stkIdx]['closeDates']
	

### write_output_closeDates_txt function writes closeDates from json object into a text file ###
def write_output_closeDates_txt(obj):	
	with open('output_closeDates.txt', 'w') as output:
		objStk = obj['stockData'][0]['StockRecord'][0]
		output.write(objStk['name'] + "'s Close Dates:\n")
	
		for hobby in objStk['closeDates']:
			output.write(hobby + "\n")
				

### write_output_id_txt function writes id from json object into a text file ###
def write_output_id_txt(obj):	
	with open('output_id.txt', 'w') as output:
		objStk = obj['stockData'][0]['StockRecord'][0]
		output.write(objStk['name'] + "'s Id:\n")

		output.write(objStk['symbol'] + "\n")

		

### write_output_closeDates_selected function writes closeDates from list object into a text file ###
def read_input_closeDates_selected(name):	
	stk_closeDates = read_input_json(name + ".json")
	closeDates = []
	closeDates_json = stk_closeDates['selectedNameCloseDates']['to_closeDates']
	# for hobby in closeDates_json:
		# if 'hobbyName' in hobby:	
			# closeDates.append(hobby['hobbyName'])	
	return closeDates

### write_output_closeDates_selected function writes closeDates from list object into a text file ###
def write_output_closeDates_selected(name, obj):	
	with open(name +'.json', 'w') as output:
		closeDates_json = json.dumps(obj)

		output.write(closeDates_json)
		

### write_output_json function writes stkoyee from object into a json file ###
def write_output_json(obj, file_nm):	
	with open(file_nm, 'w') as output:
		stk_json = json.dumps(obj)

		output.write(stk_json)
		

### main function is program execution of main functions to read json and write txt files ###
def main(file_nm):
	obj = read_input_json(file_nm)
	write_output_closeDates_txt(obj)
	write_output_id_txt(obj)


## execute main function if run from command line other wise do nothing ##
if __name__ == '__main__':
	main(sys.argv[1])