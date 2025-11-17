/**
 * Template Builder - Fluent API for building templates
 */

import { Step, StepType, CopyOptions, ReadyCheck, BuildOptions, BuildResult, RegistryAuth, GCPRegistryAuth, AWSRegistryAuth } from './types.js';
import { buildTemplate } from './build-flow.js';
import * as fs from 'fs';
import * as path from 'path';

export class Template {
  private fromImage?: string;
  private registryAuth?: RegistryAuth;
  private steps: Step[] = [];
  private startCmd?: string;
  private readyCheck?: ReadyCheck;
  
  /**
   * Create a new template builder
   * 
   * @param fromImage - Optional base Docker image (e.g., "python:3.11-slim", "ubuntu:22.04")
   */
  constructor(fromImage?: string) {
    this.fromImage = fromImage;
  }
  
  // ==================== Base Images ====================
  
  /**
   * Start from Ubuntu base image
   */
  fromUbuntuImage(version: string): Template {
    this.fromImage = `ubuntu:${version}`;
    return this;
  }
  
  /**
   * Start from Python base image
   */
  fromPythonImage(version: string): Template {
    this.fromImage = `python:${version}`;
    return this;
  }
  
  /**
   * Use a Node.js base image (Debian-based)
   * 
   * Note: Only Debian-based Node.js images are supported. Alpine variants are not compatible
   * with our VM agent system due to musl libc limitations.
   * 
   * @param version - Node.js version (e.g., '18', '20', '22')
   * @returns Template builder for method chaining
   * 
   * @example
   * template.fromNodeImage('20');  // Uses ubuntu/node:20-22.04_edge
   * 
   * @see https://hub.docker.com/r/ubuntu/node
   */
  fromNodeImage(version: string): Template {
    this.fromImage = `ubuntu/node:${version}-22.04_edge`;
    return this;
  }
  
  /**
   * Use a Docker image from a private registry with basic authentication
   * 
   * @param image - Docker image URL (e.g., "registry.example.com/myimage:tag")
   * @param auth - Registry credentials (username and password/token)
   * @returns Template builder for method chaining
   * 
   * @example
   * // Docker Hub private repository
   * template.fromPrivateImage('myuser/private-app:v1', {
   *   username: 'myuser',
   *   password: process.env.DOCKER_HUB_TOKEN
   * });
   * 
   * @example
   * // GitLab Container Registry
   * template.fromPrivateImage('registry.gitlab.com/mygroup/myproject/app:latest', {
   *   username: 'gitlab-ci-token',
   *   password: process.env.CI_JOB_TOKEN
   * });
   */
  fromPrivateImage(image: string, auth: RegistryAuth): Template {
    this.fromImage = image;
    this.registryAuth = auth;
    return this;
  }
  
  /**
   * Use a Docker image from Google Container Registry (GCR) or Artifact Registry
   * 
   * @param image - GCP registry image URL (e.g., "gcr.io/myproject/myimage:tag" or "us-docker.pkg.dev/myproject/myrepo/myimage:tag")
   * @param auth - GCP service account credentials
   * @returns Template builder for method chaining
   * 
   * @example
   * // With service account JSON file path
   * template.fromGCPPrivateImage('gcr.io/myproject/api-server:v1', {
   *   serviceAccountJSON: './service-account.json'
   * });
   * 
   * @example
   * // With service account JSON object
   * const serviceAccount = JSON.parse(process.env.GCP_SERVICE_ACCOUNT);
   * template.fromGCPPrivateImage('us-docker.pkg.dev/myproject/myrepo/app:latest', {
   *   serviceAccountJSON: serviceAccount
   * });
   */
  fromGCPPrivateImage(image: string, auth: GCPRegistryAuth): Template {
    let serviceAccount: any;
    
    if (typeof auth.serviceAccountJSON === 'string') {
      // It's a file path
      const filePath = path.resolve(auth.serviceAccountJSON);
      const fileContent = fs.readFileSync(filePath, 'utf-8');
      serviceAccount = JSON.parse(fileContent);
    } else {
      // It's already an object
      serviceAccount = auth.serviceAccountJSON;
    }
    
    // GCP uses _json_key as username and full JSON as password
    const registryAuth: RegistryAuth = {
      username: '_json_key',
      password: JSON.stringify(serviceAccount),
    };
    
    this.fromImage = image;
    this.registryAuth = registryAuth;
    return this;
  }
  
