# perf-testing-aws-resources

CloudFormation template to create an S3 bucket for storing performance reports

This repo contains a python script generating a CloudFormation template that can be used to create
an S3 bucket for storing performance reports.

An optional `PREFIX` environment variable can defined (if defined, it should end with `'-'` for naming consistency).
An environment variable called `ENVIRONMENT` should also be defined. It represents the environment for which 
the performance testing resources are created. For example, it could be the name of a Kubernetes namespace.

The bucket created will be called:
`${PREFIX}${ENVIRONMENT}-performance-tests`

Managed policies are also created:

* `${PREFIX}${ENVIRONMENT}-performance-test-bucket-writeonly` allowing to write to the S3 bucket and intended to be used by the
performance tool
* `${PREFIX}${ENVIRONMENT}-performance-tests-bucket-readonly` allowing a user to read the reports
* `${PREFIX}${ENVIRONMENT}-performance-tests-bucket-admin` allowing an admin to read and delete S3 objets (but not write)

## Creating the resources

```bash
# define PREFIX and ENVIRONMENT variables
# PREFIX can be empty but ENVIRONMENT should not
aws cloudformation create-change-set --stack-name "${PREFIX}${ENVIRONMENT}-perf-testing" \
  --change-set-name=perf-testing-$RANDOM \
  --change-set-type=CREATE \
  --capabilities CAPABILITY_NAMED_IAM \
  --template-body "$(python generate_cf_template.py)" \
  --parameters ParameterKey=Prefix,ParameterValue=${PREFIX} \
  ParameterKey=Environment,ParameterValue=${ENVIRONMENT}
```

## Testing

Chef Inspec is used to test the resources.

Assuming credentials are available as `AWS_*` environment variables, the following will test the AWS resources:

```bash
cat <<EOF > attributes.yml
prefix: "${PREFIX}"
environment: "${ENVIRONMENT}"
EOF
inspec exec perf-test-inspec --input-file=attributes.yml --target aws://
```
