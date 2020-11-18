Requirements
=
1. [AWS cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)
2. [AWS sam](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)
3. [Python 3](https://www.python.org/)
4. `pip install -r requirements.txt`
5. [AWS account](https://aws.amazon.com/)

Configure
=
1. Log in to AWS account
2. [Create API keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey)
3. On your local machine, execute
    ```shell script
    aws configure
    ```
   Follow the prompt, fill details about your api keys and region
4. Create an S3 bucket to store Stacks info
   ```shell script
    aws s3api create-bucket --bucket <put the bucket name here> --create-bucket-configuration LocationConstraint=<put aws region descriptor here> --acl private
   ```
   Note, `bucket name` should be unique across the entire AWS
5. Run
   ```shell script
   ./update_stack.py \
     --s3-bucket <value> \
     --sign-key <value> \
     --primary-url <value> \
     --primary-trust <value> \
     --node-identifier <value> \
     --account-number <value> \
     --default-transaction-fee <value> \
     --root-account-file <value> \
     --version-number <value>
   ```
   Refer to `./update_stack.py --help` about values
6. In the end you will see something like
   ```shell script

   Key                 EC2InstanceIpAddress
   Description         Server Public IP
   Value               <ip address>

   ```
   Put the http://<ip address>/config to your browser, in a while (on avg in 3-5 minutes) you should a correct response
