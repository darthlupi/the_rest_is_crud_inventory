#!/usr/bin/python

import ansible.runner
import ansible.inventory
import sys

#Load inventory from file
#I need to exception handling in case of the myriad of file issues possible here :)
#ans_inventory=ansible.inventory.Inventory('/home/rlupinek/scripts/python/test.inv')
ans_inventory=ansible.inventory.Inventory( sys.argv[1] )

# construct the ansible runner and execute on all hosts
results = ansible.runner.Runner(
  pattern='all', forks=10,
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
  #If the key failed doesn't exist then start collecting the facts :) 
  if not 'failed' in result:
    facts = results['contacted'][hostname]['ansible_facts']
    print "%s >>> %s" % (hostname, "Contacted")
    hostname = hostname
    ip = facts['ansible_default_ipv4']['address']
    ip_split = ip.split('.')
    if ip_split[1] == '120':
      location = "Lorain" 
    else:
      location = "Johns Creek"
    os = facts['facter_os']['name'] + facts['facter_os']['release']['full']
    print "%s , %s , %s, %s" % (hostname, ip, location, os)
    #Uncomment if you want to see the dictionary for all returned anisble facts
    #print facts
  else:
    print "Failed to contact host: " + hostname

print "FAILED *******"
for (hostname, result) in results['contacted'].items():
  if 'failed' in result:
    print "%s >>> %s" % (hostname, result['msg'])

print "DOWN *********"
for (hostname, result) in results['dark'].items():
  print "%s >>> %s" % (hostname, result)

