## Go to gcloud console

### environment variables
```
export root_project=smx-gcloud-cis
export command_topic=smx-command
export command_subscription=smx-command-subscription
export log_topic=log-aggregation
export root_report=smx-cis-reports
export root_bucket=smx-cis-root/system
export root_bucket=smx-cis-root/config
```
## Pubsub

```
gcloud pubsub topics create --project $root_project $command_topic
gcloud pubsub subscriptions create --project $root_project --topic $command_topic $command_subscription
```
### Test pubsub

```
gcloud pubsub topics publish --project $root_project $command_topic --attribute Command=RunScan,ScanType=GCloudStorage,Project=wired-ripsaw-209512

gcloud pubsub topics publish --project $root_project $command_topic --attribute Command=RunScan,ScanType=GCloudCIS,Project=wired-ripsaw-209512

gcloud pubsub subscriptions pull --project $root_project --auto-ack $command_subscription --format="json(message.attributes, message.messageId, message.publishTime)"

#gcloud pubsub subscriptions pull --project $root_project --auto-ack $command_subscription #--format="json(message.attributes, message.data.decode(\"base64\"), message.messageId, #message.publishTime)"
```

## Start VM
```
curl -o https://raw.githubusercontent.com/changli3/smx-cis-git/master/vm-config.yaml
gcloud deployment-manager deployments create smx-cis-vm --config vm-config.yaml
```

### Need to set up public IP
```
gcloud compute addresses list
gcloud compute instances add-access-config smx-cis-vm-147603613607 --zone us-east4-c --address=35.199.60.27 
```

### Set up VM

```
gcloud compute ssh smx-cis-vm-147603613607 --zone us-east4-c
sudo su ubuntu -
git clone https://github.com/changli3/smx-cis-git
cd smx-cis-git/
cat install.sh | sh
```

### SSH with putty
```
gcloud config list (find the role the computer is using, then all the projects need to 
provide auth, this is in the vm.yaml)
cd smx-cis-git/

# test it
./gsPubsub
```

### Set up Cron
```
crontab -e
*/2 * * * * /home/ubuntu/smx-cis-git/gsPubsub
*/2 * * * * /home/ubuntu/smx-cis-git/gsAlertPubsub
```

### Set up AWS SNS

```
source ./gsEnvironment 
gcloud kms keys list --location global --keyring smxcis --project $root_project

# gcloud kms keyrings create smxcis --location global  --project $root_project 
# gcloud kms keys create awsseckey --location global --keyring smxcis --purpose encryption --project $root_project

gcloud kms decrypt \
      --key=awsseckey \
      --keyring=smxcis \
      --location=global \
      --ciphertext-file=./aws-config \
      --plaintext-file=~/.aws/config	

# gcloud kms encrypt \
      --key awsseckey \
      --keyring smxcis \
      --location global \
      --plaintext-file ~/.aws/config \
      --ciphertext-file ./aws-config
```

### Prepare Projects to be tracked
create exports in GCP stackdriver logging, with -

```
# name
smx-cis-sink

# destination
# custom
pubsub.googleapis.com/projects/smx-gcloud-cis/topics/cis-alerts

# filter
resource.type="gcs_bucket"
(protoPayload.methodName = "storage.objects.update" OR protoPayload.methodName ="storage.setIamPermissions" OR protoPayload.methodName="storage.buckets.delete" OR protoPayload.methodName="storage.buckets.update")
```


### Test invoke reports

```
#create GS objects scan report
gcloud pubsub topics publish --project smx-gcloud-cis smx-command --attribute Command=RunScan,ScanType=GCloudStorage,Project=wired-ripsaw-209512

# create cis benchmark scan report
gcloud pubsub topics publish --project smx-gcloud-cis smx-command --attribute Command=RunScan,ScanType=GCloudCIS,Project=wired-ripsaw-209512
```
Equivalently, you can use GPC Console -
```
Topic: smx-command
Command: RunScan
ScanType: GCloudCIS
Project: wired-ripsaw-209512
```

### Test bucket monitoring
Create lable:
```
# smx-bucket-watch
# value - reports
# value - remediate
```

