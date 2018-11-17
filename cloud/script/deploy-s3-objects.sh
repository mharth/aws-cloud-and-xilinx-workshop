#! /bin/bash

prefix=$1
if test -z "${prefix}"; then
  echo you need to provide a bucket prefix as first argument.
fi

bitstream=/usr/local/lib/python3.6/dist-packages/pydeephi/boards/Ultra96/gstreamer_deephi.bit
bucket_name=${prefix}-s3
local_path=/home/xilinx/${bucket_name}
bucket_policy_location=./bucket-policy.json
bucket=$(aws s3api create-bucket --output text \
             --bucket "${bucket_name}" \
             --query Location \
             --create-bucket-configuration LocationConstraint=eu-west-1)

my_ip=$(curl ifconfig.co)

cat <<EOF > ${bucket_policy_location}
{
  "Version": "2012-10-17",
  "Id": "S3PolicyId1",
  "Statement": [
    {
      "Sid": "IPAllow",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::${bucket_name}/*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "${my_ip}/32"
        }
      }
    }
  ]
}
EOF

echo Constraining bucket access to this specific device

aws s3api put-bucket-policy --bucket ${bucket_name} --policy file://${bucket_policy_location}


echo Upload a bitstream to S3 bucket
mkdir -p ${local_path}
cp -f ${bitstream} ${local_path}
$aws s3 sync ${local_path} s3://${bucket_name}/ --acl public-read