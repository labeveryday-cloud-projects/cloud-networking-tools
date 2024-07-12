#!/bin/bash

# This script generates certificates and uploads them to AWS
# Docs: https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/mutual.html

# Set the desired AWS region
AWS_REGION="us-east-2"

# CD into /tmp directory
cd /tmp

# Clone Easy RSA 
git clone https://github.com/OpenVPN/easy-rsa.git 

# CD into the directory
cd easy-rsa/easyrsa3/

# Initialize the PKI (Private Key Infrastructure)
./easyrsa init-pki

# Create the Certificate Authority
./easyrsa build-ca nopass

# Create the Server Certificate
./easyrsa build-server-full demo-aws-client-vpn-test.com nopass

# Create the Client Certificate
./easyrsa build-client-full client.demo-aws-client-vpn-test.com nopass

# Upload the certificates to AWS
aws acm import-certificate --certificate "fileb://pki/issued/demo-aws-client-vpn-test.com.crt" --private-key "fileb://pki/private/demo-aws-client-vpn-test.com.key" --certificate-chain fileb://pki/ca.crt --region "$AWS_REGION"                                                                