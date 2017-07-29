
import csv
import numpy

input_file = "directors.csv"

with open(input_file, 'rb') as f:
   reader = csv.reader(f)
   company_list = list(reader)


for company in company_list:

   age = []
   tenure = []

   try:
      age = [float(i) for i in company[4].split("[")[1].split("]")[0].split(",")]

      for x in age:
         print company[0] + ",\"" + company[1] + "\"," + company[6] + ",\"" + company[7] + "\",\"" + company[8] + "\"," + company[10] + "," + str(x)

   except Exception as e:
      print str(e)
      continue

   try:
      tenure = [float(i) for i in company[5].split("[")[1].split("]")[0].split(",")]
      #for x in tenure:
         #print company[0] + ",\"" + company[1] + "\"," + company[6] + ",\"" + company[7] + "\",\"" + company[8] +  "\"," + company[10] + "," + str(x)
   except Exception as e:
      print str(e)

 


