#!/bin/bash

#flavor_id=
#servier_id= 

#openstack server resize --flavor 52af0003-3a53-4ef3-a9c1-a8ca36a238b6 76528a48-a42f-427a-90ed-f6cc97c79894
#openstack server resize --confirm 76528a48-a42f-427a-90ed-f6cc97c79894


#echo "username: $1"
#echo "Age: $2"
#echo "Full Name: $3" 

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