  /**
   * Use a Docker image from AWS Elastic Container Registry (ECR)
   * 
   * The backend will handle ECR authentication token exchange using the provided credentials.
   * 
   * @param image - ECR image URL (e.g., "123456789012.dkr.ecr.us-west-2.amazonaws.com/myapp:latest")
   * @param auth - AWS IAM credentials with ECR pull permissions
   * @returns Template builder for method chaining
   * 
   * @example
   * template.fromAWSPrivateImage('123456789012.dkr.ecr.us-west-2.amazonaws.com/myapp:v1', {
   *   accessKeyId: process.env.AWS_ACCESS_KEY_ID,
   *   secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
   *   region: 'us-west-2'
   * });
   * 
   * @example
   * // With session token for temporary credentials
   * template.fromAWSPrivateImage('123456789012.dkr.ecr.us-east-1.amazonaws.com/api:latest', {
   *   accessKeyId: process.env.AWS_ACCESS_KEY_ID,
   *   secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
   *   region: 'us-east-1',
   *   sessionToken: process.env.AWS_SESSION_TOKEN
   * });
   */
  fromAWSPrivateImage(image: string, auth: AWSRegistryAuth): Template {
    // Store AWS credentials - backend will handle ECR token exchange
    this.fromImage = image;
    this.registryAuth = {
      username: auth.accessKeyId,
      password: auth.secretAccessKey,
    };
    return this;
  }
  
  // ==================== File Operations ====================
  
  /**
   * Copy files to the template
   * 
   * @param src - Source file(s) or directory to copy (string or array of strings)
   * @param dest - Destination path in the template
   * @param options - Optional copy options (owner, permissions)
   * @returns Template builder for method chaining
   * 
   * @example
   * // Copy single file
   * template.copy('app.py', '/app/app.py');
   * 
   * @example
   * // Copy directory
   * template.copy('src/', '/app/src/');
   * 
   * @example
   * // Copy multiple files
   * template.copy(['file1.py', 'file2.py'], '/app/');
   * 
   * @example
   * // Copy with options
   * template.copy('config.json', '/etc/app/config.json', {
   *   owner: 'appuser:appgroup',
   *   permissions: '0644'
   * });
   */
  copy(src: string | string[], dest: string, options?: CopyOptions): Template {
    const sources = Array.isArray(src) ? src : [src];
    
    this.steps.push({
      type: StepType.COPY,
      args: [sources.join(','), dest],
      copyOptions: options,
      // filesHash will be calculated during build
    });
    return this;
  }
  
  // ==================== Commands ====================
  
  /**
   * Run a command during build
   */
  runCmd(cmd: string): Template {
    this.steps.push({
      type: StepType.RUN,
      args: [cmd],
    });
    return this;
  }
  
  // ==================== Environment ====================
  
  /**
   * Set an environment variable
   */
  setEnv(key: string, value: string): Template {
    this.steps.push({
      type: StepType.ENV,
      args: [key, value],
    });
    return this;
  }
  
  /**
   * Set multiple environment variables
   */
  setEnvs(vars: Record<string, string>): Template {
    for (const [key, value] of Object.entries(vars)) {
      this.setEnv(key, value);
    }
    return this;
  }
  
  // ==================== Working Directory ====================
  
  /**
   * Set working directory
   */
  setWorkdir(dir: string): Template {
    this.steps.push({
      type: StepType.WORKDIR,
      args: [dir],
    });
    return this;
  }
  
  // ==================== User ====================
  
  /**
   * Set user
   */
  setUser(user: string): Template {
    this.steps.push({
      type: StepType.USER,
      args: [user],
    });
    return this;
  }
  
  // ==================== Smart Helpers ====================
  
  /**
   * Install packages with apt
   * 
   * @example
   * .aptInstall('curl', 'git', 'vim')  // Multiple args
   * .aptInstall(['curl', 'git', 'vim'])  // Array
   * .aptInstall('curl').aptInstall('git')  // Chained
   */
  aptInstall(...packages: (string | string[])[]): Template {
    // Flatten arguments
    const pkgList: string[] = [];
    for (const pkg of packages) {
      if (Array.isArray(pkg)) {
        pkgList.push(...pkg);
      } else {
        pkgList.push(pkg);
      }
    }
    
    if (pkgList.length === 0) {
      throw new Error('aptInstall requires at least one package');
    }
    
    const pkgs = pkgList.join(' ');
    this.runCmd(`apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y ${pkgs}`);
    return this;
  }
  
