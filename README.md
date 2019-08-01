# firewall-script
Quickly manage ip rules of AWS Security Group associated with Elastic Beanstalk Environments.
This script helps you quickly add an ip security rule into your Network Security Group, allowing traffic between your computer and the server(or database) during the development process.

Change the following path to the python3 binary file on your computer:<br>
`#!/usr/local/homebrew/bin/python3`

Add the name and ID of your existing security group:<br>
`SECURITY_GROUP_ID = 'your-security-group-id'`<br>
`SECURITY_GROUP_NAME = 'your-security-group-name'`

Add the region of your security group:<br>
`SECURITY_GROUP_REGION = 'AWS-region'` 

-----------------------------------------------------------------------
# Usage

`$ ./firewall-script`<br>
Add an ip rule for your current public IP address.<br>

`$ ./firewall-script delete`<br>
Delete all rules with an ip address associated.<br>

-----------------------------------------------------------------------
# Requirements

- boto3
- awscli
- python3
