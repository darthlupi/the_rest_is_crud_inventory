#!/usr/bin/python
import ansible.runner
import ansible.inventory
import json 
import sys
import getopt
import socket
try:
    import requests
    #requests.packages.urllib3.disable_warnings()
except ImportError:
    print "Please install the python-requests module."
    sys.exit(-1)

class simplest_json:
    def __init__(self,username,password,url):
        self.username = username
        self.password = password
        self.url = url
        self.ssl_verify = False

    def get_json(self,api_url):
        try:
            #Performs a GET using the passed URL api_url
            api_url = self.url + api_url
            result = requests.get(
                api_url, 
                auth=(self.username, 
                self.password), 
                verify=self.ssl_verify)
        except Exception, e:
            print repr(e)
            sys.exit()
        return result.json()

    def post_json(self,api_url, json_data):
        try:
            api_url = self.url + api_url
            post_headers = {'content-type': 'application/json'}
            result = requests.post(
                api_url,
                data=json_data,
                auth=(self.username, self.password),
                verify=self.ssl_verify,
                headers=post_headers)
        except Exception, e:
            print repr(e)
            sys.exit()
        return result.json()

    def put_json(self,api_url, json_data):
        try:
            #Performs a POST and passes the data to the URL api_url
            api_url = self.url + api_url
            post_headers = {'content-type': 'application/json'}
            result = requests.put(
                api_url,
                data=json_data,
                auth=(self.username, self.password),
                verify=self.ssl_verify,
                headers=post_headers)
        except Exception, e:
            print repr(e)
            sys.exit()
        return result.json()

def create_or_update(sj,hostname,dump_data):
  #Check to see if the host exists:
  update_check = sj.get_json("servers?transform=1&filter=hostname,eq,"+hostname)
  #Do a put to update table or a post to create new rows.
  if update_check['servers']:
    server_id = update_check['servers'][0]['id']
    #Put the data
    sj.put_json('servers/' + server_id,dump_data)
  else:
    #Post the data
    sj.post_json('servers',dump_data)

def ansible_fact_update(sj,host_data,host_list,thread_count):
  #Load inventory from file
  #I need to exception handling in case of the myriad of file issues possible here :)
  #ans_inventory=ansible.inventory.Inventory('/home/rlupinek/scripts/python/test.inv')
  #Inventory could be a file or a list.
  ans_inventory=ansible.inventory.Inventory( host_list )
  # construct the ansible runner and execute on all hosts
  results = ansible.runner.Runner(
    pattern='all', forks=thread_count,
    module_name='setup', module_args='filter="*"',
    inventory=ans_inventory
  ).run()

  #Check to make sure there are some results
  if results is None:
    print "No hosts found"
    sys.exit(1)

  print "UP ***********"
  #Loop through the results
  for (hostname, result) in results['contacted'].items():
    #If everything was successful update or
    if not 'failed' in result:
      #Gather server facts
      facts = results['contacted'][hostname]['ansible_facts']
      #Format fact data for host_data dictionary.
      hostname = hostname
	  
	  
	  #Determine location based on subnet
	  """
      if 'address' in facts['ansible_default_ipv4']:
        ip = facts['ansible_default_ipv4']['address']
      else:
        ip = get_ip(hostname) 
      ip_split = ip.split('.')
      if ip_split[1] == '120':
        location = "This"
      else:
        location = "That"
      """
	  #os = facts['facter_os']['name'] + facts['facter_os']['release']['full']
      os = facts['ansible_distribution'] + " "+ facts['ansible_distribution_version']
      manufacturer = facts['ansible_product_name']
      print "%s , %s , %s, %s" % (hostname, ip, location, os)
      #Populate the dictionary to use to update or create the host.
      host_data = {'hostname':hostname,
                   'primary_ip':ip,
                   'os_version':os,
                   'location':location,
                   'manufacturer':manufacturer,
                   'status':'Available' }
        
      dump_data = json.dumps(host_data)
      #Uncomment if you want to see the dictionary for all returned anisble facts
      #print facts
      #Create or update the record for the host
      create_or_update(sj,hostname,dump_data)
    else:
      #System failed for some reason...
      #Print failure message.
      print "%s >>> %s" % (hostname, result['msg'])
      host_data = {'hostname':hostname,
                   'status':'Connected with Errors' }
      dump_data = json.dumps(host_data)
      #Create or update the record for the host
      create_or_update(sj,hostname,dump_data)

  print "DOWN *********"
  for (hostname, result) in results['dark'].items():
    print "%s >>> %s" % (hostname, result)
    host_data = {'hostname':hostname,
                 'status':'Unreachable' }
    dump_data = json.dumps(host_data)
    #Create or update the record for the host
    create_or_update(sj,hostname,dump_data)

