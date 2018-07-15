** Go to gcloud console

*** environment variables
export root_project=smx-gcloud-cis
export command_topic=smx-command
export command_subscription=smx-command-subscription
export log_topic=log-aggregation
export root_report=smx-cis-reports
export root_bucket=smx-cis-root

** Pubsub
gcloud pubsub topics create --project $root_project $command_topic
gcloud pubsub subscriptions create --project $root_project --topic $command_topic $command_subscription

*** Test pubsub

gcloud pubsub topics publish --project $root_project $command_topic --attribute Command=RunScan,ScanType=GCloudStorage,Project=wired-ripsaw-209512

gcloud pubsub topics publish --project $root_project $command_topic --attribute Command=RunScan,ScanType=GCloudCIS,Project=wired-ripsaw-209512

gcloud pubsub subscriptions pull --project $root_project --auto-ack $command_subscription --format="json(message.attributes, message.messageId, message.publishTime)"

#gcloud pubsub subscriptions pull --project $root_project --auto-ack $command_subscription #--format="json(message.attributes, message.data.decode(\"base64\"), message.messageId, #message.publishTime)"


** START INSTANCE

curl -o https://raw.githubusercontent.com/changli3/smx-cis-git/master/vm-config.yaml
gcloud deployment-manager deployments create smx-cis-vm --config vm-config.yaml

** PUB IP
gcloud compute addresses list
gcloud compute instances add-access-config smx-cis-vm-147603613607 --zone us-east4-c --address=35.199.60.27 

** SET UP
gcloud compute ssh smx-cis-vm-147603613607 --zone us-east4-c
sudo su ubuntu -
git clone https://github.com/changli3/smx-cis-git
cd smx-cis-git/
cat install.sh | sh

** SSH with putty

gcloud config list (find the role the computer is using, then all the projects need to 
provide auth, this is in the vm.yaml)
cd smx-cis-git/


./gsPubsub

** SET UP Crontab
crontab -e
*/3 * * * * /home/ubuntu/smx-cis-git/gsPubsub
