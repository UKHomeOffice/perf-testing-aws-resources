"""Script generating a CloudFormation template to create an S3 bucket destined to hold
performance test reports.

The template also contains IAM resources to control access to the bucket.
"""

from troposphere import Template, Parameter, Ref, Join
from troposphere import iam
from troposphere import s3


class InvalidResourceName(Exception):
    """Exception indicating that a resource name is invalid
    """


class PerfTestingTemplate(Template):
    """Template class generating a CloudFormation template to create an S3 bucket destined to hold
    performance test reports.
    """

    BUCKET_SHORT_NAME = 'performance-tests'

    def __init__(self):
        """Constructor building up the CloudFormation template
        """
        Template.__init__(self)
        self.set_description('Template creating an S3 bucket destined to hold performance test '
                             'reports. The template also contains IAM resources to control access '
                             'to the bucket.')

        self.environmnent_param = self.add_parameter(Parameter(
            'Environment',
            Description='Name of the environment the bucket is for (e.g. a k8s namespace)',
            Type='String',
        ))

        self.prefix_param = self.add_parameter(Parameter(
            'Prefix',
            Description='A prefix to prepend all resource names with',
            Type='String',
            Default='',
        ))

        self.bucket = self.add_s3_bucket()
        self.add_iam_resources()

    def resource_name(self, *names):
        """Gets the fully qualified resource name taking into account the Prefix and Environment
        parameters.

        :param names: a variadic argument (str...) specifying the suffixes to use to describe the
        resource
        :return: the fully qualified name of the resource, prepended with the prefix and environment
        name
        """
        if not names:
            raise InvalidResourceName('Provide at least one name parameter')
        if len(names) == 1:
            name = names[0]
        else:
            name = Join('-', names)
        return Join('', [Ref(self.prefix_param), Ref(self.environmnent_param), '-', name])

    def add_s3_bucket(self):
        """Adds an S3 bucket to the template

        :return: the (s3.Bucket) object that has been added
        """
        bucket = s3.Bucket(
            'Bucket',
            BucketName=self.resource_name(PerfTestingTemplate.BUCKET_SHORT_NAME),
            BucketEncryption=s3.BucketEncryption(
                ServerSideEncryptionConfiguration=[
                    s3.ServerSideEncryptionRule(
                        ServerSideEncryptionByDefault=s3.ServerSideEncryptionByDefault(
                            SSEAlgorithm='AES256',  # alternative is 'aws:kms'
                        )
                    )
                ]
            ),
            VersioningConfiguration=s3.VersioningConfiguration(
                Status='Enabled',
            )
        )
        self.add_resource(bucket)
        return bucket

    def add_iam_resources(self):
        """Adds IAM resources to the template: roles and managed policies for read-only, write-only
        and delete roles

        :return: None
        """
        readonly_policy = self.add_managed_policy(
            title='ReadOnlyPolicy',
            description_verb='reading',
            policy_name_suffix='readonly',
            allowed_actions=[
                "s3:Get*",
                "s3:List*",
            ],
        )
        self.add_role(
            title='ReadOnlyRole',
            role_name_suffix='readonly',
            managed_policy=readonly_policy,
        )

        writeonly_policy = self.add_managed_policy(
            title='WriteOnlyPolicy',
            description_verb='writing',
            policy_name_suffix='writeonly',
            allowed_actions=[
                "s3:PutObject",
                "s3:AbortMultipartUpload",
                "s3:ListMultipartUploadParts",
            ],
        )
        self.add_role(
            title='WriteOnlyRole',
            role_name_suffix='writeonly',
            managed_policy=writeonly_policy,
        )

        delete_policy = self.add_managed_policy(
            title='DeletePolicy',
            description_verb='deleting',
            policy_name_suffix='delete',
            allowed_actions=[
                "s3:Get*",
                "s3:List*",
                "s3:DeleteObject*",
            ],
        )
        self.add_role(
            title='DeleteRole',
            role_name_suffix='delete',
            managed_policy=delete_policy,
        )

    def add_managed_policy(self, title, description_verb, policy_name_suffix, allowed_actions):
        """
        Creates a managed policy (iam.Policy) with the permissions required to interact with the S3
        bucket used for performance testing data.

        :param title: (str) the title of the resource
        :param description_verb: (str) the verb to use in the description, e.g. 'reading'
        :param policy_name_suffix: (str) the suffix to append to the policy name, e.g. 'readonly'
        :param allowed_actions: (str[]) the IAM actions that should be allowed on the bucket or
        its objects
        :return: an iam.ManagedPolicy object
        """
        return self.add_resource(iam.ManagedPolicy(
            title,
            Description=Join(
                ' ',
                [
                    f"Policy allowing {description_verb} objects from the S3 bucket containing "
                    f"performance test data for",
                    Ref(self.prefix_param),
                    Ref(self.environmnent_param),
                ]
            ),
            ManagedPolicyName=self.resource_name(
                f"{PerfTestingTemplate.BUCKET_SHORT_NAME}-bucket-{policy_name_suffix}",
            ),
            PolicyDocument={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": allowed_actions,
                        "Effect": "Allow",
                        "Resource": [
                            Join('', [
                                'arn:aws:s3:::',
                                Ref(self.bucket),
                            ]),
                            Join('', [
                                'arn:aws:s3:::',
                                Ref(self.bucket),
                                '/*',
                            ]),
                        ]
                    },
                ]
            },
        ))

    def add_role(self, title, role_name_suffix, managed_policy):
        """
        Adds a iam.Role associated with the given managed policy to the template.

        :param title: (str) the title of the resource
        :param role_name_suffix: (str) the suffix to append to the role name, e.g. 'readonly'
        :param managed_policy: the managed policy to associate with this role (iam.ManagedPolicy)

        :return: an iam.Role object
        """
        return self.add_resource(iam.Role(
            title,
            RoleName=self.resource_name(
                f"{PerfTestingTemplate.BUCKET_SHORT_NAME}-bucket-{role_name_suffix}",
            ),
            AssumeRolePolicyDocument={
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        # arn:aws:iam::AWS-account-ID:role/role-name
                        "AWS": [
                            Ref("AWS::AccountId"),
                        ]
                    },
                    "Action": ["sts:AssumeRole"]
                }]
            },
            ManagedPolicyArns=[
                Ref(managed_policy)
            ],
        ))

    def get_cf_template(self):
        """Returns the CloudFormation template as a string

        :return: (str) the CloudFormation template
        """
        return self.to_yaml()


if __name__ == "__main__":
    print(PerfTestingTemplate().get_cf_template())
