
# Aws Serverless Skeleton 

![License](https://img.shields.io/badge/license-MIT-green.svg)
[![Coverage Status](https://coveralls.io/repos/github/alhazmy13/aws-serverless-skeleton/badge.svg?branch=master)](https://coveralls.io/github/alhazmy13/aws-serverless-skeleton?branch=master)
[![Build Status](https://travis-ci.com/alhazmy13/aws-serverless-skeleton.svg?branch=master)](https://travis-ci.com/alhazmy13/aws-serverless-skeleton)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?longCache=true)
![Python Versions](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue.svg)

# Overview

*Aws Serverless Skeleton* is built on top of AWS (Amazon Web Service) using multiple services :

* **API Gateway** 
* **DynamoDB**
* **DynamoDB Streams**
* **S3**
* **Lambda**
* **Cognito**
* **ES (Elasticsearch Service)**
* **CloudFormation**
* **CloudWatch**

*Note*: This project may be edited directly in the browser using the gitpod application which is provides a full blown IDE.

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io#https://github.com/alhazmy13/aws-serverless-skeleton)

## Contents

* [Requirements](#requirements)
* [Installing](#installing)
* [Setup AWS](#setup-aws)
* [Deploy to AWS](#deploy-to-aws)
* [Run it locally](#run-it-locally)
* [Trying the service with Postman](#trying-the-service-with-postman)
* [Configuration](#configuration)
    + [Authorization](#authorization)
        + [Over lambda function](#over_lambda_function)
        + [Over Cognito](#over_cognito)
    + [Cognito](#cognito)
    + [DynamoDB](#dynamodb)
    + [ElasticSearch](#elastic-search)
    + [S3](#s3)
    + [VPC](#vpc)
* [Structure](#structure)
  + [Lambda Function](#lambda-function)
  + [App Service](#app-service)
* [Seeds](#seeds)
* [Testing](#testing)


## Requirements

* `python` (Python 3.x)
* `pip` (python package manager)
* `npm` (node.js package manager)
* `serverless` (serverless Framework ) https://github.com/serverless/serverless

## Installing
in order to start running the *Skeleton* on your AWS account you need to install some requirements before starting with : 

install *python3* is via `brew`:
```
brew install python3
```

install *npm* is via `brew`:
```
brew install node
```

install *serverless* is via `npm`:

```
npm install -g serverless
```

install serverless plugins:

```
cd aws-serverless-skeleton (you have to be in the repo root directory)
npm install
```

## Setup AWS 
You need to configure AWS with your own credentials. You need to install aws cli. In your python3 virtualenv, do:
```
pip3 install awscli
``` 
Then configure it:
```
aws configure
```
you will be asked to provide your AWS Access Key ID, AWS Secret Access Key and region (eu-west-1) and default output format (json).
once you are done, make sure the configuration is working:

```
aws sts get-caller-identity
aws iam list-users --output table
```
if all is well, then you are good to go!

## Deploy to AWS
by simple command from terminal:

```js
npm run deploy-dev
// for prod env 
npm run deploy-prod
```

also you could deploy the function changed , Use this to quickly upload and overwrite your AWS Lambda code on AWS, allowing you to develop faster.

```
sls deploy function -f #function_name# --stage #stage_name#
```

## Run it locally

* first of all you need to install all python and npm requirements:

```
pip3 install -r requirements.txt
npm install
```
* Install dynamodb-local: 

```
npm run dynamo-install
```

* install elasticsearch:

The below command will install elastic search in ~/sources/

```commandline
npm run elasticsearch-install
```

* Start serverless-offline, dynamodb-local and elasticsearch. Make sure above command is executed before this. 

```
npm run start
```

By default you can send your requests to ```http://localhost:3000/``` or ```http://localhost:8000/shell``` to access the web shell for dynamodb-local or ```http://localhost:9200``` for elasticsearch.

**Please note that:**

* You'll need to restart the plugin if you modify your serverless.yml or any of the default  template files.
* The event object passed to your λs has one extra key: { isOffline: true }. Also, process.env.IS_OFFLINE is true.
* Seed config for dynamodb-local is enabled, that's mean each table will be seeded automatically on startup from JSON files. You can start the server with fresh table by this command: ``` npm run dynamo-start ```

## Trying the service with Postman: 
To install Postman, go to the apps page and click Download for Mac / Windows / Linux depending on your platform.
[Download](https://www.getpostman.com/docs/postman/launching_postman/installation_and_updates)

after downloading *Postman* you need to add the collection of endpoint of the services to be called from [collections](https://www.getpostman.com/collections/c53ce0788ad98e7b1033)

1. from import button, choose import from url and paste the url above. 
2. right click on the collection "posts", choose edit, and then choose variables tab.
3. add key = BASE_URL and value is either: *YOUR_BASE_URL* or [local](http://localhost:3000/)
4. to run any of the requests, just select it and hit run ( to test, choose post and then "get all posts" )

 
## Configuration

You will find a folder `config` that have a separate file for each environment (`dev`, `prod` and `local`) each file has 
* `environment` for environment values like DynamoDB table names or elastic search endpoint.
* `custom` to modify and update the resource configuration, for example from `custom` you can change the elastic search instance type.
* `functions` for a list of lambda function to deploy in environment.
* `authorizer` For more information please [read this section](#authorization)  

`resourse` folder that contains a bunch of files to deploy the required resources in the `CloudFormation` stack, you can enable or disable any resource from `serverless.yml` file.    

### Authorizer

#### Over lambda function

We have a dummy function `AuthorizerService` to authorize the request, you can update it with any authorizer you like.
 
For this approach, you need to append below code in your env (`dev-env.yml` or `prod-env.yml`) file.

```yaml
authorizer:
  name: auth_authorizer
  resultTtlInSeconds: 0
  type: token
```

#### Over Cognito

Please read more about this in [Cognito Section](#cognito)


### Cognito

In this skeleton, I'm counting on Cognito with Authorization and Authentication process, and there are two methods to apply cognito.

#### First approach

I prefer to separate cognito in a different stack or do it manually and then append `Pool ARN` to your environment, if you are following this approach then you need to update `POOL_ARN` value in your env file (`dev-env.yml` or `prod-env.yml`) with your user pool ARN like so:

```yaml
environment:
  POOL_ARN: 'arn:aws:cognito-idp:{REGION}:{ACCOUNT_NUMBER}:userpool/{REGION}_{USER_POOL_ID}'

```  

And in your env file just change the `authorizer` to :

```yaml
authorizer:
  name: authorizer
  arn: ${self:provider.environment.POOL_ARN}

```

And after deploying the stack, just go to your user pool and enable `PostConfirmation` trigger with `auth_post` function. 



#### Second approach

You can deploy the user pool resource by appending `${file(config/resource/cognito.yml)}` under `resources` in `serverless.yml` file.

```yaml
resources:
  - ${file(config/resource/cognito.yml)}
```

After that go to your environment file and update `POOL_ARN` value with:

```yaml
environment:
  POOL_ARN:
    Fn::GetAtt: CognitoUserPool.Arn
```  

Last step, Go to `lambda_functions/aut/functions.yml` and change:

```yaml
auth_post:
  handler: lambda_functions/auth/auth.post_auth
```

To:

```yaml
auth_post:
  handler: lambda_functions/auth/auth.post_auth
  events:
    - cognitoUserPool:
        pool:
          Ref: CognitoUserPool
        trigger: PostConfirmation
 ```

And in your env file just change the `authorizer` to :

```yaml
authorizer:
  type: COGNITO_USER_POOLS
  authorizerId:
    Ref: ApiGatewayAuthorizer
```

### DynamoDB

Working on it. 

### Elastic Search

Working on it. 

### S3

Working on it.  

### VPC

We assume that you already you have a VPC with in your AWS region, so there's no recourse to deploy a VPC with in the same stack however to deploy the lambda functions into a non-default VPC you need to update three values in (`dev-env.yml` or `prod-env.yml`) file.

```yaml
environment:
  VPC_SECURITY_GROUP: "VPC_SECURITY_GROUP"
  VPC_SUBNET_PUBLIC_1: "VPC_SUBNET_PUBLIC_1"
  VPC_SUBNET_PUBLIC_2: "VPC_SUBNET_PUBLIC_2"
```

**NOTE** to deploy the lambda functions with default VPC just remove `vpc` value from `serverless.yml` file.

```yaml
provider:
  vpc:
      securityGroupIds:
        - ${self:provider.environment.VPC_SECURITY_GROUP}
      subnetIds:
        - ${self:provider.environment.VPC_SUBNET_PUBLIC_1}
        - ${self:provider.environment.VPC_SUBNET_PUBLIC_2}
```  

## Structure

In this skeleton, you will find that we separate the lambda function handler from the business logic itself, for too many reasons.

### Lambda Function

It contains a list of folders, each folder for only one route and each folder contains only two files.

* `route_name.py` with a list of lambda function handler that returns the service response.
* `functions.yml` with a list of lambda function recourse name and the configuration for each function, for example `events` type, `http` method or the `path` for the route.   

### App Service

This folder (`src`) contains all our business logic
* `app package` has a list of packages, each package has the name for the route with a list of services that represent our `CRUD` and `model` class
* `common` contains a list of helper classes.

## Seeds

we inject some seed data into our tables with local env, this helped us with test our application, to change the data just update any `json` file from `seed` folder.


## Testing

The project contains a set of unit and integration tests but before all make sure you follow this [instruction](#installing) before run test commands.

You need to install `tox` tool:

```
pip install -r requirements-dev.txt
```

Make sure all the services are ruining on your device:

```
npm run start
```

To install dev requirements and test this project against Python3.6, just type: 
 
```
tox
```