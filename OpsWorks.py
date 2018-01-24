#!/usr/bin/env python
import boto3
import datetime
import time
import sys
from time import mktime
from boto.ec2 import connect_to_region
from datetime import datetime, timedelta

ec2 = boto3.resource('ec2')

instance_iterator = ec2.instances.all()
for instance in instance_iterator:
    instance_name = "unnamed"
    for tag in instance.tags:
         if tag['Key'] == "Name":
             instance_name = tag['Value']
    if instance.state["Name"] == "stopped" :
         print ("The following EC2 instance(s) is found stopped", "Name:",  instance_name, "ID:",  instance.id)
         stop_instance_id = instance.id 
         current_datetime = datetime.datetime.now()
         full_date_stamp = current_datetime.strftime("%Y-%m-%d-%Hh%M-%S")

         # descriptive tag based on the EC2 name along with the current date.
         bak_ami_name = full_date_stamp + instance_name + "_bak"

         # Creation of the AMI
         bak_ami_id = instance.create_image(
         Name=bak_ami_name, 
         NoReboot=True, 
         DryRun=False, 
         Description='DevOpsTest')

         waiter = client.get_waiter('snapshot_completed')
         print ("AMI of the stopped instance has been created")
         # Remvoe sopeed instance  
         remove_ec2 = instance.terminate(
         InstanceIds = [instance.id],  
         DryRun=False)

         waiter = client.get_waiter('instance_terminated')

         print ("Stopped EC2 instance has been terminated") 

    print ( instance.id, instance_name, instance.state["Name"] )




try:
        days = int(sys.argv[1])
except IndexError:
        days = 7

delete_time = datetime.utcnow() - timedelta(days=days)

filters = {
        'tag-key': 'bak'
}

print 'Deleting any snapshots older than {days} days'.format(days=days)

ec2 = connect_to_region('eu-west-2')

snapshots = ec2.get_all_snapshots(filters=filters)

deletion_counter = 0
size_counter = 0

for snapshot in snapshots:
        start_time = datetime.strptime(
                snapshot.start_time,
                '%Y-%m-%dT%H:%M:%S.000Z'
        )

        if start_time < delete_time:
                print 'Deleting {id}'.format(id=snapshot.id)
                deletion_counter = deletion_counter + 1
                size_counter = size_counter + snapshot.volume_size
                snapshot.delete(dry_run=True)

print 'Deleted {number} snapshots totalling {size} GB'.format(
        number=deletion_counter,
        size=size_counter
)

