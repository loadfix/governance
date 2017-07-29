#
# Reuters Director List Website Scraper
#
#
# ---------- Start of User Configurable Variables ------------- #
start_at = 0
start_count = 0
debug = True
outfile = "directors." + str(start_at) + ".csv" 
input_file = "companies.csv"
# ---------- End of User Configurable Variables --------------- #

# Imports
import mechanize
import cookielib
from bs4 import BeautifulSoup
import csv
import sys
from datetime import datetime
import signal
import traceback
import numpy

# Catch Control-C
def signal_handler(signal, frame):
   end_time = datetime.now()
   print "\n" + str(count) + " companies processed in " + str(end_time - start_time) + " seconds\n"
   sys.exit(0)

# Set codepage
reload(sys)  
sys.setdefaultencoding('utf8')

# Start timing
start_time = datetime.now()

# Catch Control-C, flush buffer to CSV
signal.signal(signal.SIGINT, signal_handler)

# URLs
base_url = 'https://www.reuters.com/finance/stocks/companyOfficers?symbol='
count = 0
errors = []

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# Want HTTP debug messages?
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)

# User-Agent, not!
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]


# Read company list
with open(input_file, 'rb') as f:
    reader = csv.reader(f)
    company_list = list(reader)


# Now Open / Overwrite a (new/old) CSV file
with open(outfile, 'w') as csvfile:

   fieldnames = [
    'symbol', 'name', 'directors', 'independent', 'ages', 'tenures', 'market_cap', 'sector', 'industry', 'ipo_year','exchange'
   ]
   writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
   writer.writeheader()

   for company in range(1, len(company_list) - 1):


      if start_at > start_count:
         start_count = start_count + 1
         print start_at, start_count
         continue
      

      failure = False      

      if '^' in company_list[company][0] or '.' in company_list[company][0]:
         continue


      suffix = ""
      if company_list[company][8] is "AMEX":
         suffix = ".A"
      if company_list[company][8] is "NYSE":
         suffix = ".N"
      if company_list[company][8] is "NASDAQ":
         suffix = ".O"

      row = {
         'symbol':'', 'name':'', 'directors':'', 'independent':'', 'ages':'', 'tenures':'', 'market_cap':'', 'sector':'', 'industry':'', 'ipo_year':'', 'exchange':''
      }


      # Debug 
      #company_list[company][0] = "HPF"
      #suffix = ".N"
   
      if debug:
         print "=============== Processing company " + company_list[company][0] + " (" + str(count) + ") " + "=================="

      # Get companies one at a time
      r = br.open(base_url + company_list[company][0] + suffix)
      soup = BeautifulSoup(r.read(), 'html.parser')

      try:
         officer_table = soup.find_all('table')[0]
         no_of_rows= len(officer_table.find_all('tr')) - 1
      
         if "Shares Traded" in officer_table.find_all('tr')[0].text:
            if debug:
               print "No officers found, skipping..."
            continue

      except Exception as e:
         if debug:
            print "Error getting directors for " + company_list[company][0]
         continue

      count = count + 1   
      independent_directors = 0 
      all_directors = 0
      director_age = []
      director_tenure = []
         
      for y in range(1, no_of_rows + 1):

         try:
         
            title = officer_table.find_all('tr')[y].find_all('td')[3].text.encode('utf-8').strip()

            if title == "Director" or \
               title.find("Independent Director") is not -1 or \
               title.find("Independent Trustee") is not -1 or \
               title.find("Chairman of the Board") is not -1 or \
               title.find("Member of the Board of Directors") is not -1 or \
               title.find("Chairman of the Supervisory Board") is not -1 or \
               title.find("Member of the Supervisory Board") is not -1 or \
               title.find("Member of the Management Board") is not -1 or \
               title.find("Chairman of the Executive Board") is not -1 or \
               title.find("Chairman of the Management Board") is not -1 or \
               title.endswith(", Director") is True:

               print "Found Director: " + title
               all_directors = all_directors + 1

               # Calculate average director tenure
               if officer_table.find_all('tr')[y].find_all('td')[2].text.encode('utf-8').strip() != "":
                  director_tenure.append(int(officer_table.find_all('tr')[y].find_all('td')[2].text.encode('utf-8').strip()))


               # Calculate average director age
               if officer_table.find_all('tr')[y].find_all('td')[1].text.encode('utf-8').strip() != "":
                  director_age.append(int(officer_table.find_all('tr')[y].find_all('td')[1].text.encode('utf-8').strip()))
	      

               # Number of independent directors
               if title.find(u"Independent Director") != -1 or \
                  title.find("Member of the Supervisory Board") is not -1 or \
                  title.find("Independent Trustee") is not -1 or \
                  title.find("Non-Executive Member of the Board of Directors") is not -1 or \
                  title.find("Independent Chairman of the Board") is not -1:
                  independent_directors = independent_directors + 1

               row['symbol'] = company_list[company][0]
               row['exchange'] = company_list[company][8]
               row['name'] = company_list[company][1]
               row['directors'] = all_directors
               row['independent'] = independent_directors
               row['tenures'] = director_tenure
               row['ages'] = director_age

               if company_list[company][3].startswith("$") and company_list[company][3].endswith("M"):
                  try:
                     row['market_cap'] = float(company_list[company][3].split("$")[1].split("M")[0]) * 1000000
                  except Exception as e:
                     print str(e)

               elif company_list[company][3].startswith("$") and company_list[company][3].endswith("B"):
                  try:
                     row['market_cap'] = float(company_list[company][3].split("$")[1].split("B")[0]) * 1000000000
                  except Exception as e:
                     print str(e)
               else:
                  row['market_cap'] = company_list[company][3]
            
               row['sector'] = company_list[company][5]
               row['industry'] = company_list[company][6]
               row['ipo_year'] = company_list[company][4]

         except Exception as e:
            if debug:
               print "Error parsing company: " + company_list[company][0]
               print "---------- DEBUG ------------"
               print "Error: " + str(e)
               traceback.print_exc()
               print "-----------------------------"
            errors.append(company_list[company][0])
            failure = True
            break

      # Write row
      if failure is not True:
         try:
            writer.writerow(row)
         except Exception as e:
            print str(e)
         
         if  all_directors is 0:
            continue

         if debug:
            print "Company:          " + row['name'] + " (" + row['exchange'] + ")"
            print "No of directors:  " + str(row['directors'])
            print "No of ind         " + str(row['independent'])
            print "Average tenure:   " + str(2017 - numpy.mean(row['tenures']))
            print "Average Age:      " + str(numpy.mean(row['ages']))
            print "Market Cap:       " + str(row['market_cap'])
            print "Director tenures: " + str(director_tenure)
            print "Director ages:    " + str(director_age)
   
   if len(errors) != 0:
      print "The following companies had errors and were not included in the dump file:"
      for z in range(0, len(errors)):
         print errors[z]
