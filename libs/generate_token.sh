#!/bin/bash

#
# Q. What is the debug token exactly ?
#
# Answer: The APIC system generates a 12-byte challenge. This challenge token from the field
#         is submitted to Cisco TAC to obtain a 'debug token'. The product has an RSA 512
#         public key embedded in it. The Private key corresponding to the public key never
#         leaves Cisco servers - we generate a RSA-512 + SHA1 signature of the Challenge token
#         which can then be used to login as root only on the APIC system on which the challenge 
#         was generated. Also, the challenge on the APIC system expires in 10 mins, so this
#         debug token is invalid and is unusable after 10 mins from the time the challenge was
#         generated.

set -e
echo $1 > challenge.raw
# Write the command line argument to a file and then copy exactly 12 bytes
# using dd to the openssl digest generation file - all other tools (other than dd)
# seem to randomly insert new line characters etc which throw off the SHA1 digest
dd if=challenge.raw of=challenge.txt bs=1 count=12 > /dev/null 2>&1
openssl dgst -sha1 -sign ./private.key -out token.bin challenge.txt
# Convert the digest into Base64 (should be exactly 88 bytes)
openssl base64 -e -in token.bin > response
# Why this way ? Because openssl base64 decides to output the 88 bytes in two separate lines!
read a b <<< `cat response`
# Combine the two lines back into a contiguous 88 bytes of Base64 'debug token'.
echo $a$b
exit 0


