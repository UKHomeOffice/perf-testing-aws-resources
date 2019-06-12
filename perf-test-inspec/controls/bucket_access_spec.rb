prefix = attribute('prefix')
environment = attribute('environment')
bucket_name = "#{prefix}#{environment}-performance-tests"

bucket = aws_s3_bucket(bucket_name)

control 'bucket-access-controls' do
  impact 1.0                                # The criticality, if this control fails.
  title 'Check access controls for the bucket'             # A human-readable title
  desc 'Check that the bucket is not public and that all access is handled through IAM policies'

  # http://inspec.io/docs/reference/resources/aws_s3_bucket
  describe bucket do
    it { should exist }

    it { should_not be_public }

    it { should have_default_encryption_enabled }

    its(:bucket_policy) { should be_empty }
  end

  # http://inspec.io/docs/reference/resources/aws_s3_bucket
  describe bucket.bucket_acl do
    # only the canonical user should be listed in the ACLs
    its(:length) { should be == 1 }
  end
end