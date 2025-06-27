import { Stack, StackProps, SecretValue } from "aws-cdk-lib";
import { Construct } from "constructs";
import * as codepipeline from "aws-cdk-lib/aws-codepipeline";
import * as codepipeline_actions from "aws-cdk-lib/aws-codepipeline-actions";
import * as codebuild from "aws-cdk-lib/aws-codebuild";
import * as iam from 'aws-cdk-lib/aws-iam';


export class PipelineStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const sourceOutput = new codepipeline.Artifact();

    const deployProject = new codebuild.PipelineProject(this, "CDKPipelineProject", {
      projectName: "CdkPipelineProject",
      description: "Synthesizes and deploys the CDK app",
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_7_0,
      },
      buildSpec: codebuild.BuildSpec.fromObject({
        version: "0.2",
        phases: {
          install: {
            "runtime-versions": {
              nodejs: "20",
            },
            commands: [
              "npm install -g aws-cdk@latest",
              "npm ci",
            ],
          },
          build: {
            commands: [
              "npx cdk deploy --all --require-approval never"
            ],
          },
        },
      }),
    });
    
    deployProject.addToRolePolicy(new iam.PolicyStatement({
        actions: [
          "cloudformation:*",
          "s3:*",
          "iam:PassRole",
          "ec2:Describe*",
          "lambda:*",
          "logs:*",
          "sts:GetCallerIdentity",
        ],
        resources: ["*"],
      }));
      

    const sourceAction = new codepipeline_actions.GitHubSourceAction({
      actionName: 'GitHub_Source',
      owner: 'mocktail-fantasy',
      repo: 'nfl-dw-cdk',
      oauthToken: SecretValue.secretsManager('GitHubOAuthToken'),
      output: sourceOutput,
      branch: 'main',
    });

    const deployAction = new codepipeline_actions.CodeBuildAction({
      actionName: "DeployCdk",
      project: deployProject,
      input: sourceOutput,
    });

    new codepipeline.Pipeline(this, "Pipeline", {
      pipelineType: codepipeline.PipelineType.V2,
      pipelineName: "Pipeline",
      stages: [
        {
          stageName: "Source",
          actions: [sourceAction],
        },
        {
          stageName: "Deploy",
          actions: [deployAction],
        },
      ],
    });
  }
}
