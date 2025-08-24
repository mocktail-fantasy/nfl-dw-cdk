import { App } from 'aws-cdk-lib';
import { DataWarehouseStack } from '../lib/dw-stack';
import { PipelineStack } from '../lib/cdk-pipeline-stacks';

const app = new App();

new  DataWarehouseStack(app, 'DataWarehouseStack',  {
    env: {
      account: process.env.CDK_DEFAULT_ACCOUNT,
      region: process.env.CDK_DEFAULT_REGION,
    },
  },);

new  PipelineStack(app, 'PipelineStack');

app.synth();