def ip_location(ip):
  ip_split = ip.split('.')
  if is_it_ip(ip):
    #If the second octet is 120 we consider it Lorain.
    if ip_split[1] == '120':
      location = "Lorain"
    else:
      location = "Johns Creek"
  else:
    location = "Location not found."
  return location

def is_it_ip(ip):
  try:
    socket.inet_aton(ip)
    return True
  except socket.error:
    return False

def get_ip(host):
  ip = ''
  error = ''
  try:
    ip = socket.gethostbyname(host)
  except Exception, e:
    error = str(e)
    ip = 'lookup failed'
  return ip


def flat_file_load(sj,infile,columns):
 
  lines = open_file(infile)
  columns_list = columns.split(',')
  host_data = {}
  #loop through the contents of the file...
  for line in lines:
    line = line.rstrip('\n') 
    line = line.rstrip('\r')
    #Create or update the record for the host
    cells = line.split(',')
    cell_count = 0;
    for column_name in columns_list:
      host_data[column_name] = cells[cell_count]
      cell_count +=1
    host_data['primary_ip'] = get_ip(host_data['hostname'])
    host_data['location'] = ip_location( host_data['primary_ip'] ) 
    host_data['hostname'] = host_data['hostname'].lower()
    print host_data
    dump_data = json.dumps(host_data)
    create_or_update(sj,cells[0],dump_data)

def open_file(file):
  try:
    file_object = open(file)
    lines = file_object.readlines(  )
    file_object.close(  )
    return lines
  except Exception, e:
    print str(e)
    sys.exit()


def main():

  url = 'http://my_host/inventory/api/api.php/'
  user = ''
  password = ''
  sj = simplest_json(user,password,url) 

  hostname = ''
  ip = ''
  os = ''
  location = ''
  idrac_ip = ''
  application = ''
  contact = 'es_unix'
  comments = ''
  groups = ''
  status = 'Polling Failed'
  host_data = {'hostname':hostname,
               'primary_ip':ip,
               'os_version':os,
               'location':location,
               'idrac_ip':idrac_ip,
               'application':'application',
               'contact':contact,
               'comments':comments,
               'groups':groups,
               'status':status }
  #Declare parameter variables
  infile = ''
  outfile = ''
  ansible_on = ''
  columns = '' 
  #Setup paramters
  try:
      options, remainder = getopt.getopt(sys.argv[1:], 'o:v', ['ansible_on=',
                                                               'infile=',
                                                               'outfile=',
                                                               'columns=',
                                                                 ])
  except getopt.GetoptError, e:
      print "Error!  Error! " + str(e)
      print input_help
      sys.exit()
  for opt, arg in options:
      if opt in ('--ansible_on'):
          ansible_on = arg
      elif opt in ('--infile'):
          infile = arg
      elif opt in ('--outfile'):
          outfile = arg
      elif opt in ('--columns'):
          columns = arg
 
  if ansible_on == 'y' or ansible_on == 'yes': 
    #Use ansible to update the inventory status and facts.
    #The first entry in the csv must be the hostname at this time for this to work.
    lines = open_file(infile)
    #We create host list that 
    host_list = []
    #How many hosts to process at once
    thread_count = 10;
    #How many entries we have processed in the lines list
    count = 0;
    #loop through the contents of the file...
    for line in lines: 
      line = line.rstrip('\n')
      line = line.rstrip('\r')
      line = line.split(',')
      #Append the first entry in the csv or only entry in the file to the host list to be processed
      host_list.append(line[0])
      #Increment the count variable to indicate which index of the lines list 
      count += 1;
      #If we have  hosts in the host_list = to thread_count OR we have reached the end of the main list
      #then we can run our ansible checks against the hosts.
      if len(host_list) == thread_count or count == len(lines): 
        ansible_fact_update(sj,host_data,host_list,thread_count)
        print "Processing the following hosts: "
        print host_list
        host_list = []
  elif infile:
    flat_file_load(sj,infile,columns)
  elif outfile:
     out_dict = sj.get_json("servers?transform=1")
     for servers_key, servers_value in out_dict.iteritems():
         print servers_value
         for f in servers_value:
              print f
     
  
if __name__ == "__main__":
    main()