  /**
   * Install Python packages with pip
   * 
   * @example
   * .pipInstall('numpy', 'pandas')  // Multiple args
   * .pipInstall(['numpy', 'pandas'])  // Array
   * .pipInstall('numpy').pipInstall('pandas')  // Chained
   * .pipInstall()  // Install from requirements.txt
   */
  pipInstall(...packages: (string | string[])[]): Template {
    // Handle no args (requirements.txt)
    if (packages.length === 0) {
      this.runCmd('/usr/local/bin/pip3 install --no-cache-dir -r requirements.txt');
      return this;
    }
    
    // Flatten arguments
    const pkgList: string[] = [];
    for (const pkg of packages) {
      if (Array.isArray(pkg)) {
        pkgList.push(...pkg);
      } else {
        pkgList.push(pkg);
      }
    }
    
    if (pkgList.length === 0) {
      throw new Error('pipInstall requires at least one package or no args for requirements.txt');
    }
    
    const pkgs = pkgList.join(' ');
    // Use full path for pip (works after systemd restart)
    this.runCmd(`/usr/local/bin/pip3 install --no-cache-dir ${pkgs}`);
    return this;
  }
  
  /**
   * Install Node packages with npm
   * 
   * @example
   * .npmInstall('typescript', 'tsx')  // Multiple args
   * .npmInstall(['typescript', 'tsx'])  // Array
   * .npmInstall('typescript').npmInstall('tsx')  // Chained
   * .npmInstall()  // Install from package.json
   */
  npmInstall(...packages: (string | string[])[]): Template {
    // Handle no args (package.json)
    if (packages.length === 0) {
      this.runCmd('/usr/local/bin/npm install');
      return this;
    }
    
    // Flatten arguments
    const pkgList: string[] = [];
    for (const pkg of packages) {
      if (Array.isArray(pkg)) {
        pkgList.push(...pkg);
      } else {
        pkgList.push(pkg);
      }
    }
    
    if (pkgList.length === 0) {
      throw new Error('npmInstall requires at least one package or no args for package.json');
    }
    
    const pkgs = pkgList.join(' ');
    // Use full path for npm (works after systemd restart)
    this.runCmd(`/usr/local/bin/npm install -g ${pkgs}`);
    return this;
  }
  
  /**
   * Install Go packages
   */
  goInstall(packages: string[]): Template {
    for (const pkg of packages) {
      this.runCmd(`go install ${pkg}`);
    }
    return this;
  }
  
  /**
   * Install Rust packages with cargo
   */
  cargoInstall(packages: string[]): Template {
    for (const pkg of packages) {
      this.runCmd(`cargo install ${pkg}`);
    }
    return this;
  }
  
  /**
   * Clone a git repository
   */
  gitClone(url: string, dest: string): Template {
    this.runCmd(`git clone ${url} ${dest}`);
    return this;
  }
  
  // ==================== Caching ====================
  
  /**
   * Skip cache for this step
   */
  skipCache(): Template {
    if (this.steps.length > 0) {
      this.steps[this.steps.length - 1].skipCache = true;
    }
    return this;
  }
  
  // ==================== Start Command ====================
  
  /**
   * Set the start command and ready check
   */
  setStartCmd(cmd: string, ready?: ReadyCheck): Template {
    this.startCmd = cmd;
    this.readyCheck = ready;
    return this;
  }
  
  // ==================== Build ====================
  
  /**
   * Get base image
   */
  getFromImage(): string | undefined {
    return this.fromImage;
  }
  
  /**
   * Get registry authentication
   */
  getRegistryAuth(): RegistryAuth | undefined {
    return this.registryAuth;
  }
  
  /**
   * Get all steps (excludes FROM - that's in from_image)
   */
  getSteps(): Step[] {
    return this.steps;
  }
  
  /**
   * Get start command
   */
  getStartCmd(): string | undefined {
    return this.startCmd;
  }
  
  /**
   * Get ready check
   */
  getReadyCheck(): ReadyCheck | undefined {
    return this.readyCheck;
  }
  
  /**
   * Build the template
   */
  static async build(template: Template, options: BuildOptions): Promise<BuildResult> {
    return buildTemplate(template, options);
  }
}

// Factory function
export function createTemplate(fromImage?: string): Template {
  return new Template(fromImage);
}

