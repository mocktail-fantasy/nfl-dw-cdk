import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as events from 'aws-cdk-lib/aws-events';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import { SecretValue } from 'aws-cdk-lib';
import { RemovalPolicy, Stack, StackProps, Duration, Size } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class DataWarehouseStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const s3Bucket = new s3.Bucket(this, "nfl-data-bucket", {
      bucketName: "nfl-data-bucket",
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const s3Lambda = new lambda.Function(this, 'LambdaFunction', {
      runtime: lambda.Runtime.PYTHON_3_9,
      code: lambda.Code.fromAsset(path.join(__dirname, '..'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_9.bundlingImage,
          command: [
            'bash', '-c', [
              'cp -R /asset-input/lambdas/update_s3/* /asset-output/',
              'cp -R /asset-input/shared/ /asset-output/',
            ].join(' && ')
          ],
        },
        exclude: ['.env', '**/*.ts']
      }),
      memorySize: 3008,
      ephemeralStorageSize: Size.mebibytes(1024), // Ephemeral storage size in MB
      timeout: Duration.seconds(900),
      environment: {
        "NFL_DATA_BUCKET": s3Bucket.bucketName
      },
      handler: 'lambda_function.lambda_handler',
    });

    s3Bucket.grantPut(s3Lambda);
    s3Bucket.grantReadWrite(s3Lambda)

    const rule = new events.Rule(this, 'ScheduleRule', {
      schedule: events.Schedule.cron({ minute: '0', hour: '12' }),
    });

    rule.addTarget(new targets.LambdaFunction(s3Lambda));

    const vpc = new ec2.Vpc(this, 'DwVpc', {
      maxAzs: 2, 
      subnetConfiguration: [
        {
          name: 'public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          name: 'private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
      ],
    });

    const rdsSecurityGroup = new ec2.SecurityGroup(this, 'RDSSecurityGroup', {
      vpc,
      description: 'Security group for RDS PostgreSQL instance',
      allowAllOutbound: true,
    });

    const ec2SecurityGroup = new ec2.SecurityGroup(this, 'EC2SecurityGroup', {
      vpc,
      description: 'Security group for EC2',
      allowAllOutbound: true,
    });

    const codeBuildSecurityGroup = new ec2.SecurityGroup(this, 'CodeBuildSecurityGroup', {
      vpc,
      description: 'Security Group for CodeBuild',
      allowAllOutbound: true,
    });

    ec2SecurityGroup.addIngressRule(
      ec2.Peer.ipv4('0.0.0.0/0'),
      ec2.Port.tcp(22),
      'Allow SSH access'
    );

    rdsSecurityGroup.addIngressRule(ec2SecurityGroup, ec2.Port.tcp(5432), 'Allow PostgreSQL access from EC2 instance');
    rdsSecurityGroup.addIngressRule(codeBuildSecurityGroup, ec2.Port.tcp(5432), 'Allow PostgreSQL access from CodeBuild');

    const rdsRole = new iam.Role(this, 'RdsS3ReadRole', {
      assumedBy: new iam.ServicePrincipal('rds.amazonaws.com'),
      description: 'Allows RDS instances to access S3 bucket',
    });

    s3Bucket.grantRead(rdsRole);

    const parameterGroup = new rds.ParameterGroup(this, 'ParameterGroup', {
      engine: rds.DatabaseInstanceEngine.postgres({ version: rds.PostgresEngineVersion.VER_15_4}),
      parameters: {
        'shared_preload_libraries': 'pg_cron',
        'cron.database_name': 'mocktailDWH', 
      },
    });

    const rdsInstance = new rds.DatabaseInstance(this, 'dw', {
      engine: rds.DatabaseInstanceEngine.postgres({ version: rds.PostgresEngineVersion.VER_15_4}),
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
      credentials: rds.Credentials.fromGeneratedSecret('postgres'),
      databaseName: 'mocktailDWH',
      vpc,
      securityGroups: [rdsSecurityGroup],
      s3ImportRole: rdsRole,
      removalPolicy: RemovalPolicy.DESTROY,
      deletionProtection: false,
      parameterGroup: parameterGroup
    });

    const bastion = new ec2.Instance(this, 'BastionHost', {
      vpc,
      instanceType: new ec2.InstanceType('t3.micro'),
      machineImage: new ec2.AmazonLinuxImage(),
      securityGroup: ec2SecurityGroup,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
      keyName: 'dw-bastion-admin', // created in the console
    });

    // Create CI/CD Pipeline
    const sourceArtifact = new codepipeline.Artifact();

    const sourceAction = new codepipeline_actions.GitHubSourceAction({
      actionName: 'GitHub_Source',
      owner: 'mocktail-fantasy',
      repo: 'dwh-sql', // Replace with your repository name
      oauthToken: SecretValue.secretsManager('GitHubOAuthToken'), // This was created manually in the AWS Secrets Manager console
      output: sourceArtifact,
      branch: 'main',
    });

    const buildProject = new codebuild.PipelineProject(this, 'SQLBuildProject', {
        projectName: 'SQLBuildProject',
        description: 'Builds SQL scripts',
        vpc: vpc,
        securityGroups: [codeBuildSecurityGroup],
        environment: {
          buildImage: codebuild.LinuxBuildImage.STANDARD_5_0,
        },
        buildSpec: codebuild.BuildSpec.fromSourceFilename('buildspec.yml'), 
      });

    rdsInstance.secret?.grantRead(buildProject);

    const buildAction = new codepipeline_actions.CodeBuildAction({
      actionName: 'Build',
      project: buildProject,
      input: sourceArtifact,
    });

    new codepipeline.Pipeline(this, 'Pipeline', {
      pipelineName: 'MyRDSUpdatePipeline',
      stages: [
        {
          stageName: 'Source',
          actions: [sourceAction],
        },
        {
          stageName: 'Build',
          actions: [buildAction],
        },
      ],
    });

    }

}
