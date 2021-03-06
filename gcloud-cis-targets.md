### GCloud CIS metrics (AWS equivalents) - checking
===============================================
##### Metric 1.12 Ensure no root account access key exists.
```
gcp: check service accounts has owner role
```
##### Metric 2.1: Ensure CloudTrail is enabled in all regions.
```
gcp: check cloud audit logging enabled
```
##### Metric 2.8: Ensure rotation for customer created CMKs is enabled.
```
gcp: check keys rotation is enabled and less than 180 days
```

##### Metric 4.1: Ensure no security groups allow ingress from 0.../0 to port 22.
```
gcp: check vpc firewall setting no rule allow ingress from 0.../0 to port 22.
```
##### Metric 4.2: Ensure no security groups allow ingress from 0.../0 to port 3389.
```
gcp: check vpc firewall setting no rule allow ingress from 0.../0 to port 3389.
```
##### Metric 4.3: Ensure VPC flow logging is enabled in all VPCs.
```
gcp: check fire setting flow logging is enabled for all subnet
```
##### Metric 4.5: Ensure routing tables for VPC peering are least access.
```
gcp: provide count for peered VPC
```
### GCloud CIS metrics (AWS equivalents) - alerting & enforcing
==================================================
##### Metric 3.1: Ensure log metric filter exists for unauthorized api calls.
```
gcp: smx-gcloud-cis can create log metric for unauthorized api calls
```
##### Metric 3.4: Ensure a log metric filter and alarm exist for IAM changes.
```
gcp: smx-gcloud-cis can create log metric and alarm exist for IAM changes
```
##### Metric 3.7: Ensure a log metric filter and alarm exist for disabling or scheduling deletion of KMS CMK.
```
gcp: smx-gcloud-cis can create log metric and alarm for disabling or deletion of KMS
```
##### Metric 3.8: Ensure a log metric filter and alarm exist for GS bucket policy changes.
```
gcp: smx-gcloud-cis can create log metric and alarm for GS bucket policy changes.
gcp: smx-gcloud-cis can enforce tagged GS bucket policy to be immutable 
```
##### Metric 3.10: Ensure a log metric filter and alarm exist for security group changes.
##### Metric 3.11: Ensure a log metric filter and alarm exist for changes to Network Access Control Lists (NACL).
```
gcp: smx-gcloud-cis can create log metric and alarm for firewall rule changes.
```
##### Metric 3.12: Ensure a log metric filter and alarm exist for changes to network gateways.
##### Metric 3.13: Ensure a log metric filter and alarm exist for route table changes.
```
gcp: smx-gcloud-cis can create log metric and alarm for route and VPC peer changes.
```
##### Metric 3.14: Ensure a log metric filter and alarm exist for VPC changes.
```
gcp: smx-gcloud-cis can create log metric and alarm for VPC changes.
```
