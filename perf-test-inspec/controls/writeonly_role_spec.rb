prefix = attribute('prefix')
environment = attribute('environment')
bucket_name = "#{prefix}#{environment}-performance-tests"
role_name = "#{bucket_name}-bucket-writeonly"

control "#{role_name}-least-privilege" do
  impact 0.7                                # The criticality, if this control fails.
  title 'Check writeonly role privileges'             # A human-readable title
  desc 'Check that the writeonly role associated with the bucket applies the principle of least privilege'

  describe aws_iam_role(role_name) do
    it { should exist }

    # attachment of policy to role is described in policy spec
  end
end