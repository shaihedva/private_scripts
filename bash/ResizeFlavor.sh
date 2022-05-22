#!/bin/bash

#Load Openrc

# give me your cloud name
echo "give me your cloud name:" 
read CLOUD_NAME   
echo "give me your Tennat name:" 
read TENANT_NAME

#Download Openrc from Nexsus3
echo "wget http://nexus3-prod.radcom.co.il:8081/repository/radcom-files/openrc/${CLOUD_NAME}/${CLOUD_NAME}-${TENANT_NAME}-openrc -O temp.openrc.txt"
wget "http://nexus3-prod.radcom.co.il:8081/repository/radcom-files/openrc/${CLOUD_NAME}/${CLOUD_NAME}-${TENANT_NAME}-openrc" -O temp.openrc.txt


# Loading Openrc :

for i in `cat temp.openrc.txt | grep -v PS1 |  awk '{print $2}'`;do export "$i";done






### Openstack Commands

echo "enter your server id: "
read server_id

echo "enter your flavor id:"
read flavor_id 


echo "This is your server id: $server_id"
echo "This is your flavor id $flavor_id"

echo resize your server for new flavor

echo step 1  
openstack server resize --flavor $flavor_id $server_id

echo step 2 
openstack server resize --confirm $server_id

echo restart your vm: 
nova reboot $server_id
