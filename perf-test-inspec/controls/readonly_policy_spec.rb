prefix = attribute('prefix')
environment = attribute('environment')
bucket_name = "#{prefix}#{environment}-performance-tests"
policy_name = "#{bucket_name}-bucket-readonly"
role_name = policy_name

control 'bucket-readonly-policy-least-privilege' do
  impact 0.7                                # The criticality, if this control fails.
  title 'Check read-only policy privileges'             # A human-readable title
  desc 'Check that the read-only policy associated with the bucket applies the principle of least privilege'

  describe aws_iam_policy(policy_name) do
    it { should exist }
    
    # should allow to s3:List* on the bucket or it objects
    it { should have_statement(
      Effect: 'Allow',
      Action: /^s3:List/,
      Resource: /^arn:aws:s3:::#{bucket_name}/
    )}
    
    # should allow to s3:Get* on the bucket or it objects
    it { should have_statement(
      Effect: 'Allow',
      Action: /^s3:Get/,
      Resource: /^arn:aws:s3:::#{bucket_name}/
    )}
    
    # should not allow any actions on resources other than the bucket or its objects
    # this cover not being able to perform actions on services other than s3
    it { should_not have_statement(
      Effect: 'Allow',
      Resource: /^(?!arn:aws:s3:::#{bucket_name}).*$/
    )}

    # should not allow s3:Put* actions on the bucket or objects
    it { should_not have_statement(
      Effect: 'Allow',
      Action: /^s3:Put/,
      Resource: /^arn:aws:s3:::#{bucket_name}/
    )}

    # should not allow s3:Delete* actions on the bucket or objects
    it { should_not have_statement(
      Effect: 'Allow',
      Action: /^s3:Delete/,
      Resource: /^arn:aws:s3:::#{bucket_name}/
    )}

    its(:attached_roles) {should include role_name}
  end
end