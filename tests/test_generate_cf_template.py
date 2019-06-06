"""Test the CloudFormation template generated to manage the S3 bucket for performance testing
data and associated resources.
"""
from generate_cf_template import PerfTestingTemplate

# pylint: disable=line-too-long
EXPECTED_TEMPLATE = '''Description: Template creating an S3 bucket destined to hold performance test reports.
  The template also contains IAM resources to control access to the bucket.
Parameters:
  Environment:
    Description: Name of the environment the bucket is for (e.g. a k8s namespace)
    Type: String
  Prefix:
    Default: ''
    Description: A prefix to prepend all resource names with
    Type: String
Resources:
  Bucket:
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      BucketName: !Join
        - ''
        - - !Ref 'Prefix'
          - !Ref 'Environment'
          - '-'
          - performance-tests
      VersioningConfiguration:
        Status: Enabled
    Type: AWS::S3::Bucket
  DeletePolicy:
    Properties:
      Description: !Join
        - ' '
        - - Policy allowing deleting objects from the S3 bucket containing performance
            test data for
          - !Ref 'Prefix'
          - !Ref 'Environment'
      ManagedPolicyName: !Join
        - ''
        - - !Ref 'Prefix'
          - !Ref 'Environment'
          - '-'
          - performance-tests-bucket-delete
      PolicyDocument:
        Statement:
          - Action:
              - s3:Get*
              - s3:List*
              - s3:DeleteObject*
            Effect: Allow
            Resource:
              - !Join
                - ''
                - - 'arn:aws:s3:::'
                  - !Ref 'Bucket'
              - !Join
                - ''
                - - 'arn:aws:s3:::'
                  - !Ref 'Bucket'
                  - /*
        Version: '2012-10-17'
    Type: AWS::IAM::ManagedPolicy
  DeleteRole:
    Properties:
      AssumeRolePolicyDocument:
        Statement:
          - Action:
              - sts:AssumeRole
            Effect: Allow
            Principal:
              AWS:
                - !Ref 'AWS::AccountId'
      ManagedPolicyArns:
        - !Ref 'DeletePolicy'
      RoleName: !Join
        - ''
        - - !Ref 'Prefix'
          - !Ref 'Environment'
          - '-'
          - performance-tests-bucket-delete
    Type: AWS::IAM::Role
  ReadOnlyPolicy:
    Properties:
      Description: !Join
        - ' '
        - - Policy allowing reading objects from the S3 bucket containing performance
            test data for
          - !Ref 'Prefix'
          - !Ref 'Environment'
      ManagedPolicyName: !Join
        - ''
        - - !Ref 'Prefix'
          - !Ref 'Environment'
          - '-'
          - performance-tests-bucket-readonly
      PolicyDocument:
        Statement:
          - Action:
              - s3:Get*
              - s3:List*
            Effect: Allow
            Resource:
              - !Join
                - ''
                - - 'arn:aws:s3:::'
                  - !Ref 'Bucket'
              - !Join
                - ''
                - - 'arn:aws:s3:::'
                  - !Ref 'Bucket'
                  - /*
        Version: '2012-10-17'
    Type: AWS::IAM::ManagedPolicy
  ReadOnlyRole:
    Properties:
      AssumeRolePolicyDocument:
        Statement:
          - Action:
              - sts:AssumeRole
            Effect: Allow
            Principal:
              AWS:
                - !Ref 'AWS::AccountId'
      ManagedPolicyArns:
        - !Ref 'ReadOnlyPolicy'
      RoleName: !Join
        - ''
        - - !Ref 'Prefix'
          - !Ref 'Environment'
          - '-'
          - performance-tests-bucket-readonly
    Type: AWS::IAM::Role
  WriteOnlyPolicy:
    Properties:
      Description: !Join
        - ' '
        - - Policy allowing writing objects from the S3 bucket containing performance
            test data for
          - !Ref 'Prefix'
          - !Ref 'Environment'
      ManagedPolicyName: !Join
        - ''
        - - !Ref 'Prefix'
          - !Ref 'Environment'
          - '-'
          - performance-tests-bucket-writeonly
      PolicyDocument:
        Statement:
          - Action:
              - s3:PutObject
              - s3:AbortMultipartUpload
              - s3:ListMultipartUploadParts
            Effect: Allow
            Resource:
              - !Join
                - ''
                - - 'arn:aws:s3:::'
                  - !Ref 'Bucket'
              - !Join
                - ''
                - - 'arn:aws:s3:::'
                  - !Ref 'Bucket'
                  - /*
        Version: '2012-10-17'
    Type: AWS::IAM::ManagedPolicy
  WriteOnlyRole:
    Properties:
      AssumeRolePolicyDocument:
        Statement:
          - Action:
              - sts:AssumeRole
            Effect: Allow
            Principal:
              AWS:
                - !Ref 'AWS::AccountId'
      ManagedPolicyArns:
        - !Ref 'WriteOnlyPolicy'
      RoleName: !Join
        - ''
        - - !Ref 'Prefix'
          - !Ref 'Environment'
          - '-'
          - performance-tests-bucket-writeonly
    Type: AWS::IAM::Role
'''
# pylint: enable=line-too-long


def test_perftestingtemplate_get_cf_template():
    """Test the CloudFormation template generated by Troposphere to manage the S3 bucket for
    performance testing data and associated resources.

    :return: None
    """
    assert EXPECTED_TEMPLATE == PerfTestingTemplate().get_cf_template()
