# SubModel CLI Usage Guide

This document explains how to use the command line tools provided by SubModel SDK.

## Environment Setup

First, set up authentication information using environment variables or command line parameters:

```bash
# Using environment variables
export SUBMODEL_TOKEN="your-token"
export SUBMODEL_API_KEY="your-api-key"

# Or provide in command
submodel --token "your-token" <command>
submodel --api-key "your-api-key" <command>
```

## User Authentication

### Register Account
```bash
submodel auth register <username> <password>
```

### Login Account
```bash
submodel auth login <username> <password>
```

### Get User Information
```bash
submodel auth info
```

## Instance Management

### Create Instance
```bash
# Create basic instance
submodel instance create

# Custom configuration
submodel instance create \
    --billing-method payg \
    --mode pod \
    --plan gpu-rtx4090-24g-1 \
    --image ubuntu-22.04 \
    --pod-num 1
```

### View Instance List
```bash
# Default view
submodel instance list

# Page query
submodel instance list --page 1 --limit 20

# Query by mode
submodel instance list --mode serverless
```

### Get Instance Details
```bash
submodel instance get <instance-id>
```

### Control Instance
```bash
# Start instance
submodel instance control <instance-id> run

# Stop instance
submodel instance control <instance-id> stop

# Release instance
submodel instance control <instance-id> release

# Restart instance
submodel instance control <instance-id> restart
```

## Device Management

### View Device List
```bash
# Default view
submodel device list

# Page query
submodel device list --page 1 --limit 20
```

### Get Device Details
```bash
submodel device get <device-id>
```

## Debug Mode

Add `--debug` parameter to view detailed request and response information:

```bash
submodel --debug instance list
```

## Common Issues

1. Authentication Failed
```bash
# Check authentication status
submodel auth info
```

2. Instance Creation Failed
```bash
# Use debug mode to view detailed error information
submodel --debug instance create
```

3. Command Help
```bash
# View all commands
submodel --help

# View specific command help
submodel instance --help
submodel instance create --help
```