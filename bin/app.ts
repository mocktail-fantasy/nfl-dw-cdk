import { App } from 'aws-cdk-lib';
import { DataWarehouseStack } from '../lib/dw-stack';

const app = new App();

new  DataWarehouseStack(app, 'DataWarehouseStack');

app.synth();
